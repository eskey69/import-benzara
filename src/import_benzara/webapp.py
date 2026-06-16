from __future__ import annotations

import json
import os
from functools import wraps
from pathlib import Path
from secrets import token_hex
from typing import Any, Callable

from flask import Flask, Response, abort, flash, redirect, render_template, request, send_file, url_for

from .config import StockFeedConfig, WebAppConfig
from .stock_pipeline import generate_stock_feed
from .storage import (
    build_app_paths,
    copy_run_to_latest,
    ensure_app_directories,
    file_info,
    latest_uploaded_file,
    new_run_id,
    save_uploaded_file,
)


DOWNLOADABLE_LATEST_FILES = {
    "feed.xml",
    "feed.summary.json",
    "feed.inventory-only.csv",
    "feed.catalog-only.csv",
}


def load_web_config(data_root: Path | None = None) -> WebAppConfig:
    resolved_data_root = data_root or Path(os.environ.get("IMPORT_BENZARA_DATA_DIR", Path.cwd() / "data"))
    return WebAppConfig(
        data_root=resolved_data_root,
        secret_key=os.environ.get("IMPORT_BENZARA_SECRET_KEY", token_hex(24)),
        minimum_stock_threshold=int(os.environ.get("IMPORT_BENZARA_MIN_STOCK_THRESHOLD", "10")),
        admin_username=os.environ.get("IMPORT_BENZARA_ADMIN_USER"),
        admin_password=os.environ.get("IMPORT_BENZARA_ADMIN_PASSWORD"),
    )


def create_app(data_root: Path | None = None) -> Flask:
    config = load_web_config(data_root)
    paths = build_app_paths(config.data_root)
    ensure_app_directories(paths)

    app = Flask(__name__)
    app.secret_key = config.secret_key
    app.config["IMPORT_BENZARA_WEB_CONFIG"] = config
    app.config["IMPORT_BENZARA_PATHS"] = paths

    def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            if not config.admin_username or not config.admin_password:
                return view(*args, **kwargs)

            auth = request.authorization
            if auth and auth.username == config.admin_username and auth.password == config.admin_password:
                return view(*args, **kwargs)

            return Response(
                "Authentication required",
                401,
                {"WWW-Authenticate": 'Basic realm="Import Benzara Admin"'},
            )

        return wrapped

    def latest_catalog() -> Path | None:
        return latest_uploaded_file(paths.uploads_catalog, (".xlsx",))

    def latest_inventory() -> Path | None:
        return latest_uploaded_file(paths.uploads_inventory, (".csv",))

    def latest_summary() -> dict[str, Any] | None:
        summary_path = paths.generated_latest / "feed.summary.json"
        if not summary_path.exists():
            return None
        return json.loads(summary_path.read_text(encoding="utf-8"))

    def recent_runs(limit: int = 10) -> list[dict[str, Any]]:
        if not paths.generated_runs.exists():
            return []

        runs: list[dict[str, Any]] = []
        for run_dir in sorted(
            [path for path in paths.generated_runs.iterdir() if path.is_dir()],
            key=lambda path: path.name,
            reverse=True,
        )[:limit]:
            files = sorted([file.name for file in run_dir.iterdir() if file.is_file()])
            runs.append({"id": run_dir.name, "files": files})
        return runs

    @app.get("/")
    @admin_required
    def dashboard() -> str:
        return render_template(
            "dashboard.html",
            config=config,
            catalog=file_info(latest_catalog()),
            inventory=file_info(latest_inventory()),
            latest_summary=latest_summary(),
            latest_files=sorted([name for name in DOWNLOADABLE_LATEST_FILES if (paths.generated_latest / name).exists()]),
            recent_runs=recent_runs(),
            public_feed_url=url_for("public_feed", _external=True),
        )

    @app.post("/upload/catalog")
    @admin_required
    def upload_catalog() -> Response:
        uploaded = request.files.get("catalog")
        if uploaded is None or not uploaded.filename:
            flash("Wybierz plik katalogowy XLSX.", "error")
            return redirect(url_for("dashboard"))
        if not uploaded.filename.lower().endswith(".xlsx"):
            flash("Plik katalogowy musi miec rozszerzenie .xlsx.", "error")
            return redirect(url_for("dashboard"))

        saved_path = save_uploaded_file(uploaded, paths.uploads_catalog)
        flash(f"Zapisano katalog: {saved_path.name}", "success")
        return redirect(url_for("dashboard"))

    @app.post("/upload/inventory")
    @admin_required
    def upload_inventory() -> Response:
        uploaded = request.files.get("inventory")
        if uploaded is None or not uploaded.filename:
            flash("Wybierz plik inventory CSV.", "error")
            return redirect(url_for("dashboard"))
        if not uploaded.filename.lower().endswith(".csv"):
            flash("Plik inventory musi miec rozszerzenie .csv.", "error")
            return redirect(url_for("dashboard"))

        saved_path = save_uploaded_file(uploaded, paths.uploads_inventory)
        flash(f"Zapisano inventory: {saved_path.name}", "success")
        return redirect(url_for("dashboard"))

    @app.post("/generate")
    @admin_required
    def generate() -> Response:
        catalog = latest_catalog()
        inventory = latest_inventory()
        if catalog is None:
            flash("Brak katalogu XLSX do generowania feedu.", "error")
            return redirect(url_for("dashboard"))
        if inventory is None:
            flash("Brak pliku inventory CSV do generowania feedu.", "error")
            return redirect(url_for("dashboard"))

        threshold_text = (request.form.get("minimum_stock_threshold") or str(config.minimum_stock_threshold)).strip()
        try:
            threshold = int(threshold_text)
        except ValueError:
            flash("Prog stocku musi byc liczba calkowita.", "error")
            return redirect(url_for("dashboard"))

        run_id = new_run_id()
        run_dir = paths.generated_runs / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        feed_path = run_dir / "feed.xml"
        summary_path = run_dir / "feed.summary.json"
        inventory_only_path = run_dir / "feed.inventory-only.csv"
        catalog_only_path = run_dir / "feed.catalog-only.csv"

        try:
            summary = generate_stock_feed(
                StockFeedConfig(
                    inventory_csv=inventory,
                    catalog_xlsx=catalog,
                    output_xml=feed_path,
                    summary_json=summary_path,
                    inventory_only_csv=inventory_only_path,
                    catalog_only_csv=catalog_only_path,
                    minimum_stock_threshold=threshold,
                )
            )
        except Exception as exc:  # noqa: BLE001 - dashboard should show the exact processing error.
            flash(f"Generowanie feedu nie powiodlo sie: {exc}", "error")
            return redirect(url_for("dashboard"))

        copy_run_to_latest(run_dir, paths.generated_latest)
        flash(
            "Wygenerowano feed XML. "
            f"Instock: {summary.in_stock_rows}, outofstock: {summary.out_of_stock_rows}, "
            f"wyzerowane progiem: {summary.zeroed_below_threshold_rows}.",
            "success",
        )
        return redirect(url_for("dashboard"))

    @app.get("/feed.xml")
    def public_feed() -> Response:
        feed_path = paths.generated_latest / "feed.xml"
        if not feed_path.exists():
            abort(404, description="Feed has not been generated yet.")
        return send_file(feed_path, mimetype="application/xml", download_name="feed.xml")

    @app.get("/latest/<path:filename>")
    @admin_required
    def download_latest(filename: str) -> Response:
        if filename not in DOWNLOADABLE_LATEST_FILES:
            abort(404)
        path = paths.generated_latest / filename
        if not path.exists():
            abort(404)
        return send_file(path, as_attachment=True, download_name=filename)

    @app.get("/runs/<run_id>/<path:filename>")
    @admin_required
    def download_run_file(run_id: str, filename: str) -> Response:
        if filename not in DOWNLOADABLE_LATEST_FILES:
            abort(404)
        path = paths.generated_runs / run_id / filename
        if not path.exists():
            abort(404)
        return send_file(path, as_attachment=True, download_name=filename)

    @app.get("/healthz")
    def healthz() -> Response:
        return Response("ok", mimetype="text/plain")

    return app

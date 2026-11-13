"""Flask routes for dashboard, transaction import, budgets, and reports."""

import tempfile
from pathlib import Path

import pandas as pd
from flask import (Blueprint, abort, current_app, flash, redirect, render_template,
                   request, send_file, url_for)

from src import database
from src.report_generator import generate_report
from src.web_services import (ALLOWED_CATEGORIES, budget_amount,
                              monthly_budget_results, parse_upload, report_frame,
                              summarize, summarize_month, valid_month)

web = Blueprint("web", __name__)
REPORT_COLUMNS = ["date", "description", "amount", "type", "category"]


def db_path():
    return current_app.config["DATABASE"]


def selected_month():
    value = request.values.get("month", "")
    if value and value != valid_month(value):
        abort(400, "Invalid month format.")
    return valid_month(value)


@web.get("/")
def dashboard():
    month = selected_month()
    frame = database.get_transactions(db_path())
    summary = summarize(frame)
    monthly_summary = summarize_month(frame, month)
    month_label = pd.Timestamp(f"{month}-01").strftime("%B %Y")
    budgets = database.get_budgets(db_path(), month)
    results = monthly_budget_results(frame, budgets, month)
    transactions = database.get_transactions(db_path(), month=month).head(8)
    return render_template("dashboard.html", month=month, month_label=month_label,
                           summary=summary, monthly_summary=monthly_summary,
                           transactions=transactions.to_dict("records"),
                           budget_results=results.to_dict("records"))


@web.route("/transactions", methods=["GET", "POST"])
def transactions():
    month = selected_month()
    if request.method == "POST":
        uploaded = request.files.get("file")
        if not uploaded or not uploaded.filename:
            flash("Choose a CSV file to upload.", "error")
        else:
            try:
                frame = parse_upload(uploaded)
                database.add_transactions(db_path(), frame)
                flash(f"Imported {len(frame)} transactions.", "success")
                return redirect(url_for("web.transactions", month=month))
            except (ValueError, OSError) as error:
                flash(str(error), "error")
    rows = database.get_transactions(
        db_path(), month=month, kind=request.args.get("type"),
        category=request.args.get("category"), search=request.args.get("search", "").strip(),
        start_date=request.args.get("start_date"), end_date=request.args.get("end_date"),
    )
    return render_template("transactions.html", month=month,
                           transactions=rows.to_dict("records"),
                           categories=sorted(ALLOWED_CATEGORIES))


@web.route("/budgets", methods=["GET", "POST"])
def budgets():
    month = selected_month()
    if request.method == "POST":
        category = request.form.get("category", "")
        try:
            if category not in ALLOWED_CATEGORIES:
                raise ValueError("Choose a valid expense category.")
            database.save_budget(db_path(), month, category,
                                 budget_amount(request.form.get("amount")))
            flash("Monthly budget saved.", "success")
            return redirect(url_for("web.budgets", month=month))
        except ValueError as error:
            flash(str(error), "error")
    frame = database.get_transactions(db_path())
    results = monthly_budget_results(frame, database.get_budgets(db_path(), month), month)
    return render_template("budgets.html", month=month,
                           budget_results=results.to_dict("records"),
                           categories=sorted(ALLOWED_CATEGORIES))


@web.get("/reports/monthly.pdf")
def report_download():
    month = selected_month()
    frame = database.get_transactions(db_path(), month=month)
    budgets = database.get_budgets(db_path(), month)
    with tempfile.TemporaryDirectory(prefix="finance-report-") as directory:
        path = Path(directory) / f"financial-report-{month}.pdf"
        # Keep report generation isolated to this month and a private temporary directory.
        normalized_report_frame = report_frame(frame).reindex(
            columns=REPORT_COLUMNS
        )
        generate_report(normalized_report_frame, output_path=path, budgets=budgets)
        payload = path.read_bytes()
    from io import BytesIO
    return send_file(BytesIO(payload), mimetype="application/pdf",
                     as_attachment=True, download_name=f"financial-report-{month}.pdf",
                     max_age=0)

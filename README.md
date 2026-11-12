# Personal Finance & Expense Analytics Tool

## Project Description

A Python-based application that analyzes personal
financial transactions, tracks expenses, and provides
insights through statistical analysis and visualization.

## Technologies Used

- Python 3
- NumPy
- Pandas
- Matplotlib
- Bash
- Git and GitHub
- Flask, SQLite, Chart.js

## Project Structure

- data/: Input transaction datasets
- src/: Application modules
- tests/: Functional tests
- scripts/: Bash automation
- output/: Generated reports and charts

## Installation

Create a virtual environment:

python -m venv .venv

Activate on Windows:

.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

## Execution

python main.py

## Web application

Install dependencies with `pip install -r requirements.txt`, then start the
Flask dashboard from the project root:

```bash
python -m flask --app src.web_app:create_app run --debug
```

The application stores transactions and monthly category budgets in
`instance/finance.sqlite3`. Set `FINANCE_DATABASE` to choose another SQLite
file and `FINANCE_SECRET_KEY` to set the session secret. CSV uploads are limited
to 5 MB and require `date,description,amount,type` columns; dates must be
`YYYY-MM-DD`, and amounts must be positive. The dashboard can download a
month-scoped PDF report. Budgets are unique per month and category.

## Team Members

To be updated.

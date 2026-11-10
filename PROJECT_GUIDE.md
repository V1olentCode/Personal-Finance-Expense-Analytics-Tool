# Personal Finance & Expense Analytics Tool
## Team Development Guide

### 1. Project Overview

We are developing a Python-based Personal Finance & Expense Analytics Tool.

The application will accept financial transaction data in CSV format, process and categorize transactions, calculate financial statistics, monitor budgets, and generate visual reports.

**Main objectives:**
- Load and validate financial transaction data.
- Clean and preprocess datasets.
- Categorize expenses automatically.
- Calculate monthly and category-wise expenditure.
- Detect budget violations.
- Generate charts and financial reports.
- Automate execution using Bash scripts.
- Test and profile the application.

### 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3 | Main programming language |
| NumPy | Numerical computations |
| Pandas | Data processing and analysis |
| Matplotlib | Data visualization |
| Bash | Automation |
| Git & GitHub | Collaboration and version control |
| pytest | Functional testing |
| cProfile | Performance profiling |

### 3. Input Dataset

All members must use the same CSV format.

Filename: `data/transactions.csv`

| Column | Data type | Description |
|---|---|---|
| date | Date | Transaction date (YYYY-MM-DD) |
| description | String | Transaction description |
| amount | Float | Positive transaction amount |
| type | String | income or expense |

Example:

```csv
date,description,amount,type
2026-10-01,Grocery Store,1200,expense
2026-10-02,Uber,300,expense
2026-10-03,Salary,30000,income
```

All amounts are positive. The `type` column determines whether a transaction is income or expenditure.

### 4. Team Responsibilities

#### Member 1 — Data Loading and Cleaning

Branch: `feature/data-processing`

Files owned:
- `src/data_loader.py`

Responsibilities:
- Load CSV datasets using Pandas.
- Handle missing values.
- Remove duplicate transactions.
- Validate dates and amounts.
- Validate transaction types.
- Return a clean Pandas DataFrame.

Required function:

```python
def load_transactions(filepath: str):
    pass

def clean_transactions(df):
    pass
```

#### Member 2 — Expense Categorization and Analytics

Branch: `feature/analytics`

Files owned:
- `src/analytics.py`
- `src/budget.py`

Responsibilities:
- Categorize transactions using keyword matching.
- Calculate total expenditure.
- Calculate monthly expenditure.
- Calculate category-wise expenditure.
- Calculate income and remaining balance.
- Detect budget violations.

Required functions:

```python
def categorize_expenses(df):
    pass

def calculate_total_expenses(df):
    pass

def calculate_monthly_expenses(df):
    pass

def calculate_category_expenses(df):
    pass

def calculate_total_income(df):
    pass

def check_budget(df, budgets):
    pass
```

The categorization function must add a `category` column to the DataFrame.

Income transactions must be classified as `Income`, not as an expense category.

#### Member 3 — Visualization and Reporting

Branch: `feature/visualization`

Files owned:
- `src/visualization.py`
- `src/report_generator.py`

Responsibilities:
- Generate monthly expenditure charts.
- Generate category-wise spending charts.
- Generate budget versus actual spending charts.
- Save charts in the output directory.
- Generate a financial summary report.
- Export the final report as PDF.

Required functions:

```python
def plot_monthly_expenses(df):
    pass

def plot_category_expenses(df):
    pass

def plot_budget_comparison(df, budgets):
    pass

def generate_report(df, output_path):
    pass
```

#### Member 4 — Integration and Automation

Branch: `feature/integration`

Files owned:
- `main.py`
- `scripts/run.sh`
- `scripts/profile.sh`

Responsibilities:
- Integrate all modules.
- Build the main application workflow.
- Coordinate module integration.
- Create Bash automation scripts.
- Run functional tests.
- Perform performance profiling.
- Maintain project documentation.

### 5. Module Communication Rules

To prevent integration conflicts, all members must follow these rules:

1. Transaction data must be represented using Pandas DataFrames.
2. The original columns must remain `date`, `description`, `amount`, and `type`.
3. The cleaning module must return a cleaned DataFrame.
4. The categorization module must return a DataFrame with an additional `category` column.
5. Analytics functions must exclude income when calculating expenses.
6. Dates must be converted into Pandas datetime objects during cleaning.
7. Functions must not unexpectedly modify the input DataFrame.
8. All functions must have meaningful return values and documentation.

### 6. Git Collaboration Rules

Each member has an assigned branch.

| Member | Branch |
|---|---|
| Member 1 | `feature/data-processing` |
| Member 2 | `feature/analytics` |
| Member 3 | `feature/visualization` |
| Member 4 | `feature/integration` |

Rules:

- Never push directly to `main`.
- Work only on your assigned feature branch.
- Commit meaningful changes regularly.
- Push completed work to GitHub.
- Create a Pull Request before merging into `main`.
- Review changes before merging.
- Update your branch with the latest `main` before starting new work.

Example:

```bash
git switch feature/data-processing

git add .
git commit -m "Implement transaction data loading"

git push origin feature/data-processing
```

### 7. Testing Requirements

Use pytest for functional testing.

Test cases should cover:

- Valid CSV input.
- Missing and invalid values.
- Duplicate transactions.
- Incorrect transaction types.
- Expense categorization.
- Monthly expenditure calculations.
- Category-wise calculations.
- Budget violations.
- Empty datasets.

Run tests using:

```bash
pytest -v
```

Every member must contribute tests for their own module.

### 8. Performance Profiling

Use Python's cProfile module.

```bash
python -m cProfile -s cumulative main.py
```

Record the profiling results and identify potential bottlenecks.

### 9. Bash and Unix Requirements

The project must demonstrate:

- Bash automation.
- Automated application execution.
- Performance profiling through scripts.
- Unix commands such as grep, sort, wc, head and cut.

### 10. Final Deliverables

- Working Python application.
- GitHub repository with meaningful commit history.
- README documentation.
- Bash automation scripts.
- Functional test suite.
- Performance profiling results.
- LaTeX technical report.
- Beamer presentation.
- Five-minute live demonstration.

### 11. Important Development Rule

Complete your assigned module independently, test it, document it, and submit a Pull Request.

Do not wait until the final deadline to integrate your code. Integration should happen incrementally throughout development.
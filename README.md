Expense Tracker
A desktop personal finance app built with Python — track spending, set monthly budgets, visualize breakdowns, and export PDF invoices.

Features
Add / Edit / Delete expenses with date, amount, category, and description
12 categories — Food & Dining, Travel, Healthcare, Entertainment, and more
Monthly budgets with live alerts when you go over
Pie chart visualization of spending by category (all-time or per month)
PDF invoice export — professional monthly expense reports
Dashboard — at-a-glance stats: total entries, all-time spend, monthly spend, budget status
Filter by month or category

Requirements
Python 3.8+
The following packages:
matplotlib
reportlab

Install them with:
pip install matplotlib reportlab

tkinter ships with most standard Python installations. If it's missing, install python3-tk via your system package manager.

How it works
expenses_frontend.py: GUI — all Tkinter windows, forms, tables, and charts
expenses_backend.py: Logic — CSV read/write, budget management, chart generation, PDF export
expenses.csv: Auto-created on first run; stores all expense records
budget.json: Auto-created when you set a budget; stores per-month limits

Usage Guide
Adding an Expense
Go to Add Expense in the sidebar. Fill in the date (DD-MM-YYYY format), amount, category, and an optional description. You'll get a budget alert popup if the addition pushes you over your monthly limit.

Setting a Budget
Go to Budget in the sidebar. Select a month, enter an amount, and hit Set Budget. The dashboard and filter views will show remaining or over-budget status in real time.

Exporting a PDF Invoice
Go to Filter Month, select a month, and click ⬇ Download Invoice (PDF). The invoice includes a summary table, total, budget status, and generation timestamp.

Viewing the Pie Chart
Go to Pie Chart. Choose a scope — all-time or a specific month — and hit Refresh. Hover over segments to see category amounts and percentages.

Data Storage
All data is stored locally in flat files — no database, no cloud sync, no account needed.
expenses.csv — one row per expense entry
budget.json — one key per month in MM-YYYY format

Contributing
Pull requests are welcome. For significant changes, open an issue first to discuss what you'd like to change.

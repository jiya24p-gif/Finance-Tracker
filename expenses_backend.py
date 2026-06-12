import csv
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

FILE_NAME = "expenses.csv"
BUDGET_FILE = "budget.json"

CATEGORIES = [
    "Food & Dining",
    "Travel & Transport",
    "Bills & Utilities",
    "Rent / Housing",
    "Groceries",
    "Education",
    "Healthcare",
    "Entertainment",
    "Shopping",
    "Mobile & Internet",
    "Subscriptions",
    "Miscellaneous"
]

if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Amount", "Category", "Description"])


def load_budget():
    if not os.path.exists(BUDGET_FILE):
        return {}
    with open(BUDGET_FILE, "r") as f:
        return json.load(f)

def save_budget(data):
    with open(BUDGET_FILE, "w") as f:
        json.dump(data, f)

def set_budget(month_key, amount):
    budgets = load_budget()
    budgets[month_key] = amount
    save_budget(budgets)

def get_budget(month_key):
    budgets = load_budget()
    return budgets.get(month_key, None)

def get_monthly_total(month_key):
    total = 0
    if not os.path.exists(FILE_NAME):
        return 0
    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if row and len(row) >= 2:
                try:
                    row_date = datetime.strptime(row[0], "%d-%m-%Y")
                    row_month_key = row_date.strftime("%m-%Y")
                    if row_month_key == month_key:
                        total += float(row[1])
                except:
                    continue
    return total

def check_budget_alert(month_key):
    budget = get_budget(month_key)
    if budget is None:
        return None, None, None
    spent = get_monthly_total(month_key)
    return spent >= budget, budget, spent


def read_all_expenses():
    rows = []
    if not os.path.exists(FILE_NAME):
        return rows
    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if row:
                rows.append(row)
    return rows

def write_all_expenses(rows):
    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Amount", "Category", "Description"])
        writer.writerows(rows)


def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def add_expense(date, amount, category, description):
    if not validate_date(date):
        return False, "Invalid date format. Use DD-MM-YYYY."
    try:
        amount = float(amount)
    except:
        return False, "Invalid amount."
    if category not in CATEGORIES:
        return False, "Invalid category."

    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date, amount, category, description])

    row_date = datetime.strptime(date, "%d-%m-%Y")
    month_key = row_date.strftime("%m-%Y")
    over, budget, spent = check_budget_alert(month_key)
    if over is True:
        return True, f"BUDGET_ALERT:₹{spent:.0f} spent of ₹{budget:.0f} budget for {month_key}"
    return True, "Expense added successfully!"

def edit_expense(index, date, amount, category, description):
    rows = read_all_expenses()
    if index < 0 or index >= len(rows):
        return False, "Invalid row index."
    if not validate_date(date):
        return False, "Invalid date format."
    try:
        amount = float(amount)
    except:
        return False, "Invalid amount."
    rows[index] = [date, amount, category, description]
    write_all_expenses(rows)
    return True, "Expense updated successfully!"

def delete_expense(index):
    rows = read_all_expenses()
    if index < 0 or index >= len(rows):
        return False, "Invalid row index."
    rows.pop(index)
    write_all_expenses(rows)
    return True, "Expense deleted successfully!"

def get_all_expenses():
    return read_all_expenses()

def get_expenses_by_category(category):
    return [r for r in read_all_expenses() if r[2] == category]

def get_expenses_by_month(month_key):
    result = []
    for row in read_all_expenses():
        try:
            row_date = datetime.strptime(row[0], "%d-%m-%Y")
            if row_date.strftime("%m-%Y") == month_key:
                result.append(row)
        except:
            continue
    return result

def get_total():
    rows = read_all_expenses()
    return sum(float(r[1]) for r in rows if r)

#pie chart
def get_pie_figure(rows=None):
    if rows is None:
        rows = read_all_expenses()

    category_totals = {}
    for row in rows:
        if len(row) < 3:
            continue
        try:
            category_totals[row[2]] = category_totals.get(row[2], 0) + float(row[1])
        except:
            continue

    fig = Figure(figsize=(6, 5), facecolor="#1a1a2e")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#1a1a2e")

    if not category_totals:
        ax.text(0.5, 0.5, "No expense data\nto visualize yet",
                ha='center', va='center', fontsize=14,
                color='#aaaaaa', transform=ax.transAxes)
        ax.axis('off')
        return fig

    labels = list(category_totals.keys())
    sizes = list(category_totals.values())
    total = sum(sizes)

    colors_list = [
        "#e63946","#2a9d8f","#e9c46a","#f4a261","#264653",
        "#a8dadc","#457b9d","#1d3557","#6a4c93","#f77f00",
        "#4cc9f0","#80b918"
    ][:len(labels)]

    def autopct_fmt(pct):
        val = pct / 100 * total
        return f"₹{val:.0f}\n({pct:.1f}%)"

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct=autopct_fmt,
        startangle=140,
        colors=colors_list,
        pctdistance=0.75,
        wedgeprops=dict(linewidth=1.5, edgecolor="#1a1a2e")
    )

    for at in autotexts:
        at.set_fontsize(7)
        at.set_color("white")

    ax.legend(
        wedges, labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=3,
        fontsize=7,
        frameon=False,
        labelcolor="white"
    )

    ax.set_title("Expense Distribution", color="white", fontsize=13, pad=10)
    ax.axis('equal')
    fig.tight_layout()
    return fig

#Invoice
def generate_invoice(month_key, output_path=None):
    """Generate a PDF invoice for the given month. Returns (True, filepath) or (False, error)."""
    rows = get_expenses_by_month(month_key)
    if not rows:
        return False, "No expenses found for this month."

    if output_path is None:
        output_path = f"Invoice_{month_key.replace('-', '_')}.pdf"

    try:
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('InvTitle',
            fontSize=24, textColor=colors.HexColor("#e63946"),
            fontName="Helvetica-Bold", spaceAfter=10)

        sub_style = ParagraphStyle('InvSub',
            fontSize=10, textColor=colors.HexColor("#888899"),
            fontName="Helvetica", spaceAfter=6)

        label_style = ParagraphStyle('InvLabel',
            fontSize=8, textColor=colors.HexColor("#888899"),
            fontName="Helvetica-Bold")

        value_style = ParagraphStyle('InvValue',
            fontSize=11, textColor=colors.HexColor("#0f0f1a"),
            fontName="Helvetica-Bold")

        normal_style = ParagraphStyle('InvNormal',
            fontSize=9, textColor=colors.HexColor("#0f0f1a"),
            fontName="Helvetica")

        elements = []

        elements.append(Paragraph("EXPENSE INVOICE", title_style))
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph(f"Monthly Report  •  {month_key}", sub_style))
        elements.append(Spacer(1, 0.4*cm))

        budget = get_budget(month_key)
        total = get_monthly_total(month_key)
        generated_on = datetime.now().strftime("%d %b %Y, %I:%M %p")
        over_under = ""
        if budget:
            diff = budget - total
            over_under = f"Rs. {abs(diff):,.2f} {'remaining' if diff >= 0 else 'over budget'}"

        meta_data = [
            [
                Paragraph("MONTH", label_style),
                Paragraph("TOTAL SPENT", label_style),
                Paragraph("BUDGET", label_style),
                Paragraph("STATUS", label_style),
                Paragraph("GENERATED ON", label_style),
            ],
            [
                Paragraph(month_key, value_style),
                Paragraph(f"Rs. {total:,.2f}", value_style),
                Paragraph(f"Rs. {budget:,.2f}" if budget else "Not Set", value_style),
                Paragraph(over_under if over_under else "—", value_style),
                Paragraph(generated_on, value_style),
            ],
        ]

        meta_table = Table(meta_data, colWidths=[2.8*cm, 3.5*cm, 3.2*cm, 4*cm, 4*cm])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#f0f4f8")),
            ("BACKGROUND",   (0, 1), (-1, 1), colors.HexColor("#ffffff")),
            ("BOX",          (0, 0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
            ("INNERGRID",    (0, 0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
            ("TOPPADDING",   (0, 0), (-1,-1), 8),
            ("BOTTOMPADDING",(0, 0), (-1,-1), 8),
            ("LEFTPADDING",  (0, 0), (-1,-1), 8),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 0.6*cm))


        header_row = [[
            Paragraph("#", label_style),
            Paragraph("Date", label_style),
            Paragraph("Category", label_style),
            Paragraph("Description", label_style),
            Paragraph("Amount (Rs.)", label_style),
        ]]

        table_rows = []
        for i, row in enumerate(rows):
            table_rows.append([
                Paragraph(str(i + 1), normal_style),
                Paragraph(row[0], normal_style),
                Paragraph(row[2], normal_style),
                Paragraph(row[3] if len(row) > 3 else "", normal_style),
                Paragraph(f"{float(row[1]):,.2f}", normal_style),
            ])

        full_data = header_row + table_rows
        col_widths = [1*cm, 3*cm, 4.5*cm, 6*cm, 3*cm]
        expense_table = Table(full_data, colWidths=col_widths, repeatRows=1)

        row_styles = [
            ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#e63946")),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("ALIGN",         (4, 0), (4, -1),  "RIGHT"),
            ("ALIGN",         (0, 0), (0, -1),  "CENTER"),
            ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (4, 0), (4, -1),  8),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ]

        for i in range(1, len(table_rows) + 1):
            bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            row_styles.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(bg)))

        expense_table.setStyle(TableStyle(row_styles))
        elements.append(expense_table)
        elements.append(Spacer(1, 0.5*cm))


        total_data = [
            ["", "", "", Paragraph("TOTAL", label_style), Paragraph(f"Rs. {total:,.2f}", value_style)],
        ]
        total_table = Table(total_data, colWidths=col_widths)
        total_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#fff3f4")),
            ("LINEABOVE",     (0, 0), (-1,  0), 1.5, colors.HexColor("#e63946")),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("ALIGN",         (4, 0), (4,  -1), "RIGHT"),
            ("ALIGN",         (3, 0), (3,  -1), "RIGHT"),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 0.8*cm))


        footer_style = ParagraphStyle('Footer',
            fontSize=8, textColor=colors.HexColor("#aaaaaa"),
            fontName="Helvetica", alignment=1)
        elements.append(Paragraph(
            f"Generated by Expense Tracker  •  {generated_on}  •  This is a system-generated invoice.",
            footer_style))

        doc.build(elements)
        return True, output_path

    except Exception as e:
        return False, str(e)
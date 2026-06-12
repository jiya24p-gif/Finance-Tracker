import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import expenses_backend as backend

BG        = "#0f0f1a"
PANEL     = "#1a1a2e"
CARD      = "#16213e"
ACCENT    = "#e63946"
ACCENT2   = "#4cc9f0"
TEXT      = "#eaeaea"
SUBTEXT   = "#888899"
SUCCESS   = "#2a9d8f"
WARNING   = "#e9c46a"
FONT_H    = ("Georgia", 22, "bold")
FONT_SUB  = ("Georgia", 12)
FONT_BODY = ("Consolas", 10)
FONT_BTN  = ("Consolas", 10, "bold")
FONT_LABEL= ("Consolas", 9)


class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("1050x680")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._current_frame = None
        self._build_sidebar()
        self._build_main_area()
        self.show_dashboard()


    def _build_sidebar(self):
        sb = tk.Frame(self, bg=PANEL, width=200)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text="₹", font=("Georgia", 36, "bold"),
                 bg=PANEL, fg=ACCENT).pack(pady=(30, 0))
        tk.Label(sb, text="Expense\nTracker", font=("Georgia", 13, "bold"),
                 bg=PANEL, fg=TEXT, justify="center").pack(pady=(0, 30))

        ttk.Separator(sb, orient="horizontal").pack(fill="x", padx=15)

        nav_items = [
            ("Dashboard",     self.show_dashboard),
            ("Add Expense",   self.show_add),
            ("All Expenses",  self.show_all),
            ("Filter Month",  self.show_monthly),
            ("Filter Cat.",   self.show_category),
            ("Budget",        self.show_budget),
            ("Pie Chart",     self.show_chart),
        ]
        self._nav_btns = []
        for label, cmd in nav_items:
            btn = tk.Button(sb, text=label, font=FONT_BTN,
                            bg=PANEL, fg=TEXT, relief="flat",
                            activebackground=ACCENT, activeforeground="white",
                            cursor="hand2", anchor="w", padx=20,
                            command=lambda c=cmd: c())
            btn.pack(fill="x", pady=2)
            self._nav_btns.append((btn, label))

        ttk.Separator(sb, orient="horizontal").pack(fill="x", padx=15, pady=10)
        tk.Label(sb, text="v2.0  •  2025", font=("Consolas", 8),
                 bg=PANEL, fg=SUBTEXT).pack(side="bottom", pady=10)

    def _build_main_area(self):
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

    def _clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _header(self, title, subtitle=""):
        tk.Label(self.main, text=title, font=FONT_H,
                 bg=BG, fg=TEXT).pack(anchor="w", padx=35, pady=(30, 0))
        if subtitle:
            tk.Label(self.main, text=subtitle, font=FONT_SUB,
                     bg=BG, fg=SUBTEXT).pack(anchor="w", padx=35)
        tk.Frame(self.main, bg=ACCENT, height=2).pack(fill="x", padx=35, pady=(8, 15))

    def _make_entry(self, parent, label, row, default=""):
        tk.Label(parent, text=label, font=FONT_LABEL, bg=CARD, fg=SUBTEXT).grid(
            row=row, column=0, sticky="w", padx=15, pady=6)
        var = tk.StringVar(value=default)
        e = tk.Entry(parent, textvariable=var, font=FONT_BODY,
                     bg="#0f0f1a", fg=TEXT, insertbackground=TEXT,
                     relief="flat", width=30)
        e.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        return var

    def _make_dropdown(self, parent, label, options, row):
        tk.Label(parent, text=label, font=FONT_LABEL, bg=CARD, fg=SUBTEXT).grid(
            row=row, column=0, sticky="w", padx=15, pady=6)
        var = tk.StringVar(value=options[0])
        dd = ttk.Combobox(parent, textvariable=var, values=options,
                          state="readonly", width=28, font=FONT_BODY)
        dd.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        return var

    def _action_btn(self, parent, text, cmd, color=ACCENT):
        tk.Button(parent, text=text, font=FONT_BTN,
                  bg=color, fg="white", relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  activebackground=BG, activeforeground=TEXT,
                  command=cmd).pack(pady=15)

    def _make_table(self, parent, columns, rows, show_actions=False, action_cb=None):
        frame = tk.Frame(parent, bg=PANEL)
        frame.pack(fill="both", expand=True, padx=35, pady=5)

        cols = columns + (["Actions"] if show_actions else [])

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview",
                        background=CARD, foreground=TEXT,
                        fieldbackground=CARD, rowheight=26,
                        font=FONT_BODY, borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                        background=PANEL, foreground=ACCENT2,
                        font=("Consolas", 9, "bold"), relief="flat")
        style.map("Custom.Treeview", background=[("selected", ACCENT)])

        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            style="Custom.Treeview", height=16)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120 if col not in ("Description", "Actions") else 180, anchor="w")

        for i, row in enumerate(rows):
            tree.insert("", "end", iid=str(i), values=row + (["✏ Edit  🗑 Del"] if show_actions else []))

        sb_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb_y.set)
        tree.pack(side="left", fill="both", expand=True)
        sb_y.pack(side="right", fill="y")

        if show_actions and action_cb:
            tree.bind("<Double-1>", lambda e: action_cb(tree))

        return tree

    def _download_invoice_btn(self, parent, month_key):
        """Renders a download invoice button for the given month_key."""
        frame = tk.Frame(parent, bg=BG)
        frame.pack(anchor="w", padx=35, pady=(8, 2))

        def do_download():
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"Invoice_{month_key.replace('-', '_')}.pdf",
                title="Save Invoice As"
            )
            if not save_path:
                return
            ok, result = backend.generate_invoice(month_key, save_path)
            if ok:
                messagebox.showinfo("Invoice Saved", f"Invoice saved to:\n{result}")
            else:
                messagebox.showerror("Error", f"Could not generate invoice:\n{result}")

        tk.Button(
            frame,
            text="⬇  Download Invoice (PDF)",
            font=FONT_BTN,
            bg=SUCCESS,
            fg="white",
            relief="flat",
            padx=16,
            pady=7,
            cursor="hand2",
            activebackground=BG,
            activeforeground=TEXT,
            command=do_download
        ).pack(side="left")

        tk.Label(
            frame,
            text=f"  Save a PDF invoice for {month_key}",
            font=("Consolas", 9),
            bg=BG,
            fg=SUBTEXT
        ).pack(side="left", padx=8)


    def show_dashboard(self):
        self._clear_main()
        self._header("Dashboard", "Your financial snapshot")

        now = datetime.now()
        month_key = now.strftime("%m-%Y")
        all_exp = backend.get_all_expenses()
        total_all = backend.get_total()
        month_exp = backend.get_expenses_by_month(month_key)
        month_total = sum(float(r[1]) for r in month_exp)
        budget = backend.get_budget(month_key)

        cards_frame = tk.Frame(self.main, bg=BG)
        cards_frame.pack(fill="x", padx=35, pady=5)

        def stat_card(parent, label, value, color):
            c = tk.Frame(parent, bg=CARD, padx=20, pady=15, relief="flat")
            c.pack(side="left", expand=True, fill="both", padx=8)
            tk.Label(c, text=label, font=("Consolas", 9), bg=CARD, fg=SUBTEXT).pack(anchor="w")
            tk.Label(c, text=value, font=("Georgia", 18, "bold"), bg=CARD, fg=color).pack(anchor="w", pady=(4, 0))

        stat_card(cards_frame, "Total Entries",    str(len(all_exp)),        ACCENT2)
        stat_card(cards_frame, "All-Time Spent",   f"₹{total_all:,.0f}",    ACCENT)
        stat_card(cards_frame, f"Spent in {month_key}", f"₹{month_total:,.0f}", WARNING)
        budget_str   = f"₹{budget:,.0f}" if budget else "Not set"
        budget_color = ACCENT if (budget and month_total > budget) else SUCCESS
        stat_card(cards_frame, f"Budget {month_key}", budget_str, budget_color)

        if budget and month_total > budget:
            tk.Label(self.main,
                     text=f"⚠  Over budget by ₹{month_total - budget:,.0f} this month!",
                     font=("Consolas", 10, "bold"), bg=BG, fg=ACCENT).pack(pady=5)

        tk.Label(self.main, text="Recent Expenses", font=("Consolas", 10, "bold"),
                 bg=BG, fg=ACCENT2).pack(anchor="w", padx=35, pady=(15, 3))
        recent = all_exp[-5:][::-1]
        self._make_table(self.main, ["Date", "Amount", "Category", "Description"], recent)

    def show_add(self):
        self._clear_main()
        self._header("Add Expense", "Record a new transaction")

        form = tk.Frame(self.main, bg=CARD, padx=20, pady=20)
        form.pack(padx=35, pady=5, anchor="w")

        today    = datetime.now().strftime("%d-%m-%Y")
        date_var = self._make_entry(form, "Date (DD-MM-YYYY)", 0, today)
        amt_var  = self._make_entry(form, "Amount (₹)", 1)
        cat_var  = self._make_dropdown(form, "Category", backend.CATEGORIES, 2)
        desc_var = self._make_entry(form, "Description", 3)

        msg_var = tk.StringVar()
        msg_lbl = tk.Label(self.main, textvariable=msg_var, font=FONT_BODY, bg=BG)
        msg_lbl.pack()

        def submit():
            ok, msg = backend.add_expense(
                date_var.get(), amt_var.get(), cat_var.get(), desc_var.get())
            if ok:
                if msg.startswith("BUDGET_ALERT:"):
                    alert = msg.replace("BUDGET_ALERT:", "")
                    messagebox.showwarning("⚠ Budget Alert", f"Expense added!\n\n{alert}")
                else:
                    msg_var.set("✅ " + msg)
                    msg_lbl.config(fg=SUCCESS)
                amt_var.set("")
                desc_var.set("")
            else:
                msg_var.set("❌ " + msg)
                msg_lbl.config(fg=ACCENT)

        self._action_btn(self.main, "  Add Expense  ", submit, ACCENT)

    def show_all(self):
        self._clear_main()
        self._header("All Expenses", "Double-click a row to edit or delete")
        rows = backend.get_all_expenses()

        def on_action(tree):
            sel = tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            row = rows[idx]
            choice = messagebox.askquestion(
                "Action", f"Row {idx+1}: {row[2]}  ₹{row[1]}\n\nYes = Edit   No = Delete",
                icon="question")
            if choice == "yes":
                self._edit_dialog(idx, row, lambda: self.show_all())
            else:
                if messagebox.askyesno("Confirm Delete", "Delete this expense?"):
                    ok, msg = backend.delete_expense(idx)
                    messagebox.showinfo("Result", msg)
                    self.show_all()

        self._make_table(self.main,
                         ["Date", "Amount", "Category", "Description"],
                         rows, show_actions=True, action_cb=on_action)

    def _edit_dialog(self, idx, row, refresh_cb):
        win = tk.Toplevel(self)
        win.title("Edit Expense")
        win.geometry("400x280")
        win.configure(bg=CARD)
        win.grab_set()

        form = tk.Frame(win, bg=CARD, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        date_var = self._make_entry(form, "Date", 0, row[0])
        amt_var  = self._make_entry(form, "Amount", 1, row[1])
        cat_var  = self._make_dropdown(form, "Category", backend.CATEGORIES, 2)
        cat_var.set(row[2])
        desc_var = self._make_entry(form, "Description", 3, row[3])

        def save():
            ok, msg = backend.edit_expense(
                idx, date_var.get(), amt_var.get(), cat_var.get(), desc_var.get())
            messagebox.showinfo("Result", msg)
            win.destroy()
            refresh_cb()

        tk.Button(form, text="Save", font=FONT_BTN, bg=ACCENT, fg="white",
                  relief="flat", padx=15, pady=6, command=save).grid(
                  row=4, column=1, sticky="e", pady=10)

    def show_monthly(self):
        self._clear_main()
        self._header("Filter by Month", "View expenses for a specific month")

        ctrl = tk.Frame(self.main, bg=BG)
        ctrl.pack(anchor="w", padx=35, pady=5)

        months = sorted(set(
            datetime.strptime(r[0], "%d-%m-%Y").strftime("%m-%Y")
            for r in backend.get_all_expenses()
            if len(r) >= 1
        ), reverse=True) or [datetime.now().strftime("%m-%Y")]

        month_var = tk.StringVar(value=months[0])
        tk.Label(ctrl, text="Select Month:", font=FONT_LABEL, bg=BG, fg=SUBTEXT).pack(side="left")
        ttk.Combobox(ctrl, textvariable=month_var, values=months,
                     state="readonly", width=12, font=FONT_BODY).pack(side="left", padx=10)

        result_frame = tk.Frame(self.main, bg=BG)
        result_frame.pack(fill="both", expand=True)

        total_lbl = tk.Label(self.main, text="", font=("Consolas", 10, "bold"), bg=BG, fg=WARNING)
        total_lbl.pack(anchor="w", padx=35)

        budget_lbl = tk.Label(self.main, text="", font=("Consolas", 10), bg=BG, fg=SUBTEXT)
        budget_lbl.pack(anchor="w", padx=35)

        invoice_frame = tk.Frame(self.main, bg=BG)
        invoice_frame.pack(anchor="w", padx=35, pady=(6, 0))

        def load():
            for w in result_frame.winfo_children():
                w.destroy()
            for w in invoice_frame.winfo_children():
                w.destroy()

            mk = month_var.get()
            rows = backend.get_expenses_by_month(mk)
            t = sum(float(r[1]) for r in rows)
            total_lbl.config(text=f"Total: ₹{t:,.0f}")

            b = backend.get_budget(mk)
            if b:
                rem = b - t
                color = ACCENT if rem < 0 else SUCCESS
                budget_lbl.config(
                    text=f"Budget: ₹{b:,.0f}  •  {'Over by' if rem < 0 else 'Remaining'}: ₹{abs(rem):,.0f}",
                    fg=color)
            else:
                budget_lbl.config(text="No budget set for this month.", fg=SUBTEXT)

            self._make_table(result_frame, ["Date", "Amount", "Category", "Description"], rows)

            if rows:
                def do_download(m=mk):
                    save_path = filedialog.asksaveasfilename(
                        defaultextension=".pdf",
                        filetypes=[("PDF Files", "*.pdf")],
                        initialfile=f"Invoice_{m.replace('-', '_')}.pdf",
                        title="Save Invoice As"
                    )
                    if not save_path:
                        return
                    ok, result = backend.generate_invoice(m, save_path)
                    if ok:
                        messagebox.showinfo("Invoice Saved", f"Invoice saved to:\n{result}")
                    else:
                        messagebox.showerror("Error", f"Could not generate invoice:\n{result}")

                tk.Button(
                    invoice_frame,
                    text="⬇  Download Invoice (PDF)",
                    font=FONT_BTN,
                    bg=SUCCESS,
                    fg="white",
                    relief="flat",
                    padx=16,
                    pady=7,
                    cursor="hand2",
                    activebackground=BG,
                    activeforeground=TEXT,
                    command=do_download
                ).pack(side="left")

                tk.Label(
                    invoice_frame,
                    text=f"  Export all {len(rows)} expense(s) for {mk} as PDF",
                    font=("Consolas", 9),
                    bg=BG,
                    fg=SUBTEXT
                ).pack(side="left", padx=8)

        tk.Button(ctrl, text="Show", font=FONT_BTN, bg=ACCENT2, fg=BG,
                  relief="flat", padx=12, pady=4, cursor="hand2",
                  command=load).pack(side="left")
        load()

    def show_category(self):
        self._clear_main()
        self._header("Filter by Category")

        ctrl = tk.Frame(self.main, bg=BG)
        ctrl.pack(anchor="w", padx=35, pady=5)

        cat_var = tk.StringVar(value=backend.CATEGORIES[0])
        tk.Label(ctrl, text="Category:", font=FONT_LABEL, bg=BG, fg=SUBTEXT).pack(side="left")
        ttk.Combobox(ctrl, textvariable=cat_var, values=backend.CATEGORIES,
                     state="readonly", width=22, font=FONT_BODY).pack(side="left", padx=10)

        result_frame = tk.Frame(self.main, bg=BG)
        result_frame.pack(fill="both", expand=True)
        total_lbl = tk.Label(self.main, text="", font=("Consolas", 10, "bold"), bg=BG, fg=WARNING)
        total_lbl.pack(anchor="w", padx=35)

        def load():
            for w in result_frame.winfo_children():
                w.destroy()
            rows = backend.get_expenses_by_category(cat_var.get())
            t = sum(float(r[1]) for r in rows)
            total_lbl.config(text=f"Total for {cat_var.get()}: ₹{t:,.0f}")
            self._make_table(result_frame, ["Date", "Amount", "Category", "Description"], rows)

        tk.Button(ctrl, text="Show", font=FONT_BTN, bg=ACCENT2, fg=BG,
                  relief="flat", padx=12, pady=4, cursor="hand2",
                  command=load).pack(side="left")
        load()

    def show_budget(self):
        self._clear_main()
        self._header("Budget Manager", "Set monthly spending limits")

        months = []
        for r in backend.get_all_expenses():
            try:
                mk = datetime.strptime(r[0], "%d-%m-%Y").strftime("%m-%Y")
                if mk not in months:
                    months.append(mk)
            except:
                pass
        now_mk = datetime.now().strftime("%m-%Y")
        if now_mk not in months:
            months.insert(0, now_mk)

        form = tk.Frame(self.main, bg=CARD, padx=20, pady=20)
        form.pack(padx=35, pady=5, anchor="w")

        month_var = tk.StringVar(value=months[0])
        tk.Label(form, text="Month (MM-YYYY):", font=FONT_LABEL, bg=CARD, fg=SUBTEXT).grid(
            row=0, column=0, sticky="w", padx=15, pady=8)
        ttk.Combobox(form, textvariable=month_var, values=months,
                     width=14, font=FONT_BODY, state="normal").grid(row=0, column=1, sticky="w", padx=10)

        amt_var = tk.StringVar()
        tk.Label(form, text="Budget Amount (₹):", font=FONT_LABEL, bg=CARD, fg=SUBTEXT).grid(
            row=1, column=0, sticky="w", padx=15, pady=8)
        tk.Entry(form, textvariable=amt_var, font=FONT_BODY,
                 bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", width=16).grid(
                 row=1, column=1, sticky="w", padx=10)

        info_lbl = tk.Label(self.main, text="", font=FONT_BODY, bg=BG, fg=SUBTEXT)
        info_lbl.pack(anchor="w", padx=35)

        def refresh_info():
            mk = month_var.get()
            b  = backend.get_budget(mk)
            spent = backend.get_monthly_total(mk)
            if b:
                rem = b - spent
                color = ACCENT if rem < 0 else SUCCESS
                info_lbl.config(
                    text=f"Current budget: ₹{b:,.0f}  |  Spent: ₹{spent:,.0f}  |  "
                         f"{'Over by' if rem < 0 else 'Left'}: ₹{abs(rem):,.0f}",
                    fg=color)
            else:
                info_lbl.config(text=f"No budget set for {mk}.  Spent so far: ₹{spent:,.0f}", fg=SUBTEXT)

        def save():
            try:
                amt = float(amt_var.get())
            except:
                messagebox.showerror("Error", "Enter a valid amount.")
                return
            backend.set_budget(month_var.get(), amt)
            messagebox.showinfo("Saved", f"Budget set to ₹{amt:,.0f} for {month_var.get()}")
            amt_var.set("")
            refresh_info()

        tk.Button(form, text="Set Budget", font=FONT_BTN, bg=ACCENT, fg="white",
                  relief="flat", padx=15, pady=6, cursor="hand2",
                  command=save).grid(row=2, column=1, sticky="e", pady=12)

        month_var.trace_add("write", lambda *_: refresh_info())
        refresh_info()

    def show_chart(self):
        self._clear_main()
        self._header("Expense Chart", "Spending breakdown by category")

        ctrl = tk.Frame(self.main, bg=BG)
        ctrl.pack(anchor="w", padx=35, pady=(0, 5))

        scope_var = tk.StringVar(value="All Time")
        scopes = ["All Time"] + sorted(set(
            datetime.strptime(r[0], "%d-%m-%Y").strftime("%m-%Y")
            for r in backend.get_all_expenses() if len(r) >= 1
        ), reverse=True)

        tk.Label(ctrl, text="Scope:", font=FONT_LABEL, bg=BG, fg=SUBTEXT).pack(side="left")
        ttk.Combobox(ctrl, textvariable=scope_var, values=scopes,
                     state="readonly", width=14, font=FONT_BODY).pack(side="left", padx=10)

        chart_frame = tk.Frame(self.main, bg=BG)
        chart_frame.pack(fill="both", expand=True, padx=35)

        canvas_widget = [None]

        def draw():
            for w in chart_frame.winfo_children():
                w.destroy()
            scope = scope_var.get()
            rows  = backend.get_all_expenses() if scope == "All Time" else backend.get_expenses_by_month(scope)
            fig   = backend.get_pie_figure(rows)
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas_widget[0] = canvas

        tk.Button(ctrl, text="Refresh", font=FONT_BTN, bg=ACCENT2, fg=BG,
                  relief="flat", padx=12, pady=4, cursor="hand2",
                  command=draw).pack(side="left")
        draw()

if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()
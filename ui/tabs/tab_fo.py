import tkinter as tk
from tkinter import ttk, messagebox

class FOTab(ttk.Frame):
    def __init__(self, parent, db_manager, financial_orgs, central_bank):
        super().__init__(parent)
        self.db_manager = db_manager
        self.financial_orgs = financial_orgs
        self.central_bank = central_bank

        # --- Выбор ФО ---
        select_frame = ttk.LabelFrame(self, text="Выбор Финансовой Организации")
        select_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(select_frame, text="ID ФО:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.fo_id_var = tk.StringVar()
        self.fo_combo = ttk.Combobox(select_frame, textvariable=self.fo_id_var, values=list(financial_orgs.keys()), state="readonly", width=20)
        self.fo_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.fo_combo.bind('<<ComboboxSelected>>', self.on_fo_select)

        # --- Функции ФО ---
        func_frame = ttk.LabelFrame(self, text="Функции ФО")
        func_frame.pack(fill=tk.X, padx=5, pady=5)

        # 1. Запрос на эмиссию
        ttk.Label(func_frame, text="Сумма эмиссии:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.emission_amount_var = tk.StringVar(value="100000")
        ttk.Entry(func_frame, textvariable=self.emission_amount_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.request_emission_btn = ttk.Button(func_frame, text="Запросить эмиссию", command=self.request_emission, state=tk.DISABLED)
        self.request_emission_btn.grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)

        # --- Таблица транзакций ---
        tx_frame = ttk.LabelFrame(self, text="Транзакции, обработанные ФО")
        tx_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаём Treeview для отображения транзакций
        self.tx_tree = ttk.Treeview(tx_frame, columns=("Sender", "Recipient", "Amount", "Type", "Timestamp", "Status"), show="headings")
        self.tx_tree.heading("Sender", text="Отправитель")
        self.tx_tree.heading("Recipient", text="Получатель")
        self.tx_tree.heading("Amount", text="Сумма")
        self.tx_tree.heading("Type", text="Тип")
        self.tx_tree.heading("Timestamp", text="Время")
        self.tx_tree.heading("Status", text="Статус")

        # Устанавливаем ширину столбцов
        self.tx_tree.column("Sender", width=100)
        self.tx_tree.column("Recipient", width=100)
        self.tx_tree.column("Amount", width=100)
        self.tx_tree.column("Type", width=100)
        self.tx_tree.column("Timestamp", width=150)
        self.tx_tree.column("Status", width=100)

        # Добавляем полосы прокрутки
        tx_scrollbar_y = ttk.Scrollbar(tx_frame, orient=tk.VERTICAL, command=self.tx_tree.yview)
        tx_scrollbar_x = ttk.Scrollbar(tx_frame, orient=tk.HORIZONTAL, command=self.tx_tree.xview)
        self.tx_tree.configure(yscrollcommand=tx_scrollbar_y.set, xscrollcommand=tx_scrollbar_x.set)

        self.tx_tree.grid(row=0, column=0, sticky='nsew')
        tx_scrollbar_y.grid(row=0, column=1, sticky='ns')
        tx_scrollbar_x.grid(row=1, column=0, sticky='ew')

        tx_frame.grid_rowconfigure(0, weight=1)
        tx_frame.grid_columnconfigure(0, weight=1)

    def on_fo_select(self, event):
        fo_id = self.fo_id_var.get()
        if fo_id in self.financial_orgs:
            self.selected_fo = self.financial_orgs[fo_id]
            self.request_emission_btn.config(state=tk.NORMAL)
            self.update_transaction_table()

    def request_emission(self):
        if hasattr(self, 'selected_fo'):
            try:
                amount = float(self.emission_amount_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная сумма эмиссии.")
                return

            success = self.selected_fo.request_emission(amount)
            if success:
                messagebox.showinfo("Успех", f"Запрос на эмиссию {amount} ЦР для {self.selected_fo.id} одобрен ЦБ.")
                # Обновим данные в БД для ФО (хотя в модели FO это не напрямую хранится, но можно логировать)
                # ЦБ обновит свои данные
            else:
                messagebox.showerror("Ошибка", f"Запрос на эмиссию {amount} ЦР для {self.selected_fo.id} отклонён ЦБ.")

    def update_transaction_table(self):
        if hasattr(self, 'selected_fo'):
            # Очищаем таблицу
            for item in self.tx_tree.get_children():
                self.tx_tree.delete(item)

            # Получаем транзакции из БД, связанные с этой ФО
            all_transactions = self.db_manager.get_all_transactions_data()
            fo_transactions = [tx for tx in all_transactions if tx['fo_id'] == self.selected_fo.id]

            # Заполняем таблицу
            for tx in fo_transactions:
                self.tx_tree.insert("", "end", values=(
                    tx['sender_id'],
                    tx['recipient_id'],
                    tx['amount'],
                    tx['type'],
                    tx['timestamp'],
                    tx['status']
                ))

import tkinter as tk
from tkinter import ttk

class TxDataTab(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager

        # --- Таблица данных транзакций ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаём Treeview
        self.tx_tree = ttk.Treeview(tree_frame, columns=(
            "Sender", "Recipient", "Type", "Amount", "Timestamp", "FO"
        ), show="headings")

        # Определяем заголовки
        self.tx_tree.heading("Sender", text="Отправитель транзакции")
        self.tx_tree.heading("Recipient", text="Получатель транзакции")
        self.tx_tree.heading("Type", text="Тип перевода")
        self.tx_tree.heading("Amount", text="Сумма транзакции")
        self.tx_tree.heading("Timestamp", text="Время совершения транзакции")
        self.tx_tree.heading("FO", text="Банк, через который операция")

        # Устанавливаем ширину столбцов
        self.tx_tree.column("Sender", width=100)
        self.tx_tree.column("Recipient", width=100)
        self.tx_tree.column("Type", width=150)
        self.tx_tree.column("Amount", width=100)
        self.tx_tree.column("Timestamp", width=150)
        self.tx_tree.column("FO", width=150)

        # Полосы прокрутки
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tx_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tx_tree.xview)
        self.tx_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tx_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Кнопка обновления
        self.refresh_btn = ttk.Button(self, text="Обновить данные", command=self.update_table)
        self.refresh_btn.pack(pady=5)

    def update_table(self):
        # Очищаем таблицу
        for item in self.tx_tree.get_children():
            self.tx_tree.delete(item)

        # Получаем данные из БД
        transactions_data = self.db_manager.get_all_transactions_data()

        # Заполняем таблицу
        for tx in transactions_data:
            self.tx_tree.insert("", "end", values=(
                tx['sender_id'],
                tx['recipient_id'],
                tx['type'],
                tx['amount'],
                tx['timestamp'],
                tx['fo_id']
            ))

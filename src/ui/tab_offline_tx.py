import tkinter as tk
from tkinter import ttk

class OfflineTxTab(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager

        # --- Таблица офлайн-транзакций ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаём Treeview
        self.offline_tx_tree = ttk.Treeview(tree_frame, columns=(
            "Sender", "Recipient", "Amount", "FO", "Timestamp", "Status"
        ), show="headings")

        # Определяем заголовки
        self.offline_tx_tree.heading("Sender", text="Отправитель транзакции")
        self.offline_tx_tree.heading("Recipient", text="Получатель транзакции")
        self.offline_tx_tree.heading("Amount", text="Сумма транзакции")
        self.offline_tx_tree.heading("FO", text="Банк, через который операция")
        self.offline_tx_tree.heading("Timestamp", text="Время совершения транзакции")
        self.offline_tx_tree.heading("Status", text="Состояние транзакции")

        # Устанавливаем ширину столбцов
        self.offline_tx_tree.column("Sender", width=100)
        self.offline_tx_tree.column("Recipient", width=100)
        self.offline_tx_tree.column("Amount", width=100)
        self.offline_tx_tree.column("FO", width=150)
        self.offline_tx_tree.column("Timestamp", width=150)
        self.offline_tx_tree.column("Status", width=150)

        # Полосы прокрутки
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.offline_tx_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.offline_tx_tree.xview)
        self.offline_tx_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.offline_tx_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Кнопка обновления
        self.refresh_btn = ttk.Button(self, text="Обновить данные", command=self.update_table)
        self.refresh_btn.pack(pady=5)

    def update_table(self):
        # Очищаем таблицу
        for item in self.offline_tx_tree.get_children():
            self.offline_tx_tree.delete(item)

        # Получаем ВСЕ транзакции из БД
        all_transactions_data = self.db_manager.get_all_transactions_data()
        # Фильтруем только офлайн-транзакции (по статусу или типу)
        # В requirements тип "OFFLINE" и статус "ОФФЛАЙН"
        offline_transactions_data = [tx for tx in all_transactions_data if tx['type'] == 'OFFLINE' or tx['status'] in ['ОФФЛАЙН', 'ПОСТУПИЛО В ОБРАБОТКУ', 'ОБРАБОТАНА']]

        # Заполняем таблицу
        for tx in offline_transactions_data:
            self.offline_tx_tree.insert("", "end", values=(
                tx['sender_id'],
                tx['recipient_id'],
                tx['amount'],
                tx['fo_id'],
                tx['timestamp'],
                tx['status']
            ))

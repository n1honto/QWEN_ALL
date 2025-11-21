import tkinter as tk
from tkinter import ttk

class SmartContractsTab(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager

        # --- Таблица смарт-контрактов ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаём Treeview
        self.sc_tree = ttk.Treeview(tree_frame, columns=(
            "Sender", "Recipient", "Amount", "FO", "Functionality", "ExecutionTime", "RequiredAmount"
        ), show="headings")

        # Определяем заголовки
        self.sc_tree.heading("Sender", text="Отправитель транзакции")
        self.sc_tree.heading("Recipient", text="Получатель транзакции")
        self.sc_tree.heading("Amount", text="Сумма транзакции")
        self.sc_tree.heading("FO", text="Банк, через который операция")
        self.sc_tree.heading("Functionality", text="Функционал смарт-контракта")
        self.sc_tree.heading("ExecutionTime", text="Дата и время исполнения")
        self.sc_tree.heading("RequiredAmount", text="Сумма для исполнения")

        # Устанавливаем ширину столбцов
        self.sc_tree.column("Sender", width=100)
        self.sc_tree.column("Recipient", width=100)
        self.sc_tree.column("Amount", width=100)
        self.sc_tree.column("FO", width=100)
        self.sc_tree.column("Functionality", width=200)
        self.sc_tree.column("ExecutionTime", width=150)
        self.sc_tree.column("RequiredAmount", width=100)

        # Полосы прокрутки
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.sc_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.sc_tree.xview)
        self.sc_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.sc_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Кнопка обновления
        self.refresh_btn = ttk.Button(self, text="Обновить данные", command=self.update_table)
        self.refresh_btn.pack(pady=5)

    def update_table(self):
        # Очищаем таблицу
        for item in self.sc_tree.get_children():
            self.sc_tree.delete(item)

        # Получаем ВСЕ транзакции из БД
        all_transactions_data = self.db_manager.get_all_transactions_data()
        # Фильтруем только транзакции смарт-контрактов
        sc_transactions_data = [tx for tx in all_transactions_data if tx['type'] == 'SMART_CONTRACT']

        # Заполняем таблицу
        for tx in sc_transactions_data:
            # Пример фиксированных данных для столбцов, не представленных в транзакции
            functionality = "Оплата коммунальных платежей" # Берётся из details контракта
            execution_time = tx['timestamp'] # В реальности это было бы отдельное поле
            required_amount = tx['amount'] # Часто совпадает с суммой транзакции

            self.sc_tree.insert("", "end", values=(
                tx['sender_id'],
                tx['recipient_id'],
                tx['amount'],
                tx['fo_id'],
                functionality,
                execution_time,
                required_amount
            ))

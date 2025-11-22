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
            "Sender", "Recipient", "Type", "Amount", "Timestamp", "FO", "Status"
        ), show="headings")

        # Определяем заголовки
        self.tx_tree.heading("Sender", text="Отправитель транзакции")
        self.tx_tree.heading("Recipient", text="Получатель транзакции")
        self.tx_tree.heading("Type", text="Тип перевода") # Изменили текст заголовка
        self.tx_tree.heading("Amount", text="Сумма транзакции")
        self.tx_tree.heading("Timestamp", text="Время совершения транзакции")
        self.tx_tree.heading("FO", text="Банк, через который операция")
        self.tx_tree.heading("Status", text="Статус транзакции") # Добавили статус

        # Устанавливаем ширину столбцов
        self.tx_tree.column("Sender", width=100)
        self.tx_tree.column("Recipient", width=100)
        self.tx_tree.column("Type", width=150)
        self.tx_tree.column("Amount", width=100)
        self.tx_tree.column("Timestamp", width=150)
        self.tx_tree.column("FO", width=150)
        self.tx_tree.column("Status", width=150) # Установили ширину для статуса

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
        # Проверяем, инициализирован ли self.db_manager
        if self.db_manager is None:
            print("[WARN] tab_tx_data: db_manager не инициализирован. Невозможно обновить таблицу.")
            # Очищаем таблицу, если нет данных
            for item in self.tx_tree.get_children():
                self.tx_tree.delete(item)
            return

        # Очищаем таблицу
        for item in self.tx_tree.get_children():
            self.tx_tree.delete(item)

        # Получаем данные из БД
        transactions_data = self.db_manager.get_all_transactions_data()

        # Заполняем таблицу
        for tx in transactions_data:
            # Используем tx['type'] для отображения типа перевода
            # Он может быть C2C, OFFLINE, SMART_CONTRACT_EXECUTION и т.д.
            # Для столбца "Тип перевода" отобразим 'онлайн', 'офлайн', 'смарт-контракт' на основе tx['type']
            tx_type_display = "неизвестно"
            if tx['type'] in ['C2C', 'C2B', 'B2C', 'B2B', 'G2B', 'B2G', 'C2G', 'G2C']: # Пример онлайн-типов
                tx_type_display = "онлайн"
            elif tx['type'] == 'OFFLINE' or tx['type'] == 'OFFLINE_SYNC': # Пример офлайн-типов
                tx_type_display = "офлайн"
            elif tx['type'] == 'SMART_CONTRACT_EXECUTION': # Пример смарт-контракта
                tx_type_display = "смарт-контракт"
            # Добавьте другие типы по мере необходимости

            self.tx_tree.insert("", "end", values=(
                tx['sender_id'],
                tx['recipient_id'],
                tx_type_display, # Отображаем тип перевода
                tx['amount'],
                tx['timestamp'],
                tx['fo_id'],
                tx['status'] # Отображаем статус
            ))

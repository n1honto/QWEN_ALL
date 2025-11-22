import tkinter as tk
from tkinter import ttk

class UserDataTab(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager # Может быть None

        # --- Таблица данных пользователей ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаём Treeview
        self.user_tree = ttk.Treeview(tree_frame, columns=(
            "ID", "Type", "BalanceNonCash", "StatusDigital", "StatusOffline",
            "BalanceDigital", "BalanceOffline", "ActivationTime", "DeactivationTime"
        ), show="headings")

        # Определяем заголовки
        self.user_tree.heading("ID", text="ID пользователя")
        self.user_tree.heading("Type", text="Тип пользователя")
        self.user_tree.heading("BalanceNonCash", text="Баланс безналичного кошелька")
        self.user_tree.heading("StatusDigital", text="Статус цифрового кошелька")
        self.user_tree.heading("StatusOffline", text="Статус оффлайн кошелька")
        self.user_tree.heading("BalanceDigital", text="Баланс цифрового кошелька")
        self.user_tree.heading("BalanceOffline", text="Баланс оффлайн кошелька")
        self.user_tree.heading("ActivationTime", text="Время активации оффлайн кошелька")
        self.user_tree.heading("DeactivationTime", text="Время деактивации оффлайн кошелька")

        # Устанавливаем ширину столбцов
        self.user_tree.column("ID", width=100)
        self.user_tree.column("Type", width=100)
        self.user_tree.column("BalanceNonCash", width=150)
        self.user_tree.column("StatusDigital", width=150)
        self.user_tree.column("StatusOffline", width=150)
        self.user_tree.column("BalanceDigital", width=150)
        self.user_tree.column("BalanceOffline", width=150)
        self.user_tree.column("ActivationTime", width=200)
        self.user_tree.column("DeactivationTime", width=200)

        # Полосы прокрутки
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.user_tree.xview)
        self.user_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.user_tree.grid(row=0, column=0, sticky='nsew')
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
            print("[WARN] tab_user_data: db_manager не инициализирован. Невозможно обновить таблицу.")
            # Очищаем таблицу, если нет данных
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            return

        # Очищаем таблицу
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

        # Получаем данные из БД
        users_data = self.db_manager.get_all_users_data()

        # Заполняем таблицу
        # ИСПРАВЛЕНО: используем 'users_data' вместо 'users_'
        for user in users_data:
            self.user_tree.insert("", "end", values=(
                user['id'],
                user['type'],
                user['balance_non_cash'],
                user['status_digital_wallet'],
                user['status_offline_wallet'],
                user['balance_digital'],
                user['balance_offline'],
                user['offline_wallet_expiry'], # Показываем время деактивации как ActivationTime, если логика другая
                user['offline_wallet_expiry']  # Показываем время деактивации
            ))

import tkinter as tk
from tkinter import ttk, messagebox
import random

class UserTab(ttk.Frame):
    def __init__(self, parent, db_manager, users, financial_orgs):
        super().__init__(parent)
        self.db_manager = db_manager
        self.users = users
        self.financial_orgs = financial_orgs

        # --- Выбор пользователя ---
        select_frame = ttk.LabelFrame(self, text="Выбор пользователя")
        select_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(select_frame, text="ID пользователя:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.user_id_var = tk.StringVar()
        self.user_combo = ttk.Combobox(select_frame, textvariable=self.user_id_var, values=list(users.keys()), state="readonly", width=20)
        self.user_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.user_combo.bind('<<ComboboxSelected>>', self.on_user_select)

        # --- Функции пользователя ---
        func_frame = ttk.LabelFrame(self, text="Функции пользователя")
        func_frame.pack(fill=tk.X, padx=5, pady=5)

        # 1. Создание цифрового кошелька
        self.create_digital_wallet_btn = ttk.Button(func_frame, text="Открыть цифровой кошелёк", command=self.create_digital_wallet, state=tk.DISABLED)
        self.create_digital_wallet_btn.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)

        # 2. Обмен безналичных на цифровые
        ttk.Label(func_frame, text="Сумма обмена:").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.exchange_amount_var = tk.StringVar(value="1000")
        ttk.Entry(func_frame, textvariable=self.exchange_amount_var, width=10).grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.exchange_btn = ttk.Button(func_frame, text="Обменять", command=self.exchange_to_digital, state=tk.DISABLED)
        self.exchange_btn.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        # 3. Онлайн транзакция
        ttk.Label(func_frame, text="Получатель (ID):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.tx_recipient_var = tk.StringVar()
        ttk.Combobox(func_frame, textvariable=self.tx_recipient_var, values=list(users.keys()), state="readonly", width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(func_frame, text="Сумма:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.tx_amount_var = tk.StringVar(value="500")
        ttk.Entry(func_frame, textvariable=self.tx_amount_var, width=10).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        self.send_tx_btn = ttk.Button(func_frame, text="Отправить транзакцию", command=self.send_transaction, state=tk.DISABLED)
        self.send_tx_btn.grid(row=1, column=4, sticky=tk.W, padx=5, pady=2)

        # 4. Открытие офлайн кошелька
        self.open_offline_wallet_btn = ttk.Button(func_frame, text="Открыть офлайн-кошелёк", command=self.open_offline_wallet, state=tk.DISABLED)
        self.open_offline_wallet_btn.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)

        # 5. Пополнение офлайн кошелька
        ttk.Label(func_frame, text="Сумма пополнения (офлайн):").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        self.offline_fill_amount_var = tk.StringVar(value="200")
        ttk.Entry(func_frame, textvariable=self.offline_fill_amount_var, width=10).grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        self.fill_offline_btn = ttk.Button(func_frame, text="Пополнить офлайн", command=self.fill_offline_wallet, state=tk.DISABLED)
        self.fill_offline_btn.grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)

        # 6. Создание офлайн транзакции
        ttk.Label(func_frame, text="Получатель (ID, офлайн):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.offline_recipient_var = tk.StringVar()
        ttk.Combobox(func_frame, textvariable=self.offline_recipient_var, values=list(users.keys()), state="readonly", width=20).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(func_frame, text="Сумма (офлайн):").grid(row=3, column=2, sticky=tk.W, padx=5, pady=2)
        self.offline_tx_amount_var = tk.StringVar(value="100")
        ttk.Entry(func_frame, textvariable=self.offline_tx_amount_var, width=10).grid(row=3, column=3, sticky=tk.W, padx=5, pady=2)
        self.create_offline_tx_btn = ttk.Button(func_frame, text="Создать офлайн-транзакцию", command=self.create_offline_transaction, state=tk.DISABLED)
        self.create_offline_tx_btn.grid(row=3, column=4, sticky=tk.W, padx=5, pady=2)

        # 7. Создание смарт-контракта
        self.create_smart_contract_btn = ttk.Button(func_frame, text="Создать смарт-контракт", command=self.create_smart_contract, state=tk.DISABLED)
        self.create_smart_contract_btn.grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)

        # --- Информация о пользователе ---
        info_frame = ttk.LabelFrame(self, text="Информация о пользователе")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.info_text = tk.Text(info_frame, height=8, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def on_user_select(self, event):
        user_id = self.user_id_var.get()
        if user_id in self.users:
            self.selected_user = self.users[user_id]
            # Обновляем состояние кнопок в зависимости от статуса кошельков
            self.update_button_states()
            self.display_user_info()

    def update_button_states(self):
        if hasattr(self, 'selected_user'):
            # Цифровой кошелёк
            if self.selected_user.status_digital_wallet == "ЗАКРЫТ":
                self.create_digital_wallet_btn.config(state=tk.NORMAL)
                self.exchange_btn.config(state=tk.DISABLED)
                self.send_tx_btn.config(state=tk.DISABLED)
            else:
                self.create_digital_wallet_btn.config(state=tk.DISABLED)
                self.exchange_btn.config(state=tk.NORMAL)
                self.send_tx_btn.config(state=tk.NORMAL)

            # Офлайн кошелёк
            if self.selected_user.status_offline_wallet == "ЗАКРЫТ":
                self.open_offline_wallet_btn.config(state=tk.NORMAL)
                self.fill_offline_btn.config(state=tk.DISABLED)
                self.create_offline_tx_btn.config(state=tk.DISABLED)
            else:
                self.open_offline_wallet_btn.config(state=tk.DISABLED)
                self.fill_offline_btn.config(state=tk.NORMAL)
                self.create_offline_tx_btn.config(state=tk.NORMAL)

            # Смарт-контракт (всегда доступен, если кошелёк открыт)
            if self.selected_user.status_digital_wallet == "ОТКРЫТ":
                 self.create_smart_contract_btn.config(state=tk.NORMAL)
            else:
                 self.create_smart_contract_btn.config(state=tk.DISABLED)

    def display_user_info(self):
        if hasattr(self, 'selected_user'):
            info = self.selected_user.get_wallet_info()
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"ID: {info['id']}\n")
            self.info_text.insert(tk.END, f"Тип: {info['type']}\n")
            self.info_text.insert(tk.END, f"Баланс безналичного: {info['balance_non_cash']}\n")
            self.info_text.insert(tk.END, f"Баланс цифрового: {info['balance_digital']}\n")
            self.info_text.insert(tk.END, f"Баланс офлайн: {info['balance_offline']}\n")
            self.info_text.insert(tk.END, f"Статус цифрового кошелька: {info['status_digital_wallet']}\n")
            self.info_text.insert(tk.END, f"Статус офлайн кошелька: {info['status_offline_wallet']}\n")
            if info['offline_wallet_activation_time']:
                self.info_text.insert(tk.END, f"Время активации офлайн кошелька: {info['offline_wallet_activation_time']}\n")
            if info['offline_wallet_deactivation_time']:
                self.info_text.insert(tk.END, f"Время деактивации офлайн кошелька: {info['offline_wallet_deactivation_time']}\n")
            self.info_text.config(state=tk.DISABLED)

    def create_digital_wallet(self):
        if hasattr(self, 'selected_user'):
            success = self.selected_user.create_digital_wallet()
            if success:
                self.update_button_states()
                self.display_user_info()
                self.db_manager.save_user(self.selected_user.get_wallet_info()) # Сохраняем в БД

    def exchange_to_digital(self):
        if hasattr(self, 'selected_user'):
            try:
                amount = float(self.exchange_amount_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная сумма обмена.")
                return
            success = self.selected_user.exchange_to_digital(amount)
            if success:
                self.display_user_info()
                self.db_manager.save_user(self.selected_user.get_wallet_info()) # Сохраняем в БД

    def send_transaction(self):
        if hasattr(self, 'selected_user'):
            recipient_id = self.tx_recipient_var.get()
            if recipient_id not in self.users:
                 messagebox.showerror("Ошибка", f"Получатель {recipient_id} не найден.")
                 return
            try:
                amount = float(self.tx_amount_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная сумма транзакции.")
                return

            # Найти ФО отправителя
            sender_fo = None
            for fo_id, fo in self.financial_orgs.items():
                if self.selected_user.id in fo.users:
                    sender_fo = fo
                    break

            if not sender_fo:
                 messagebox.showerror("Ошибка", "Не удалось найти ФО отправителя.")
                 return

            # Отправить транзакцию через ФО
            tx_id = sender_fo.submit_transaction(self.selected_user.id, recipient_id, amount, 'C2C')
            if tx_id:
                messagebox.showinfo("Успех", f"Транзакция {tx_id} создана и отправлена на обработку.")
                # Обновим данные в БД для отправителя и получателя
                self.db_manager.save_user(self.selected_user.get_wallet_info())
                recipient_user = self.users[recipient_id]
                self.db_manager.save_user(recipient_user.get_wallet_info())

    def open_offline_wallet(self):
        if hasattr(self, 'selected_user'):
            success = self.selected_user.open_offline_wallet()
            if success:
                self.update_button_states()
                self.display_user_info()
                self.db_manager.save_user(self.selected_user.get_wallet_info()) # Сохраняем в БД

    def fill_offline_wallet(self):
        if hasattr(self, 'selected_user'):
            try:
                amount = float(self.offline_fill_amount_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная сумма пополнения офлайн-кошелька.")
                return
            success = self.selected_user.fill_offline_wallet(amount)
            if success:
                self.display_user_info()
                self.db_manager.save_user(self.selected_user.get_wallet_info()) # Сохраняем в БД

    def create_offline_transaction(self):
        if hasattr(self, 'selected_user'):
            recipient_id = self.offline_recipient_var.get()
            if recipient_id not in self.users:
                 messagebox.showerror("Ошибка", f"Получатель {recipient_id} не найден.")
                 return
            try:
                amount = float(self.offline_tx_amount_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная сумма офлайн-транзакции.")
                return

            tx_data = self.selected_user.create_offline_transaction(recipient_id, amount)
            if tx_data:
                messagebox.showinfo("Успех", f"Офлайн-транзакция создана. Она будет обработана при синхронизации.")
                # В реальной системе, tx_data нужно было бы сохранить отдельно и обработать позже
                # Для симуляции сохраним в БД как транзакцию со статусом OFFLINE
                tx_data['status'] = 'ОФФЛАЙН'
                # Нужно определить fo_id для офлайн-транзакции. Пусть это будет ФО отправителя.
                sender_fo_id = None
                for fo_id, fo in self.financial_orgs.items():
                    if self.selected_user.id in fo.users:
                        sender_fo_id = fo_id
                        break
                tx_data['fo_id'] = sender_fo_id
                self.db_manager.save_transaction(tx_data)
                self.display_user_info() # Баланс офлайн кошелька изменился

    def create_smart_contract(self):
        if hasattr(self, 'selected_user'):
            # Пример: смарт-контракт на оплату 1000 ЦР
            contract_details = {"type": "utility_payment", "amount": 1000.0, "recipient": "UTILITY_PROVIDER_ID"}
            contract_id = self.selected_user.create_smart_contract(contract_details)
            messagebox.showinfo("Успех", f"Смарт-контракт {contract_id} создан.")
            # В реальной системе, логика исполнения контракта была бы сложнее
            # Для симуляции просто создадим транзакцию, которая будет выполнена позже
            # Предположим, ФО отправителя выполнит её
            sender_fo_id = None
            for fo_id, fo in self.financial_orgs.items():
                if self.selected_user.id in fo.users:
                    sender_fo_id = fo_id
                    break
            # Создаём "транзакцию смарт-контракта" и сохраняем в БД
            sc_tx_data = {
                'id': f"SC_{contract_id}",
                'sender_id': self.selected_user.id,
                'recipient_id': contract_details['recipient'],
                'amount': contract_details['amount'],
                'type': 'SMART_CONTRACT',
                'fo_id': sender_fo_id,
                'status': 'PENDING_EXECUTION', # Статус для обработки контракта
            }
            self.db_manager.save_transaction(sc_tx_data)

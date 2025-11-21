import tkinter as tk
from tkinter import ttk, messagebox

class CBTab(ttk.Frame):
    def __init__(self, parent, db_manager, central_bank, financial_orgs):
        super().__init__(parent)
        self.db_manager = db_manager # Может быть None
        # Сохраняем ссылки, но они могут быть None на момент инициализации
        self.central_bank = central_bank # Может быть None
        self.financial_orgs = financial_orgs # Может быть {}

        # --- Информация от ЦБ ---
        info_frame = ttk.LabelFrame(self, text="Информация от Центрального банка")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        # Состояние системы
        self.system_state_text = tk.Text(info_frame, height=6, state=tk.DISABLED)
        self.system_state_text.pack(fill=tk.X, padx=5, pady=5)
        # Не вызываем update_system_state() сразу при инициализации
        # self.update_system_state() # Закомментировано

        # Кнопка обновления
        self.refresh_btn = ttk.Button(info_frame, text="Обновить данные ЦБ", command=self.update_system_state)
        self.refresh_btn.pack(pady=5)

        # --- Таблица запросов на эмиссию ---
        emission_frame = ttk.LabelFrame(self, text="Запросы на эмиссию от ФО")
        emission_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview для запросов
        self.emission_tree = ttk.Treeview(emission_frame, columns=("FO_ID", "Amount", "Status"), show="headings")
        self.emission_tree.heading("FO_ID", text="ID ФО")
        self.emission_tree.heading("Amount", text="Сумма")
        self.emission_tree.heading("Status", text="Статус (Запрошено/Одобрено/Отклонено)")

        self.emission_tree.column("FO_ID", width=100)
        self.emission_tree.column("Amount", width=100)
        self.emission_tree.column("Status", width=200)

        # Кнопки для одобрения/отклонения
        button_frame = ttk.Frame(emission_frame)
        approve_btn = ttk.Button(button_frame, text="Одобрить", command=self.approve_selected_emission)
        approve_btn.pack(side=tk.LEFT, padx=5, pady=5)
        reject_btn = ttk.Button(button_frame, text="Отклонить", command=self.reject_selected_emission)
        reject_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Полосы прокрутки
        emission_scrollbar_y = ttk.Scrollbar(emission_frame, orient=tk.VERTICAL, command=self.emission_tree.yview)
        self.emission_tree.configure(yscrollcommand=emission_scrollbar_y.set)

        self.emission_tree.grid(row=0, column=0, sticky='nsew', rowspan=2)
        emission_scrollbar_y.grid(row=0, column=1, sticky='ns')
        button_frame.grid(row=1, column=0, sticky=tk.S, pady=5)

        emission_frame.grid_rowconfigure(0, weight=1)
        emission_frame.grid_columnconfigure(0, weight=1)

    def update_system_state(self):
        # Проверяем, инициализирован ли self.central_bank
        if self.central_bank is None:
            print("[WARN] Центральный банк не инициализирован. Невозможно обновить состояние.")
            # Можно обновить текстовое поле с сообщением
            self.system_state_text.config(state=tk.NORMAL)
            self.system_state_text.delete(1.0, tk.END)
            self.system_state_text.insert(tk.END, "Центральный банк не инициализирован.")
            self.system_state_text.config(state=tk.DISABLED)
            return

        state = self.central_bank.get_system_state()
        self.system_state_text.config(state=tk.NORMAL)
        self.system_state_text.delete(1.0, tk.END)
        self.system_state_text.insert(tk.END, f"Общее предложение ЦР: {state['total_supply']}\n")
        self.system_state_text.insert(tk.END, f"Резерв ЦБ: {state['reserve']}\n")
        self.system_state_text.insert(tk.END, f"Количество авторизованных ФО: {state['number_of_authorized_fos']}\n")
        self.system_state_text.insert(tk.END, f"Обработано транзакций: {state['total_transactions_processed']}\n")
        self.system_state_text.config(state=tk.DISABLED)

    def update_emission_requests(self):
        # В реальной системе запросы на эмиссию были бы в очереди или БД.
        # В нашей симуляции ЦБ обрабатывает их сразу в `request_emission`.
        # Для UI, мы можем отслеживать количество запросов к ЦБ.
        # Пока что просто обновим системное состояние.
        # Допустим, у нас есть список запросов.
        # Создадим его искусственно, например, на основе лога транзакций или отдельной структуры.
        # Для простоты, покажем текущую информацию о ФО и их эмиссии.
        # Лучше всего это интегрировать с логикой ЦБ и БД.
        # Пока что оставим таблицу пустой или с фиктивными данными.
        # Обновим системное состояние, так как оно более актуально.
        self.update_system_state()

    def approve_selected_emission(self):
        # В текущей реализации ЦБ одобряет запрос сразу при его получении.
        # Это место было бы для ручного одобрения, если бы была очередь.
        # Пока что покажем сообщение.
        selected_item = self.emission_tree.selection()
        if selected_item:
             item_values = self.emission_tree.item(selected_item, 'values')
             fo_id = item_values[0]
             amount = item_values[1]
             messagebox.showinfo("Одобрено", f"Запрос от {fo_id} на {amount} ЦР одобрен (имитация).")
        else:
            messagebox.showwarning("Предупреждение", "Выберите запрос для одобрения.")

    def reject_selected_emission(self):
        selected_item = self.emission_tree.selection()
        if selected_item:
             item_values = self.emission_tree.item(selected_item, 'values')
             fo_id = item_values[0]
             amount = item_values[1]
             messagebox.showinfo("Отклонено", f"Запрос от {fo_id} на {amount} ЦР отклонён (имитация).")
        else:
            messagebox.showwarning("Предупреждение", "Выберите запрос для отклонения.")

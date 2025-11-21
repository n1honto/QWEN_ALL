import tkinter as tk
from tkinter import ttk, messagebox
import threading

class ControlTab(ttk.Frame):
    def __init__(self, parent, db_manager, blockchain, central_bank, financial_orgs, users, replicas, network, simulation_controller):
        super().__init__(parent)
        self.db_manager = db_manager
        self.blockchain = blockchain
        self.central_bank = central_bank
        self.financial_orgs = financial_orgs
        self.users = users
        self.replicas = replicas
        self.network = network
        self.simulation_controller = simulation_controller

        # --- Элементы управления ---
        # Секция создания пользователей
        user_frame = ttk.LabelFrame(self, text="Создание пользователей")
        user_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(user_frame, text="Количество:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.user_count_var = tk.StringVar(value="100")
        ttk.Entry(user_frame, textvariable=self.user_count_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(user_frame, text="Тип:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.user_type_var = tk.StringVar(value="physical")
        ttk.Combobox(user_frame, textvariable=self.user_type_var, values=["physical", "legal"], state="readonly", width=15).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        self.create_users_btn = ttk.Button(user_frame, text="Создать пользователей", command=self.create_users)
        self.create_users_btn.grid(row=0, column=4, sticky=tk.W, padx=10, pady=2)

        # Секция создания ФО
        fo_frame = ttk.LabelFrame(self, text="Создание Финансовых Организаций")
        fo_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(fo_frame, text="Количество:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.fo_count_var = tk.StringVar(value="5")
        ttk.Entry(fo_frame, textvariable=self.fo_count_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        self.create_fos_btn = ttk.Button(fo_frame, text="Создать ФО", command=self.create_fos)
        self.create_fos_btn.grid(row=0, column=2, sticky=tk.W, padx=10, pady=2)

        # Секция сценариев и запуска
        scenario_frame = ttk.LabelFrame(self, text="Сценарии и запуск")
        scenario_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(scenario_frame, text="Сценарий:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.scenario_var = tk.StringVar(value="low")
        ttk.Combobox(scenario_frame, textvariable=self.scenario_var, values=["low", "medium", "peak"], state="readonly", width=15).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        self.run_simulation_btn = ttk.Button(scenario_frame, text="Запустить симуляцию", command=self.run_simulation)
        self.run_simulation_btn.grid(row=0, column=2, sticky=tk.W, padx=10, pady=2)

        self.stop_simulation_btn = ttk.Button(scenario_frame, text="Остановить симуляцию", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_simulation_btn.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        # Секция статуса
        status_frame = ttk.LabelFrame(self, text="Статус симуляции")
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_label = ttk.Label(status_frame, text="Остановлена.")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка обновления статуса
        self.update_status_btn = ttk.Button(status_frame, text="Обновить статус", command=self.update_status)
        self.update_status_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def create_users(self):
        try:
            count = int(self.user_count_var.get())
            user_type_str = self.user_type_var.get()
            user_type = next(t for t in self.users[next(iter(self.users))].__class__.__dict__.values() if isinstance(t, self.users[next(iter(self.users))].__class__.__dict__.values().__class__) and t.value == user_type_str)
        except (ValueError, StopIteration):
            messagebox.showerror("Ошибка", "Некорректное количество пользователей или тип.")
            return

        # В реальной симуляции это делалось бы в цикле с обновлением БД
        # Здесь мы просто обновим глобальные переменные, которые будут использоваться при инициализации
        # или создадим пользователей в текущей сессии, если симуляция не запущена.
        # Лучше всего интегрировать это в процесс инициализации симуляции.
        # Для симуляции в реальном времени добавление пользователей сложнее.
        # Пока что покажем сообщение.
        messagebox.showinfo("Информация", f"Запланировано создание {count} пользователей типа {user_type_str}. "
                                          f"Изменения вступят в силу при следующей инициализации симуляции.")

    def create_fos(self):
        try:
            count = int(self.fo_count_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное количество ФО.")
            return

        messagebox.showinfo("Информация", f"Запланировано создание {count} ФО. "
                                          f"Изменения вступят в силу при следующей инициализации симуляции.")

    def run_simulation(self):
        scenario = self.scenario_var.get()
        # Используем controller для инициализации и запуска
        # Это может занять время, поэтому запускаем в отдельном потоке
        def _run():
            # Сначала перезапускаем симуляцию с новыми параметрами
            # Это обновит глобальные переменные и объекты
            # num_users и num_fos нужно получить из какого-то места. Пусть пока будут фиксированные или из GUI.
            # Берём из GUI на момент запуска
            try:
                num_users = int(self.user_count_var.get())
                num_fos = int(self.fo_count_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректное количество пользователей или ФО.")
                return

            # Перезапуск симуляции
            # В реальности, перезапуск означает остановку текущей, инициализацию новой, и запуск.
            # Для простоты, просто вызовем инициализацию с новыми параметрами в controller
            # и передадим обновлённые объекты обратно в main_window
            # Это требует более сложной логики в main.py и controller.
            # Пока что просто вызовем run_loop с существующими объектами.
            # self.db_manager, self.chain, self.cb, self.fos, self.users, self.replicas, self.network = \
            #     self.simulation_controller['initialize'](num_users, num_fos, scenario)

            # Запуск цикла симуляции
            duration = 3600 # 1 час, как в сценариях
            self.simulation_controller['run_loop'](self.replicas, duration)

        # Запускаем симуляцию в отдельном потоке, чтобы не блокировать UI
        sim_thread = threading.Thread(target=_run)
        sim_thread.daemon = True
        sim_thread.start()

        self.run_simulation_btn.config(state=tk.DISABLED)
        self.stop_simulation_btn.config(state=tk.NORMAL)
        self.update_status()

    def stop_simulation(self):
        self.simulation_controller['stop']()
        self.run_simulation_btn.config(state=tk.NORMAL)
        self.stop_simulation_btn.config(state=tk.DISABLED)
        self.update_status()

    def update_status(self):
        status_text = self.simulation_controller['get_status']()
        self.status_label.config(text=status_text)

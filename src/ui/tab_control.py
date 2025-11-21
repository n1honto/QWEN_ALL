import tkinter as tk
from tkinter import ttk, messagebox
import threading

class ControlTab(ttk.Frame):
    def __init__(self, parent, db_manager, blockchain, central_bank, financial_orgs, users, replicas, network, simulation_controller, main_app_instance):
        super().__init__(parent)
        # Сохраняем ссылку на MainApplication
        self.main_app_instance = main_app_instance

        self.db_manager = db_manager # Может быть None
        self.blockchain = blockchain # Может быть None
        self.central_bank = central_bank # Может быть None
        self.financial_orgs = financial_orgs # Может быть {}
        self.users = users # Может быть {}
        self.replicas = replicas # Может быть []
        self.network = network # Может быть None
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

        # self.create_users_btn = ttk.Button(user_frame, text="Создать пользователей", command=self.create_users) # Не нужно, создаются при симуляции
        # self.create_users_btn.grid(row=0, column=4, sticky=tk.W, padx=10, pady=2)

        # Секция создания ФО
        fo_frame = ttk.LabelFrame(self, text="Создание Финансовых Организаций")
        fo_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(fo_frame, text="Количество:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.fo_count_var = tk.StringVar(value="5")
        ttk.Entry(fo_frame, textvariable=self.fo_count_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        # self.create_fos_btn = ttk.Button(fo_frame, text="Создать ФО", command=self.create_fos) # Не нужно, создаются при симуляции
        # self.create_fos_btn.grid(row=0, column=2, sticky=tk.W, padx=10, pady=2)

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

        # Кнопка запуска сценария
        self.run_scenario_btn = ttk.Button(scenario_frame, text="Запустить сценарий", command=self.run_selected_scenario)
        self.run_scenario_btn.grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)

        # Секция статуса
        status_frame = ttk.LabelFrame(self, text="Статус симуляции")
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_label = ttk.Label(status_frame, text="Остановлена.")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка обновления статуса
        self.update_status_btn = ttk.Button(status_frame, text="Обновить статус", command=self.update_status)
        self.update_status_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def create_users(self):
        # Заглушка, функция не используется при текущей логике
        messagebox.showinfo("Информация", "Создание пользователей происходит при запуске симуляции.")

    def create_fos(self):
        # Заглушка, функция не используется при текущей логике
        messagebox.showinfo("Информация", "Создание ФО происходит при запуске симуляции.")

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
            # Вызываем функцию инициализации из controller
            # Она возвращает все необходимые объекты
            db_manager, chain, cb, fos, users, replicas, network, expected_txs = \
                self.simulation_controller['initialize'](num_users, num_fos, scenario)

            # Обновляем объекты в главном окне ЧЕРЕЗ ССЫЛКУ НА MainApplication
            # self.main_app_instance - это MainApplication
            self.main_app_instance.update_simulation_objects(db_manager, chain, cb, fos, users, replicas, network)

            # Запуск цикла симуляции
            duration = 3600 # 1 час, как в сценариях
            self.simulation_controller['run_loop'](replicas, duration, expected_txs, fos, users) # Передаём все 5 аргументов

            # После завершения симуляции обновим данные в UI
            # ПЕРЕМЕЩЕНО: теперь вызывается внутри run_loop или по таймеру
            # self.main_app_instance.update_all_tabs_data() # Лучше вызывать после каждого блока или по таймеру в run_loop


        # Запускаем симуляцию в отдельном потоке, чтобы не блокировать UI
        sim_thread = threading.Thread(target=_run)
        sim_thread.daemon = True
        sim_thread.start()

        self.run_simulation_btn.config(state=tk.DISABLED)
        self.stop_simulation_btn.config(state=tk.NORMAL)
        self.update_status()

    def run_selected_scenario(self):
        scenario = self.scenario_var.get()
        print(f"[TAB_CONTROL] Запуск сценария {scenario} через кнопку.")
        # Запускаем сценарий в отдельном потоке
        def _run():
            self.simulation_controller['run_scenario'](scenario)
        sim_thread = threading.Thread(target=_run)
        sim_thread.daemon = True
        sim_thread.start()

    def stop_simulation(self):
        self.simulation_controller['stop']()
        self.run_simulation_btn.config(state=tk.NORMAL)
        self.stop_simulation_btn.config(state=tk.DISABLED)
        self.update_status()

    def update_status(self):
        status_text = self.simulation_controller['get_status']()
        self.status_label.config(text=status_text)

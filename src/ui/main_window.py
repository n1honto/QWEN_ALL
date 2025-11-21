import tkinter as tk
from tkinter import ttk
# --- Используем абсолютные импорты ---
from digital_ruble_simulation.src.ui import tab_control, tab_user, tab_fo, tab_cb, tab_user_data, tab_tx_data, tab_offline_tx, tab_smart_contracts, tab_consensus, tab_blockchain, tab_metrics

class MainApplication(tk.Tk):
    """
    Главное окно приложения.
    """
    def __init__(self, db_manager, blockchain, central_bank, financial_orgs, users, replicas, network, simulation_controller):
        super().__init__()
        self.title("Имитационная модель цифрового рубля")
        self.geometry("1200x800")

        # Храним контроллер и изначально переданные объекты (могут быть None)
        self.simulation_controller = simulation_controller
        self.db_manager = db_manager
        self.blockchain = blockchain
        self.central_bank = central_bank
        self.financial_orgs = financial_orgs
        self.users = users
        self.replicas = replicas
        self.network = network

        # Создаём Notebook (табы)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Создание вкладок ---
        # 1. Управление
        # ПЕРЕДАЁМ self (MainApplication) в ControlTab
        self.tab_control_frame = tab_control.ControlTab(
            self.notebook,
            self.db_manager, # Может быть None
            self.blockchain, # Может быть None
            self.central_bank, # Может быть None
            self.financial_orgs, # Может быть None
            self.users, # Может быть None
            self.replicas, # Может быть None
            self.network, # Может быть None
            self.simulation_controller,
            self # Передаём экземпляр MainApplication
        )
        self.notebook.add(self.tab_control_frame, text="Управление")

        # 2. Пользователь
        self.tab_user_frame = tab_user.UserTab(
            self.notebook,
            self.db_manager, # Может быть None
            self.users, # Может быть None
            self.financial_orgs # Может быть None
        )
        self.notebook.add(self.tab_user_frame, text="Пользователь")

        # 3. Финансовая организация
        self.tab_fo_frame = tab_fo.FOTab(
            self.notebook,
            self.db_manager, # Может быть None
            self.financial_orgs, # Может быть None
            self.central_bank # Может быть None
        )
        self.notebook.add(self.tab_fo_frame, text="Финансовая организация")

        # 4. Центральный банк
        self.tab_cb_frame = tab_cb.CBTab(
            self.notebook,
            self.db_manager, # Может быть None
            self.central_bank, # Может быть None
            self.financial_orgs # Может быть None
        )
        self.notebook.add(self.tab_cb_frame, text="Центральный банк")

        # 5. Данные о пользователях
        self.tab_user_data_frame = tab_user_data.UserDataTab(
            self.notebook,
            self.db_manager # Может быть None
        )
        self.notebook.add(self.tab_user_data_frame, text="Данные о пользователях")

        # 6. Данные о транзакциях
        self.tab_tx_data_frame = tab_tx_data.TxDataTab(
            self.notebook,
            self.db_manager # Может быть None
        )
        self.notebook.add(self.tab_tx_data_frame, text="Данные о транзакциях")

        # 7. Оффлайн-транзакции
        self.tab_offline_tx_frame = tab_offline_tx.OfflineTxTab(
            self.notebook,
            self.db_manager # Может быть None
        )
        self.notebook.add(self.tab_offline_tx_frame, text="Оффлайн-транзакции")

        # 8. Смарт-контракты
        self.tab_smart_contracts_frame = tab_smart_contracts.SmartContractsTab(
            self.notebook,
            self.db_manager # Может быть None
        )
        self.notebook.add(self.tab_smart_contracts_frame, text="Смарт-контракты")

        # 9. Консенсус
        self.tab_consensus_frame = tab_consensus.ConsensusTab(
            self.notebook,
            self.replicas, # Может быть None
            self.network # Может быть None
        )
        self.notebook.add(self.tab_consensus_frame, text="Консенсус")

        # 10. Распределенный реестр
        self.tab_blockchain_frame = tab_blockchain.BlockchainTab(
            self.notebook,
            self.blockchain # Может быть None
        )
        self.notebook.add(self.tab_blockchain_frame, text="Распределенный реестр")

        # 11. Анализ метрик
        self.tab_metrics_frame = tab_metrics.MetricsTab(
            self.notebook,
            self.blockchain, # Может быть None
            self.db_manager # Может быть None
        )
        self.notebook.add(self.tab_metrics_frame, text="Анализ метрик")

        # --- УБРАНО: self.update_all_tabs_data() # Не вызываем сразу при инициализации ---


    def update_all_tabs_data(self):
        """
        Обновляет данные на всех вкладках.
        """
        # Обновление данных в таблицах на вкладках
        # Это может быть вызвано периодически или по событию
        # Проверяем, инициализированы ли объекты перед обновлением
        try:
            # Проверяем, инициализирован ли self.db_manager
            if self.db_manager:
                 # Проверяем, инициализированы ли вкладки (на случай, если их нет)
                 if hasattr(self, 'tab_user_data_frame'):
                     self.tab_user_data_frame.update_table()
                 if hasattr(self, 'tab_tx_data_frame'):
                     self.tab_tx_data_frame.update_table()
                 if hasattr(self, 'tab_offline_tx_frame'):
                     self.tab_offline_tx_frame.update_table()
                 if hasattr(self, 'tab_smart_contracts_frame'):
                     self.tab_smart_contracts_frame.update_table()
            # Проверяем, инициализирован ли self.replicas и self.network
            if self.replicas and self.network:
                 if hasattr(self, 'tab_consensus_frame'):
                     self.tab_consensus_frame.update_display()
            # Проверяем, инициализирован ли self.blockchain
            if self.blockchain:
                 if hasattr(self, 'tab_blockchain_frame'):
                     self.tab_blockchain_frame.update_display()
            # Проверяем, инициализированы ли self.blockchain и self.db_manager
            if self.blockchain and self.db_manager:
                 if hasattr(self, 'tab_metrics_frame'):
                     self.tab_metrics_frame.update_display()
        except Exception as e:
            print(f"[ERROR] Ошибка при обновлении данных вкладок: {e}")

    def update_simulation_objects(self, db_manager, blockchain, central_bank, financial_orgs, users, replicas, network):
        """
        Обновляет внутренние объекты после инициализации симуляции.
        """
        # Сначала обновляем свои атрибуты
        self.db_manager = db_manager
        self.blockchain = blockchain
        self.central_bank = central_bank
        self.financial_orgs = financial_orgs
        self.users = users
        self.replicas = replicas
        self.network = network

        # Обновляем объекты в вкладках, если они хранят ссылки
        # Это зависит от реализации вкладок. Лучше, если вкладки получают объекты при вызове update.
        # Для простоты, обновим ссылки в контроле
        # Убедимся, что вкладки существуют перед обновлением
        if hasattr(self, 'tab_control_frame'):
            self.tab_control_frame.db_manager = db_manager
            self.tab_control_frame.blockchain = blockchain
            self.tab_control_frame.central_bank = central_bank
            self.tab_control_frame.financial_orgs = financial_orgs
            self.tab_control_frame.users = users
            self.tab_control_frame.replicas = replicas
            self.tab_control_frame.network = network

        if hasattr(self, 'tab_user_frame'):
            self.tab_user_frame.db_manager = db_manager
            self.tab_user_frame.users = users
            self.tab_user_frame.financial_orgs = financial_orgs

        if hasattr(self, 'tab_fo_frame'):
            self.tab_fo_frame.db_manager = db_manager
            self.tab_fo_frame.financial_orgs = financial_orgs
            self.tab_fo_frame.central_bank = central_bank

        if hasattr(self, 'tab_cb_frame'):
            self.tab_cb_frame.db_manager = db_manager
            self.tab_cb_frame.central_bank = central_bank
            self.tab_cb_frame.financial_orgs = financial_orgs

        if hasattr(self, 'tab_user_data_frame'):
            self.tab_user_data_frame.db_manager = db_manager # Обновляем ссылку в вкладке

        if hasattr(self, 'tab_tx_data_frame'):
            self.tab_tx_data_frame.db_manager = db_manager

        if hasattr(self, 'tab_offline_tx_frame'):
            self.tab_offline_tx_frame.db_manager = db_manager

        if hasattr(self, 'tab_smart_contracts_frame'):
            self.tab_smart_contracts_frame.db_manager = db_manager

        if hasattr(self, 'tab_consensus_frame'):
            self.tab_consensus_frame.replicas = replicas
            self.tab_consensus_frame.network = network

        if hasattr(self, 'tab_blockchain_frame'):
            self.tab_blockchain_frame.blockchain = blockchain

        if hasattr(self, 'tab_metrics_frame'):
            self.tab_metrics_frame.blockchain = blockchain
            self.tab_metrics_frame.db_manager = db_manager

        # После обновления всех объектов, обновляем данные на вкладках
        # Проверим, инициализированы ли объекты перед обновлением
        self.update_all_tabs_data() # Вызываем обновление после обновления объектов


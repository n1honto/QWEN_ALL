import tkinter as tk
from tkinter import ttk
from . import tab_control, tab_user, tab_fo, tab_cb, tab_user_data, tab_tx_data, tab_offline_tx, tab_smart_contracts, tab_consensus, tab_blockchain, tab_metrics

class MainApplication(tk.Tk):
    """
    Главное окно приложения.
    """
    def __init__(self, db_manager, blockchain, central_bank, financial_orgs, users, replicas, network, simulation_controller):
        super().__init__()
        self.title("Имитационная модель цифрового рубля")
        self.geometry("1200x800")

        self.db_manager = db_manager
        self.blockchain = blockchain
        self.central_bank = central_bank
        self.financial_orgs = financial_orgs
        self.users = users
        self.replicas = replicas
        self.network = network
        self.simulation_controller = simulation_controller

        # Создаём Notebook (табы)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Создание вкладок ---
        # 1. Управление
        self.tab_control_frame = tab_control.ControlTab(
            self.notebook,
            self.db_manager,
            self.blockchain,
            self.central_bank,
            self.financial_orgs,
            self.users,
            self.replicas,
            self.network,
            self.simulation_controller
        )
        self.notebook.add(self.tab_control_frame, text="Управление")

        # 2. Пользователь
        self.tab_user_frame = tab_user.UserTab(
            self.notebook,
            self.db_manager,
            self.users,
            self.financial_orgs
        )
        self.notebook.add(self.tab_user_frame, text="Пользователь")

        # 3. Финансовая организация
        self.tab_fo_frame = tab_fo.FOTab(
            self.notebook,
            self.db_manager,
            self.financial_orgs,
            self.central_bank
        )
        self.notebook.add(self.tab_fo_frame, text="Финансовая организация")

        # 4. Центральный банк
        self.tab_cb_frame = tab_cb.CBTab(
            self.notebook,
            self.db_manager,
            self.central_bank,
            self.financial_orgs
        )
        self.notebook.add(self.tab_cb_frame, text="Центральный банк")

        # 5. Данные о пользователях
        self.tab_user_data_frame = tab_user_data.UserDataTab(
            self.notebook,
            self.db_manager
        )
        self.notebook.add(self.tab_user_data_frame, text="Данные о пользователях")

        # 6. Данные о транзакциях
        self.tab_tx_data_frame = tab_tx_data.TxDataTab(
            self.notebook,
            self.db_manager
        )
        self.notebook.add(self.tab_tx_data_frame, text="Данные о транзакциях")

        # 7. Оффлайн-транзакции
        self.tab_offline_tx_frame = tab_offline_tx.OfflineTxTab(
            self.notebook,
            self.db_manager
        )
        self.notebook.add(self.tab_offline_tx_frame, text="Оффлайн-транзакции")

        # 8. Смарт-контракты
        self.tab_smart_contracts_frame = tab_smart_contracts.SmartContractsTab(
            self.notebook,
            self.db_manager
        )
        self.notebook.add(self.tab_smart_contracts_frame, text="Смарт-контракты")

        # 9. Консенсус
        self.tab_consensus_frame = tab_consensus.ConsensusTab(
            self.notebook,
            self.replicas,
            self.network
        )
        self.notebook.add(self.tab_consensus_frame, text="Консенсус")

        # 10. Распределенный реестр
        self.tab_blockchain_frame = tab_blockchain.BlockchainTab(
            self.notebook,
            self.blockchain
        )
        self.notebook.add(self.tab_blockchain_frame, text="Распределенный реестр")

        # 11. Анализ метрик
        self.tab_metrics_frame = tab_metrics.MetricsTab(
            self.notebook,
            self.blockchain,
            self.db_manager
        )
        self.notebook.add(self.tab_metrics_frame, text="Анализ метрик")

        # После создания всех вкладок, вызываем обновление данных, чтобы заполнить таблицы
        self.update_all_tabs_data()

    def update_all_tabs_data(self):
        """
        Обновляет данные на всех вкладках.
        """
        # Обновление данных в таблицах на вкладках
        # Это может быть вызвано периодически или по событию
        # Для простоты, вызовем сразу после инициализации
        self.tab_user_data_frame.update_table()
        self.tab_tx_data_frame.update_table()
        self.tab_offline_tx_frame.update_table()
        self.tab_smart_contracts_frame.update_table()
        self.tab_consensus_frame.update_display()
        self.tab_blockchain_frame.update_display()
        self.tab_metrics_frame.update_display()

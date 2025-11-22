import time
from .. import utils # Относительный импорт utils из core

class FinancialOrg:
    """
    Класс, представляющий Финансовую Организацию (Кредитную Организацию).
    """
    def __init__(self, fo_id, central_bank_instance, db_manager): # Добавлен аргумент db_manager
        self.id = fo_id
        self.cb = central_bank_instance  # Ссылка на экземпляр ЦБ
        self.db_manager = db_manager # Сохраняем ссылку на db_manager
        self.users = {}  # Словарь {user_id: User_instance}
        self.transaction_pool = [] # Пул неподтверждённых транзакций
        self.transaction_log = [] # Локальный лог транзакций, прошедших через эту ФО
        self.total_emitted_digital_rubles = 0.0 # Общая сумма эмиссии, полученной от ЦБ

        # Регистрируем себя в ЦБ
        self.cb.register_fo(self.id)

    def add_user(self, user_instance):
        """
        Добавляет пользователя в обслуживание ФО.
        """
        if user_instance.id not in self.users:
            self.users[user_instance.id] = user_instance
            print(f"[INFO] Пользователь {user_instance.id} добавлен в ФО {self.id}.")
            # Сохраняем пользователя в БД при добавлении
            user_db_data = user_instance.get_wallet_info()
            self.db_manager.save_user(user_db_data)
            return True
        else:
            print(f"[WARN] Пользователь {user_instance.id} уже обслуживается ФО {self.id}.")
            return False

    def request_emission(self, amount):
        """
        Отправляет запрос ЦБ на эмиссию цифровых рублей.
        """
        success = self.cb.approve_emission_request(self.id, amount)
        if success:
            self.total_emitted_digital_rubles += amount
            print(f"[INFO] ФО {self.id} получила {amount} цифровых рублей от ЦБ. Общая эмиссия: {self.total_emitted_digital_rubles}")
        else:
            print(f"[ERROR] Запрос на эмиссию от ФО {self.id} отклонён ЦБ.")
        return success

    def submit_transaction(self, sender_id, recipient_id, amount, tx_type='C2C'):
        """
        Создаёт и отправляет транзакцию в систему (в пул, затем ЦБ).
        """
        sender = self.users.get(sender_id)
        recipient = self.users.get(recipient_id)

        if not sender:
            print(f"[ERROR] Отправитель {sender_id} не найден в ФО {self.id}.")
            return False
        if not recipient:
            print(f"[ERROR] Получатель {recipient_id} не найден в ФО {self.id}.")
            return False
        if sender.balance_digital < amount:
            print(f"[ERROR] Недостаточно средств на цифровом кошельке отправителя {sender_id}.")
            return False

        # --- ИСПРАВЛЕНИЕ: Генерируем ID для транзакции ---
        # Используем utils.calculate_hash для генерации уникального ID
        # ИСПРАВЛЕНО: убран .encode() из аргумента calculate_hash
        tx_id = utils.calculate_hash(f"{sender_id}{recipient_id}{amount}{time.time()}{tx_type}")
        tx_data = {
            'id': tx_id, # --- ДОБАВЛЕНО: ID транзакции ---
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'amount': int(amount), # Убедимся, что сумма целая
            'type': tx_type,
            'timestamp': time.time(),
            'status': 'PENDING',
            'fo_id': self.id,
        }

        # В реальной системе тут была бы подпись отправителя
        print(f"[INFO] Создана транзакция {tx_id} от {sender_id} к {recipient_id} через ФО {self.id}.")

        # Сохраняем транзакцию в БД
        self.db_manager.save_transaction(tx_data) # --- ИСПРАВЛЕНИЕ: Вызов метода save_transaction ---

        # Добавляем в пул
        self.transaction_pool.append(tx_data)
        print(f"[INFO] Транзакция {tx_id} добавлена в пул ФО {self.id}.")
        return tx_id # Возвращаем ID

    def get_transaction_pool(self):
        """
        Возвращает пул неподтверждённых транзакций.
        """
        return self.transaction_pool

    def process_pool_for_consensus(self):
        """
        Извлекает транзакции из пула для включения в блок.
        """
        if not self.transaction_pool:
            return []
        # Извлекаем транзакции (например, первые 10 или все, если меньше)
        # В реальной системе могли бы быть приоритеты
        transactions_to_process = self.transaction_pool[:10] # Примерный лимит
        self.transaction_pool = self.transaction_pool[10:] # Удаляем из пула
        return transactions_to_process

    def log_transaction(self, tx_data):
        """
        Логирует транзакцию, прошедшую через эту ФО.
        """
        tx_log_entry = tx_data.copy()
        tx_log_entry['timestamp_logged'] = time.time()
        self.transaction_log.append(tx_log_entry)

    def get_user_wallet_info(self, user_id):
        """
        Возвращает информацию о кошельке пользователя, обслуживаемого этой ФО.
        """
        user = self.users.get(user_id)
        if user:
            return user.get_wallet_info()
        else:
            print(f"[ERROR] Пользователь {user_id} не найден в ФО {self.id}.")
            return None

    def get_all_user_wallets_info(self):
        """
        Возвращает информацию о кошельках всех пользователей этой ФО.
        """
        all_info = []
        for user_id, user_instance in self.users.items():
            all_info.append(user_instance.get_wallet_info())
        return all_info

    def get_all_transactions_info(self):
        """
        Возвращает информацию о транзакциях, прошедших через эту ФО.
        """
        return self.transaction_log

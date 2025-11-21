import hashlib
import time
from enum import Enum
# Исправленный импорт utils: используем абсолютный путь
# from .. import utils # Потенциальная проблема с относительным импортом из participants
from digital_ruble_simulation.src.core import utils # Абсолютный импорт utils

class UserType(Enum):
    PHYSICAL = "physical"
    LEGAL = "legal"

class User:
    """
    Класс, представляющий виртуального пользователя (физическое или юридическое лицо).
    """
    def __init__(self, user_id, user_type, initial_balance=10000):
        """
        Инициализирует пользователя.

        Args:
            user_id (str): Уникальный идентификатор пользователя.
            user_type (UserType): Тип пользователя (физическое или юридическое лицо).
            initial_balance (float): Начальный баланс безналичного кошелька.
        """
        self.id = user_id
        self.type = user_type.value  # Сохраняем как строку
        self.offline_wallet = None
        self.offline_wallet_expiry = None
        self.offline_wallet_active = False

        # Балансы
        self.balance_non_cash = initial_balance  # Баланс безналичного кошелька - ИНИЦИАЛИЗАЦИЯ
        self.balance_digital = 0.0               # Баланс цифрового кошелька
        self.balance_offline = 0.0               # Баланс офлайн-кошелька

        # Статусы кошельков
        self.status_digital_wallet = "ЗАКРЫТ"
        self.status_offline_wallet = "ЗАКРЫТ"

    def create_digital_wallet(self):
        """Открывает цифровой кошелёк."""
        if self.status_digital_wallet == "ЗАКРЫТ":
            self.status_digital_wallet = "ОТКРЫТ"
            print(f"[INFO] Цифровой кошелёк пользователя {self.id} открыт.")
            return True
        else:
            print(f"[WARN] Цифровой кошелёк пользователя {self.id} уже открыт.")
            return False

    def exchange_to_digital(self, amount):
        """
        Обменяет безналичные деньги на цифровые рубли.
        Баланс безналичного кошелька уменьшается, баланс цифрового увеличивается.
        """
        if self.status_digital_wallet != "ОТКРЫТ":
            print(f"[ERROR] Цифровой кошелёк пользователя {self.id} не открыт.")
            return False
        if amount <= 0:
            print(f"[ERROR] Сумма обмена должна быть положительной.")
            return False
        if self.balance_non_cash < amount:
            print(f"[ERROR] Недостаточно средств на безналичном кошельке пользователя {self.id}.")
            return False

        self.balance_non_cash -= amount
        self.balance_digital += amount
        print(f"[INFO] Пользователь {self.id} обменял {amount} на цифровые рубли. "
              f"Баланс безналичного: {self.balance_non_cash}, Баланс цифрового: {self.balance_digital}")
        return True

    def open_offline_wallet(self):
        """Открывает офлайн-кошелёк сроком на 14 дней."""
        if self.status_digital_wallet != "ОТКРЫТ":
            print(f"[ERROR] Цифровой кошелёк пользователя {self.id} должен быть открыт для создания офлайн-кошелька.")
            return False
        if self.status_offline_wallet == "ОТКРЫТ":
            print(f"[WARN] Офлайн-кошелёк пользователя {self.id} уже открыт.")
            return False

        current_time = time.time()
        self.offline_wallet_expiry = current_time + (14 * 24 * 60 * 60)  # 14 дней в секундах
        self.status_offline_wallet = "ОТКРЫТ"
        self.offline_wallet_active = True
        print(f"[INFO] Офлайн-кошелёк пользователя {self.id} открыт до {time.ctime(self.offline_wallet_expiry)}.")
        return True

    def fill_offline_wallet(self, amount):
        """Пополняет офлайн-кошелёк цифровыми рублями."""
        if not self.offline_wallet_active:
            print(f"[ERROR] Офлайн-кошелёк пользователя {self.id} не активен.")
            return False
        if amount <= 0:
            print(f"[ERROR] Сумма пополнения должна быть положительной.")
            return False
        if self.balance_digital < amount:
            print(f"[ERROR] Недостаточно средств на цифровом кошельке пользователя {self.id}.")
            return False

        self.balance_digital -= amount
        self.balance_offline += amount
        print(f"[INFO] Офлайн-кошелёк пользователя {self.id} пополнен на {amount}. "
              f"Баланс цифрового: {self.balance_digital}, Баланс офлайн: {self.balance_offline}")
        return True

    def create_offline_transaction(self, amount, recipient_id): # Поменяли порядок аргументов для соответствия вызову в tab_user.py
        """
        Создаёт офлайн-транзакцию.
        Возвращает словарь с данными транзакции или None в случае ошибки.
        """
        if not self.offline_wallet_active:
            print(f"[ERROR] Офлайн-кошелёк пользователя {self.id} не активен для создания транзакции.")
            return None
        if amount <= 0:
            print(f"[ERROR] Сумма транзакции должна быть положительной.")
            return None
        if self.balance_offline < amount:
            print(f"[ERROR] Недостаточно средств на офлайн-кошельке пользователя {self.id}.")
            return None

        tx_data = {
            'sender_id': self.id,
            'recipient_id': recipient_id,
            'amount': amount,
            'timestamp': time.time(),
            'type': 'OFFLINE',
            'status': 'ОФФЛАЙН'
        }
        # Простая подпись данных (в реальной системе использовалась бы криптография)
        # Используем utils.calculate_hash
        tx_data['signature'] = utils.calculate_hash(f"{self.id}{recipient_id}{amount}{tx_data['timestamp']}OFFLINE".encode())

        self.balance_offline -= amount
        print(f"[INFO] Создана офлайн-транзакция от {self.id} к {recipient_id} на сумму {amount}.")
        return tx_data

    def create_smart_contract(self, contract_details):
        """
        Создаёт смарт-контракт. Возвращает его идентификатор.
        """
        # contract_details - словарь с описанием условий контракта
        contract_id = utils.calculate_hash(f"{self.id}{time.time()}{str(contract_details)}".encode())
        print(f"[INFO] Создан смарт-контракт {contract_id} пользователем {self.id}.")
        return contract_id

    def get_wallet_info(self):
        """Возвращает информацию о кошельках пользователя."""
        # Возвращаем текущие значения атрибутов объекта
        return {
            'id': self.id,
            'type': self.type,
            'balance_non_cash': self.balance_non_cash, # Текущий баланс
            'status_digital_wallet': self.status_digital_wallet,
            'status_offline_wallet': self.status_offline_wallet,
            'balance_digital': self.balance_digital, # Текущий баланс
            'balance_offline': self.balance_offline, # Текущий баланс
            'offline_wallet_activation_time': time.ctime(self.offline_wallet_expiry - (14 * 24 * 60 * 60)) if self.offline_wallet_expiry else None,
            'offline_wallet_deactivation_time': time.ctime(self.offline_wallet_expiry) if self.offline_wallet_expiry else None,
        }

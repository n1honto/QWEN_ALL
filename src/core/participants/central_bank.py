import hashlib
import time
# from . import utils # НЕПРАВИЛЬНО: ищет utils в participants
# from digital_ruble_simulation.src.core import utils # Импортируем пакет core.utils
from .. import utils # Относительный импорт utils из core

class CentralBank:
    """
    Класс, представляющий Центральный банк (Банк России).
    Является оператором платформы, эмитентом цифровых рублей и владельцем главного реестра.
    """
    def __init__(self, initial_reserve=1000000000.0): # Начальный резерв, например, 1 млрд цифровых рублей
        self.id = "CBR"  # Уникальный ID ЦБ
        self.total_supply = 0.0 # Общее количество выпущенных цифровых рублей
        self.reserve = initial_reserve # Общий резерв ЦБ
        self.authorized_fos = set() # Множество ID авторизованных ФО
        self.transaction_log = [] # Лог всех транзакций (упрощённый реестр)

    def register_fo(self, fo_id):
        """
        Регистрирует финансовую организацию в системе.
        """
        if fo_id not in self.authorized_fos:
            self.authorized_fos.add(fo_id)
            print(f"[INFO] Финансовая организация {fo_id} зарегистрирована ЦБ.")
            return True
        else:
            print(f"[WARN] Финансовая организация {fo_id} уже зарегистрирована.")
            return False

    def approve_emission_request(self, fo_id, amount):
        """
        Обрабатывает и одобряет/отклоняет запрос ФО на эмиссию цифровых рублей.
        """
        if fo_id not in self.authorized_fos:
            print(f"[ERROR] Запрос на эмиссию от неавторизованной ФО {fo_id}.")
            return False

        if amount <= 0:
            print(f"[ERROR] Запрос на эмиссию отрицательной или нулевой суммы от {fo_id}.")
            return False

        if self.reserve < amount:
            print(f"[ERROR] Недостаточно резерва ЦБ для эмиссии {amount} для {fo_id}. Резерв: {self.reserve}")
            return False

        # Одобряем эмиссию
        self.reserve -= amount
        self.total_supply += amount
        print(f"[INFO] ЦБ одобрил эмиссию {amount} цифровых рублей для {fo_id}. "
              f"Общее предложение: {self.total_supply}, Резерв: {self.reserve}")
        return True

    def process_transaction(self, transaction_data):
        """
        Обрабатывает транзакцию, полученную от ФО.
        В реальной системе тут был бы сложный процесс валидации и консенсуса.
        В этой симуляции мы просто добавляем транзакцию в лог, если она валидна.
        """
        # Валидация (упрощённая)
        if not transaction_data.get('sender_id') or not transaction_data.get('recipient_id'):
            print(f"[ERROR] Транзакция не содержит отправителя или получателя: {transaction_data}")
            return False
        if transaction_data.get('amount', 0) <= 0:
            print(f"[ERROR] Транзакция содержит недопустимую сумму: {transaction_data}")
            return False

        # Здесь могла бы быть проверка балансов отправителя, подписей и т.д.
        # Для симуляции просто добавляем в лог
        transaction_data['status'] = 'CONFIRMED_BY_CB'
        transaction_data['timestamp_processed_by_cb'] = time.time()
        self.transaction_log.append(transaction_data)
        print(f"[INFO] ЦБ подтвердил транзакцию от {transaction_data['sender_id']} к {transaction_data['recipient_id']} на сумму {transaction_data['amount']}.")
        return True

    def get_system_state(self):
        """
        Возвращает общую информацию о состоянии системы.
        """
        return {
            'total_supply': self.total_supply,
            'reserve': self.reserve,
            'number_of_authorized_fos': len(self.authorized_fos),
            'total_transactions_processed': len(self.transaction_log),
        }

    def get_transaction_log(self):
        """
        Возвращает лог транзакций (упрощённый распределённый реестр).
        """
        return self.transaction_log

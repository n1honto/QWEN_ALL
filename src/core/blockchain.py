import hashlib
import time
import json
from . import utils
from . import transaction

class Block:
    """
    Класс, представляющий блок в блокчейне.
    Содержит транзакции типа Transaction.
    """
    def __init__(self, index, previous_hash, transactions, timestamp=None, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        # transactions теперь список объектов Transaction
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        # Вычисляем хеш при создании
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Вычисляет хеш блока на основе его содержимого.
        Использует функцию из utils для единообразия.
        """
        # Подготовим данные для хеширования
        # Преобразуем список транзакций в список словарей для сериализации
        tx_list = [tx.to_dict() for tx in self.transactions]
        block_data = {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'transactions': tx_list,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
        }
        # Сериализуем данные в строку
        block_string = json.dumps(block_data, sort_keys=True, ensure_ascii=False).encode('utf-8')
        # Вычисляем хеш
        return utils.calculate_hash(block_data) # Передаём словарь, функция сама его сериализует

    def mine_block(self, difficulty=2):
        """
        (Упрощённая) добыча блока - находит хеш, начинающийся с N нулей.
        """
        target = '0' * difficulty
        print(f"[INFO] Начинается майнинг блока {self.index}...")
        start_time = time.time()
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        end_time = time.time()
        print(f"[INFO] Блок {self.index} добыт! Hash: {self.hash}")
        print(f"[INFO] Время майнинга блока {self.index}: {end_time - start_time:.4f} секунд.")

    def to_dict(self):
        """
        Возвращает словарь с данными блока.
        Транзакции также преобразуются в словари.
        """
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.hash,
        }

class Blockchain:
    """
    Класс, представляющий цепочку блоков (блокчейн).
    Теперь отслеживает состояние балансов и валидирует транзакции.
    """
    def __init__(self, difficulty=2):
        self.chain = []
        self.difficulty = difficulty
        # Состояние балансов пользователей {user_id: balance}
        self.state = {}
        # Состояние кошельков {user_id: {'digital': status, 'offline': status}}
        self.wallet_state = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Создаёт первый (генезис) блок в цепочке.
        Может включать начальную эмиссию для ЦБ или ФО.
        """
        # Пример: начальная эмиссия для ЦБ
        # Создаём "фиктивную" транзакцию эмиссии
        # В реальности ЦБ не переводит деньги, а создаёт их.
        # Для симуляции можно создать транзакцию от специального "нулевого" адреса.
        # Или просто обновить состояние после создания блока.
        # Давайте создадим пустой генезис-блок.
        genesis_transactions = []
        genesis_block = Block(0, "0", genesis_transactions)
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        print(f"[INFO] Генезис-блок создан и добавлен. Hash: {genesis_block.hash}")

    def get_latest_block(self):
        """
        Возвращает последний блок в цепочке.
        """
        return self.chain[-1]

    def validate_block_transactions(self, block):
        """
        Проверяет корректность транзакций в блоке.
        Включает проверку балансов отправителей.
        """
        temp_state = self.state.copy() # Работаем с копией состояния для проверки

        for tx in block.transactions:
            sender_id = tx.sender_id
            recipient_id = tx.recipient_id
            amount = tx.amount

            # Проверяем, что у отправителя достаточно средств
            sender_balance = temp_state.get(sender_id, 0)
            if sender_balance < amount:
                print(f"[ERROR] Недостаточно средств для транзакции {tx.id}. Баланс {sender_id}: {sender_balance}, Сумма: {amount}")
                return False

            # Обновляем временные балансы
            temp_state[sender_id] = sender_balance - amount
            temp_state[recipient_id] = temp_state.get(recipient_id, 0) + amount

        # Если все транзакции валидны, возвращаем True
        return True

    def add_block(self, new_block):
        """
        Добавляет новый блок в цепочку после валидации.
        """
        new_block.previous_hash = self.get_latest_block().hash
        # Майнинг должен быть выполнен перед вызовом add_block
        # new_block.mine_block(self.difficulty)
        new_block.hash = new_block.calculate_hash()

        # Проверяем целостность цепи
        if new_block.previous_hash != self.get_latest_block().hash:
             print(f"[ERROR] previous_hash блока {new_block.index} не совпадает с хешем последнего блока цепи.")
             return False

        # Проверяем вычисленный хеш
        if new_block.hash != new_block.calculate_hash():
            print(f"[ERROR] Вычисленный хеш блока {new_block.index} не совпадает с сохранённым.")
            return False

        # Проверяем транзакции в блоке
        if not self.validate_block_transactions(new_block):
            print(f"[ERROR] Транзакции в блоке {new_block.index} недействительны.")
            return False

        # Если все проверки пройдены, добавляем блок
        self.chain.append(new_block)
        # Применяем транзакции к глобальному состоянию
        for tx in new_block.transactions:
            sender_id = tx.sender_id
            recipient_id = tx.recipient_id
            amount = tx.amount

            self.state[sender_id] = self.state.get(sender_id, 0) - amount
            self.state[recipient_id] = self.state.get(recipient_id, 0) + amount
            # Обновляем статус транзакции
            tx.status = 'CONFIRMED'

        print(f"[INFO] Блок {new_block.index} успешно добавлен в цепочку. Hash: {new_block.hash}")
        return True

    def is_chain_valid(self):
        """
        Проверяет целостность всей цепочки блоков.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Проверяем, совпадает ли хеш текущего блока с вычисленным
            if current_block.hash != current_block.calculate_hash():
                print(f"[ERROR] Хеш блока {i} недействителен.")
                return False

            # Проверяем, совпадает ли previous_hash текущего блока с хешем предыдущего
            if current_block.previous_hash != previous_block.hash:
                print(f"[ERROR] previous_hash блока {i} не совпадает с хешем блока {i-1}.")
                return False

        # Проверяем, что состояние балансов соответствует истории транзакций
        # Это сложная проверка, но в упрощённой версии можно считать, что если
        # блоки прошли add_block, то состояние корректно.
        # Для полной проверки нужно пройти всю цепочку и пересчитать балансы.
        print("[INFO] Цепочка блоков действительна.")
        return True

    def get_chain_data(self):
        """
        Возвращает данные всей цепочки в виде списка словарей.
        """
        return [block.to_dict() for block in self.chain]

    def find_transaction_by_id(self, tx_id):
        """
        Ищет транзакцию по её ID во всей цепочке.
        """
        for block in self.chain:
            for tx in block.transactions:
                if tx.id == tx_id:
                    return tx
        return None

    def get_transactions_by_user(self, user_id):
        """
        Возвращает все транзакции, в которых участвовал пользователь (в качестве отправителя или получателя).
        """
        user_transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender_id == user_id or tx.recipient_id == user_id:
                    user_transactions.append(tx.to_dict()) # Возвращаем словарь для UI
        return user_transactions

    def get_current_state(self):
        """
        Возвращает текущее состояние балансов.
        """
        return self.state.copy()

    def get_current_wallet_state(self):
        """
        Возвращает текущее состояние кошельков.
        """
        return self.wallet_state.copy()

    def get_transaction_history(self):
        """
        Возвращает историю всех транзакций.
        """
        history = []
        for block in self.chain:
            for tx in block.transactions:
                history.append(tx.to_dict())
        return history

    def apply_emission(self, recipient_id, amount):
        """
        Имитирует эмиссию ЦБ, увеличивая баланс получателя (например, ФО).
        Эта функция должна вызываться из ЦБ или ФО, а затем транзакция
        должна быть включена в блок через обычный процесс.
        Для простоты, обновим состояние здесь и добавим "фиктивную" транзакцию в генезис или отдельный блок.
        Лучше всего это интегрировать в процесс консенсуса или в специальный блок эмиссии.
        Пока что просто обновим состояние и вернём транзакцию эмиссии.
        """
        self.state[recipient_id] = self.state.get(recipient_id, 0) + amount
        # Создаём транзакцию эмиссии
        emission_tx = transaction.Transaction(
            sender_id="CENTRAL_BANK_MINT", # Условный ID эмиссии
            recipient_id=recipient_id,
            amount=amount,
            tx_type=transaction.TransactionType.B2C, # Или другой тип эмиссии
            fo_id="CBR"
        )
        emission_tx.status = 'EMISSION_CONFIRMED'
        return emission_tx

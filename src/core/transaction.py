import hashlib
import time
from enum import Enum

class TransactionType(Enum):
    C2C = "C2C" # Client to Client
    C2B = "C2B" # Client to Business
    B2C = "B2C" # Business to Client
    B2B = "B2B" # Business to Business
    G2B = "G2B" # Government to Business
    B2G = "B2G" # Business to Government
    C2G = "C2G" # Client to Government
    G2C = "G2C" # Government to Client
    OFFLINE = "OFFLINE" # Offline transaction
    SMART_CONTRACT = "SMART_CONTRACT" # Transaction via smart contract

class Transaction:
    """
    Класс, представляющий транзакцию в системе цифрового рубля.
    """
    def __init__(self, sender_id, recipient_id, amount, tx_type, fo_id, additional_data=None):
        """
        Инициализирует транзакцию.

        Args:
            sender_id (str): ID отправителя.
            recipient_id (str): ID получателя.
            amount (float): Сумма транзакции.
            tx_type (TransactionType): Тип транзакции.
            fo_id (str): ID ФО, через которую идёт транзакция.
            additional_data (dict, optional): Дополнительные данные (например, для смарт-контрактов).
        """
        self.id = hashlib.sha256(f"{sender_id}{recipient_id}{amount}{time.time()}".encode()).hexdigest()
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = amount
        self.type = tx_type.value # Сохраняем как строку
        self.fo_id = fo_id
        self.timestamp = time.time()
        self.status = 'CREATED'
        self.additional_data = additional_data or {}

    def to_dict(self):
        """
        Возвращает словарь с данными транзакции.
        """
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'amount': self.amount,
            'type': self.type,
            'fo_id': self.fo_id,
            'timestamp': self.timestamp,
            'status': self.status,
            'additional_data': self.additional_data,
        }

    def __repr__(self):
        return (f"Transaction(id={self.id}, sender={self.sender_id}, "
                f"recipient={self.recipient_id}, amount={self.amount}, type={self.type})")

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

# --- Модель для пользователей ---
class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, index=True)
    type = Column(String, index=True) # 'physical' или 'legal'
    balance_non_cash = Column(Float, default=10000.0)
    balance_digital = Column(Float, default=0.0)
    balance_offline = Column(Float, default=0.0)
    status_digital_wallet = Column(String, default="ЗАКРЫТ") # "ЗАКРЫТ", "ОТКРЫТ"
    status_offline_wallet = Column(String, default="ЗАКРЫТ") # "ЗАКРЫТ", "ОТКРЫТ"
    offline_wallet_expiry = Column(DateTime, nullable=True) # Время деактивации офлайн-кошелька
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Связь с транзакциями (отправитель)
    sent_transactions = relationship("Transaction", foreign_keys="Transaction.sender_id", back_populates="sender")
    # Связь с транзакциями (получатель)
    received_transactions = relationship("Transaction", foreign_keys="Transaction.recipient_id", back_populates="recipient")

# --- Модель для Финансовых Организаций ---
class FinancialOrg(Base):
    __tablename__ = 'financial_orgs'
    id = Column(String, primary_key=True, index=True)
    name = Column(String, default="") # Имя ФО (опционально)
    total_emitted_digital_rubles = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Связь с транзакциями, обработанными этой ФО
    processed_transactions = relationship("Transaction", back_populates="financial_org")

# --- Модель для транзакций ---
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey('users.id'), nullable=False)
    recipient_id = Column(String, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False) # C2C, C2B, OFFLINE, SMART_CONTRACT, etc.
    fo_id = Column(String, ForeignKey('financial_orgs.id'), nullable=False) # ID ФО, через которую прошла транзакция
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='CREATED') # CREATED, PENDING, CONFIRMED, etc.
    additional_data = Column(Text, default="{}") # JSON строка для смарт-контрактов и т.д.
    block_hash = Column(String, nullable=True) # Хеш блока, в который включена транзакция (если подтверждена)

    # Связи
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_transactions")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_transactions")
    financial_org = relationship("FinancialOrg", back_populates="processed_transactions")

# --- Модель для блоков блокчейна ---
class Block(Base):
    __tablename__ = 'blocks'
    index = Column(Integer, primary_key=True)
    hash = Column(String, unique=True, index=True, nullable=False)
    previous_hash = Column(String, nullable=False)
    # Транзакции хранятся как JSON-строка (или можно создать отдельную таблицу для транзакций в блоке)
    transactions_json = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    nonce = Column(Integer, default=0)

# --- Модель для логов ---
class LogEntry(Base):
    __tablename__ = 'log_entries'
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, index=True) # INFO, WARN, ERROR
    message = Column(Text)
    node_id = Column(String, nullable=True) # ID узла, если применимо
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# -*- coding: utf-8 -*-
"""
Модели SQLAlchemy для базы данных симуляции цифрового рубля.
"""

# --- ИМПОРТЫ ---
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
import datetime
# --- КОНЕЦ ИМПОРТОВ ---

# --- СОЗДАНИЕ Base (КРИТИЧЕСКИ ВАЖНО) ---
# Base - это базовый класс для всех моделей SQLAlchemy.
# Он должен быть создан ДО определения любых классов моделей.
Base = declarative_base()
# --- КОНЕЦ СОЗДАНИЯ Base ---

# --- ОПРЕДЕЛЕНИЕ МОДЕЛЕЙ ---
class User(Base):
    """
    Модель SQLAlchemy для таблицы пользователей.
    """
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    type = Column(String, index=True) # 'physical' или 'legal'
    balance_non_cash = Column(Float, default=10000.0) # Баланс безналичного кошелька (по умолчанию 10000)
    balance_digital = Column(Float, default=0.0)
    balance_offline = Column(Float, default=0.0)
    status_digital_wallet = Column(String, default="ЗАКРЫТ")
    status_offline_wallet = Column(String, default="ЗАКРЫТ")
    offline_wallet_expiry = Column(DateTime, nullable=True) # Время деактивации офлайн-кошелька (timestamp)

    def __repr__(self):
        return f"<User(id='{self.id}', type='{self.type}', balance_non_cash={self.balance_non_cash})>"

class Transaction(Base):
    """
    Модель SQLAlchemy для таблицы транзакций.
    """
    __tablename__ = 'transactions'

    id = Column(String, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey('users.id'), nullable=False)
    recipient_id = Column(String, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False) # C2C, C2B, B2C, B2B, G2B, B2G, C2G, G2C, OFFLINE, SMART_CONTRACT_EXECUTION
    fo_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='PENDING')
    additional_data = Column(Text, default="{}") # JSON строка
    block_hash = Column(String, nullable=True)

    def __repr__(self):
        return f"<Transaction(id='{self.id}', sender='{self.sender_id}', recipient='{self.recipient_id}', amount={self.amount})>"

class Block(Base):
    """
    Модель SQLAlchemy для таблицы блоков.
    """
    __tablename__ = 'blocks'

    index = Column(Integer, primary_key=True)
    hash = Column(String, unique=True, index=True, nullable=False)
    previous_hash = Column(String, nullable=False)
    transactions_json = Column(Text, nullable=False) # JSON строка с транзакциями
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    nonce = Column(Integer, default=0)

    def __repr__(self):
        return f"<Block(index={self.index}, hash='{self.hash[:8]}...', prev_hash='{self.previous_hash[:8]}...')>"

class LogEntry(Base):
    """
    Модель SQLAlchemy для таблицы логов.
    """
    __tablename__ = 'log_entries'

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, index=True) # INFO, WARN, ERROR
    message = Column(Text)
    node_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<LogEntry(level='{self.level}', message='{self.message[:20]}...', node_id='{self.node_id}')>"

# --- КОНЕЦ ОПРЕДЕЛЕНИЯ МОДЕЛЕЙ ---
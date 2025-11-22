# -*- coding: utf-8 -*-
"""
Менеджер базы данных для симуляции цифрового рубля.
Использует SQLAlchemy для взаимодействия с БД.
"""

# --- ИМПОРТЫ ---
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# ИМПОРТИРУЕМ models из ТОГО ЖЕ ПАКЕТА (data)
from . import models  # <-- ОТНОСИТЕЛЬНЫЙ ИМПОРТ, КРИТИЧЕСКИ ВАЖЕН
import os
import json
import datetime
# --- КОНЕЦ ИМПОРТОВ ---

class DatabaseManager:
    """
    Класс для управления подключением и операциями с базой данных.
    """
    def __init__(self, db_path="sqlite:///../../db/simulation_data.db"):
        """
        Инициализирует менеджер БД.
        """
        # Убедимся, что директория для БД существует
        db_dir = os.path.dirname(db_path.replace("sqlite:///", ""))
        os.makedirs(db_dir, exist_ok=True)

        self.engine = create_engine(db_path, echo=False) # echo=True для отладки SQL
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables() # Вызываем create_tables после инициализации engine

    def create_tables(self):
        """
        Создаёт таблицы в БД на основе моделей SQLAlchemy.
        """
        # --- КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ---
        # Используем models.Base, который определён в соседнем файле models.py
        # Если Base не будет найден, возникнет AttributeError на этой строке
        try:
            # Проверим, существует ли Base в модуле models
            base_attr = getattr(models, 'Base', None)
            if base_attr is None:
                raise AttributeError("Модуль 'models' не содержит атрибут 'Base'")
            print(f"[DB] Base найден в models: {base_attr}") # Для отладки

            models.Base.metadata.create_all(bind=self.engine)
            print(f"[DB] Таблицы созданы в {self.engine.url}")
        except AttributeError as e:
            print(f"[ERROR] Ошибка при создании таблиц: {e}")
            raise # Переподнимаем исключение, чтобы остановить выполнение
        except Exception as e:
            print(f"[ERROR] Не удалось создать таблицы: {e}")
            raise # Переподнимаем исключение
        # --- КОНЕЦ КРИТИЧЕСКОГО ИСПРАВЛЕНИЯ ---

    def get_session(self):
        """
        Возвращает сессию SQLAlchemy для выполнения операций.
        """
        return self.SessionLocal()

    def close_session(self, session):
        """
        Закрывает сессию.
        """
        session.close()

    def save_user(self, user_data):
        """
        Сохраняет или обновляет данные пользователя в БД.
        """
        session = self.get_session()
        try:
            # Проверяем, существует ли пользователь в БД
            db_user = session.query(models.User).filter(models.User.id == user_data['id']).first()
            if db_user:
                # Обновляем поля модели БД
                for key, value in user_data.items():
                    if hasattr(models.User, key):
                        setattr(db_user, key, value)
            else:
                # Создаём нового пользователя
                # Убедимся, что все поля в user_data существуют в модели User
                # SQLAlchemy сама проверит это, но мы можем отфильтровать заранее
                from sqlalchemy import inspect
                mapper = inspect(models.User)
                valid_fields = [column.key for column in mapper.columns]
                filtered_data = {k: v for k, v in user_data.items() if k in valid_fields}
                # Обработка offline_wallet_expiry, если оно строковое (возвращается из time.ctime)
                # get_wallet_info возвращает datetime объекты для expiry, так что это не должно быть проблемой
                # Но на всякий случай, если придет строка:
                if 'offline_wallet_expiry' in filtered_data and isinstance(filtered_data['offline_wallet_expiry'], str):
                    try:
                        filtered_data['offline_wallet_expiry'] = datetime.datetime.fromisoformat(filtered_data['offline_wallet_expiry'])
                    except ValueError:
                        print(f"[ERROR] Невозможно преобразовать offline_wallet_expiry '{filtered_data['offline_wallet_expiry']}' в datetime. Устанавливаем в None.")
                        filtered_data['offline_wallet_expiry'] = None

                db_user = models.User(**filtered_data)
                session.add(db_user)

            session.commit()
            print(f"[DB] Данные пользователя {user_data['id']} сохранены/обновлены.")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Не удалось сохранить пользователя {user_data['id']}: {e}")
        finally:
            self.close_session(session)

    def save_transaction(self, tx_data):
        """
        Сохраняет транзакцию в БД.
        """
        session = self.get_session()
        try:
            db_tx = session.query(models.Transaction).filter(models.Transaction.id == tx_data['id']).first()
            if db_tx:
                for key, value in tx_data.items():
                    if hasattr(models.Transaction, key):
                        setattr(db_tx, key, value)
            else:
                tx_data_for_db = tx_data.copy()
                if 'timestamp' in tx_data_for_db and isinstance(tx_data_for_db['timestamp'], float):
                    tx_data_for_db['timestamp'] = datetime.datetime.fromtimestamp(tx_data_for_db['timestamp'])
                db_tx = models.Transaction(**tx_data_for_db)
                session.add(db_tx)

            session.commit()
            print(f"[DB] Транзакция {tx_data['id']} сохранена.")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Не удалось сохранить транзакцию {tx_data['id']}: {e}")
        finally:
            self.close_session(session)

    def save_block(self, block_data):
        """
        Сохраняет блок в БД.
        """
        session = self.get_session()
        try:
            db_block = session.query(models.Block).filter(models.Block.hash == block_data['hash']).first()
            if db_block:
                print(f"[WARN] Блок с хешем {block_data['hash']} уже существует в БД.")
                return
            block_data_for_db = block_data.copy()
            if 'timestamp' in block_data_for_db and isinstance(block_data_for_db['timestamp'], float):
                block_data_for_db['timestamp'] = datetime.datetime.fromtimestamp(block_data_for_db['timestamp'])
            tx_json = json.dumps(block_data_for_db.get('transactions', []), default=str)
            db_block = models.Block(
                index=block_data_for_db['index'],
                hash=block_data_for_db['hash'],
                previous_hash=block_data_for_db['previous_hash'],
                transactions_json=tx_json,
                timestamp=block_data_for_db['timestamp'],
                nonce=block_data_for_db['nonce']
            )
            session.add(db_block)
            session.commit()
            print(f"[DB] Блок {block_data_for_db['index']} (hash {block_data_for_db['hash'][:8]}) сохранён.")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Не удалось сохранить блок {block_data['index']}: {e}")
        finally:
            self.close_session(session)

    def get_user_data(self, user_id):
        """
        Получает данные пользователя из БД по ID.
        """
        session = self.get_session()
        try:
            db_user = session.query(models.User).filter(models.User.id == user_id).first()
            if db_user:
                return {
                    'id': db_user.id,
                    'type': db_user.type,
                    'balance_non_cash': db_user.balance_non_cash,
                    'balance_digital': db_user.balance_digital,
                    'balance_offline': db_user.balance_offline,
                    'status_digital_wallet': db_user.status_digital_wallet,
                    'status_offline_wallet': db_user.status_offline_wallet,
                    'offline_wallet_expiry': db_user.offline_wallet_expiry,
                }
            else:
                print(f"[WARN] Пользователь {user_id} не найден в БД.")
                return None
        finally:
            self.close_session(session)

    def get_all_users_data(self):
        """
        Получает данные всех пользователей из БД.
        """
        session = self.get_session()
        try:
            db_users = session.query(models.User).all()
            return [{
                    'id': u.id,
                    'type': u.type,
                    'balance_non_cash': u.balance_non_cash,
                    'balance_digital': u.balance_digital,
                    'balance_offline': u.balance_offline,
                    'status_digital_wallet': u.status_digital_wallet,
                    'status_offline_wallet': u.status_offline_wallet,
                    'offline_wallet_expiry': u.offline_wallet_expiry,
                } for u in db_users]
        finally:
            self.close_session(session)

    def get_all_transactions_data(self):
        """
        Получает данные всех транзакций из БД.
        """
        session = self.get_session()
        try:
            db_transactions = session.query(models.Transaction).all()
            return [{
                    'id': t.id,
                    'sender_id': t.sender_id,
                    'recipient_id': t.recipient_id,
                    'amount': t.amount,
                    'type': t.type,
                    'fo_id': t.fo_id,
                    'timestamp': t.timestamp,
                    'status': t.status,
                    'block_hash': t.block_hash,
                } for t in db_transactions]
        finally:
            self.close_session(session)

    def get_all_blocks_data(self):
        """
        Получает данные всех блоков из БД.
        """
        session = self.get_session()
        try:
            db_blocks = session.query(models.Block).all()
            return [{
                    'index': b.index,
                    'hash': b.hash,
                    'previous_hash': b.previous_hash,
                    'transactions': json.loads(b.transactions_json),
                    'timestamp': b.timestamp,
                    'nonce': b.nonce,
                } for b in db_blocks]
        finally:
            self.close_session(session)

    def log_entry(self, level, message, node_id=None):
        """
        Сохраняет запись в лог БД.
        """
        session = self.get_session()
        try:
            log_entry = models.LogEntry(level=level, message=message, node_id=node_id)
            session.add(log_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Не удалось записать лог в БД: {e}")
        finally:
            self.close_session(session)

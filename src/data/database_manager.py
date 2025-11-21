from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models
import os

class DatabaseManager:
    """
    Класс для управления подключением и операциями с базой данных.
    """
    def __init__(self, db_path="sqlite:///../db/simulation_data.db"):
        """
        Инициализирует менеджер БД.

        Args:
            db_path (str): Путь к файлу базы данных. По умолчанию используется SQLite.
        """
        self.engine = create_engine(db_path, echo=False) # echo=True для отладки SQL
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()

    def create_tables(self):
        """
        Создаёт таблицы в БД на основе моделей SQLAlchemy.
        """
        models.Base.metadata.create_all(bind=self.engine)
        print(f"[DB] Таблицы созданы в {self.engine.url}")

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
            # Проверяем, существует ли пользователь
            db_user = session.query(models.User).filter(models.User.id == user_data['id']).first()
            if db_user:
                # Обновляем поля
                for key, value in user_data.items():
                    if hasattr(db_user, key):
                        setattr(db_user, key, value)
            else:
                # Создаём нового пользователя
                db_user = models.User(**user_data)
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
            # Проверяем, существует ли транзакция
            db_tx = session.query(models.Transaction).filter(models.Transaction.id == tx_data['id']).first()
            if db_tx:
                # Обновляем поля, например, статус или хеш блока
                for key, value in tx_data.items():
                    if hasattr(db_tx, key):
                        setattr(db_tx, key, value)
            else:
                # Создаём новую транзакцию
                # Преобразуем timestamp из float в datetime, если нужно
                if isinstance(tx_data.get('timestamp'), float):
                    import datetime
                    tx_data['timestamp'] = datetime.datetime.fromtimestamp(tx_data['timestamp'])
                db_tx = models.Transaction(**tx_data)
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
            # Проверяем, существует ли блок
            db_block = session.query(models.Block).filter(models.Block.hash == block_data['hash']).first()
            if db_block:
                print(f"[WARN] Блок с хешем {block_data['hash']} уже существует в БД.")
                return # Не сохраняем дубликат
            # Создаём новый блок
            # Преобразуем timestamp из float в datetime, если нужно
            if isinstance(block_data.get('timestamp'), float):
                import datetime
                block_data['timestamp'] = datetime.datetime.fromtimestamp(block_data['timestamp'])
            # Преобразуем список транзакций в JSON строку
            import json
            tx_json = json.dumps([tx for tx in block_data.get('transactions', [])])
            db_block = models.Block(
                index=block_data['index'],
                hash=block_data['hash'],
                previous_hash=block_data['previous_hash'],
                transactions_json=tx_json,
                timestamp=block_data['timestamp'],
                nonce=block_data['nonce']
            )
            session.add(db_block)
            session.commit()
            print(f"[DB] Блок {block_data['index']} (hash {block_data['hash'][:8]}) сохранён.")
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
            import json
            return [{
                    'index': b.index,
                    'hash': b.hash,
                    'previous_hash': b.previous_hash,
                    'transactions': json.loads(b.transactions_json), # Возвращает список транзакций
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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models
import os
import json
import datetime # Импортируем datetime для преобразования timestamp

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
        user_data должен содержать только поля, соответствующие модели models.User.
        """
        session = self.get_session()
        try:
            # Проверяем, существует ли пользователь в БД
            db_user = session.query(models.User).filter(models.User.id == user_data['id']).first()
            if db_user:
                # Обновляем поля модели БД, соответствующие ключам в user_data
                # Используем setattr для безопасного обновления
                for key, value in user_data.items():
                    # Проверяем, есть ли такое поле в модели SQLAlchemy
                    if hasattr(models.User, key):
                        setattr(db_user, key, value)
                    # else:
                    #     print(f"[WARN] Поле {key} не найдено в модели User SQLAlchemy. Пропускаем.")
            else:
                # Создаём нового пользователя
                # Создаём экземпляр модели SQLAlchemy
                # Поля, которые не существуют в модели, вызовут ошибку SQLAlchemy
                # Поэтому user_data должен быть совместим с моделью User
                # Проверим совместимость перед созданием
                # ИСПРАВЛЕНО: используем список полей из модели
                # valid_fields = ['id', 'type', 'balance_non_cash', 'balance_digital', 'balance_offline', 'status_digital_wallet', 'status_offline_wallet', 'offline_wallet_expiry']
                # filtered_data = {k: v for k, v in user_data.items() if k in valid_fields}

                # Альтернатива: просто передать весь user_data и позволить SQLAlchemy обработать ошибки
                # Но лучше отфильтровать, чтобы избежать проблем
                # Используем атрибуты самой модели для получения валидных полей
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
                # Если это объект datetime или None, оставляем как есть

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
            # Проверяем, существует ли транзакция в БД
            db_tx = session.query(models.Transaction).filter(models.Transaction.id == tx_data['id']).first()
            if db_tx:
                # Обновляем поля модели БД, соответствующие ключам в tx_data
                for key, value in tx_data.items():
                    if hasattr(models.Transaction, key):
                        setattr(db_tx, key, value)
                    # else:
                    #     print(f"[WARN] Поле {key} не найдено в модели Transaction SQLAlchemy. Пропускаем.")
            else:
                # Создаём новую транзакцию
                # Преобразуем timestamp из float в datetime, если нужно
                # и если он присутствует в tx_data
                tx_data_for_db = tx_data.copy()
                if 'timestamp' in tx_data_for_db and isinstance(tx_data_for_db['timestamp'], float):
                    tx_data_for_db['timestamp'] = datetime.datetime.fromtimestamp(tx_data_for_db['timestamp'])

                # Убедимся, что все поля в tx_data_for_db существуют в модели Transaction
                # SQLAlchemy сама проверит это, но мы можем отфильтровать заранее
                # valid_fields = ['id', 'sender_id', 'recipient_id', 'amount', 'type', 'fo_id', 'timestamp', 'status', 'additional_data', 'block_hash']
                # filtered_tx_data = {k: v for k, v in tx_data_for_db.items() if k in valid_fields}

                db_tx = models.Transaction(**tx_data_for_db) # Используем оригинальные данные, SQLAlchemy проверит
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
            # Проверяем, существует ли блок в БД
            db_block = session.query(models.Block).filter(models.Block.hash == block_data['hash']).first()
            if db_block:
                print(f"[WARN] Блок с хешем {block_data['hash']} уже существует в БД.")
                return # Не сохраняем дубликат

            # Создаём новый блок
            # Преобразуем timestamp из float в datetime, если нужно
            # и если он присутствует в block_data
            block_data_for_db = block_data.copy()
            if 'timestamp' in block_data_for_db and isinstance(block_data_for_db['timestamp'], float):
                block_data_for_db['timestamp'] = datetime.datetime.fromtimestamp(block_data_for_db['timestamp'])

            # Преобразуем список транзакций в JSON строку
            # и убедимся, что поле называется transactions_json в модели
            tx_json = json.dumps(block_data_for_db.get('transactions', []), default=str) # default=str на случай, если транзакции - объекты
            block_data_for_db['transactions_json'] = tx_json

            # Убедимся, что используем правильные имена полей для модели Block
            # index, hash, previous_hash, transactions_json, timestamp, nonce
            db_block = models.Block(
                index=block_data_for_db['index'],
                hash=block_data_for_db['hash'],
                previous_hash=block_data_for_db['previous_hash'],
                transactions_json=block_data_for_db['transactions_json'], # Используем преобразованное поле
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
        Возвращает словарь, совместимый с моделью User SQLAlchemy.
        """
        session = self.get_session()
        try:
            db_user = session.query(models.User).filter(models.User.id == user_id).first()
            if db_user:
                # Возвращаем словарь с атрибутами модели
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
        Возвращает список словарей, совместимых с моделью User SQLAlchemy.
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

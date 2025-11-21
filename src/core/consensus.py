import time
import threading
import hashlib
from . import blockchain
from . import transaction
from . import utils # Импортируем utils для криптографии

# --- Вспомогательные классы для HotStuff ---

class QuorumCertificate:
    """
    Сертификат кворума (QC), подтверждающий, что 2f+1 узлов проголосовали за определённый блок в определённом view.
    """
    def __init__(self, view, block_hash, signatures):
        self.view = view
        self.block_hash = block_hash
        self.signatures = signatures # Словарь {node_id: signature}

    def to_dict(self):
        return {
            'view': self.view,
            'block_hash': self.block_hash,
            'signatures': self.signatures
        }

class Replica:
    """
    Класс, представляющий узел (реплику) в консенсусе HotStuff.
    В нашей модели это будет Финансовая Организация (FO), участвующая в консенсусе.
    """
    def __init__(self, node_id, blockchain_instance, financial_org_instance, validator_set, crypto_instance):
        self.node_id = node_id
        self.blockchain = blockchain_instance
        self.fo = financial_org_instance # Ссылка на ФО, которая является узлом
        self.validator_set = validator_set # Объект, хранящий узлы и их веса (упрощённо)
        self.crypto = crypto_instance # Объект для криптографических операций (заглушка)

        # Состояние узла
        self.current_view = 0
        self.high_qc = None # Наивысший известный QC
        self.high_commit_qc = None # Наивысший QC для коммита
        self.pending_blocks = {} # {block_hash: Block_object}
        self.pending_qcs = {} # {block_hash: QuorumCertificate_object}
        self.votes = {} # {block_hash: {node_id: signature}}
        self.lock = threading.Lock()
        self._running = True # Флаг для остановки

        # Для симуляции: ссылка на сеть (упрощённая)
        self.network = None

    def set_network(self, network_instance):
        """Устанавливает ссылку на сеть для обмена сообщениями."""
        self.network = network_instance

    def is_primary(self, view, for_node_id=None):
        """
        Проверяет, является ли указанный узел (или self, если не указан) лидером (primary) для данного view.
        """
        # Простой способ: round-robin по ID узлов
        sorted_nodes = sorted(self.validator_set.validators.keys())
        primary_index = view % len(sorted_nodes)
        primary_id = sorted_nodes[primary_index]
        node_to_check = for_node_id if for_node_id is not None else self.node_id
        return primary_id == node_to_check

    def propose_block(self):
        """
        Инициирует создание и отправку сообщения PROPOSE, если этот узел лидер (primary).
        """
        with self.lock:
            if not self.is_primary(self.current_view):
                # print(f"[HOTSTUFF] Узел {self.node_id} (Non-Primary) пропускает propose для view {self.current_view}.")
                return

            print(f"[HOTSTUFF] Узел {self.node_id} (Primary) начинает формирование блока для view {self.current_view}.")

            # Получаем транзакции из пула ФО
            transactions_to_include = self.fo.process_pool_for_consensus()
            if not transactions_to_include:
                 print(f"[HOTSTUFF] Узел {self.node_id} (Primary) не нашёл транзакций для view {self.current_view}. Предлагает пустой блок.")
                 # Даже если транзакций нет, всё равно можно предложить пустой блок
                 transactions_to_include = []

            # Создаём блок
            latest_block = self.blockchain.get_latest_block()
            new_block = blockchain.Block(
                index=latest_block.index + 1,
                previous_hash=latest_block.hash,
                transactions=transactions_to_include,
                timestamp=time.time()
            )

            # Привязываемся к high_qc
            new_block.parent_qc = self.high_qc.to_dict() if self.high_qc else None

            block_hash = new_block.calculate_hash()
            self.pending_blocks[block_hash] = new_block

            # Формируем сообщение PROPOSE
            propose_msg = {
                'type': 'PROPOSE',
                'view': self.current_view,
                'block': new_block.to_dict(),
                'parent_qc': new_block.parent_qc,
                'sender_id': self.node_id
            }

            print(f"[HOTSTUFF] Узел {self.node_id} (Primary) отправляет PROPOSE для блока {new_block.index} (view {self.current_view}).")

            # Отправляем всем узлам
            if self.network:
                self.network.broadcast_message(propose_msg, exclude_sender=True)

    def handle_propose(self, msg):
        """
        Обрабатывает сообщение PROPOSE.
        """
        with self.lock:
            view = msg['view']
            block_data = msg['block']
            parent_qc_data = msg['parent_qc']
            sender_id = msg['sender_id']

            # Проверяем, что view актуален
            if view != self.current_view:
                print(f"[HOTSTUFF] Узел {self.node_id}: Получен PROPOSE для неактуального view {view} (ожидается {self.current_view}).")
                # Здесь может быть логика для ViewChange, если view устарел
                return

            # Проверяем, что отправитель - primary для этого view
            # ИСПРАВЛЕНО: используем is_primary для проверки sender_id
            if not self.is_primary(view, for_node_id=sender_id):
                 print(f"[HOTSTUFF] Узел {self.node_id}: Получен PROPOSE от не-лидера {sender_id} для view {view}.")
                 return

            # Валидация блока (упрощённо)
            # Проверим parent_qc, если он есть
            if parent_qc_data:
                parent_block_hash = parent_qc_data['block_hash']
                # В реальной системе проверяется подпись QC
                print(f"[HOTSTUFF] Узел {self.node_id}: Проверяет parent_qc для блока {block_data['index']}.")
                # Предположим, проверка прошла успешно

            # Создаём объект Block из словаря
            try:
                new_block = blockchain.Block(
                    index=block_data['index'],
                    previous_hash=block_data['previous_hash'],
                    # transactions - список словарей, нужно преобразовать в объекты Transaction
                    transactions=[transaction.Transaction(**tx) for tx in block_data['transactions']],
                    timestamp=block_data['timestamp'],
                    nonce=block_data['nonce']
                )
                # Устанавливаем хеш, вычисленный при создании объекта Block
                new_block.hash = block_data['hash']
                new_block.parent_qc = parent_qc_data # Сохраняем родительский QC
            except Exception as e:
                print(f"[HOTSTUFF] Узел {self.node_id}: Ошибка при создании объекта Block из PROPOSE: {e}")
                return

            block_hash = new_block.hash

            # Проверяем, что блок можно применить к текущему состоянию
            if not self.blockchain.validate_block_transactions(new_block):
                print(f"[HOTSTUFF] Узел {self.node_id}: Блок {new_block.index} не прошёл валидацию. Отклоняем.")
                return

            print(f"[HOTSTUFF] Узел {self.node_id}: Принят PROPOSE для блока {new_block.index} (view {view}).")

            # Шаг 2: Голосование (Vote)
            self._vote_for_block(block_hash, view)

    def _vote_for_block(self, block_hash, view):
        """
        Отправляет сообщение VOTE за указанный блок в указанном view.
        """
        vote_msg = {
            'type': 'VOTE',
            'view': view,
            'block_hash': block_hash,
            'sender_id': self.node_id
        }
        print(f"[HOTSTUFF] Узел {self.node_id} отправляет VOTE за блок {block_hash[:8]} (view {view}).")

        # Отправляем лидеру следующего view (или текущему, если голосование в том же view)
        # В простой модели отправляем всем
        if self.network:
            self.network.broadcast_message(vote_msg, exclude_sender=True)

    def handle_vote(self, msg):
        """
        Обрабатывает сообщение VOTE.
        """
        with self.lock:
            view = msg['view']
            block_hash = msg['block_hash']
            sender_id = msg['sender_id']

            # Проверяем view
            if view != self.current_view:
                 # Голоса для устаревших view игнорируются или обрабатываются по-другому
                 print(f"[HOTSTUFF] Узел {self.node_id}: Получен VOTE для неактуального view {view}.")
                 return

            # Проверяем, что узел может голосовать (реально проверяется подпись и ключ)
            if sender_id not in self.validator_set.validators:
                print(f"[HOTSTUFF] Узел {self.node_id}: Получен VOTE от неизвестного узла {sender_id}.")
                return

            # Инициализируем словарь для голосов за этот блок
            if block_hash not in self.votes:
                self.votes[block_hash] = {}

            # Сохраняем голос (в реальности проверяется подпись)
            self.votes[block_hash][sender_id] = msg.get('signature', 'dummy_sig') # Заглушка для подписи

            print(f"[HOTSTUFF] Узел {self.node_id}: Принят VOTE от {sender_id} за блок {block_hash[:8]} (view {view}). Всего голосов: {len(self.votes[block_hash])}")

            # Проверяем, набран ли кворум (2f+1 голосов)
            # f = (len(validators) - 1) // 3
            f = len(self.validator_set.validators) // 3 # Примерное f
            quorum_threshold = 2 * f + 1

            if len(self.votes[block_hash]) >= quorum_threshold:
                print(f"[HOTSTUFF] Узел {self.node_id}: Набран кворум голосов ({len(self.votes[block_hash])}) за блок {block_hash[:8]} (view {view}).")
                # Создаём QC
                qc = QuorumCertificate(view, block_hash, self.votes[block_hash].copy())
                self.pending_qcs[block_hash] = qc

                # Пытаемся зафиксировать (commit) блок
                self._try_commit_block(block_hash, qc)

    def _try_commit_block(self, block_hash, qc):
        """
        Проверяет правило коммита (3 подряд идущих QC) и фиксирует блок, если правило выполнено.
        """
        # Правило коммита HotStuff: если есть цепочка из 3 подряд идущих блоков с QC,
        # то третий с конца (leaf) можно коммитить.
        # Для упрощения: если у нас есть QC для текущего блока (C), и он ссылается на
        # блок с parent_qc (P), и этот parent_qc (P) ссылается на блок с high_commit_qc (G),
        # то можно коммитить блок, на который ссылается parent_qc (т.е. P).
        # high_commit_qc -> parent_qc -> qc_current
        # Тогда блок, на который ссылается parent_qc (P), можно коммитить.

        # Найдём блок, для которого у нас есть qc_current
        block_current = self.pending_blocks.get(block_hash)
        if not block_current:
            print(f"[HOTSTUFF] Узел {self.node_id}: QC для неизвестного блока {block_hash[:8]}.")
            return # Блок не найден

        parent_qc_data = block_current.parent_qc
        if not parent_qc_data:
            # Если нет parent_qc, это может быть genesis или первый блок
            # Пока что просто обновим high_qc
            self.high_qc = qc
            print(f"[HOTSTUFF] Узел {self.node_id}: Обновлён high_qc до view {qc.view} для блока {block_hash[:8]}.")
            return

        # Проверим, есть ли parent_qc (P) у current (C), и есть ли high_commit_qc (G) у parent_qc (P)
        parent_block_hash = parent_qc_data.get('block_hash')
        parent_block = self.pending_blocks.get(parent_block_hash)

        if parent_block:
            # Проверим, есть ли QC для parent_block (P), который является "дедушкой" для current (C)
            # Это означает, что у нас есть QC для P (parent_qc), и если у нас есть QC для G (high_commit_qc),
            # и parent_qc(P) ссылается на G, то можно коммитить P.
            # Однако, в нашей упрощенной логике, если у нас есть QC для C, и parent_qc(P) для C,
            # и QC для P (в pending_qcs), и parent_qc(G) для P (в pending_qcs или в high_commit_qc),
            # то можно коммитить G (т.е. "дедушку" P).
            # Уточним: если у нас есть QC(C), parent_qc(P) для C, и QC(P) для P, и parent_qc(G) для P,
            # и QC(G) для G, то можно коммитить G.
            # Или, если есть high_commit_qc (G), и QC(P) для P, и parent_qc(P) указывает на G, и QC(C) для C, и parent_qc(C) указывает на P,
            # то можно коммитить P.
            # Попробуем упрощённую версию: если у нас есть high_commit_qc(G), и QC(P), и parent_qc(P) указывает на G, то можно коммитить P.
            # Но для этого нужно, чтобы parent_qc(P) был доступен у P.
            # В нашем случае, parent_qc хранится в блоке (new_block.parent_qc).
            # Проверим, есть ли QC для parent_block (P)
            parent_qc_for_p = self.pending_qcs.get(parent_block_hash)
            if parent_qc_for_p and self.high_commit_qc and self.high_commit_qc.block_hash == parent_block.parent_qc.get('block_hash'):
                # high_commit_qc -> parent_qc_for_p -> qc_for_current
                # Коммитим parent_qc_for_p (т.е. блок P)
                block_to_commit_hash = parent_block_hash
                block_to_commit = parent_block
                if block_to_commit:
                    print(f"[HOTSTUFF] Узел {self.node_id}: Правило коммита выполнено. Коммитит блок {block_to_commit.index} (hash {block_to_commit_hash[:8]}).")
                    # Добавляем блок в цепочку
                    success = self.blockchain.add_block(block_to_commit)
                    if success:
                        # Обновляем high_commit_qc на QC, который подтверждает коммитнутый блок
                        self.high_commit_qc = parent_qc_for_p
                        print(f"[HOTSTUFF] Узел {self.node_id}: Блок {block_to_commit.index} успешно закоммичен.")
                    else:
                        print(f"[HOTSTUFF] Узел {self.node_id}: Не удалось закоммитить блок {block_to_commit.index}.")


        # Обновляем high_qc на текущий, если он "новее"
        if not self.high_qc or qc.view > self.high_qc.view:
            self.high_qc = qc
            print(f"[HOTSTUFF] Узел {self.node_id}: Обновлён high_qc до view {qc.view} для блока {block_hash[:8]}.")

    def run(self):
        """
        Основной цикл работы узла (реплики).
        """
        print(f"[HOTSTUFF] Узел {self.node_id} запущен.")
        while self._running:
            # Проверяем, пора ли предлагать новый блок (например, по таймеру)
            # В упрощённой модели, просто вызываем propose_block периодически
            # или когда есть транзакции. Добавим искусственную задержку.
            time.sleep(2) # Имитация времени между раундами
            self.propose_block()
            # Логика обработки сообщений должна быть асинхронной, например, через очередь в сети

    def stop(self):
        """Останавливает цикл работы узла."""
        self._running = False

    # Метод handle_message в Replica для универсальной обработки
    def handle_message(self, message):
        """
        Универсальный обработчик входящих сообщений.
        """
        msg_type = message.get('type')
        if msg_type == 'PROPOSE':
            self.handle_propose(message)
        elif msg_type == 'VOTE':
            self.handle_vote(message)
        #elif msg_type == 'TIMEOUT':
        #    self.handle_timeout(message)
        else:
            print(f"[HOTSTUFF] Узел {self.node_id}: Получено неизвестное сообщение типа {msg_type}.")


# --- Вспомогательные классы для симуляции сети и валидаторов ---

class ValidatorSet:
    """
    Упрощённый класс для хранения валидаторов и их весов.
    """
    def __init__(self, validators, voting_power):
        self.validators = validators # {node_id: public_key}
        self.voting_power = voting_power # {node_id: power}

class MockCrypto:
    """
    Заглушка для криптографических операций.
    В реальной системе тут были бы подлинные функции подписи и проверки.
    """
    def sign(self, data, private_key):
        return f"mock_signature_of_{utils.calculate_hash(data)}_with_{private_key}"

    def verify(self, signature, data, public_key):
        expected_sig = f"mock_signature_of_{utils.calculate_hash(data)}_with_{public_key}"
        return signature == expected_sig

class InMemoryNetwork:
    """
    Упрощённая "сеть" для симуляции передачи сообщений между узлами.
    """
    def __init__(self, replicas):
        self.replicas = {r.node_id: r for r in replicas} # Словарь {node_id: Replica_object}

    def broadcast_message(self, message, exclude_sender=False):
        """
        Рассылает сообщение всем узлам.
        """
        sender_id = message.get('sender_id')
        for node_id, replica in self.replicas.items():
            if exclude_sender and node_id == sender_id:
                continue
            # В реальной системе тут был бы сетевой вызов
            # Имитируем вызов обработчика на другом узле
            replica.handle_message(message)

    def send_message_to(self, message, target_node_id):
        """
        Отправляет сообщение конкретному узлу.
        """
        target_replica = self.replicas.get(target_node_id)
        if target_replica:
            target_replica.handle_message(message)

    def get_replica(self, node_id):
        """Возвращает объект реплики по ID."""
        return self.replicas.get(node_id)

    def get_all_replica_ids(self):
        """Возвращает список всех ID реплик."""
        return list(self.replicas.keys())

    # Метод для обработки сообщений должен быть вызван из реплики
    # или из центрального менеджера.
    # Добавим его в Replica как публичный метод для вызова из Network
    # (это не идеальная архитектура, но работает для симуляции)
    def deliver_message_to_replica(self, message, target_node_id):
        replica = self.get_replica(target_node_id)
        if replica:
            replica.handle_message(message)

    # --- Добавим метод для симуляции смены view (упрощённо) ---
    def change_view(self):
        """
        (Упрощённая) симуляция смены view, например, по таймеру или при отсутствии прогресса.
        """
        # В реальной системе тут была бы сложная логика с таймаутами и голосованием за смену.
        # Для симуляции просто увеличим view.
        for replica in self.replicas.values():
            with replica.lock:
                replica.current_view += 1
        print(
            f"[HOTSTUFF-NETWORK] Смена view на {self.replicas[next(iter(self.replicas))].current_view} для всех узлов (симуляция).")

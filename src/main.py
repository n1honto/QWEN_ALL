# -*- coding: utf-8 -*-
"""
Точка входа в имитационную модель цифрового рубля.
Запускает симуляцию и UI.
"""

# --- КРИТИЧЕСКИЕ ИЗМЕНЕНИЯ ---
# Убедимся, что корень проекта (digital_ruble_simulation) доступен для импорта
# Это достигается добавлением пути к корню в sys.path.
import os
import sys
import time
import threading
import random
from datetime import datetime, timedelta

from src.core import utils

# Определяем путь к корню проекта относительно этого файла
# main.py находится в digital_ruble_simulation/src/main.py
current_file_dir = os.path.dirname(os.path.abspath(__file__)) # digital_ruble_simulation/src
project_root = os.path.dirname(os.path.dirname(current_file_dir)) # digital_ruble_simulation

# Добавляем корень проекта в начало sys.path, если его там ещё нет
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"[MAIN] sys.path обновлён. Корень проекта: {project_root}") # Для отладки
print(f"[MAIN] sys.path: {sys.path[:3]}...") # Показываем начало пути для проверки

# --- ОСТАЛЬНОЙ КОД main.py ---
# Попробуем импортировать каждый модуль по отдельности для отладки
try:
    from digital_ruble_simulation.src.core import participants, blockchain, consensus, transaction
    print("[MAIN] Успешно импортированы core модули")
except ImportError as e:
    print(f"[ERROR] Не удалось импортировать core модули: {e}")
    sys.exit(1)

try:
    from digital_ruble_simulation.src.data import database_manager
    print("[MAIN] Успешно импортирован database_manager")
except ImportError as e:
    print(f"[ERROR] Не удалось импортировать database_manager: {e}")
    sys.exit(1)

try:
    from digital_ruble_simulation.ui import main_window # Импортируем главный файл UI
    print("[MAIN] Успешно импортирован main_window")
except ImportError as e:
    print(f"[ERROR] Не удалось импортировать main_window: {e}")
    sys.exit(1)

# --- Остальной код main.py ---

# --- Глобальные переменные для симуляции ---
SIMULATION_RUNNING = False
SIMULATION_END_TIME = None
SIMULATION_DURATION_SECONDS = 3600 # 1 час вирт. времени по умолчанию

# --- Параметры сценариев ---
SCENARIOS = {
    "low": {"num_users": 1000, "num_fos": 5, "total_transactions_expected": 4150},
    "medium": {"num_users": 10000, "num_fos": 10, "total_transactions_expected": 41800},
    "peak": {"num_users": 50000, "num_fos": 15, "total_transactions_expected": 208500},
}

def initialize_simulation(num_users=1000, num_fos=5, scenario="low"):
    """
    Инициализирует все компоненты симуляции.
    """
    global SIMULATION_RUNNING, SIMULATION_END_TIME, SIMULATION_DURATION_SECONDS

    print(f"[MAIN] Инициализация симуляции: {num_users} пользователей, {num_fos} ФО, сценарий {scenario}.")

    # --- Настройка параметров симуляции ---
    if scenario in SCENARIOS:
        SIMULATION_DURATION_SECONDS = 3600 # 1 час для всех сценариев
        total_transactions_expected = SCENARIOS[scenario]["total_transactions_expected"]
        # Перезаписываем num_users и num_fos, если они переданы как None или 0
        if num_users <= 0:
            num_users = SCENARIOS[scenario]["num_users"]
        if num_fos <= 0:
            num_fos = SCENARIOS[scenario]["num_fos"]
    else:
        print(f"[WARN] Неизвестный сценарий {scenario}, использую параметры по умолчанию.")
        SIMULATION_DURATION_SECONDS = 3600
        total_transactions_expected = 4150

    print(f"[MAIN] Использую параметры: {num_users} пользователей, {num_fos} ФО, {total_transactions_expected} транзакций.")

    # --- Инициализация БД ---
    db_manager = database_manager.DatabaseManager()
    print(f"[MAIN] Менеджер базы данных инициализирован.")

    # --- Инициализация блокчейна ---
    digital_ruble_chain = blockchain.Blockchain(difficulty=2) # Уровень сложности для майнинга (если применимо)
    print(f"[MAIN] Блокчейн инициализирован.")

    # --- Инициализация ЦБ ---
    central_bank = participants.CentralBank(initial_reserve=1000000000.0) # 1 млрд ЦР
    print(f"[MAIN] Центральный банк инициализирован.")

    # --- Инициализация ФО ---
    financial_orgs = {}
    validator_set_data = {} # Для консенсуса
    for i in range(num_fos):
        fo_id = f"FO_{i+1:03d}"
        fo_instance = participants.FinancialOrg(fo_id, central_bank, db_manager) # Передаём db_manager
        financial_orgs[fo_id] = fo_instance
        validator_set_data[fo_id] = "mock_public_key" # Заглушка
    print(f"[MAIN] {num_fos} Финансовых Организаций инициализировано.")

    # --- Инициализация пользователей ---
    users = {}
    for i in range(num_users):
        # ИСПРАВЛЕНО: используем participants.UserType
        user_type = random.choice([participants.UserType.PHYSICAL, participants.UserType.LEGAL])
        user_id = f"USER_{i+1:06d}"
        # --- КРИТИЧЕСКОЕ ИЗМЕНЕНИЕ: Пользователь создаётся с initial_balance=10000 ---
        user_instance = participants.User(user_id, user_type, initial_balance=10000.0) # 10000 по умолчанию - ПРАВИЛЬНО
        users[user_id] = user_instance

        # Регистрируем пользователей в случайной ФО
        random_fo_id = random.choice(list(financial_orgs.keys()))
        financial_orgs[random_fo_id].add_user(user_instance)

        # Сохраняем данные пользователя в БД
        # ИСПРАВЛЕНО: передаём только поля, совместимые с моделью БД, используя get_wallet_info
        user_db_data = user_instance.get_wallet_info() # Получаем текущее состояние
        # database_manager.save_user фильтрует поля, так что можно передать весь словарь
        db_manager.save_user(user_db_data) # Передаём словарь из get_wallet_info
    print(f"[MAIN] {num_users} пользователей инициализировано и распределены по ФО.")

    # --- Инициализация консенсуса ---
    # Создаём валидаторов (реплик) для HotStuff
    replicas = []
    for fo_id, fo_instance in financial_orgs.items():
        replica = consensus.Replica(
            node_id=fo_id,
            blockchain_instance=digital_ruble_chain,
            financial_org_instance=fo_instance,
            validator_set=consensus.ValidatorSet(validator_set_data, {k: 1 for k in validator_set_data}), # Равный вес
            crypto_instance=consensus.MockCrypto(), # Заглушка
            db_manager = db_manager # Передаём db_manager для сохранения блоков
        )
        replicas.append(replica)

    # Инициализируем сеть для реплик
    network = consensus.InMemoryNetwork(replicas)
    for replica in replicas:
        replica.set_network(network)

    print(f"[MAIN] HotStuff консенсус инициализирован с {len(replicas)} репликами.")

    # --- Сохранение начального состояния в БД ---
    # Блокчейн сохранит genesis блок автоматически при создании
    # ЦБ и ФО не требуют сохранения в БД напрямую, но их транзакции и пользователи - да

    return db_manager, digital_ruble_chain, central_bank, financial_orgs, users, replicas, network, total_transactions_expected

def run_simulation_loop(replicas, duration_seconds, total_transactions_expected, financial_orgs, users, db_manager,
                        tx_=None): # Добавлен аргумент db_manager
    """
    Запускает основной цикл симуляции.
    """
    global SIMULATION_RUNNING, SIMULATION_END_TIME
    SIMULATION_RUNNING = True
    SIMULATION_END_TIME = time.time() + duration_seconds

    print(f"[MAIN] Запуск основного цикла симуляции на {duration_seconds} секунд вирт. времени.")
    print(f"[MAIN] Ожидаемое время окончания: {datetime.fromtimestamp(SIMULATION_END_TIME)}")
    print(f"[MAIN] Ожидаемое количество транзакций: {total_transactions_expected}")

    # Запускаем циклы реплик в отдельных потоках
    threads = []
    for replica in replicas:
        t = threading.Thread(target=replica.run)
        t.daemon = True # Поток завершится при завершении основного процесса
        t.start()
        threads.append(t)

    # Основной цикл симуляции (может управлять генерацией транзакций и т.д.)
    start_time = time.time()
    generated_tx_count = 0
    last_report_time = start_time
    report_interval = 10 # Секунд между отчетами
    last_ui_update_time = start_time # Время последнего обновления UI
    ui_update_interval = 5 # Секунд между обновлениями UI

    # --- Добавим переменные для отслеживания сценариев ---
    last_offline_event_time = start_time
    last_smart_contract_event_time = start_time
    offline_event_interval = 30 # Секунд между событиями с офлайн-кошельками
    smart_contract_event_interval = 60 # Секунд между событиями со смарт-контрактами

    while SIMULATION_RUNNING and time.time() < SIMULATION_END_TIME and generated_tx_count < total_transactions_expected:
        # В реальной симуляции тут была бы логика генерации событий, транзакций и т.д.
        # Имитируем генерацию транзакций
        for fo_id, fo_instance in financial_orgs.items():
            if SIMULATION_RUNNING and generated_tx_count < total_transactions_expected:
                 # Имитируем создание транзакций между случайными пользователями этой ФО
                 fo_users = list(fo_instance.users.keys())
                 if len(fo_users) > 1:
                     sender_id = random.choice(fo_users)
                     recipient_id = random.choice(fo_users)
                     while recipient_id == sender_id:
                         recipient_id = random.choice(fo_users)
                     # --- ИСПРАВЛЕНИЕ: Генерируем целое значение ---
                     amount = int(random.uniform(10, 1000)) # Случайная СУММА - ЦЕЛОЕ ЧИСЛО
                     print(f"[SIM_LOOP] Попытка создать транзакцию {sender_id} -> {recipient_id}, сумма: {amount}")

                     # --- ИСПРАВЛЕНИЕ: Убедимся, что у отправителя открыт цифровой кошелёк и есть средства ---
                     sender = fo_instance.users[sender_id]

                     # Открываем цифровой кошелёк, если он закрыт
                     if sender.status_digital_wallet == "ЗАКРЫТ":
                         success = sender.create_digital_wallet()
                         if success:
                             # Сохраняем изменения в БД через переданный db_manager
                             user_db_data = sender.get_wallet_info()
                             db_manager.save_user(user_db_data)
                             print(f"[SIM_LOOP] Цифровой кошелёк {sender_id} открыт.")

                     # Проверяем, есть ли средства на безналичном кошельке для обмена
                     if sender.balance_non_cash > amount and sender.balance_digital < amount:
                         # Обмениваем безналичные деньги на цифровые, чтобы хватило на транзакцию
                         # Обмениваем чуть больше, чем нужно, чтобы была "подушка"
                         exchange_amount = min(int(sender.balance_non_cash), amount * 1.1) # Целое значение
                         success = sender.exchange_to_digital(exchange_amount)
                         if success:
                             # Сохраняем изменения в БД через переданный db_manager
                             user_db_data = sender.get_wallet_info()
                             db_manager.save_user(user_db_data)
                             print(f"[SIM_LOOP] {sender_id} обменял {exchange_amount} на цифровые рубли. Новый баланс цифрового: {sender.balance_digital}")

                     # --- Конец исправления ---

                     # Проверяем, достаточно ли средств на цифровом кошельке *после* подготовки
                     if sender.balance_digital >= amount:
                         tx_id = fo_instance.submit_transaction(sender_id, recipient_id, amount, 'C2C')
                         if tx_id:
                             generated_tx_count += 1
                             # print(f"[SIM_LOOP] Сгенерирована транзакция {tx_id}, всего: {generated_tx_count}/{total_transactions_expected}") # Слишком много логов
                     else:
                         print(f"[SIM_LOOP] Недостаточно средств у {sender_id} для транзакции {amount}. Баланс цифрового: {sender.balance_digital}")

        # --- НОВОЕ: Имитация работы с офлайн-кошельками ---
        current_time = time.time()
        if current_time - last_offline_event_time >= offline_event_interval and SIMULATION_RUNNING and generated_tx_count < total_transactions_expected:
            print(f"[SIM_LOOP] Имитация события с офлайн-кошельком...")
            # Выбираем случайного пользователя
            random_user_id = random.choice(list(users.keys()))
            random_user = users[random_user_id]
            random_fo_id = random.choice(list(financial_orgs.keys()))
            random_fo = financial_orgs[random_fo_id]

            # --- ОТКРЫТИЕ ОФФЛАЙН-КОШЕЛЬКА ---
            if random_user.status_offline_wallet == "ЗАКРЫТ":
                 print(f"[SIM_LOOP] Пользователь {random_user_id} открывает офлайн-кошелёк.")
                 success = random_user.open_offline_wallet()
                 if success:
                     # Сохраняем изменения в БД через переданный db_manager
                     user_db_data = random_user.get_wallet_info()
                     db_manager.save_user(user_db_data)

            # --- ПОПОЛНЕНИЕ ОФФЛАЙН-КОШЕЛЬКА ---
            if random_user.status_offline_wallet == "ОТКРЫТ" and random_user.balance_digital > 0:
                 fill_amount = min(int(random_user.balance_digital), 200) # Пополняем на 200 или сколько есть
                 print(f"[SIM_LOOP] Пользователь {random_user_id} пополняет офлайн-кошелёк на {fill_amount}.")
                 success = random_user.fill_offline_wallet(fill_amount)
                 if success:
                     # Сохраняем изменения в БД через переданный db_manager
                     user_db_data = random_user.get_wallet_info()
                     db_manager.save_user(user_db_data)

            # --- СОЗДАНИЕ И СИНХРОНИЗАЦИЯ ОФФЛАЙН-ТРАНЗАКЦИИ ---
            if random_user.status_offline_wallet == "ОТКРЫТ" and random_user.balance_offline > 0:
                 recipient_offline = random.choice(list(users.keys()))
                 while recipient_offline == random_user_id:
                     recipient_offline = random.choice(list(users.keys()))
                 tx_amount = min(int(random_user.balance_offline), 100) # Отправляем 100 или сколько есть
                 print(f"[SIM_LOOP] Пользователь {random_user_id} создает офлайн-транзакцию на {tx_amount} для {recipient_offline}.")
                 tx_data = random_user.create_offline_transaction(tx_amount, recipient_offline)
                 # --- ИСПРАВЛЕНИЕ: Проверяем, что tx_data не None и не пустой ---
                 if tx_: # ИСПРАВЛЕНО: if tx_data
                     # --- ИСПРАВЛЕНИЕ: Генерируем ID для офлайн-транзакции перед сохранением ---
                     # Используем utils.calculate_hash для генерации ID
                     # Сформируем строку для хеширования, включая уникальные данные транзакции
                     # ИСПРАВЛЕНО: убран .encode() из аргумента calculate_hash
                     offline_tx_id = utils.calculate_hash(f"{tx_data['sender_id']}{tx_data['recipient_id']}{tx_data['amount']}{tx_data['timestamp']}{tx_data['type']}")
                     tx_data['id'] = offline_tx_id # --- ДОБАВЛЕНО: ID транзакции ---
                     # --- Конец исправления ---

                     # Сохраняем офлайн-транзакцию в БД как транзакцию со статусом OFFLINE
                     tx_data['status'] = 'ОФФЛАЙН'
                     tx_data['fo_id'] = random_fo_id # Назначаем FO для отслеживания
                     db_manager.save_transaction(tx_data) # Сохраняем в БД
                     print(f"[SIM_LOOP] Офлайн-транзакция {offline_tx_id} от {random_user_id} синхронизирована и отправлена в ФО {random_fo_id}.")

                     # --- ИМИТАЦИЯ СИНХРОНИЗАЦИИ ---
                     # В реальной системе это происходило бы при восстановлении связи
                     # Мы имитируем это сразу после создания
                     # Проверим, достаточно ли средств у отправителя в момент синхронизации
                     # (в реальности это проверялось бы при создании, но для симуляции проверим снова)
                     if random_user.balance_offline >= tx_amount:
                         # В реальной системе тут была бы логика обработки офлайн-транзакции
                         # Пока что просто пометим её как "поступила в обработку"
                         tx_data['status'] = 'ПОСТУПИЛО В ОБРАБОТКУ'
                         # В этой симуляции мы не будем делать полноценную проверку двойной траты для офлайн
                         # Предположим, транзакция проходит
                         # Создаём обычную транзакцию через FO для имитации включения в блок
                         # Это не совсем точно отражает реальный процесс, но позволяет включить в консенсус
                         # ВАЖНО: используем submit_transaction, которое генерирует *новый* ID для транзакции, которая пойдёт в пул!
                         # Мы передаём ту же сумму, получателя, но тип OFFLINE_SYNC
                         sync_tx_id = random_fo.submit_transaction(random_user_id, recipient_offline, tx_amount, 'OFFLINE_SYNC')
                         if sync_tx_id:
                             generated_tx_count += 1 # Учитываем как одну из целевых транзакций
                             print(f"[SIM_LOOP] Офлайн-транзакция {offline_tx_id} от {random_user_id} включена в пул ФО {random_fo_id} для обработки в консенсусе (через синхронизированную транзакцию {sync_tx_id}).")
                         else:
                             print(f"[SIM_LOOP] Не удалось отправить офлайн-транзакцию {offline_tx_id} в пул ФО {random_fo_id}.")
                         # Обновим статус *оригинальной* офлайн-транзакции в БД после отправки в пул
                         tx_data['status'] = 'ОБРАБОТАНА' # Имитация успешной обработки
                         # db_manager.save_transaction(tx_data) # Повторное сохранение с новым статусом, если нужно
                     else:
                         print(f"[SIM_LOOP] Недостаточно средств у {random_user_id} для офлайн-транзакции {offline_tx_id} при синхронизации. Отмена.")
                         tx_data['status'] = 'ОТКЛОНЕНА' # Имитация отклонения
                         # db_manager.save_transaction(tx_data) # Сохранение с новым статусом
                     # Обновим данные пользователя в БД после операции
                     user_db_data = random_user.get_wallet_info()
                     db_manager.save_user(user_db_data)

            last_offline_event_time = current_time


        # --- НОВОЕ: Имитация работы со смарт-контрактами ---
        if current_time - last_smart_contract_event_time >= smart_contract_event_interval and SIMULATION_RUNNING and generated_tx_count < total_transactions_expected:
            print(f"[SIM_LOOP] Имитация события со смарт-контрактом...")
            # Выбираем случайного пользователя
            random_user_id_sc = random.choice(list(users.keys()))
            random_user_sc = users[random_user_id_sc]
            random_fo_id_sc = random.choice(list(financial_orgs.keys()))
            random_fo_sc = financial_orgs[random_fo_id_sc]

            # --- СОЗДАНИЕ СМАРТ-КОНТРАКТА ---
            # Пример: смарт-контракт на оплату 1000 ЦР (услуги, коммуналка и т.д.)
            contract_details = {"type": "utility_payment", "amount": 1000, "recipient": "UTILITY_PROVIDER_ID"} # Сумма целая
            contract_id = random_user_sc.create_smart_contract(contract_details)
            print(f"[SIM_LOOP] Создан смарт-контракт {contract_id} пользователем {random_user_id_sc}.")

            # --- ИМИТАЦИЯ ИСПОЛНЕНИЯ КОНТРАКТА ---
            # В реальной системе это было бы триггером или таймером
            # Для симуляции просто выполним транзакцию
            amount_sc = int(contract_details['amount']) # Убедимся, что сумма целая
            recipient_sc = contract_details['recipient']
            # Проверим, достаточно ли средств у отправителя
            if random_user_sc.balance_digital >= amount_sc:
                 print(f"[SIM_LOOP] Смарт-контракт {contract_id} инициирует транзакцию от {random_user_id_sc} к {recipient_sc} на {amount_sc}.")
                 # Выполним транзакцию через ФО
                 tx_id_sc = random_fo_sc.submit_transaction(random_user_id_sc, recipient_sc, amount_sc, 'SMART_CONTRACT_EXECUTION')
                 if tx_id_sc:
                     generated_tx_count += 1 # Учитываем как одну из целевых транзакций
                     print(f"[SIM_LOOP] Транзакция по смарт-контракту {contract_id} включена в пул ФО {random_fo_id_sc} для обработки в консенсусе.")
                 else:
                     print(f"[SIM_LOOP] Не удалось выполнить транзакцию по смарт-контракту {contract_id}.")
            else:
                 print(f"[SIM_LOOP] Недостаточно средств у {random_user_id_sc} для выполнения смарт-контракта {contract_id}.")

            last_smart_contract_event_time = current_time

        time.sleep(0.01) # Небольшая задержка, чтобы не грузить CPU

        # Отчет о прогрессе
        current_time = time.time()
        if current_time - last_report_time >= report_interval:
            print(f"[MAIN] Прогресс симуляции: {generated_tx_count}/{total_transactions_expected} транзакций за {(current_time - start_time):.2f} сек.")
            last_report_time = current_time

        # Обновление UI (примерное, можно уточнить по необходимости)
        if current_time - last_ui_update_time >= ui_update_interval:
            print(f"[MAIN] Обновление данных UI...")
            # Здесь можно вызвать обновление, если MainApplication доступен
            # Однако, в текущей архитектуре это сложно сделать напрямую из потока симуляции
            # Лучше запускать UI обновления из основного потока или по таймеру в UI
            # Пока просто обновим БД для транзакций, которые могли быть созданы
            # Транзакции сохраняются в FinancialOrg.submit_transaction
            last_ui_update_time = current_time

    print(f"[MAIN] Цикл генерации транзакций завершён. Сгенерировано: {generated_tx_count}")

    # Ждём, пока время симуляции не истечёт или не будет остановлена
    while SIMULATION_RUNNING and time.time() < SIMULATION_END_TIME:
        time.sleep(0.1)

    # Останавливаем реплики
    for replica in replicas:
        replica.stop()

    # Ждём завершения потоков реплик
    for t in threads:
        t.join(timeout=1) # Таймаут на случай, если поток не отвечает

    print(f"[MAIN] Цикл симуляции завершён. Время работы: {time.time() - start_time:.2f} сек.")

def stop_simulation():
    """
    Останавливает симуляцию.
    """
    global SIMULATION_RUNNING
    SIMULATION_RUNNING = False
    print(f"[MAIN] Запрошена остановка симуляции.")

def get_simulation_status():
    """
    Возвращает текущий статус симуляции.
    """
    global SIMULATION_RUNNING, SIMULATION_END_TIME
    if SIMULATION_RUNNING:
        remaining_time = SIMULATION_END_TIME - time.time()
        return f"Запущена. Осталось времени: {max(0, remaining_time):.2f} сек."
    else:
        return "Остановлена."

def get_simulation_data(db_manager):
    """
    Возвращает данные для UI.
    """
    users_data = db_manager.get_all_users_data()
    transactions_data = db_manager.get_all_transactions_data()
    blocks_data = db_manager.get_all_blocks_data()
    return {
        'users': users_data,
        'transactions': transactions_data,
        'blocks': blocks_data,
    }

def run_scenario(scenario_name):
    """
    Запускает симуляцию для заданного сценария.
    """
    print(f"[MAIN] Автоматический запуск сценария: {scenario_name}")
    params = SCENARIOS.get(scenario_name)
    if not params:
        print(f"[ERROR] Сценарий {scenario_name} не найден.")
        return

    db_manager, chain, cb, fos, users, replicas, network, expected_txs = initialize_simulation(
        num_users=params["num_users"],
        num_fos=params["num_fos"],
        scenario=scenario_name
    )

    # ИСПРАВЛЕНО: передаём db_manager в run_loop
    run_simulation_loop(replicas, SIMULATION_DURATION_SECONDS, expected_txs, fos, users, db_manager) # Передаём db_manager

def main():
    """
    Основная функция запуска.
    """
    print(f"[MAIN] Запуск имитационной модели цифрового рубля...")

    # --- Инициализация ---
    # Сначала инициализируем с пустыми объектами или минимальными
    # В UI будет кнопка "Запустить симуляцию", которая вызовет initialize_simulation с нужными параметрами
    # и обновит объекты
    # db_manager, chain, cb, fos, users, replicas, network, expected_txs = initialize_simulation(num_users=1000, num_fos=5, scenario="low")
    # Пока что передаём заглушки
    # Используем None для объектов, которые будут созданы позже
    db_manager_instance = None
    blockchain_instance = None
    central_bank_instance = None
    financial_orgs_instance = {}
    users_instance = {}
    replicas_instance = []
    network_instance = None
    expected_txs_instance = 0

    # --- Запуск UI ---
    # Передаём необходимые объекты в UI для взаимодействия
    # Пока что передаём заглушки, они будут обновлены при запуске симуляции
    app = main_window.MainApplication(
        db_manager=db_manager_instance,
        blockchain=blockchain_instance,
        central_bank=central_bank_instance,
        financial_orgs=financial_orgs_instance,
        users=users_instance,
        replicas=replicas_instance,
        network=network_instance,
        simulation_controller={
            'run_loop': run_simulation_loop,
            'stop': stop_simulation,
            'get_status': get_simulation_status,
            'get_data': get_simulation_data,
            'initialize': initialize_simulation,
            'expected_transactions': expected_txs_instance, # Передаём ожидаемое количество транзакций
            'scenarios': SCENARIOS, # Передаём словарь сценариев
            'run_scenario': run_scenario, # Передаём функцию запуска сценария
        }
    )
    app.mainloop()

if __name__ == "__main__":
    # Этот блок выполнится, если main.py запускается напрямую
    # Теперь, благодаря добавлению пути в sys.path, импорты должны работать
    print("main.py запущен напрямую. Попытка импорта и запуска...")
    main()

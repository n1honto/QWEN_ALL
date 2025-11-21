# -*- coding: utf-8 -*-
"""
Точка входа в имитационную модель цифрового рубля.
Запускает симуляцию и UI.
"""

# Используем абсолютные импорты
# Убедимся, что корень проекта (digital_ruble_simulation) доступен для импорта
# Это достигается добавлением пути к корню в sys.path.
import os
import sys
import time
import threading
import random
from datetime import datetime, timedelta

# --- КРИТИЧЕСКИЕ ИЗМЕНЕНИЯ ---
# Определяем путь к корню проекта относительно этого файла
# main.py находится в digital_ruble_simulation/src/main.py
current_file_dir = os.path.dirname(os.path.abspath(__file__)) # digital_ruble_simulation/src
project_root = os.path.dirname(os.path.dirname(current_file_dir)) # digital_ruble_simulation

# Добавляем корень проекта в начало sys.path, если его там ещё нет
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"[MAIN] sys.path обновлён. Корень проекта: {project_root}") # Для отладки
print(f"[MAIN] sys.path: {sys.path[:3]}...") # Показываем начало пути для проверки

# Теперь можно импортировать модули из digital_ruble_simulation
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
    from digital_ruble_simulation.src.ui import main_window # Импортируем главный файл UI
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
        fo_instance = participants.FinancialOrg(fo_id, central_bank)
        financial_orgs[fo_id] = fo_instance
        validator_set_data[fo_id] = "mock_public_key" # Заглушка
    print(f"[MAIN] {num_fos} Финансовых Организаций инициализировано.")

    # --- Инициализация пользователей ---
    users = {}
    for i in range(num_users):
        # ИСПРАВЛЕНО: используем participants.UserType
        user_type = random.choice([participants.UserType.PHYSICAL, participants.UserType.LEGAL])
        user_id = f"USER_{i+1:06d}"
        user_instance = participants.User(user_id, user_type, initial_balance=10000.0) # 10000 по умолчанию - ПРАВИЛЬНО
        users[user_id] = user_instance

        # Регистрируем пользователей в случайной ФО
        random_fo_id = random.choice(list(financial_orgs.keys()))
        financial_orgs[random_fo_id].add_user(user_instance)

        # Сохраняем данные пользователя в БД
        # ИСПРАВЛЕНО: передаём только поля, совместимые с моделью БД, используя get_wallet_info
        user_db_data = user_instance.get_wallet_info() # Получаем текущее состояние
        # Убираем поля, которые не нужны для создания/обновления в БД, но есть в get_wallet_info
        # offline_wallet_activation_time и offline_wallet_deactivation_time - производные, не обязательны для БД
        # Но в модели User SQLAlchemy они есть (offline_wallet_expiry), так что оставим их
        # filtered_db_data = {k: v for k, v in user_db_data.items() if k in ['id', 'type', 'balance_non_cash', 'balance_digital', 'balance_offline', 'status_digital_wallet', 'status_offline_wallet', 'offline_wallet_expiry']}
        # На самом деле, database_manager.save_user фильтрует, так что можно передать весь словарь
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
            crypto_instance=consensus.MockCrypto() # Заглушка
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

def run_simulation_loop(replicas, duration_seconds, total_transactions_expected, financial_orgs, users):
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
                     amount = random.uniform(10, 1000) # Случайная сумма
                     tx_id = fo_instance.submit_transaction(sender_id, recipient_id, amount, 'C2C')
                     if tx_id:
                         generated_tx_count += 1
                         # print(f"[SIM_LOOP] Сгенерирована транзакция {tx_id}, всего: {generated_tx_count}/{total_transactions_expected}") # Слишком много логов
        time.sleep(0.01) # Небольшая задержка, чтобы не грузить CPU

        # Отчет о прогрессе
        current_time = time.time()
        if current_time - last_report_time >= report_interval:
            print(f"[MAIN] Прогресс симуляции: {generated_tx_count}/{total_transactions_expected} транзакций за {(current_time - start_time):.2f} сек.")
            last_report_time = current_time

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

    run_simulation_loop(replicas, SIMULATION_DURATION_SECONDS, expected_txs, fos, users)

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

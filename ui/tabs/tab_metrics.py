import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

class MetricsTab(ttk.Frame):
    def __init__(self, parent, blockchain, db_manager):
        super().__init__(parent)
        self.blockchain = blockchain
        self.db_manager = db_manager

        # --- Таблица метрик ---
        table_frame = ttk.LabelFrame(self, text="Таблица метрик")
        table_frame.pack(fill=tk.X, padx=5, pady=5)

        self.metrics_tree = ttk.Treeview(table_frame, columns=("Metric", "Value"), show="headings", height=6)
        self.metrics_tree.heading("Metric", text="Метрика")
        self.metrics_tree.heading("Value", text="Значение")
        self.metrics_tree.column("Metric", width=200)
        self.metrics_tree.column("Value", width=200)

        self.metrics_tree.pack(fill=tk.X, padx=5, pady=5)

        # --- График метрик ---
        graph_frame = ttk.LabelFrame(self, text="График метрик")
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаём фигуру matplotlib
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления
        self.refresh_btn = ttk.Button(self, text="Обновить метрики", command=self.update_display)
        self.refresh_btn.pack(pady=5)

    def update_display(self):
        # Обновляем таблицу
        # Очищаем таблицу
        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)

        # Получаем данные
        chain_data = self.blockchain.get_chain_data()
        transactions_data = self.db_manager.get_all_transactions_data()

        # Вычисляем метрики
        total_transactions = len(transactions_data)
        total_blocks = len(chain_data)
        # Пример: среднее время между блоками (если есть временные метки)
        block_times = [b['timestamp'] for b in chain_data]
        avg_block_time = "N/A"
        if len(block_times) > 1:
            time_diffs = [block_times[i] - block_times[i-1] for i in range(1, len(block_times))]
            avg_block_time = sum(time_diffs) / len(time_diffs)

        # Заполняем таблицу
        self.metrics_tree.insert("", "end", values=("Количество транзакций", total_transactions))
        self.metrics_tree.insert("", "end", values=("Количество блоков", total_blocks))
        self.metrics_tree.insert("", "end", values=("Среднее время между блоками (с)", f"{avg_block_time:.2f}" if avg_block_time != "N/A" else avg_block_time))
        # Добавьте другие метрики по мере необходимости

        # Обновляем график
        # Пример: график количества транзакций по блокам
        self.ax.clear()
        if chain_data:
            block_indices = [b['index'] for b in chain_data]
            tx_counts = [len(b['transactions']) for b in chain_data]
            self.ax.plot(block_indices, tx_counts, marker='o')
            self.ax.set_xlabel('Индекс блока')
            self.ax.set_ylabel('Количество транзакций')
            self.ax.set_title('Количество транзакций в блоке')
            self.ax.grid(True)

        self.canvas.draw()

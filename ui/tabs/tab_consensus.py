import tkinter as tk
from tkinter import ttk

class ConsensusTab(ttk.Frame):
    def __init__(self, parent, replicas, network):
        super().__init__(parent)
        self.replicas = replicas
        self.network = network

        # --- Визуальное представление (простое текстовое для начала) ---
        visual_frame = ttk.LabelFrame(self, text="Визуальное представление функционирования консенсуса")
        visual_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.visual_text = tk.Text(visual_frame, state=tk.DISABLED)
        self.visual_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Таблица данных консенсуса ---
        data_frame = ttk.LabelFrame(self, text="Данные о функционировании консенсуса")
        data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview для данных
        self.consensus_tree = ttk.Treeview(data_frame, columns=(
            "Hash", "BlockIndex", "TimeTaken"
        ), show="headings")

        self.consensus_tree.heading("Hash", text="Приходящий хеш транзакции / Сформированный блок")
        self.consensus_tree.heading("BlockIndex", text="Индекс блока")
        self.consensus_tree.heading("TimeTaken", text="Время формирования блока (сек)")

        self.consensus_tree.column("Hash", width=200)
        self.consensus_tree.column("BlockIndex", width=100)
        self.consensus_tree.column("TimeTaken", width=150)

        scrollbar_y = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.consensus_tree.yview)
        self.consensus_tree.configure(yscrollcommand=scrollbar_y.set)

        self.consensus_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')

        data_frame.grid_rowconfigure(0, weight=1)
        data_frame.grid_columnconfigure(0, weight=1)

        # Кнопка обновления
        self.refresh_btn = ttk.Button(self, text="Обновить данные", command=self.update_display)
        self.refresh_btn.pack(pady=5)

    def update_display(self):
        # Обновляем визуальное текстовое поле
        # Это может быть сложной визуализацией (граф, диаграмма), но пока простой текст
        self.visual_text.config(state=tk.NORMAL)
        self.visual_text.delete(1.0, tk.END)

        # Пример простой визуализации состояния реплик
        for replica in self.replicas:
            self.visual_text.insert(tk.END, f"Узел {replica.node_id}:\n")
            self.visual_text.insert(tk.END, f"  - Current View: {replica.current_view}\n")
            self.visual_text.insert(tk.END, f"  - High QC View: {replica.high_qc.view if replica.high_qc else 'None'}\n")
            self.visual_text.insert(tk.END, f"  - High Commit QC View: {replica.high_commit_qc.view if replica.high_commit_qc else 'None'}\n")
            self.visual_text.insert(tk.END, f"  - Status: {'RUNNING' if replica._running else 'STOPPED'}\n\n")

        self.visual_text.config(state=tk.DISABLED)

        # Обновляем таблицу (в реальной системе данные приходили бы из логов консенсуса или блокчейна)
        # Пока что обновим, показав последние блоки из цепочки
        # Предположим, у нас есть доступ к блокчейну через одну из реплик
        # Возьмём блокчейн из первой реплики для примера
        if self.replicas:
            blockchain_instance = self.replicas[0].blockchain
            chain_data = blockchain_instance.get_chain_data()

            # Очищаем таблицу
            for item in self.consensus_tree.get_children():
                self.consensus_tree.delete(item)

            # Заполняем таблицу данными о блоках (хеш, индекс, время - разница между блоками)
            previous_block_time = None
            for block_info in chain_data:
                time_taken = "N/A"
                if previous_block_time is not None:
                    time_taken = block_info['timestamp'] - previous_block_time
                self.consensus_tree.insert("", "end", values=(
                    block_info['hash'][:16] + "...", # Обрезаем хеш для отображения
                    block_info['index'],
                    time_taken
                ))
                previous_block_time = block_info['timestamp']

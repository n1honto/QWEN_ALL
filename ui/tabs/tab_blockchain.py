import tkinter as tk
from tkinter import ttk

class BlockchainTab(ttk.Frame):
    def __init__(self, parent, blockchain):
        super().__init__(parent)
        self.blockchain = blockchain

        # --- Визуальное представление (простое текстовое для начала) ---
        visual_frame = ttk.LabelFrame(self, text="Визуальное представление распределенного реестра")
        visual_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.visual_text = tk.Text(visual_frame, state=tk.DISABLED)
        self.visual_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Кнопка обновления
        self.refresh_btn = ttk.Button(self, text="Обновить визуализацию", command=self.update_display)
        self.refresh_btn.pack(pady=5)

    def update_display(self):
        self.visual_text.config(state=tk.NORMAL)
        self.visual_text.delete(1.0, tk.END)

        # Получаем данные цепочки
        chain_data = self.blockchain.get_chain_data()

        # Простая визуализация: перечисляем блоки и их связи
        for i, block_info in enumerate(chain_data):
            if i == 0:
                self.visual_text.insert(tk.END, f"Блок {block_info['index']}\n")
                self.visual_text.insert(tk.END, f"  Хеш: {block_info['hash']}\n")
                self.visual_text.insert(tk.END, f"  Предыдущий хеш: {block_info['previous_hash']} (Genesis)\n\n")
            else:
                self.visual_text.insert(tk.END, f"Блок {block_info['index']}\n")
                self.visual_text.insert(tk.END, f"  Хеш: {block_info['hash']}\n")
                self.visual_text.insert(tk.END, f"  Предыдущий хеш: {block_info['previous_hash']} -> (Блок {i-1})\n\n")

        # Можно добавить отображение транзакций в каждом блоке
        # self.visual_text.insert(tk.END, "--- Транзакции в блоках ---\n")
        # for block_info in chain_data:
        #     self.visual_text.insert(tk.END, f"\nТранзакции в Блоке {block_info['index']}:\n")
        #     for tx in block_info['transactions']:
        #         self.visual_text.insert(tk.END, f"  {tx}\n")

        self.visual_text.config(state=tk.DISABLED)

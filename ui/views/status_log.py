from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class StatusLog:
    def __init__(self, parent: ttk.Frame) -> None:
        self.text = tk.Text(parent, height=14, wrap="word")
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(parent, command=self.text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scroll.set)
        self.text.configure(state=tk.DISABLED)

    def append(self, msg: str) -> None:
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, msg.rstrip() + "\n")
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

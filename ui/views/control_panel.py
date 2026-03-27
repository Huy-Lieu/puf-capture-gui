from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable


@dataclass
class ControlPanelWidgets:
    btn_start: ttk.Button
    btn_stop: ttk.Button
    btn_capture: ttk.Button
    lbl_state: ttk.Label


def build_control_panel(
    parent: ttk.Frame,
    *,
    on_connect: Callable[[], None],
    on_disconnect: Callable[[], None],
    on_capture: Callable[[], None],
) -> ControlPanelWidgets:
    btns = ttk.Frame(parent)
    btns.grid(row=0, column=0, sticky="ew")
    btns.columnconfigure(0, weight=1)
    btns.columnconfigure(1, weight=1)

    btn_start = ttk.Button(btns, text="Connect to RealTerm", command=on_connect)
    btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 6))

    btn_stop = ttk.Button(
        btns, text="Disconnect RealTerm", command=on_disconnect, state=tk.DISABLED
    )
    btn_stop.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    btn_capture = ttk.Button(parent, text="Capture", command=on_capture, state=tk.DISABLED)
    btn_capture.grid(row=1, column=0, sticky="ew", pady=(10, 0))

    ttk.Separator(parent).grid(row=2, column=0, sticky="ew", pady=12)

    lbl_state = ttk.Label(parent, text="Idle")
    lbl_state.grid(row=3, column=0, sticky="w")

    return ControlPanelWidgets(
        btn_start=btn_start,
        btn_stop=btn_stop,
        btn_capture=btn_capture,
        lbl_state=lbl_state,
    )

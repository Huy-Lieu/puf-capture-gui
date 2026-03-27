from __future__ import annotations

import queue
import time
import tkinter as tk
from tkinter import messagebox, ttk

from ui.controllers import EventController, PreviewController, apply_defaults
from ui.services.capture_worker import CaptureWorker
from ui.views.capture_form import CaptureForm, build_capture_form
from ui.views.control_panel import ControlPanelWidgets, build_control_panel
from ui.views.status_log import StatusLog


class RealTermControllerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("RealTerm Controller")
        self.geometry("820x540")
        self.minsize(720, 480)

        self._msg_q: queue.Queue[str] = queue.Queue()
        self._worker = CaptureWorker(self._msg_q, on_done=self._notify_worker_done)
        self.form: CaptureForm
        self.controls: ControlPanelWidgets
        self.log: StatusLog
        self.events: EventController
        self.preview: PreviewController
        self._build_ui()
        apply_defaults(self.form)
        self.preview.apply_naming_mode_ui()
        self.events.refresh_com_ports()
        self.after(100, self._drain_queue)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)

        cfg_frame = ttk.LabelFrame(root, text="Capture Configuration", padding=10)
        cfg_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        cfg_frame.columnconfigure(1, weight=1)

        ctrl_frame = ttk.LabelFrame(root, text="Control", padding=10)
        ctrl_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        ctrl_frame.columnconfigure(0, weight=1)

        log_frame = ttk.LabelFrame(root, text="Status", padding=10)
        log_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        root.rowconfigure(1, weight=1)

        self.form = build_capture_form(
            cfg_frame,
            on_naming_mode_changed=lambda: self.preview.apply_naming_mode_ui(),
            on_refresh_com_ports=lambda: self.events.refresh_com_ports(),
            on_browse_dir=lambda: self.events.browse_dir(),
            on_browse_vivado_bat=lambda: self.events.browse_vivado_bat(),
            on_browse_vivado_project=lambda: self.events.browse_vivado_project(),
            on_browse_vivado_tcl=lambda: self.events.browse_vivado_tcl(),
        )
        self.controls = build_control_panel(
            ctrl_frame,
            on_connect=lambda: self.events.connect(),
            on_disconnect=lambda: self.events.disconnect(),
            on_capture=lambda: self.events.capture_now(),
            on_run_vivado=lambda: self.events.run_vivado_tcl(),
        )
        self.log = StatusLog(log_frame)
        self.preview = PreviewController(self.form)
        self.events = EventController(
            form=self.form,
            controls=self.controls,
            log=self.log,
            worker=self._worker,
        )
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _append(self, msg: str) -> None:
        self.events.append_status(msg)

    def _drain_queue(self) -> None:
        try:
            while True:
                self._append(self._msg_q.get_nowait())
        except queue.Empty:
            pass
        self.after(100, self._drain_queue)

    def _notify_worker_done(self) -> None:
        self.after(0, lambda: self.events.set_running(False))

    def _on_close(self) -> None:
        if self._worker.is_running():
            if not messagebox.askyesno("Quit", "A capture is running. Stop and quit?"):
                return
            self._worker.stop()
            time.sleep(0.05)
        self.destroy()


def main() -> None:
    app = RealTermControllerApp()

    app.form.var_fpga_index.trace_add("write", lambda *_: app.preview.update_filename_preview())
    for var in (
        app.form.var_file_naming_mode,
        app.form.var_end_fpga_index,
        app.form.var_base_name,
        app.form.var_start_index,
        app.form.var_end_index,
        app.form.var_flipflop_position,
        app.form.var_mux_pair,
        app.form.var_ldist_case,
        app.form.var_r1_pair_suffix,
        app.form.var_r1_loop_all_pairs,
    ):
        var.trace_add("write", lambda *_: app.preview.update_filename_preview())
    app.form.var_loop_ff_only.trace_add(
        "write", lambda *_: app.preview.apply_naming_mode_ui()
    )
    app.form.var_loop_mdist_only.trace_add(
        "write", lambda *_: app.preview.apply_naming_mode_ui()
    )
    app.form.var_loop_ldist_only.trace_add(
        "write", lambda *_: app.preview.apply_naming_mode_ui()
    )
    app.form.var_mdist_value.trace_add(
        "write", lambda *_: (app.preview.refresh_mdist_pairs(), app.preview.update_filename_preview())
    )
    app.mainloop()

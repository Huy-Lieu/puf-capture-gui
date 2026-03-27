from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from ui.services.config_mapper import parse_realterm_config
from ui.services.port_service import detect_com_ports
from ui.services.capture_worker import CaptureWorker
from ui.views.capture_form import CaptureForm
from ui.views.control_panel import ControlPanelWidgets
from ui.views.status_log import StatusLog


class EventController:
    def __init__(
        self,
        *,
        form: CaptureForm,
        controls: ControlPanelWidgets,
        log: StatusLog,
        worker: CaptureWorker,
    ) -> None:
        self._form = form
        self._controls = controls
        self._log = log
        self._worker = worker
        self._com_label_to_port: dict[str, str] = {}

    @property
    def com_label_to_port(self) -> dict[str, str]:
        return self._com_label_to_port

    def append_status(self, msg: str) -> None:
        self._log.append(msg)

    def set_running(self, running: bool) -> None:
        self._controls.btn_start.configure(state=tk.DISABLED if running else tk.NORMAL)
        self._controls.btn_stop.configure(state=tk.NORMAL if running else tk.DISABLED)
        self._controls.btn_capture.configure(state=tk.NORMAL if running else tk.DISABLED)
        self._controls.lbl_state.configure(text="Running" if running else "Idle")

    def browse_dir(self) -> None:
        path = filedialog.askdirectory(title="Select save directory")
        if path:
            self._form.var_save_dir.set(path)

    def refresh_com_ports(self) -> None:
        ports, mapping = detect_com_ports()
        self._com_label_to_port = mapping
        self._form.cmb_com_port["values"] = ports

        current = self._form.var_com_port.get().strip().upper()
        if current.startswith("COM") and current not in ports:
            ports = ports + [current]
            self._form.cmb_com_port["values"] = ports

        if ports and not self._form.var_com_port.get().strip():
            self._form.var_com_port.set(ports[0])

    def read_config(self):
        return parse_realterm_config(
            base_name=self._form.var_base_name.get(),
            naming_mode=self._form.var_file_naming_mode.get(),
            fpga_index_raw=self._form.var_fpga_index.get(),
            end_fpga_index_raw=self._form.var_end_fpga_index.get(),
            start_index_raw=self._form.var_start_index.get(),
            end_index_raw=self._form.var_end_index.get(),
            com_port_raw=self._form.var_com_port.get(),
            com_label_to_port=self._com_label_to_port,
            baud_raw=self._form.var_baud.get(),
            save_dir=self._form.var_save_dir.get(),
            auto_delay_raw=self._form.var_auto_delay.get(),
            flipflop_position=self._form.var_flipflop_position.get(),
            mdist_value_raw=self._form.var_mdist_value.get(),
            mux_pair_raw=self._form.var_mux_pair.get(),
            ff_loop_fixed_mux=self._form.var_loop_ff_only.get(),
            mdist_loop_fixed_mux=self._form.var_loop_mdist_only.get(),
            ldist_case_raw=self._form.var_ldist_case.get(),
            ldist_loop=self._form.var_loop_ldist_only.get(),
        )

    def connect(self) -> None:
        if self._worker.is_running():
            return
        try:
            cfg = self.read_config()
        except Exception as exc:
            messagebox.showerror("Invalid configuration", str(exc))
            return
        self.set_running(True)
        self.append_status("Connecting to RealTerm...")
        self._worker.start(cfg)

    def disconnect(self) -> None:
        disconnected = self._worker.stop()
        if disconnected:
            self.append_status("Disconnected RealTerm serial port.")
        else:
            self.append_status("No active RealTerm connection found to disconnect.")

    def capture_now(self) -> None:
        if not self._worker.is_running():
            self.append_status("Capture ignored: not connected.")
            return
        self._worker.trigger_capture()
        self.append_status("Capture trigger sent.")

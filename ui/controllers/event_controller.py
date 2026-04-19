from __future__ import annotations

from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from ui.services.config_mapper import parse_realterm_config
from ui.services.port_service import detect_com_ports
from ui.services.vivado_runner import VivadoRunConfig, start_vivado_batch
from ui.services.capture_worker import CaptureWorker
from ui.views.capture_form import CaptureForm
from ui.views.control_panel import ControlPanelWidgets
from ui.views.status_log import StatusLog
from ui.views.vivado_config import VivadoPanelWidgets


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
        self._vivado_proc = None
        self._vivado_thread: threading.Thread | None = None
        self._vivado_panel: VivadoPanelWidgets | None = None

    def bind_vivado_panel(self, panel: VivadoPanelWidgets) -> None:
        self._vivado_panel = panel

    @property
    def com_label_to_port(self) -> dict[str, str]:
        return self._com_label_to_port

    def append_status(self, msg: str) -> None:
        self._log.append(msg)

    def _append_status_threadsafe(self, msg: str) -> None:
        self._log.text.after(0, lambda: self.append_status(msg))

    def _set_vivado_running(self, running: bool) -> None:
        if self._vivado_panel is None:
            return
        state = tk.DISABLED if running else tk.NORMAL
        self._vivado_panel.btn_generate_bitstream.configure(state=state)
        self._vivado_panel.btn_program_device.configure(state=state)

    def _stream_vivado_output(self, process, tcl: Path, action_label: str) -> None:
        tag = f"[Vivado:{action_label}]"
        if process.stdout is not None:
            for line in process.stdout:
                text = line.rstrip()
                if text:
                    self._append_status_threadsafe(f"{tag} {text}")
        exit_code = process.wait()
        self._vivado_proc = None
        self._vivado_thread = None
        self._log.text.after(0, lambda: self._set_vivado_running(False))
        self._append_status_threadsafe(f"{tag} finished for {tcl.name} (exit code {exit_code}).")

    def set_running(self, running: bool) -> None:
        self._controls.btn_start.configure(state=tk.DISABLED if running else tk.NORMAL)
        self._controls.btn_stop.configure(state=tk.NORMAL if running else tk.DISABLED)
        self._controls.btn_capture.configure(state=tk.NORMAL if running else tk.DISABLED)
        self._controls.lbl_state.configure(text="Running" if running else "Idle")

    def browse_dir(self) -> None:
        path = filedialog.askdirectory(title="Select save directory")
        if path:
            self._form.var_save_dir.set(path)

    def browse_vivado_bat(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Vivado batch file",
            filetypes=(("Batch files", "*.bat"), ("All files", "*.*")),
        )
        if path:
            self._form.var_vivado_bat_path.set(path)

    def browse_vivado_project(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Vivado project file",
            filetypes=(("Vivado projects", "*.xpr"), ("All files", "*.*")),
        )
        if path:
            self._form.var_vivado_project_path.set(path)

    def _browse_vivado_tcl(self, target: tk.StringVar) -> None:
        path = filedialog.askopenfilename(
            title="Select TCL script file",
            filetypes=(("TCL files", "*.tcl"), ("All files", "*.*")),
        )
        if path:
            target.set(path)

    def browse_vivado_tcl_bitstream(self) -> None:
        self._browse_vivado_tcl(self._form.var_vivado_tcl_bitstream)

    def browse_vivado_tcl_program(self) -> None:
        self._browse_vivado_tcl(self._form.var_vivado_tcl_program)

    def browse_vivado_bitstream_program(self) -> None:
        path = filedialog.askopenfilename(
            title="Select bitstream file",
            filetypes=(("Bitstream files", "*.bit"), ("All files", "*.*")),
        )
        if path:
            self._form.var_vivado_bitstream_program.set(path)

    def run_vivado_generate_bitstream(self) -> None:
        name = self._form.var_vivado_bitstream_generate_name.get().strip()
        extra = (name,) if name else ()
        self._run_vivado_for_tcl(
            self._form.var_vivado_tcl_bitstream.get().strip(),
            "GenerateBitstream",
            extra_tclargs=extra,
        )

    def run_vivado_program_device(self) -> None:
        bit_raw = self._form.var_vivado_bitstream_program.get().strip()
        if not bit_raw:
            messagebox.showerror(
                "Missing bitstream path",
                "Please set the bitstream file (.bit) for programming.",
            )
            return
        bit = Path(bit_raw)
        if bit.suffix.lower() != ".bit":
            messagebox.showerror(
                "Invalid bitstream file", "Bitstream path must point to a .bit file."
            )
            return
        if not bit.is_file():
            messagebox.showerror("Missing file", f"Bitstream file not found:\n{bit}")
            return
        self._run_vivado_for_tcl(
            self._form.var_vivado_tcl_program.get().strip(),
            "ProgrammingDevice",
            extra_tclargs=(str(bit),),
        )

    def _run_vivado_for_tcl(
        self,
        tcl_path: str,
        action_label: str,
        *,
        extra_tclargs: tuple[str, ...] = (),
    ) -> None:
        if self._vivado_proc is not None and self._vivado_proc.poll() is None:
            self.append_status("Vivado run already in progress.")
            return

        vivado_bat = self._form.var_vivado_bat_path.get().strip()
        project_path = self._form.var_vivado_project_path.get().strip()

        if not vivado_bat or not project_path or not tcl_path:
            messagebox.showerror(
                "Missing Vivado paths",
                "Please set Vivado bat path, project (.xpr), and the TCL script path for this action.",
            )
            return

        bat = Path(vivado_bat)
        project = Path(project_path)
        tcl = Path(tcl_path)
        if bat.suffix.lower() != ".bat":
            messagebox.showerror("Invalid Vivado path", "Vivado path must point to a .bat file.")
            return
        if project.suffix.lower() != ".xpr":
            messagebox.showerror(
                "Invalid project file", "Vivado project path must point to a .xpr file."
            )
            return
        if tcl.suffix.lower() != ".tcl":
            messagebox.showerror("Invalid TCL file", "TCL path must point to a .tcl file.")
            return
        if not bat.is_file():
            messagebox.showerror("Missing file", f"Vivado batch file not found:\n{bat}")
            return
        if not project.is_file():
            messagebox.showerror("Missing file", f"Vivado project file not found:\n{project}")
            return
        if not tcl.is_file():
            messagebox.showerror("Missing file", f"TCL file not found:\n{tcl}")
            return

        try:
            process = start_vivado_batch(
                VivadoRunConfig(
                    vivado_bat_path=str(bat),
                    project_path=str(project),
                    tcl_path=str(tcl),
                    extra_tclargs=extra_tclargs,
                )
            )
        except OSError as exc:
            messagebox.showerror("Vivado launch failed", str(exc))
            return

        self._vivado_proc = process
        self._set_vivado_running(True)
        self.append_status(f"[Vivado:{action_label}] Starting: {tcl}")
        self._vivado_thread = threading.Thread(
            target=self._stream_vivado_output,
            args=(process, tcl, action_label),
            daemon=True,
        )
        self._vivado_thread.start()

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
            r1_pair_suffix_raw=self._form.var_r1_pair_suffix.get(),
            r1_loop_all_pairs=self._form.var_r1_loop_all_pairs.get(),
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

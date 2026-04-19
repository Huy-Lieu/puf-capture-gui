from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from ui.controllers.event_controller import EventController
from ui.views.vivado_config import VivadoPanelWidgets


class DummyVar:
    def __init__(self, value: str = "") -> None:
        self._value = value

    def get(self) -> str:
        return self._value

    def set(self, value: str) -> None:
        self._value = value


class DummyLog:
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.text = SimpleNamespace(after=lambda _delay, cb: cb())

    def append(self, msg: str) -> None:
        self.messages.append(msg)


class DummyWorker:
    def __init__(self, running: bool = False) -> None:
        self.running = running
        self.capture_triggers = 0

    def is_running(self) -> bool:
        return self.running

    def start(self, _cfg) -> bool:
        self.running = True
        return True

    def stop(self) -> bool:
        self.running = False
        return True

    def enqueue_capture(self, _cfg) -> None:
        self.capture_triggers += 1


class DummyButton:
    def __init__(self) -> None:
        self.state = "normal"

    def configure(self, **kwargs) -> None:
        if "state" in kwargs:
            self.state = kwargs["state"]


class FakeProcess:
    def __init__(self, lines: list[str], exit_code: int = 0) -> None:
        self.stdout = lines
        self._exit_code = exit_code
        self._running = True

    def poll(self):
        return None if self._running else self._exit_code

    def wait(self) -> int:
        self._running = False
        return self._exit_code


class ImmediateThread:
    def __init__(self, *, target, args, daemon) -> None:
        self._target = target
        self._args = args

    def start(self) -> None:
        self._target(*self._args)


class EventControllerVivadoTests(unittest.TestCase):
    def _make_controller(
        self, *, worker: DummyWorker | None = None
    ) -> tuple[EventController, SimpleNamespace, DummyLog, VivadoPanelWidgets]:
        form = SimpleNamespace(
            var_vivado_bat_path=DummyVar(""),
            var_vivado_project_path=DummyVar(""),
            var_vivado_tcl_bitstream=DummyVar(""),
            var_vivado_bitstream_generate_name=DummyVar(""),
            var_vivado_bitstream_program=DummyVar(""),
            var_vivado_tcl_program=DummyVar(""),
            var_auto_delay=DummyVar("0"),
            var_base_name=DummyVar("BASE"),
            var_file_naming_mode=DummyVar("scheme1"),
            var_fpga_index=DummyVar("7"),
            var_end_fpga_index=DummyVar("7"),
            var_start_index=DummyVar("1"),
            var_end_index=DummyVar("1"),
            var_com_port=DummyVar("COM3"),
            var_baud=DummyVar("115200"),
            var_save_dir=DummyVar("."),
            var_flipflop_position=DummyVar("DFF"),
            var_mdist_value=DummyVar("8"),
            var_mux_pair=DummyVar("M0-M7"),
            var_loop_ff_only=DummyVar(False),
            var_loop_mdist_only=DummyVar(False),
            var_ldist_case=DummyVar("DLUTA + ALUTB, LDIST6"),
            var_loop_ldist_only=DummyVar(False),
            var_r1_pair_suffix=DummyVar("1111_AAAA"),
            var_r1_loop_all_pairs=DummyVar(False),
        )
        controls = SimpleNamespace(
            btn_start=DummyButton(),
            btn_stop=DummyButton(),
            btn_capture=DummyButton(),
            lbl_state=SimpleNamespace(configure=lambda **_: None),
        )
        log = DummyLog()
        active_worker = worker if worker is not None else DummyWorker()
        controller = EventController(form=form, controls=controls, log=log, worker=active_worker)
        vivado = VivadoPanelWidgets(
            btn_generate_bitstream=DummyButton(),
            btn_program_device=DummyButton(),
        )
        controller.bind_vivado_panel(vivado)
        return controller, form, log, vivado

    def test_browse_vivado_project_sets_selected_path(self) -> None:
        controller, form, _, _ = self._make_controller()
        with patch(
            "ui.controllers.event_controller.filedialog.askopenfilename",
            return_value=r"D:\proj\example.xpr",
        ):
            controller.browse_vivado_project()
        self.assertEqual(form.var_vivado_project_path.get(), r"D:\proj\example.xpr")

    def test_run_vivado_generate_bitstream_requires_all_paths(self) -> None:
        controller, _, _, _ = self._make_controller()
        with patch("ui.controllers.event_controller.messagebox.showerror") as showerror:
            controller.run_vivado_generate_bitstream()
        showerror.assert_called_once()

    def test_run_vivado_generate_bitstream_invokes_runner_and_logs_status(self) -> None:
        controller, form, log, vivado = self._make_controller()
        with TemporaryDirectory() as tmp:
            bat = Path(tmp) / "vivado.bat"
            xpr = Path(tmp) / "design.xpr"
            tcl = Path(tmp) / "run.tcl"
            bat.write_text("echo test\n", encoding="utf-8")
            xpr.write_text("dummy\n", encoding="utf-8")
            tcl.write_text("exit\n", encoding="utf-8")
            form.var_vivado_bat_path.set(str(bat))
            form.var_vivado_project_path.set(str(xpr))
            form.var_vivado_tcl_bitstream.set(str(tcl))

            fake_process = FakeProcess(["line1\n", "line2\n"], exit_code=0)
            with patch(
                "ui.controllers.event_controller.start_vivado_batch", return_value=fake_process
            ) as starter, patch(
                "ui.controllers.event_controller.threading.Thread", ImmediateThread
            ), patch("ui.controllers.event_controller.messagebox.showerror") as showerror:
                controller.run_vivado_generate_bitstream()

            showerror.assert_not_called()
            starter.assert_called_once()
            self.assertTrue(
                any("[Vivado:GenerateBitstream] Starting" in m for m in log.messages)
            )
            self.assertTrue(any("[Vivado:GenerateBitstream] line1" in m for m in log.messages))
            self.assertTrue(any("exit code 0" in m for m in log.messages))
            self.assertEqual(vivado.btn_generate_bitstream.state, "normal")
            self.assertEqual(vivado.btn_program_device.state, "normal")
            cfg = starter.call_args[0][0]
            self.assertEqual(cfg.extra_tclargs, ())

    def test_run_vivado_generate_bitstream_passes_name_as_second_tclarg(self) -> None:
        controller, form, log, vivado = self._make_controller()
        with TemporaryDirectory() as tmp:
            bat = Path(tmp) / "vivado.bat"
            xpr = Path(tmp) / "design.xpr"
            tcl = Path(tmp) / "run.tcl"
            bat.write_text("echo test\n", encoding="utf-8")
            xpr.write_text("dummy\n", encoding="utf-8")
            tcl.write_text("exit\n", encoding="utf-8")
            form.var_vivado_bat_path.set(str(bat))
            form.var_vivado_project_path.set(str(xpr))
            form.var_vivado_tcl_bitstream.set(str(tcl))
            form.var_vivado_bitstream_generate_name.set("my_bitstem")

            fake_process = FakeProcess([], exit_code=0)
            with patch(
                "ui.controllers.event_controller.start_vivado_batch", return_value=fake_process
            ) as starter, patch(
                "ui.controllers.event_controller.threading.Thread", ImmediateThread
            ), patch("ui.controllers.event_controller.messagebox.showerror") as showerror:
                controller.run_vivado_generate_bitstream()

            showerror.assert_not_called()
            starter.assert_called_once()
            cfg = starter.call_args[0][0]
            self.assertEqual(cfg.extra_tclargs, ("my_bitstem",))
            self.assertEqual(vivado.btn_generate_bitstream.state, "normal")

    def test_run_vivado_program_device_passes_bit_as_second_tclarg(self) -> None:
        controller, form, log, _ = self._make_controller()
        with TemporaryDirectory() as tmp:
            bat = Path(tmp) / "vivado.bat"
            xpr = Path(tmp) / "design.xpr"
            tcl = Path(tmp) / "program.tcl"
            bit = Path(tmp) / "design.bit"
            bat.write_text("@echo\n", encoding="utf-8")
            xpr.write_text("dummy\n", encoding="utf-8")
            tcl.write_text("exit\n", encoding="utf-8")
            bit.write_bytes(b"\x00")
            form.var_vivado_bat_path.set(str(bat))
            form.var_vivado_project_path.set(str(xpr))
            form.var_vivado_tcl_program.set(str(tcl))
            form.var_vivado_bitstream_program.set(str(bit))

            fake_process = FakeProcess([], exit_code=0)
            with patch(
                "ui.controllers.event_controller.start_vivado_batch", return_value=fake_process
            ) as starter, patch(
                "ui.controllers.event_controller.threading.Thread", ImmediateThread
            ), patch("ui.controllers.event_controller.messagebox.showerror") as showerror:
                controller.run_vivado_program_device()

            showerror.assert_not_called()
            starter.assert_called_once()
            cfg = starter.call_args[0][0]
            self.assertEqual(cfg.extra_tclargs, (str(bit),))
            self.assertTrue(any("[Vivado:ProgrammingDevice]" in m for m in log.messages))

    def test_program_device_schedules_one_auto_capture_after_delay(self) -> None:
        worker = DummyWorker(running=True)
        controller, form, log, _ = self._make_controller(worker=worker)
        with TemporaryDirectory() as tmp:
            bat = Path(tmp) / "vivado.bat"
            xpr = Path(tmp) / "design.xpr"
            tcl = Path(tmp) / "program.tcl"
            bit = Path(tmp) / "design.bit"
            bat.write_text("@echo\n", encoding="utf-8")
            xpr.write_text("dummy\n", encoding="utf-8")
            tcl.write_text("exit\n", encoding="utf-8")
            bit.write_bytes(b"\x00")
            form.var_vivado_bat_path.set(str(bat))
            form.var_vivado_project_path.set(str(xpr))
            form.var_vivado_tcl_program.set(str(tcl))
            form.var_vivado_bitstream_program.set(str(bit))
            form.var_auto_delay.set("1.5")

            fake_process = FakeProcess([], exit_code=0)
            with patch(
                "ui.controllers.event_controller.start_vivado_batch", return_value=fake_process
            ), patch("ui.controllers.event_controller.threading.Thread", ImmediateThread):
                controller.run_vivado_program_device()

            self.assertEqual(worker.capture_triggers, 1)
            self.assertTrue(any("Auto-capture scheduled in 1.5s" in m for m in log.messages))

    def test_program_device_does_not_auto_capture_on_failure(self) -> None:
        worker = DummyWorker(running=True)
        controller, form, log, _ = self._make_controller(worker=worker)
        with TemporaryDirectory() as tmp:
            bat = Path(tmp) / "vivado.bat"
            xpr = Path(tmp) / "design.xpr"
            tcl = Path(tmp) / "program.tcl"
            bit = Path(tmp) / "design.bit"
            bat.write_text("@echo\n", encoding="utf-8")
            xpr.write_text("dummy\n", encoding="utf-8")
            tcl.write_text("exit\n", encoding="utf-8")
            bit.write_bytes(b"\x00")
            form.var_vivado_bat_path.set(str(bat))
            form.var_vivado_project_path.set(str(xpr))
            form.var_vivado_tcl_program.set(str(tcl))
            form.var_vivado_bitstream_program.set(str(bit))

            fake_process = FakeProcess([], exit_code=2)
            with patch(
                "ui.controllers.event_controller.start_vivado_batch", return_value=fake_process
            ), patch("ui.controllers.event_controller.threading.Thread", ImmediateThread):
                controller.run_vivado_program_device()

            self.assertEqual(worker.capture_triggers, 0)
            self.assertTrue(any("Auto-capture skipped: programming failed" in m for m in log.messages))

    def test_program_device_does_not_auto_capture_when_not_connected(self) -> None:
        worker = DummyWorker(running=False)
        controller, form, log, _ = self._make_controller(worker=worker)
        with TemporaryDirectory() as tmp:
            bat = Path(tmp) / "vivado.bat"
            xpr = Path(tmp) / "design.xpr"
            tcl = Path(tmp) / "program.tcl"
            bit = Path(tmp) / "design.bit"
            bat.write_text("@echo\n", encoding="utf-8")
            xpr.write_text("dummy\n", encoding="utf-8")
            tcl.write_text("exit\n", encoding="utf-8")
            bit.write_bytes(b"\x00")
            form.var_vivado_bat_path.set(str(bat))
            form.var_vivado_project_path.set(str(xpr))
            form.var_vivado_tcl_program.set(str(tcl))
            form.var_vivado_bitstream_program.set(str(bit))

            fake_process = FakeProcess([], exit_code=0)
            with patch(
                "ui.controllers.event_controller.start_vivado_batch", return_value=fake_process
            ), patch("ui.controllers.event_controller.threading.Thread", ImmediateThread):
                controller.run_vivado_program_device()

            self.assertEqual(worker.capture_triggers, 0)
            self.assertTrue(any("Auto-capture skipped: connect to RealTerm first." in m for m in log.messages))

    def test_program_device_does_not_auto_capture_with_invalid_delay(self) -> None:
        worker = DummyWorker(running=True)
        controller, form, log, _ = self._make_controller(worker=worker)
        with TemporaryDirectory() as tmp:
            bat = Path(tmp) / "vivado.bat"
            xpr = Path(tmp) / "design.xpr"
            tcl = Path(tmp) / "program.tcl"
            bit = Path(tmp) / "design.bit"
            bat.write_text("@echo\n", encoding="utf-8")
            xpr.write_text("dummy\n", encoding="utf-8")
            tcl.write_text("exit\n", encoding="utf-8")
            bit.write_bytes(b"\x00")
            form.var_vivado_bat_path.set(str(bat))
            form.var_vivado_project_path.set(str(xpr))
            form.var_vivado_tcl_program.set(str(tcl))
            form.var_vivado_bitstream_program.set(str(bit))
            form.var_auto_delay.set("abc")

            fake_process = FakeProcess([], exit_code=0)
            with patch(
                "ui.controllers.event_controller.start_vivado_batch", return_value=fake_process
            ), patch("ui.controllers.event_controller.threading.Thread", ImmediateThread):
                controller.run_vivado_program_device()

            self.assertEqual(worker.capture_triggers, 0)
            self.assertTrue(any("Auto-capture skipped: invalid Auto delay value." in m for m in log.messages))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from ui.controllers.event_controller import EventController


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

    def append(self, msg: str) -> None:
        self.messages.append(msg)


class DummyWorker:
    def is_running(self) -> bool:
        return False


class EventControllerVivadoTests(unittest.TestCase):
    def _make_controller(self) -> tuple[EventController, SimpleNamespace, DummyLog]:
        form = SimpleNamespace(
            var_vivado_bat_path=DummyVar(""),
            var_vivado_project_path=DummyVar(""),
            var_vivado_tcl_path=DummyVar(""),
        )
        controls = SimpleNamespace(
            btn_start=SimpleNamespace(configure=lambda **_: None),
            btn_stop=SimpleNamespace(configure=lambda **_: None),
            btn_capture=SimpleNamespace(configure=lambda **_: None),
            lbl_state=SimpleNamespace(configure=lambda **_: None),
        )
        log = DummyLog()
        controller = EventController(form=form, controls=controls, log=log, worker=DummyWorker())
        return controller, form, log

    def test_browse_vivado_project_sets_selected_path(self) -> None:
        controller, form, _ = self._make_controller()
        with patch(
            "ui.controllers.event_controller.filedialog.askopenfilename",
            return_value=r"D:\proj\example.xpr",
        ):
            controller.browse_vivado_project()
        self.assertEqual(form.var_vivado_project_path.get(), r"D:\proj\example.xpr")

    def test_run_vivado_tcl_requires_all_paths(self) -> None:
        controller, _, _ = self._make_controller()
        with patch("ui.controllers.event_controller.messagebox.showerror") as showerror:
            controller.run_vivado_tcl()
        showerror.assert_called_once()

    def test_run_vivado_tcl_invokes_runner_and_logs_status(self) -> None:
        controller, form, log = self._make_controller()
        with TemporaryDirectory() as tmp:
            bat = Path(tmp) / "vivado.bat"
            xpr = Path(tmp) / "design.xpr"
            tcl = Path(tmp) / "run.tcl"
            bat.write_text("echo test\n", encoding="utf-8")
            xpr.write_text("dummy\n", encoding="utf-8")
            tcl.write_text("exit\n", encoding="utf-8")
            form.var_vivado_bat_path.set(str(bat))
            form.var_vivado_project_path.set(str(xpr))
            form.var_vivado_tcl_path.set(str(tcl))

            with patch("ui.controllers.event_controller.start_vivado_batch") as starter, patch(
                "ui.controllers.event_controller.messagebox.showerror"
            ) as showerror:
                controller.run_vivado_tcl()

            showerror.assert_not_called()
            starter.assert_called_once()
            self.assertTrue(any("Vivado started with TCL" in m for m in log.messages))


if __name__ == "__main__":
    unittest.main()

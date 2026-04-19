from __future__ import annotations

import queue
import threading
import time
import unittest
from dataclasses import replace
from unittest.mock import patch

from CaptureRunner import run_capture, run_live_capture_session
from RealTermTypes import RealTermConfig


class FakeRt:
    def __init__(self) -> None:
        self.Visible = False
        self.Caption = ""
        self.DisplayAs = 0
        self.Port = 0
        self.Baud = 0
        self.PortOpen = 0
        self.CaptureFile = ""
        self.Capture = 0

    def ClearTerminal(self) -> None:
        return None

    def Open(self) -> None:
        self.PortOpen = 1


class FakeClient:
    def __init__(self, rt: object) -> None:
        self.rt = rt
        self._ticks = 0

    def setup_window(self, cfg: RealTermConfig) -> None:
        return None

    def configure_serial_and_open(self, cfg: RealTermConfig, status) -> None:
        status(f"Configured serial: COM{cfg.com_port}, {cfg.baud} baud")
        status("Serial port opened.")

    def clear_terminal(self) -> None:
        return None

    def start_capture(self, full_path: str) -> None:
        self._ticks = 0

    def is_capturing(self) -> bool:
        self._ticks += 1
        return self._ticks < 2

    def stop_capture(self) -> None:
        return None


class CaptureRunnerTests(unittest.TestCase):
    def test_run_capture_emits_expected_status_messages(self) -> None:
        cfg = RealTermConfig(
            base_name="FPGA7_BASE",
            start_index=1,
            end_index=1,
            file_naming_mode="scheme3",
            fpga_index=7,
            end_fpga_index=7,
            flipflop_position="DFF",
            mdist_value=8,
            mux_a=0,
            mux_b=7,
            ldist_case_id=1,
            ldist_lut_a="DLUTA",
            ldist_lut_b="ALUTB",
            ldist_distance=6,
            com_port=3,
            baud=115200,
            save_dir=".",
            auto_delay_s=0,
            poll_interval_s=0.001,
        )
        messages: list[str] = []
        with patch("CaptureRunner.pythoncom.CoInitialize"), patch(
            "CaptureRunner.pythoncom.CoUninitialize"
        ), patch("CaptureRunner.RealTermClient", FakeClient), patch(
            "CaptureRunner.connect_realterm", return_value=FakeRt()
        ):
            run_capture(
                cfg,
                wait_for_manual_trigger=lambda: True,
                on_status=messages.append,
            )

        self.assertTrue(any("Configured serial: COM3, 115200 baud" in m for m in messages))
        self.assertTrue(any("Capture STARTED" in m for m in messages))
        self.assertTrue(any("Capture FINISHED" in m for m in messages))


class LiveCaptureSessionTests(unittest.TestCase):
    def test_live_session_uses_each_queued_config(self) -> None:
        base = RealTermConfig(
            base_name="",
            start_index=1,
            end_index=1,
            file_naming_mode="scheme3",
            fpga_index=1,
            end_fpga_index=1,
            flipflop_position="DFF",
            mdist_value=8,
            mux_a=0,
            mux_b=7,
            ldist_case_id=1,
            ldist_lut_a="DLUTA",
            ldist_lut_b="ALUTB",
            ldist_distance=6,
            com_port=3,
            baud=115200,
            save_dir=".",
            auto_delay_s=0.0,
            poll_interval_s=0.001,
        )
        cap1 = replace(base, fpga_index=1, end_fpga_index=1, start_index=1)
        cap2 = replace(base, fpga_index=9, end_fpga_index=9, start_index=2, end_index=2)
        q: queue.Queue[RealTermConfig] = queue.Queue()
        q.put(cap1)
        q.put(cap2)
        used: list[tuple[int, int]] = []

        def record_exec(client, cfg, capture_index, stop, status):
            used.append((cfg.fpga_index, capture_index))
            return True

        stop_ev = threading.Event()

        def should_stop() -> bool:
            return stop_ev.is_set()

        def runner() -> None:
            with patch("CaptureRunner.pythoncom.CoInitialize"), patch(
                "CaptureRunner.pythoncom.CoUninitialize"
            ), patch("CaptureRunner.RealTermClient", FakeClient), patch(
                "CaptureRunner.connect_realterm", return_value=FakeRt()
            ), patch("CaptureRunner._execute_one_capture", side_effect=record_exec):
                run_live_capture_session(
                    base,
                    q,
                    should_stop=should_stop,
                    on_status=lambda _m: None,
                )

        t = threading.Thread(target=runner, daemon=True)
        t.start()
        deadline = time.time() + 2.0
        while len(used) < 2 and time.time() < deadline:
            time.sleep(0.02)
        self.assertEqual(used, [(1, 1), (9, 2)])
        stop_ev.set()
        t.join(timeout=2.0)
        self.assertFalse(t.is_alive(), "live session thread should exit after stop")


if __name__ == "__main__":
    unittest.main()

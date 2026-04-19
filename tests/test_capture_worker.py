from __future__ import annotations

import queue
import unittest
from dataclasses import replace
from unittest.mock import patch

from RealTermTypes import RealTermConfig
from ui.services.capture_worker import CaptureWorker


def _dummy_cfg(**kwargs: object) -> RealTermConfig:
    cfg = RealTermConfig(
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
    if kwargs:
        cfg = replace(cfg, **kwargs)  # type: ignore[arg-type]
    return cfg


class CaptureWorkerTests(unittest.TestCase):
    def test_session_completion_does_not_disconnect_realterm(self) -> None:
        messages: queue.Queue[str] = queue.Queue()
        done_called: list[bool] = []
        worker = CaptureWorker(messages, on_done=lambda: done_called.append(True))

        cfg = _dummy_cfg()
        with patch("ui.services.capture_worker.run_live_capture_session", return_value=None), patch(
            "ui.services.capture_worker.disconnect_realterm", return_value=True
        ) as disconnect_mock:
            started = worker.start(cfg)
            self.assertTrue(started)
            assert worker.state.worker is not None
            worker.state.worker.join(timeout=1.0)

        self.assertFalse(worker.is_running())
        self.assertEqual(done_called, [True])
        self.assertEqual(messages.get_nowait(), "Done.")
        disconnect_mock.assert_not_called()

    def test_worker_invokes_live_session_runner(self) -> None:
        messages: queue.Queue[str] = queue.Queue()
        worker = CaptureWorker(messages, on_done=lambda: None)
        cfg = _dummy_cfg()

        with patch(
            "ui.services.capture_worker.run_live_capture_session", return_value=None
        ) as live_mock:
            started = worker.start(cfg)
            self.assertTrue(started)
            assert worker.state.worker is not None
            worker.state.worker.join(timeout=1.0)

        live_mock.assert_called_once()
        args, kwargs = live_mock.call_args
        self.assertIs(args[0], cfg)
        self.assertIs(args[1], worker.state.capture_cfg_queue)
        self.assertTrue(callable(kwargs["should_stop"]))
        self.assertEqual(kwargs["on_status"], messages.put)

    def test_stop_disconnects_realterm(self) -> None:
        messages: queue.Queue[str] = queue.Queue()
        worker = CaptureWorker(messages, on_done=lambda: None)

        with patch("ui.services.capture_worker.disconnect_realterm", return_value=True) as disconnect_mock:
            disconnected = worker.stop()

        self.assertTrue(disconnected)
        disconnect_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()

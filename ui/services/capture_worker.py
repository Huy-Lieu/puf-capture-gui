from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field
from typing import Callable, Optional

from CaptureRunner import run_capture
from RealTermClient import disconnect_realterm
from RealTermTypes import RealTermConfig


@dataclass
class WorkerState:
    worker: Optional[threading.Thread] = None
    stop_event: threading.Event = field(default_factory=threading.Event)
    capture_event: threading.Event = field(default_factory=threading.Event)


class CaptureWorker:
    def __init__(self, message_queue: queue.Queue[str], on_done: Callable[[], None]) -> None:
        self.state = WorkerState()
        self._queue = message_queue
        self._on_done = on_done

    def is_running(self) -> bool:
        return self.state.worker is not None and self.state.worker.is_alive()

    def wait_for_capture_trigger(self) -> bool:
        while not self.state.stop_event.is_set():
            if self.state.capture_event.wait(timeout=0.1):
                self.state.capture_event.clear()
                return True
        return False

    def start(self, cfg: RealTermConfig) -> bool:
        if self.is_running():
            return False

        self.state.stop_event.clear()
        self.state.capture_event.clear()

        def worker() -> None:
            try:
                run_capture(
                    cfg,
                    should_stop=self.state.stop_event.is_set,
                    wait_for_manual_trigger=self.wait_for_capture_trigger,
                    on_status=self._queue.put,
                )
                self._queue.put("Done.")
            except Exception as exc:
                self._queue.put(f"ERROR: {exc}")
            finally:
                self._on_done()

        self.state.worker = threading.Thread(target=worker, daemon=True)
        self.state.worker.start()
        return True

    def trigger_capture(self) -> None:
        self.state.capture_event.set()

    def stop(self) -> bool:
        self.state.stop_event.set()
        self.state.capture_event.set()
        return disconnect_realterm()

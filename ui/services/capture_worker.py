from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field
from typing import Callable, Optional

from CaptureRunner import run_live_capture_session
from RealTermClient import disconnect_realterm
from RealTermTypes import RealTermConfig


@dataclass
class WorkerState:
    worker: Optional[threading.Thread] = None
    stop_event: threading.Event = field(default_factory=threading.Event)
    capture_cfg_queue: "queue.Queue[RealTermConfig]" = field(default_factory=queue.Queue)


class CaptureWorker:
    def __init__(self, message_queue: queue.Queue[str], on_done: Callable[[], None]) -> None:
        self.state = WorkerState()
        self._queue = message_queue
        self._on_done = on_done

    def is_running(self) -> bool:
        return self.state.worker is not None and self.state.worker.is_alive()

    def start(self, session_cfg: RealTermConfig) -> bool:
        if self.is_running():
            return False

        self.state.stop_event.clear()
        while True:
            try:
                self.state.capture_cfg_queue.get_nowait()
            except queue.Empty:
                break

        def worker() -> None:
            try:
                run_live_capture_session(
                    session_cfg,
                    self.state.capture_cfg_queue,
                    should_stop=self.state.stop_event.is_set,
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

    def enqueue_capture(self, cfg: RealTermConfig) -> None:
        self.state.capture_cfg_queue.put(cfg)

    def stop(self) -> bool:
        self.state.stop_event.set()
        return disconnect_realterm()

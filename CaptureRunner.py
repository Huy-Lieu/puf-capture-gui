from __future__ import annotations

import os
import queue
import time
from typing import Callable, Iterator, Optional

import pythoncom

from capture_planners import iter_ff_mux_jobs, iter_r1_init_jobs, iter_reliability_jobs
from RealTermClient import RealTermClient, connect_realterm
from RealTermNaming import build_capture_filename
from RealTermTypes import RealTermConfig
from RealTermValidation import validate_config

def _wait_for_trigger(
    wait_for_manual_trigger: Optional[Callable[[], bool]], status: Callable[[str], None]
) -> bool:
    if wait_for_manual_trigger is not None:
        status("Waiting for Capture button...")
        return wait_for_manual_trigger()
    input("Press [Enter] to trigger capture...")
    return True


def _wait_auto_delay(
    auto_delay_s: float, stop: Callable[[], bool], status: Callable[[str], None]
) -> bool:
    if not auto_delay_s:
        return True
    status(f"Waiting {auto_delay_s} seconds...")
    end_wait = time.time() + auto_delay_s
    while time.time() < end_wait:
        if stop():
            status("Stopped.")
            return False
        time.sleep(min(0.1, end_wait - time.time()))
    return True


def _execute_one_capture(
    client: RealTermClient,
    cfg: RealTermConfig,
    capture_index: int,
    stop: Callable[[], bool],
    status: Callable[[str], None],
) -> bool:
    file_name = build_capture_filename(cfg, capture_index)
    full_path = os.path.join(cfg.save_dir, file_name)
    status(f"File: {file_name}")
    client.clear_terminal()
    client.start_capture(full_path)
    status(">> Capture STARTED... (Waiting for RealTerm to finish)")

    while client.is_capturing():
        if stop():
            try:
                client.stop_capture()
            except Exception:
                pass
            status("Stopped.")
            return False
        time.sleep(cfg.poll_interval_s)

    status(">> Capture FINISHED.")
    return True


def capture_index_for_live_capture(cfg: RealTermConfig) -> int:
    """Index passed to build_capture_filename for one-shot GUI captures."""
    if cfg.file_naming_mode == "scheme4":
        return 1
    return cfg.start_index


def run_live_capture_session(
    session_cfg: RealTermConfig,
    capture_cfg_queue: "queue.Queue[RealTermConfig]",
    *,
    should_stop: Callable[[], bool],
    on_status: Optional[Callable[[str], None]] = None,
) -> None:
    """Open RealTerm once; each queued config runs one capture (latest form values)."""
    pythoncom.CoInitialize()
    validate_config(session_cfg)
    try:
        os.makedirs(session_cfg.save_dir, exist_ok=True)

        def status(msg: str) -> None:
            if on_status is not None:
                on_status(msg)
            else:
                print(msg)

        status("Connecting to RealTerm...")
        rt = connect_realterm()
        client = RealTermClient(rt)
        client.setup_window(session_cfg)
        client.configure_serial_and_open(session_cfg, status)

        while not should_stop():
            try:
                cfg = capture_cfg_queue.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                validate_config(cfg)
            except Exception as exc:
                status(f"ERROR: invalid capture config: {exc}")
                continue

            os.makedirs(cfg.save_dir, exist_ok=True)
            client.setup_window(cfg)
            client.configure_serial_and_open(cfg, status)

            if not _wait_auto_delay(cfg.auto_delay_s, should_stop, status):
                break

            cap_idx = capture_index_for_live_capture(cfg)
            if cfg.file_naming_mode in ("scheme1", "scheme3"):
                status(f"\n--- Index {cap_idx} ---")

            if not _execute_one_capture(client, cfg, cap_idx, should_stop, status):
                break

        if should_stop():
            status("Stopped.")
    finally:
        pythoncom.CoUninitialize()


def run_capture(
    cfg: RealTermConfig,
    *,
    rt: Optional[object] = None,
    should_stop: Optional[Callable[[], bool]] = None,
    wait_for_manual_trigger: Optional[Callable[[], bool]] = None,
    on_status: Optional[Callable[[str], None]] = None,
    keep_open_until_stop: bool = False,
) -> None:
    pythoncom.CoInitialize()
    validate_config(cfg)
    try:
        os.makedirs(cfg.save_dir, exist_ok=True)

        def status(msg: str) -> None:
            if on_status is not None:
                on_status(msg)
            else:
                print(msg)

        if rt is None:
            status("Connecting to RealTerm...")
            rt = connect_realterm()

        client = RealTermClient(rt)
        client.setup_window(cfg)
        client.configure_serial_and_open(cfg, status)

        stop = should_stop or (lambda: False)
        if cfg.file_naming_mode == "scheme3":
            jobs = iter_ff_mux_jobs(cfg)
        elif cfg.file_naming_mode == "scheme4":
            jobs = iter_r1_init_jobs(cfg)
        else:
            jobs = iter_reliability_jobs(cfg)

        for heading, step_cfg, capture_index in jobs:
            if stop():
                status("Stopped.")
                return

            if heading:
                status(heading)
            if step_cfg.file_naming_mode in ("scheme1", "scheme3"):
                status(f"\n--- Index {capture_index} ---")

            if not _wait_for_trigger(wait_for_manual_trigger, status):
                status("Stopped.")
                return

            if not _wait_auto_delay(cfg.auto_delay_s, stop, status):
                return

            if not _execute_one_capture(client, step_cfg, capture_index, stop, status):
                return

        if keep_open_until_stop:
            status("Capture plan completed. RealTerm will stay open until Disconnect.")
            while not stop():
                time.sleep(0.1)
            status("Stopped.")
    finally:
        pythoncom.CoUninitialize()

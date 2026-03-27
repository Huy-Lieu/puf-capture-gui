from __future__ import annotations

from typing import Callable

import pythoncom
import win32com.client

from RealTermTypes import RealTermConfig


def connect_realterm() -> object:
    try:
        return win32com.client.GetActiveObject("Realterm.RealtermIntf")
    except Exception:
        return win32com.client.Dispatch("Realterm.RealtermIntf")


def disconnect_realterm() -> bool:
    """Disconnect serial port on active RealTerm instance if available."""
    pythoncom.CoInitialize()
    try:
        try:
            rt = win32com.client.GetActiveObject("Realterm.RealtermIntf")
        except Exception:
            return False

        try:
            rt.PortOpen = 0
        except Exception:
            try:
                rt.Close()
            except Exception:
                return False
        return True
    finally:
        pythoncom.CoUninitialize()


class RealTermClient:
    def __init__(self, rt: object) -> None:
        self._rt = rt

    @property
    def raw(self) -> object:
        return self._rt

    def setup_window(self, cfg: RealTermConfig) -> None:
        self._rt.Visible = True
        self._rt.Caption = cfg.caption
        self._rt.DisplayAs = cfg.display_as

    def configure_serial_and_open(
        self, cfg: RealTermConfig, status: Callable[[str], None]
    ) -> None:
        self._rt.Port = cfg.com_port
        self._rt.Baud = cfg.baud
        status(f"Configured serial: COM{cfg.com_port}, {cfg.baud} baud")

        port_open = False
        try:
            port_open = bool(self._rt.PortOpen)
        except Exception:
            port_open = False

        if port_open:
            status("Port is already open.")
            return

        open_errors = []
        try:
            self._rt.PortOpen = 1
        except Exception as e:
            open_errors.append(f"PortOpen=1 failed: {e}")

        try:
            if not bool(self._rt.PortOpen):
                self._rt.Open()
        except Exception as e:
            open_errors.append(f"Open() failed: {e}")

        try:
            if bool(self._rt.PortOpen):
                status("Serial port opened.")
                return
        except Exception:
            pass

        details = "; ".join(open_errors) if open_errors else "unknown reason"
        raise RuntimeError(
            f"Failed to open COM{cfg.com_port}. Check port availability/permissions. ({details})"
        )

    def clear_terminal(self) -> None:
        self._rt.ClearTerminal()

    def start_capture(self, full_path: str) -> None:
        self._rt.CaptureFile = full_path
        self._rt.Capture = 1

    def is_capturing(self) -> bool:
        return bool(self._rt.Capture == 1)

    def stop_capture(self) -> None:
        self._rt.Capture = 0

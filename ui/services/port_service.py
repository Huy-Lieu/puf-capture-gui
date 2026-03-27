from __future__ import annotations

import re
import winreg

try:
    from serial.tools import list_ports as serial_list_ports
except Exception:
    serial_list_ports = None


def detect_com_ports() -> tuple[list[str], dict[str, str]]:
    if serial_list_ports is not None:
        ports: list[tuple[str, str]] = []
        for port in serial_list_ports.comports():
            device = (port.device or "").upper()
            if device.startswith("COM"):
                desc = (port.description or "").strip()
                label = f"{device} - {desc}" if desc else device
                ports.append((device, label))

        def port_num_from_com(com_name: str) -> int:
            match = re.search(r"(\d+)$", com_name)
            return int(match.group(1)) if match else 9999

        ports.sort(key=lambda pair: port_num_from_com(pair[0]))
        mapping = {label: com for com, label in ports}
        return [label for _, label in ports], mapping

    ports: list[str] = []
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
    except OSError:
        return [], {}

    try:
        idx = 0
        while True:
            _, value, _ = winreg.EnumValue(key, idx)
            if isinstance(value, str) and value.upper().startswith("COM"):
                ports.append(value.upper())
            idx += 1
    except OSError:
        pass
    finally:
        winreg.CloseKey(key)

    def port_num(port_name: str) -> int:
        match = re.search(r"(\d+)$", port_name)
        return int(match.group(1)) if match else 9999

    ports_sorted = sorted(set(ports), key=port_num)
    mapping = {port: port for port in ports_sorted}
    return ports_sorted, mapping

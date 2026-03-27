from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class VivadoRunConfig:
    vivado_bat_path: str
    project_path: str
    tcl_path: str


def build_vivado_command(cfg: VivadoRunConfig) -> list[str]:
    return [
        cfg.vivado_bat_path,
        "-mode",
        "batch",
        "-source",
        cfg.tcl_path,
        "-tclargs",
        cfg.project_path,
    ]


def start_vivado_batch(cfg: VivadoRunConfig) -> subprocess.Popen:
    cmd = build_vivado_command(cfg)
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

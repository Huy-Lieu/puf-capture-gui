from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FileNamingMode = Literal["scheme1", "scheme3", "scheme4"]


@dataclass(frozen=True)
class RealTermConfig:
    base_name: str
    start_index: int
    end_index: int
    file_naming_mode: FileNamingMode = "scheme1"
    fpga_index: int = 7
    end_fpga_index: int = 7
    r1_pair_suffix: str = ""
    r1_loop_all_pairs: bool = False
    flipflop_position: str = "CFF"
    mdist_value: int = 8
    mux_a: int = 0
    mux_b: int = 7
    ff_loop_fixed_mux: bool = False
    mdist_loop_fixed_mux: bool = False
    ldist_case_id: int = 1
    ldist_lut_a: str = "DLUTA"
    ldist_lut_b: str = "ALUTB"
    ldist_distance: int = 6
    ldist_loop: bool = False
    com_port: int = 3
    extension: str = ".txt"
    save_dir: str = "."
    auto_delay_s: float = 5.0
    baud: int = 115200
    display_as: int = 10  # RealTerm "Binary (Bit view)"
    poll_interval_s: float = 0.5
    caption: str = "RealTerm - Python Controller"

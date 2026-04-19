from __future__ import annotations

from RealTermNaming import R1_INIT_PAIR_SUFFIXES, get_mdist_pairs, resolve_ldist_case
from RealTermTypes import RealTermConfig


def validate_config(cfg: RealTermConfig) -> None:
    if cfg.start_index < 0:
        raise ValueError("start_index must be >= 0")
    if cfg.end_index < cfg.start_index:
        raise ValueError("end_index must be >= start_index")
    if cfg.file_naming_mode not in ("scheme1", "scheme3", "scheme4"):
        raise ValueError("file_naming_mode must be 'scheme1', 'scheme3', or 'scheme4'")
    if cfg.fpga_index <= 0:
        raise ValueError("fpga_index must be > 0")
    if cfg.end_fpga_index <= 0:
        raise ValueError("end_fpga_index must be > 0")
    if cfg.end_fpga_index < cfg.fpga_index:
        raise ValueError("end_fpga_index must be >= fpga_index")
    if cfg.file_naming_mode == "scheme4":
        if cfg.start_index != 1 or cfg.end_index != 1:
            raise ValueError("scheme4 requires start_index and end_index to be 1")
        if cfg.r1_pair_suffix not in R1_INIT_PAIR_SUFFIXES:
            raise ValueError("r1_pair_suffix must be one of the 12 CFF R1 init pair tokens")
    if cfg.file_naming_mode == "scheme3":
        if cfg.flipflop_position not in ("AFF", "BFF", "CFF", "DFF"):
            raise ValueError("flipflop_position must be one of AFF/BFF/CFF/DFF for scheme3")
        if not cfg.mdist_loop_fixed_mux:
            allowed_pairs = get_mdist_pairs(cfg.mdist_value)
            if cfg.mdist_value < 2 or cfg.mdist_value > 8 or not allowed_pairs:
                raise ValueError("mdist_value must be one of 2..8 for scheme3")
            if (cfg.mux_a, cfg.mux_b) not in allowed_pairs:
                raise ValueError("Selected MUX pair is invalid for the given mdist_value")
        if cfg.ldist_case_id not in range(1, 11):
            raise ValueError("ldist_case_id must be in range 1..10 for scheme3")
        expected_lut_a, expected_lut_b, expected_dist = resolve_ldist_case(cfg.ldist_case_id)
        if (
            cfg.ldist_lut_a != expected_lut_a
            or cfg.ldist_lut_b != expected_lut_b
            or cfg.ldist_distance != expected_dist
        ):
            raise ValueError("LDIST case mapping fields do not match selected ldist_case_id")
    if cfg.com_port <= 0:
        raise ValueError("com_port must be > 0")
    if cfg.baud <= 0:
        raise ValueError("baud must be > 0")
    if cfg.extension != ".txt":
        raise ValueError("extension is fixed and must be '.txt'")
    if cfg.auto_delay_s < 0:
        raise ValueError("auto_delay_s must be >= 0")
    if cfg.poll_interval_s <= 0:
        raise ValueError("poll_interval_s must be > 0")

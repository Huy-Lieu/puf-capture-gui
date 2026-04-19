from __future__ import annotations

import re

from RealTermNaming import R1_INIT_PAIR_SUFFIXES
from RealTermTypes import RealTermConfig
from ui.services.naming_adapter import resolve_ldist_details, resolve_mdist_mux


def parse_realterm_config(
    *,
    base_name: str,
    naming_mode: str,
    fpga_index_raw: str,
    end_fpga_index_raw: str,
    start_index_raw: str,
    end_index_raw: str,
    com_port_raw: str,
    com_label_to_port: dict[str, str],
    baud_raw: str,
    save_dir: str,
    auto_delay_raw: str,
    flipflop_position: str,
    mdist_value_raw: str,
    mux_pair_raw: str,
    ff_loop_fixed_mux: bool,
    mdist_loop_fixed_mux: bool,
    ldist_case_raw: str,
    ldist_loop: bool,
    r1_pair_suffix_raw: str = "",
    r1_loop_all_pairs: bool = False,
) -> RealTermConfig:
    base = base_name.strip()

    mode = naming_mode.strip() or "scheme1"
    if mode not in ("scheme1", "scheme3", "scheme4"):
        raise ValueError("Naming mode must be scheme1, scheme3, or scheme4.")

    try:
        fpga_index = int(fpga_index_raw.strip())
    except Exception:
        raise ValueError("FPGA index must be an integer.") from None
    if fpga_index <= 0:
        raise ValueError("FPGA index must be > 0.")

    try:
        end_fpga_index = int(end_fpga_index_raw.strip())
    except Exception:
        raise ValueError("End FPGA index must be an integer.") from None
    if end_fpga_index <= 0:
        raise ValueError("End FPGA index must be > 0.")
    if end_fpga_index < fpga_index:
        raise ValueError("End FPGA index must be >= FPGA index.")

    raw_com = com_port_raw.strip()
    if not raw_com:
        raise ValueError("COM port must not be empty.")
    mapped = com_label_to_port.get(raw_com, raw_com)
    match = re.search(r"(?:COM)?(\d+)", mapped.upper())
    if not match:
        raise ValueError("COM port must be like 3 or COM3.") from None
    com_port = int(match.group(1))
    if com_port <= 0:
        raise ValueError("COM port must be > 0.")

    try:
        baud = int(baud_raw.strip())
    except Exception:
        raise ValueError("Baud rate must be an integer (e.g. 115200).") from None
    if baud <= 0:
        raise ValueError("Baud rate must be > 0.")

    save_dir_clean = save_dir.strip()
    if not save_dir_clean:
        raise ValueError("Save directory must not be empty.")

    try:
        delay = float(auto_delay_raw.strip())
    except Exception:
        raise ValueError("Auto delay must be a number.") from None

    if mode == "scheme4":
        suffix = (r1_pair_suffix_raw or "").strip()
        if suffix not in R1_INIT_PAIR_SUFFIXES:
            raise ValueError(
                "R1 pair must be one of the 12 predefined suffix tokens (see dropdown)."
            )
        return RealTermConfig(
            base_name=base,
            start_index=1,
            end_index=1,
            file_naming_mode="scheme4",
            fpga_index=fpga_index,
            end_fpga_index=end_fpga_index,
            r1_pair_suffix=suffix,
            r1_loop_all_pairs=bool(r1_loop_all_pairs),
            com_port=com_port,
            baud=baud,
            extension=".txt",
            save_dir=save_dir_clean,
            auto_delay_s=delay,
        )

    try:
        start = int(start_index_raw.strip())
    except Exception:
        raise ValueError("Start index must be an integer.") from None

    try:
        end = int(end_index_raw.strip())
    except Exception:
        raise ValueError("End index must be an integer.") from None

    flipflop = (flipflop_position or "").strip().upper() or "DFF"
    if flipflop not in ("DFF", "CFF", "BFF", "AFF"):
        raise ValueError("Flip-flop position must be one of DFF/CFF/BFF/AFF.")

    mdist_value, mux_a, mux_b = resolve_mdist_mux(
        mdist_value_raw=mdist_value_raw,
        mux_pair_raw=mux_pair_raw,
        naming_mode=mode,
        mdist_loop_fixed_mux=bool(mdist_loop_fixed_mux),
    )
    ldist_case_id, ldist_lut_a, ldist_lut_b, ldist_distance = resolve_ldist_details(ldist_case_raw)

    return RealTermConfig(
        base_name=base,
        start_index=start,
        end_index=end,
        file_naming_mode=mode,
        fpga_index=fpga_index,
        end_fpga_index=end_fpga_index,
        flipflop_position=flipflop,
        mdist_value=mdist_value,
        mux_a=mux_a,
        mux_b=mux_b,
        ff_loop_fixed_mux=bool(ff_loop_fixed_mux),
        mdist_loop_fixed_mux=bool(mdist_loop_fixed_mux),
        ldist_case_id=ldist_case_id,
        ldist_lut_a=ldist_lut_a,
        ldist_lut_b=ldist_lut_b,
        ldist_distance=ldist_distance,
        ldist_loop=bool(ldist_loop),
        com_port=com_port,
        baud=baud,
        extension=".txt",
        save_dir=save_dir_clean,
        auto_delay_s=delay,
    )

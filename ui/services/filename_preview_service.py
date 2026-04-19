from __future__ import annotations

from RealTermNaming import (
    R1_INIT_PAIR_SUFFIXES,
    build_capture_filename,
    get_ldist_case_ids_ordered,
    resolve_ldist_case,
)
from RealTermTypes import RealTermConfig
from ui.services.naming_adapter import resolve_ldist_details, resolve_mdist_mux, safe_int


def build_preview_name(
    *,
    naming_mode: str,
    fpga_index_raw: str,
    end_fpga_index_raw: str,
    start_index_raw: str,
    end_index_raw: str,
    base_name: str,
    flipflop_position: str,
    mdist_value_raw: str,
    mux_pair_raw: str,
    ff_loop_fixed_mux: bool,
    mdist_loop_fixed_mux: bool,
    ldist_case_raw: str,
    ldist_loop: bool,
    r1_pair_suffix_raw: str = "",
    r1_loop_all_pairs: bool = False,
) -> str:
    mode = naming_mode.strip() or "scheme1"
    fpga_index = safe_int(fpga_index_raw, 1)
    # Keep preview aligned with current form input; do not inject placeholder text.
    base = base_name.strip()

    if mode == "scheme4":
        fpga_start = max(fpga_index, 1)
        fpga_end = max(safe_int(end_fpga_index_raw, fpga_start), fpga_start)
        # When looping all pairs, preview uses the first canonical suffix (planner runs all 12).
        if r1_loop_all_pairs:
            suffix = R1_INIT_PAIR_SUFFIXES[0]
        else:
            cand = (r1_pair_suffix_raw or "").strip()
            suffix = cand if cand in R1_INIT_PAIR_SUFFIXES else R1_INIT_PAIR_SUFFIXES[0]
        cfg = RealTermConfig(
            base_name=base,
            start_index=1,
            end_index=1,
            file_naming_mode="scheme4",
            fpga_index=fpga_start,
            end_fpga_index=fpga_end,
            r1_pair_suffix=suffix,
            r1_loop_all_pairs=bool(r1_loop_all_pairs),
            com_port=3,
            baud=115200,
            extension=".txt",
            save_dir=".",
        )
        return build_capture_filename(cfg, 1)

    end_fpga_index = safe_int(end_fpga_index_raw, fpga_index)
    start_index = safe_int(start_index_raw, 1)
    end_index = safe_int(end_index_raw, start_index)
    mdist_value, mux_a, mux_b = resolve_mdist_mux(
        mdist_value_raw=mdist_value_raw,
        mux_pair_raw=mux_pair_raw,
        naming_mode=mode,
        mdist_loop_fixed_mux=bool(mdist_loop_fixed_mux),
    )
    ff = (flipflop_position or "DFF").strip().upper() or "DFF"
    if ff_loop_fixed_mux and mode == "scheme3":
        ff = "DFF"
    case_num, ldist_lut_a, ldist_lut_b, ldist_distance = resolve_ldist_details(ldist_case_raw)
    if ldist_loop and mode == "scheme3":
        case_num = get_ldist_case_ids_ordered()[0]
        ldist_lut_a, ldist_lut_b, ldist_distance = resolve_ldist_case(case_num)

    cfg = RealTermConfig(
        base_name=base,
        start_index=start_index,
        end_index=end_index,
        file_naming_mode=mode,  # type: ignore[arg-type]
        fpga_index=max(fpga_index, 1),
        end_fpga_index=max(end_fpga_index, max(fpga_index, 1)),
        flipflop_position=ff,
        mdist_value=mdist_value,
        mux_a=mux_a,
        mux_b=mux_b,
        ff_loop_fixed_mux=bool(ff_loop_fixed_mux),
        mdist_loop_fixed_mux=bool(mdist_loop_fixed_mux),
        ldist_case_id=case_num,
        ldist_lut_a=ldist_lut_a,
        ldist_lut_b=ldist_lut_b,
        ldist_distance=ldist_distance,
        ldist_loop=bool(ldist_loop),
        com_port=3,
        baud=115200,
        extension=".txt",
        save_dir=".",
    )
    return build_capture_filename(cfg, start_index)

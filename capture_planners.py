from __future__ import annotations

from dataclasses import replace
from typing import Iterator

from RealTermNaming import (
    MDIST_CASES,
    R1_INIT_PAIR_SUFFIXES,
    get_ldist_case_ids_ordered,
    resolve_ldist_case,
)
from RealTermTypes import RealTermConfig

_FF_ORDER: tuple[str, ...] = ("DFF", "CFF", "BFF", "AFF")


def iter_reliability_jobs(cfg: RealTermConfig) -> Iterator[tuple[str, RealTermConfig, int]]:
    total_fpga = cfg.end_fpga_index - cfg.fpga_index + 1
    for fpga_offset, fpga in enumerate(range(cfg.fpga_index, cfg.end_fpga_index + 1), start=1):
        per_fpga_cfg = replace(cfg, fpga_index=fpga)
        heading = f"\n=== Reliability FPGA {fpga} ({fpga_offset}/{total_fpga}) ==="
        for current_index in range(cfg.start_index, cfg.end_index + 1):
            yield heading, per_fpga_cfg, current_index
            heading = ""


def iter_ff_mux_jobs(cfg: RealTermConfig) -> Iterator[tuple[str, RealTermConfig, int]]:
    if cfg.ldist_loop:
        ff_values = (cfg.flipflop_position,)
        mdist_steps = [(cfg.mdist_value, cfg.mux_a, cfg.mux_b)]
        all_ldist = get_ldist_case_ids_ordered()
        ldist_start = next((i for i, cid in enumerate(all_ldist) if cid == cfg.ldist_case_id), 0)
        ldist_case_ids = all_ldist[ldist_start:]
    else:
        if cfg.ff_loop_fixed_mux:
            ff_start = next((i for i, f in enumerate(_FF_ORDER) if f == cfg.flipflop_position), 0)
            ff_values = _FF_ORDER[ff_start:]
        else:
            ff_values = (cfg.flipflop_position,)
        mdist_steps: list[tuple[int, int, int]] = []
        if cfg.mdist_loop_fixed_mux:
            all_steps = [
                (mdist, mux_a, mux_b)
                for mdist in sorted(MDIST_CASES.keys(), reverse=True)
                for mux_a, mux_b in MDIST_CASES[mdist]
            ]
            mdist_start = next(
                (i for i, s in enumerate(all_steps) if s == (cfg.mdist_value, cfg.mux_a, cfg.mux_b)),
                0,
            )
            mdist_steps = all_steps[mdist_start:]
        else:
            mdist_steps.append((cfg.mdist_value, cfg.mux_a, cfg.mux_b))
        ldist_case_ids = (cfg.ldist_case_id,)

    total_fpga = cfg.end_fpga_index - cfg.fpga_index + 1
    total_steps = total_fpga * len(mdist_steps) * len(ff_values) * len(ldist_case_ids)
    step_idx = 0
    for fpga in range(cfg.fpga_index, cfg.end_fpga_index + 1):
        for ldist_case_id in ldist_case_ids:
            ldist_lut_a, ldist_lut_b, ldist_distance = resolve_ldist_case(ldist_case_id)
            for mdist_value, mux_a, mux_b in mdist_steps:
                for ff in ff_values:
                    step_idx += 1
                    step_cfg = replace(
                        cfg,
                        fpga_index=fpga,
                        mdist_value=mdist_value,
                        mux_a=mux_a,
                        mux_b=mux_b,
                        flipflop_position=ff,
                        ldist_case_id=ldist_case_id,
                        ldist_lut_a=ldist_lut_a,
                        ldist_lut_b=ldist_lut_b,
                        ldist_distance=ldist_distance,
                    )
                    heading = (
                        f"\n--- FF & MUX Step {step_idx} / {total_steps} -- FPGA{fpga} / {ff} "
                        f"-- MDIST{mdist_value} M{mux_a}-M{mux_b} "
                        f"-- {ldist_lut_a}-{ldist_lut_b} LDIST{ldist_distance} ---"
                    )
                    yield heading, step_cfg, 1


def iter_r1_init_jobs(cfg: RealTermConfig) -> Iterator[tuple[str, RealTermConfig, int]]:
    """CFF R1 init (scheme4): range-then-pair execution."""
    fpga_values = list(range(cfg.fpga_index, cfg.end_fpga_index + 1))
    pair_values = list(R1_INIT_PAIR_SUFFIXES) if cfg.r1_loop_all_pairs else [cfg.r1_pair_suffix]
    total_steps = len(fpga_values) * len(pair_values)
    step_idx = 0
    for fpga in fpga_values:
        for suffix in pair_values:
            step_idx += 1
            step_cfg = replace(cfg, fpga_index=fpga, r1_pair_suffix=suffix)
            heading = (
                f"\n--- CFF R1 init Step {step_idx} / {total_steps} -- FPGA{fpga} -- {suffix} ---"
            )
            yield heading, step_cfg, 1

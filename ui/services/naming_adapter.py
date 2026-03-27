from __future__ import annotations

import re

from RealTermNaming import MDIST_CASES, parse_ldist_case_label, resolve_ldist_case


def safe_int(value: str, default: int) -> int:
    try:
        return int(value.strip())
    except Exception:
        return default


def parse_mux_pair_label(label: str) -> tuple[int, int]:
    pair_match = re.search(r"M(\d+)\s*-\s*M(\d+)", (label or "").strip().upper())
    if pair_match:
        return int(pair_match.group(1)), int(pair_match.group(2))
    return 0, 7


def resolve_mdist_mux(
    *,
    mdist_value_raw: str,
    mux_pair_raw: str,
    naming_mode: str,
    mdist_loop_fixed_mux: bool,
) -> tuple[int, int, int]:
    mdist_value = safe_int(mdist_value_raw, 8)
    mux_a, mux_b = parse_mux_pair_label(mux_pair_raw)
    if naming_mode == "scheme3" and mdist_loop_fixed_mux:
        mdist_value = 8
        mux_a, mux_b = MDIST_CASES.get(8, ((0, 7),))[0]
    return mdist_value, mux_a, mux_b


def parse_ldist_case_id(raw_value: str) -> int:
    cleaned = (raw_value or "").strip()
    case_match = re.search(r"^\s*CASE\s*(\d+)\b", cleaned, flags=re.IGNORECASE)
    if case_match:
        return int(case_match.group(1))
    return parse_ldist_case_label(cleaned)


def resolve_ldist_details(raw_value: str) -> tuple[int, str, str, int]:
    case_id = parse_ldist_case_id(raw_value)
    if case_id not in range(1, 11):
        raise ValueError("LDIST case must be one of Case 1..Case 10.")
    ldist_lut_a, ldist_lut_b, ldist_distance = resolve_ldist_case(case_id)
    return case_id, ldist_lut_a, ldist_lut_b, ldist_distance

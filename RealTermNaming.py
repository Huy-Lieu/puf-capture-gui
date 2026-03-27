from __future__ import annotations

import re

from RealTermTypes import RealTermConfig

MDIST_CASES: dict[int, tuple[tuple[int, int], ...]] = {
    8: ((0, 7),),
    7: ((0, 6), (1, 7)),
    6: ((0, 5), (1, 6), (2, 7)),
    5: ((0, 4), (1, 5), (2, 6), (3, 7)),
    4: ((1, 4), (2, 5), (3, 6)),
    3: ((2, 4), (3, 5)),
    2: ((3, 4),),
}

LDIST_CASES: dict[int, tuple[str, str, int]] = {
    1: ("DLUTA", "ALUTB", 6),
    2: ("DLUTA", "BLUTB", 5),
    3: ("DLUTA", "CLUTB", 4),
    4: ("DLUTA", "DLUTB", 3),
    5: ("DLUTA", "ALUTB", 2),
    6: ("DLUTA", "BLUTB", 1),
    7: ("DLUTA", "CLUTB", 0),
    8: ("CLUTA", "ALUTB", 5),
    9: ("BLUTA", "ALUTB", 4),
    10: ("ALUTA", "ALUTB", 3),
}


def _normalize_scheme1_base(base_name: str, fpga_index: int) -> str:
    base_clean = base_name.strip()
    replaced = re.sub(r"^FPGA\d+", f"FPGA{fpga_index}", base_clean)
    if replaced == base_clean and not base_clean.startswith("FPGA"):
        replaced = f"FPGA{fpga_index}_{base_clean}"
    return replaced


def build_capture_filename(cfg: RealTermConfig, capture_index: int) -> str:
    if cfg.file_naming_mode == "scheme3":
        base_clean = cfg.base_name.strip().strip("_")
        base_clean = re.sub(r"^FPGA\d+_?", "", base_clean, flags=re.IGNORECASE)
        prefix = f"FPGA{cfg.fpga_index}_"
        if base_clean:
            prefix += f"{base_clean}_"
        return (
            f"{prefix}MDIST{cfg.mdist_value}_M{cfg.mux_a}_M{cfg.mux_b}_"
            f"{cfg.ldist_lut_a}_{cfg.ldist_lut_b}_LDIST{cfg.ldist_distance}_"
            f"{cfg.flipflop_position}{cfg.extension}"
        )

    normalized_base = _normalize_scheme1_base(cfg.base_name, cfg.fpga_index)
    suffix = f"N{capture_index:03d}"
    if normalized_base.endswith("_"):
        return f"{normalized_base}{suffix}{cfg.extension}"
    return f"{normalized_base}_{suffix}{cfg.extension}"


def get_mdist_pairs(mdist_value: int) -> tuple[tuple[int, int], ...]:
    return MDIST_CASES.get(mdist_value, ())


def resolve_ldist_case(case_id: int) -> tuple[str, str, int]:
    return LDIST_CASES[case_id]


def get_ldist_case_label(case_id: int) -> str:
    lut_a, lut_b, dist = resolve_ldist_case(case_id)
    return f"{lut_a} + {lut_b}, LDIST{dist}"


def get_ldist_case_ids_ordered() -> list[int]:
    # Higher distance first; stable tie-break by original case id.
    return sorted(LDIST_CASES.keys(), key=lambda cid: (-LDIST_CASES[cid][2], cid))


def parse_ldist_case_label(label: str) -> int:
    cleaned = (label or "").strip().upper()
    for case_id, (lut_a, lut_b, dist) in LDIST_CASES.items():
        expected = f"{lut_a} + {lut_b}, LDIST{dist}".upper()
        if cleaned == expected:
            return case_id
    return 1

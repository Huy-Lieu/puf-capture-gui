from __future__ import annotations

import unittest

from RealTermNaming import build_capture_filename
from RealTermTypes import RealTermConfig
from ui.services.naming_adapter import parse_ldist_case_id, resolve_mdist_mux


class NamingAdapterTests(unittest.TestCase):
    def test_parse_ldist_case_id_from_label(self) -> None:
        self.assertEqual(parse_ldist_case_id("DLUTA + ALUTB, LDIST6"), 1)
        self.assertEqual(parse_ldist_case_id("DLUTA + BLUTB, LDIST1"), 6)

    def test_parse_ldist_case_id_case_prefix(self) -> None:
        self.assertEqual(parse_ldist_case_id("Case 3"), 3)

    def test_resolve_mdist_mux_for_loop_mode(self) -> None:
        mdist, mux_a, mux_b = resolve_mdist_mux(
            mdist_value_raw="5",
            mux_pair_raw="M2-M6",
            naming_mode="scheme3",
            mdist_loop_fixed_mux=True,
        )
        self.assertEqual((mdist, mux_a, mux_b), (8, 0, 7))

    def test_scheme3_filename_has_no_n_suffix(self) -> None:
        cfg = RealTermConfig(
            base_name="FPGA7_BASE",
            start_index=1,
            end_index=1,
            file_naming_mode="scheme3",
            fpga_index=7,
            end_fpga_index=7,
            flipflop_position="DFF",
            mdist_value=8,
            mux_a=0,
            mux_b=7,
            ldist_case_id=1,
            ldist_lut_a="DLUTA",
            ldist_lut_b="ALUTB",
            ldist_distance=6,
        )
        name = build_capture_filename(cfg, 1)
        self.assertNotIn("_N001", name)
        self.assertTrue(name.endswith("_DFF.txt"))


if __name__ == "__main__":
    unittest.main()

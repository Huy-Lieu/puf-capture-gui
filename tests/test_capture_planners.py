from __future__ import annotations

import unittest

from capture_planners import iter_ff_mux_jobs, iter_r1_init_jobs, iter_reliability_jobs
from RealTermNaming import R1_INIT_PAIR_SUFFIXES
from RealTermTypes import RealTermConfig


class CapturePlannersTests(unittest.TestCase):
    def test_reliability_job_count(self) -> None:
        cfg = RealTermConfig(
            base_name="BASE",
            start_index=1,
            end_index=3,
            file_naming_mode="scheme1",
            fpga_index=1,
            end_fpga_index=2,
        )
        jobs = list(iter_reliability_jobs(cfg))
        self.assertEqual(len(jobs), 6)
        self.assertTrue(jobs[0][0].startswith("\n=== Reliability FPGA 1"))

    def test_ff_mux_ldist_loop_count(self) -> None:
        cfg = RealTermConfig(
            base_name="BASE",
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
            ldist_loop=True,
        )
        jobs = list(iter_ff_mux_jobs(cfg))
        self.assertEqual(len(jobs), 10)  # 10 LDIST cases, one capture each
        self.assertIn("FF & MUX Step 1 / 10", jobs[0][0])

    def test_ff_loop_starts_from_current_selection(self) -> None:
        cfg = RealTermConfig(
            base_name="BASE",
            start_index=1,
            end_index=1,
            file_naming_mode="scheme3",
            fpga_index=7,
            end_fpga_index=7,
            flipflop_position="CFF",
            mdist_value=8,
            mux_a=0,
            mux_b=7,
            ldist_case_id=1,
            ldist_lut_a="DLUTA",
            ldist_lut_b="ALUTB",
            ldist_distance=6,
            ff_loop_fixed_mux=True,
        )
        jobs = list(iter_ff_mux_jobs(cfg))
        ff_sequence = [j[1].flipflop_position for j in jobs]
        # DFF must be skipped; starts at CFF
        self.assertEqual(ff_sequence, ["CFF", "BFF", "AFF"])

    def test_mdist_loop_starts_from_current_selection(self) -> None:
        cfg = RealTermConfig(
            base_name="BASE",
            start_index=1,
            end_index=1,
            file_naming_mode="scheme3",
            fpga_index=7,
            end_fpga_index=7,
            flipflop_position="DFF",
            mdist_value=5,
            mux_a=1,
            mux_b=5,
            ldist_case_id=1,
            ldist_lut_a="DLUTA",
            ldist_lut_b="ALUTB",
            ldist_distance=6,
            mdist_loop_fixed_mux=True,
        )
        jobs = list(iter_ff_mux_jobs(cfg))
        mdist_sequence = [(j[1].mdist_value, j[1].mux_a, j[1].mux_b) for j in jobs]
        # Starts at (5, 1, 5) — skips MDIST 8, 7, 6, and M0-M4 of MDIST5
        self.assertEqual(mdist_sequence[0], (5, 1, 5))
        # MDIST8 and 7 and 6 must not appear
        self.assertNotIn(8, [m[0] for m in mdist_sequence])
        self.assertNotIn(7, [m[0] for m in mdist_sequence])
        self.assertNotIn(6, [m[0] for m in mdist_sequence])

    def test_ldist_loop_starts_from_current_selection(self) -> None:
        cfg = RealTermConfig(
            base_name="BASE",
            start_index=1,
            end_index=1,
            file_naming_mode="scheme3",
            fpga_index=7,
            end_fpga_index=7,
            flipflop_position="DFF",
            mdist_value=8,
            mux_a=0,
            mux_b=7,
            ldist_case_id=4,  # case 4 = DLUTB LDIST3; ordered position index 3
            ldist_lut_a="DLUTA",
            ldist_lut_b="DLUTB",
            ldist_distance=3,
            ldist_loop=True,
        )
        jobs = list(iter_ff_mux_jobs(cfg))
        # get_ldist_case_ids_ordered() = [1, 2, 8, 3, 9, 4, 10, 5, 6, 7]
        # case 4 is at index 5, so 5 remaining cases: [4, 10, 5, 6, 7]
        self.assertEqual(len(jobs), 5)
        self.assertEqual(jobs[0][1].ldist_case_id, 4)

    def test_r1_init_manual_one_job(self) -> None:
        cfg = RealTermConfig(
            base_name="BASE",
            start_index=1,
            end_index=1,
            file_naming_mode="scheme4",
            fpga_index=7,
            end_fpga_index=7,
            r1_pair_suffix=R1_INIT_PAIR_SUFFIXES[0],
            r1_loop_all_pairs=False,
        )
        jobs = list(iter_r1_init_jobs(cfg))
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0][2], 1)

    def test_r1_init_loop_twelve_jobs(self) -> None:
        cfg = RealTermConfig(
            base_name="BASE",
            start_index=1,
            end_index=1,
            file_naming_mode="scheme4",
            fpga_index=3,
            end_fpga_index=3,
            r1_pair_suffix=R1_INIT_PAIR_SUFFIXES[0],
            r1_loop_all_pairs=True,
        )
        jobs = list(iter_r1_init_jobs(cfg))
        self.assertEqual(len(jobs), 12)
        self.assertEqual(jobs[-1][1].r1_pair_suffix, R1_INIT_PAIR_SUFFIXES[-1])

    def test_r1_init_range_then_pair_order(self) -> None:
        cfg = RealTermConfig(
            base_name="BASE",
            start_index=1,
            end_index=1,
            file_naming_mode="scheme4",
            fpga_index=1,
            end_fpga_index=2,
            r1_pair_suffix=R1_INIT_PAIR_SUFFIXES[0],
            r1_loop_all_pairs=True,
        )
        jobs = list(iter_r1_init_jobs(cfg))
        self.assertEqual(len(jobs), 24)
        # range-then-pair: first all pairs on FPGA1, then FPGA2
        self.assertEqual(jobs[0][1].fpga_index, 1)
        self.assertEqual(jobs[11][1].fpga_index, 1)
        self.assertEqual(jobs[12][1].fpga_index, 2)
        self.assertEqual(jobs[0][1].r1_pair_suffix, R1_INIT_PAIR_SUFFIXES[0])
        self.assertEqual(jobs[11][1].r1_pair_suffix, R1_INIT_PAIR_SUFFIXES[-1])


if __name__ == "__main__":
    unittest.main()

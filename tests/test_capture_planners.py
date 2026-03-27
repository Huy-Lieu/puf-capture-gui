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
            end_index=2,
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
        self.assertEqual(len(jobs), 20)  # 10 LDIST cases * 2 captures
        self.assertIn("FF & MUX Step 1 / 10", jobs[0][0])

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

from __future__ import annotations

import unittest

from ui.services.config_mapper import parse_realterm_config


class ConfigMapperTests(unittest.TestCase):
    def test_ldist_label_maps_to_correct_case(self) -> None:
        cfg = parse_realterm_config(
            base_name="FPGA7_BASE",
            naming_mode="scheme3",
            fpga_index_raw="7",
            end_fpga_index_raw="7",
            start_index_raw="1",
            end_index_raw="2",
            com_port_raw="COM3",
            com_label_to_port={},
            baud_raw="115200",
            save_dir=".",
            auto_delay_raw="0",
            flipflop_position="DFF",
            mdist_value_raw="8",
            mux_pair_raw="M0-M7",
            ff_loop_fixed_mux=False,
            mdist_loop_fixed_mux=False,
            ldist_case_raw="DLUTA + ALUTB, LDIST6",
            ldist_loop=False,
        )
        self.assertEqual(cfg.ldist_case_id, 1)
        self.assertEqual((cfg.ldist_lut_a, cfg.ldist_lut_b, cfg.ldist_distance), ("DLUTA", "ALUTB", 6))

    def test_scheme4_coerces_indices_and_preserves_fpga_range(self) -> None:
        cfg = parse_realterm_config(
            base_name="BASE",
            naming_mode="scheme4",
            fpga_index_raw="5",
            end_fpga_index_raw="99",
            start_index_raw="10",
            end_index_raw="20",
            com_port_raw="COM3",
            com_label_to_port={},
            baud_raw="115200",
            save_dir=".",
            auto_delay_raw="0",
            flipflop_position="DFF",
            mdist_value_raw="8",
            mux_pair_raw="M0-M7",
            ff_loop_fixed_mux=False,
            mdist_loop_fixed_mux=False,
            ldist_case_raw="DLUTA + ALUTB, LDIST6",
            ldist_loop=False,
            r1_pair_suffix_raw="AAAA_1111",
            r1_loop_all_pairs=False,
        )
        self.assertEqual(cfg.file_naming_mode, "scheme4")
        self.assertEqual(cfg.fpga_index, 5)
        self.assertEqual(cfg.end_fpga_index, 99)
        self.assertEqual((cfg.start_index, cfg.end_index), (1, 1))
        self.assertEqual(cfg.r1_pair_suffix, "AAAA_1111")


if __name__ == "__main__":
    unittest.main()

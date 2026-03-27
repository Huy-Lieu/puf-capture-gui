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


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from unittest.mock import patch

from ui.services.filename_preview_service import build_preview_name


class FilenamePreviewServiceTests(unittest.TestCase):
    def test_scheme4_preview_passes_end_fpga_index_to_config(self) -> None:
        captured: list = []

        def fake_build(cfg, capture_index: int) -> str:
            captured.append((cfg, capture_index))
            return "preview.txt"

        with patch("ui.services.filename_preview_service.build_capture_filename", side_effect=fake_build):
            build_preview_name(
                naming_mode="scheme4",
                fpga_index_raw="1",
                end_fpga_index_raw="3",
                start_index_raw="1",
                end_index_raw="1",
                base_name="BASE",
                flipflop_position="DFF",
                mdist_value_raw="8",
                mux_pair_raw="M0-M7",
                ff_loop_fixed_mux=False,
                mdist_loop_fixed_mux=False,
                ldist_case_raw="DLUTA + ALUTB, LDIST6",
                ldist_loop=False,
                r1_pair_suffix_raw="1111_AAAA",
                r1_loop_all_pairs=False,
            )

        self.assertEqual(len(captured), 1)
        cfg, cap_idx = captured[0]
        self.assertEqual(cap_idx, 1)
        self.assertEqual(cfg.file_naming_mode, "scheme4")
        self.assertEqual(cfg.fpga_index, 1)
        self.assertEqual(cfg.end_fpga_index, 3)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from unittest.mock import patch

from ui.services.vivado_runner import VivadoRunConfig, build_vivado_command, start_vivado_batch


class VivadoRunnerTests(unittest.TestCase):
    def test_build_vivado_command_contains_expected_arguments(self) -> None:
        cfg = VivadoRunConfig(
            vivado_bat_path=r"C:\Xilinx\Vivado\bin\vivado.bat",
            project_path=r"D:\proj\design.xpr",
            tcl_path=r"D:\proj\run_impl.tcl",
        )

        cmd = build_vivado_command(cfg)

        self.assertEqual(
            cmd,
            [
                r"C:\Xilinx\Vivado\bin\vivado.bat",
                "-mode",
                "batch",
                "-source",
                r"D:\proj\run_impl.tcl",
                "-tclargs",
                r"D:\proj\design.xpr",
            ],
        )

    def test_start_vivado_batch_invokes_subprocess_with_command(self) -> None:
        cfg = VivadoRunConfig(
            vivado_bat_path="vivado.bat",
            project_path="design.xpr",
            tcl_path="run.tcl",
        )
        with patch("ui.services.vivado_runner.subprocess.Popen") as popen:
            start_vivado_batch(cfg)
        popen.assert_called_once_with(
            [
                "vivado.bat",
                "-mode",
                "batch",
                "-source",
                "run.tcl",
                "-tclargs",
                "design.xpr",
            ]
        )


if __name__ == "__main__":
    unittest.main()

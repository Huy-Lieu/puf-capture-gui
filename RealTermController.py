from __future__ import annotations

from CaptureRunner import run_capture
from RealTermClient import connect_realterm, disconnect_realterm
from RealTermNaming import build_capture_filename
from RealTermTypes import FileNamingMode, RealTermConfig
from RealTermValidation import validate_config


def main() -> None:
    # Defaults preserved for CLI usage; the GUI will pass its own config.
    cfg = RealTermConfig(
        base_name="FPGA7_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_",
        start_index=1,
        end_index=100,
        file_naming_mode="scheme1",
        fpga_index=7,
        end_fpga_index=7,
        flipflop_position="CFF",
        com_port=3,
        extension=".txt",
        save_dir=r"D:\All_SelfLearning\Prj\1_\PUF_Experimental_Results\Full_Test\InitialValues\Test\Raw",
        auto_delay_s=5.0,
        baud=115200,
    )

    try:
        run_capture(cfg)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
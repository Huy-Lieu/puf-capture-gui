from __future__ import annotations

from dataclasses import dataclass

from RealTermNaming import get_ldist_case_ids_ordered, get_ldist_case_label
from ui.views.capture_form import CaptureForm


@dataclass(frozen=True)
class AppDefaults:
    base_name: str = "FPGA7_LDIST6_DLUTA_ALUTB_MDIST8_M0_M7_CFF_R1_"
    naming_mode: str = "scheme1"
    fpga_index: str = "7"
    end_fpga_index: str = "7"
    start_index: str = "1"
    end_index: str = "100"
    com_port: str = "3"
    baud: str = "115200"
    save_dir: str = (
        r"D:\All_SelfLearning\Prj\1_\PUF_Experimental_Results\Full_Test\InitialValues\Test\Raw"
    )
    auto_delay: str = "5"
    flipflop_position: str = "DFF"
    mdist_value: str = "8"
    loop_ff_only: bool = True
    loop_mdist_only: bool = False
    loop_ldist_only: bool = False


def apply_defaults(form: CaptureForm, defaults: AppDefaults | None = None) -> None:
    d = defaults or AppDefaults()
    form.var_base_name.set(d.base_name)
    form.var_file_naming_mode.set(d.naming_mode)
    form.var_fpga_index.set(d.fpga_index)
    form.var_end_fpga_index.set(d.end_fpga_index)
    form.var_start_index.set(d.start_index)
    form.var_end_index.set(d.end_index)
    form.var_com_port.set(d.com_port)
    form.var_baud.set(d.baud)
    form.var_save_dir.set(d.save_dir)
    form.var_auto_delay.set(d.auto_delay)
    form.var_flipflop_position.set(d.flipflop_position)
    form.var_mdist_value.set(d.mdist_value)
    form.var_loop_ff_only.set(d.loop_ff_only)
    form.var_loop_mdist_only.set(d.loop_mdist_only)
    form.var_ldist_case.set(get_ldist_case_label(get_ldist_case_ids_ordered()[0]))
    form.var_loop_ldist_only.set(d.loop_ldist_only)

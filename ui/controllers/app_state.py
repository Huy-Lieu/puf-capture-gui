from __future__ import annotations

from dataclasses import dataclass

from RealTermNaming import R1_INIT_PAIR_SUFFIXES, get_ldist_case_ids_ordered, get_ldist_case_label
from ui.views.capture_form import CaptureForm


@dataclass(frozen=True)
class AppDefaults:
    base_name: str = ""
    top_mode: str = "reliability"
    enable_ff_mux: bool = True
    enable_init_values: bool = False
    fpga_id: str = "7"
    fpga_index: str = "7"
    end_fpga_index: str = "7"
    start_index: str = "1"
    end_index: str = "100"
    com_port: str = "3"
    baud: str = "115200"
    save_dir: str = (
        r"D:\All_SelfLearning\Prj\1_\PUF_Experimental_Results\Full_Test\InitialValues\Test\Raw"
    )
    vivado_bat_path: str = "C:/Xilinx/Vivado/2019.1/bin/vivado.bat"
    vivado_project_path: str = ""
    vivado_tcl_bitstream: str = ""
    vivado_bitstream_generate_name: str = ""
    vivado_bitstream_program: str = ""
    vivado_tcl_program: str = ""
    auto_delay: str = "5"
    flipflop_position: str = "DFF"
    mdist_value: str = "8"
    loop_ff_only: bool = False
    loop_mdist_only: bool = False
    loop_ldist_only: bool = False
    loop_initial_values: bool = False


def apply_defaults(form: CaptureForm, defaults: AppDefaults | None = None) -> None:
    d = defaults or AppDefaults()
    form.var_base_name.set(d.base_name)
    form.var_top_mode.set(d.top_mode)
    form.var_enable_ff_mux.set(d.enable_ff_mux)
    form.var_enable_init_values.set(d.enable_init_values)
    form.var_fpga_id.set(d.fpga_id)
    form.var_fpga_index.set(d.fpga_index)
    form.var_end_fpga_index.set(d.end_fpga_index)
    form.var_start_index.set(d.start_index)
    form.var_end_index.set(d.end_index)
    form.var_com_port.set(d.com_port)
    form.var_baud.set(d.baud)
    form.var_save_dir.set(d.save_dir)
    form.var_vivado_bat_path.set(d.vivado_bat_path)
    form.var_vivado_project_path.set(d.vivado_project_path)
    form.var_vivado_tcl_bitstream.set(d.vivado_tcl_bitstream)
    form.var_vivado_bitstream_generate_name.set(d.vivado_bitstream_generate_name)
    form.var_vivado_bitstream_program.set(d.vivado_bitstream_program)
    form.var_vivado_tcl_program.set(d.vivado_tcl_program)
    form.var_auto_delay.set(d.auto_delay)
    form.var_flipflop_position.set(d.flipflop_position)
    form.var_mdist_value.set(d.mdist_value)
    form.var_loop_ff_only.set(d.loop_ff_only)
    form.var_loop_mdist_only.set(d.loop_mdist_only)
    form.var_r1_loop_all_pairs.set(d.loop_initial_values)
    form.var_ldist_case.set(get_ldist_case_label(get_ldist_case_ids_ordered()[0]))
    form.var_loop_ldist_only.set(d.loop_ldist_only)
    form.var_r1_pair_suffix.set(R1_INIT_PAIR_SUFFIXES[0])

    # Keep the computed file naming mode synchronized with the top-mode / sub-section selection
    # so downstream callers reading var_file_naming_mode see a consistent default.
    form.var_file_naming_mode.set(form.effective_naming_mode())

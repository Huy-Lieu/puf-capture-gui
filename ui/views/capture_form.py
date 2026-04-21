from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable

from RealTermNaming import R1_INIT_PAIR_SUFFIXES, get_ldist_case_ids_ordered, get_ldist_case_label


@dataclass
class CaptureForm:
    var_base_name: tk.StringVar
    var_start_index: tk.StringVar
    var_end_index: tk.StringVar
    var_file_naming_mode: tk.StringVar
    var_fpga_index: tk.StringVar
    var_end_fpga_index: tk.StringVar
    var_com_port: tk.StringVar
    var_baud: tk.StringVar
    var_save_dir: tk.StringVar
    var_vivado_bat_path: tk.StringVar
    var_vivado_project_path: tk.StringVar
    var_vivado_tcl_bitstream: tk.StringVar
    var_vivado_bitstream_generate_name: tk.StringVar
    var_vivado_bitstream_program: tk.StringVar
    var_vivado_tcl_program: tk.StringVar
    var_auto_delay: tk.StringVar
    var_filename_preview: tk.StringVar
    var_flipflop_position: tk.StringVar
    var_mdist_value: tk.StringVar
    var_mux_pair: tk.StringVar
    var_loop_ff_only: tk.BooleanVar
    var_loop_mdist_only: tk.BooleanVar
    var_loop_ldist_only: tk.BooleanVar
    var_ldist_case: tk.StringVar
    var_r1_pair_suffix: tk.StringVar
    var_r1_loop_all_pairs: tk.BooleanVar
    entry_fpga_index: ttk.Entry
    entry_end_fpga_index: ttk.Entry
    entry_start_index: ttk.Entry
    entry_end_index: ttk.Entry
    cmb_flipflop_position: ttk.Combobox
    cmb_mdist_value: ttk.Combobox
    cmb_mux_pair: ttk.Combobox
    cmb_ldist_case: ttk.Combobox
    cmb_r1_pair: ttk.Combobox
    chk_loop_ff_only: ttk.Checkbutton
    chk_loop_mdist_only: ttk.Checkbutton
    chk_loop_ldist_only: ttk.Checkbutton
    chk_r1_loop_all_pairs: ttk.Checkbutton
    cmb_com_port: ttk.Combobox
    lbl_base_name: ttk.Label
    entry_base_name: ttk.Entry

    def apply_naming_mode_ui(self) -> None:
        mode = self.var_file_naming_mode.get()
        is_scheme3 = mode == "scheme3"
        is_scheme4 = mode == "scheme4"
        loop_ff = bool(self.var_loop_ff_only.get())
        loop_mdist = bool(self.var_loop_mdist_only.get())
        loop_ldist = bool(self.var_loop_ldist_only.get())

        if is_scheme3 or is_scheme4:
            self.entry_start_index.configure(state=tk.DISABLED)
            self.entry_end_index.configure(state=tk.DISABLED)
            self.entry_end_fpga_index.configure(state=tk.NORMAL)
            self.chk_r1_loop_all_pairs.configure(state=tk.NORMAL)
            if bool(self.var_r1_loop_all_pairs.get()):
                self.cmb_r1_pair.configure(state=tk.DISABLED)
            else:
                self.cmb_r1_pair.configure(state="readonly")
        else:
            self.entry_start_index.configure(state=tk.NORMAL)
            self.entry_end_index.configure(state=tk.NORMAL)
            self.entry_end_fpga_index.configure(state=tk.NORMAL)
            self.cmb_r1_pair.configure(state=tk.DISABLED)
            self.chk_r1_loop_all_pairs.configure(state=tk.DISABLED)

        mdist_state = "readonly" if (is_scheme3 and not loop_mdist) else tk.DISABLED
        ff_state = "readonly" if (is_scheme3 and not loop_ff) else tk.DISABLED
        ldist_state = "readonly" if (is_scheme3 and not loop_ldist) else tk.DISABLED
        self.cmb_flipflop_position.configure(state=ff_state)
        self.cmb_mdist_value.configure(state=mdist_state)
        self.cmb_mux_pair.configure(state=mdist_state)
        self.chk_loop_ff_only.configure(state=tk.NORMAL if is_scheme3 else tk.DISABLED)
        self.chk_loop_mdist_only.configure(state=tk.NORMAL if is_scheme3 else tk.DISABLED)
        self.chk_loop_ldist_only.configure(state=tk.NORMAL if is_scheme3 else tk.DISABLED)
        self.cmb_ldist_case.configure(state=ldist_state)
        if is_scheme3:
            self.lbl_base_name.grid_remove()
            self.entry_base_name.grid_remove()
        else:
            self.lbl_base_name.grid()
            self.entry_base_name.grid()


def build_capture_form(
    parent: ttk.Frame,
    *,
    on_naming_mode_changed: Callable[[], None],
    on_refresh_com_ports: Callable[[], None],
    on_browse_dir: Callable[[], None],
) -> CaptureForm:
    var_base_name = tk.StringVar()
    var_start_index = tk.StringVar()
    var_end_index = tk.StringVar()
    var_file_naming_mode = tk.StringVar(value="scheme1")
    var_fpga_index = tk.StringVar()
    var_end_fpga_index = tk.StringVar()
    var_com_port = tk.StringVar()
    var_baud = tk.StringVar()
    var_save_dir = tk.StringVar()
    var_vivado_bat_path = tk.StringVar()
    var_vivado_project_path = tk.StringVar()
    var_vivado_tcl_bitstream = tk.StringVar()
    var_vivado_bitstream_generate_name = tk.StringVar()
    var_vivado_bitstream_program = tk.StringVar()
    var_vivado_tcl_program = tk.StringVar()
    var_auto_delay = tk.StringVar()
    var_filename_preview = tk.StringVar(value="(set fields to preview filename)")
    var_flipflop_position = tk.StringVar(value="DFF")
    var_mdist_value = tk.StringVar(value="8")
    var_mux_pair = tk.StringVar(value="M0-M7")
    var_loop_ff_only = tk.BooleanVar(value=False)
    var_loop_mdist_only = tk.BooleanVar(value=False)
    var_loop_ldist_only = tk.BooleanVar(value=False)
    var_ldist_case = tk.StringVar(value=get_ldist_case_label(1))
    var_r1_pair_suffix = tk.StringVar(value=R1_INIT_PAIR_SUFFIXES[0])
    var_r1_loop_all_pairs = tk.BooleanVar(value=False)

    row = 0
    ttk.Label(parent, text="Name mode").grid(row=row, column=0, sticky="w", pady=4)
    naming_row = ttk.Frame(parent)
    naming_row.grid(row=row, column=1, sticky="w", pady=4)
    ttk.Radiobutton(
        naming_row,
        text="Reliability (N captures)",
        variable=var_file_naming_mode,
        value="scheme1",
        command=on_naming_mode_changed,
    ).grid(row=0, column=0, padx=(0, 8))
    ttk.Radiobutton(
        naming_row,
        text="FF & MUX",
        variable=var_file_naming_mode,
        value="scheme3",
        command=on_naming_mode_changed,
    ).grid(row=0, column=1, padx=(8, 8))
    ttk.Radiobutton(
        naming_row,
        text="Initial Values",
        variable=var_file_naming_mode,
        value="scheme4",
        command=on_naming_mode_changed,
    ).grid(row=0, column=2, padx=(8, 0))
    row += 1

    ttk.Label(parent, text="FPGA index").grid(row=row, column=0, sticky="w", pady=4)
    entry_fpga_index = ttk.Entry(parent, textvariable=var_fpga_index, width=12)
    entry_fpga_index.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    ttk.Label(parent, text="End FPGA index").grid(row=row, column=0, sticky="w", pady=4)
    entry_end_fpga_index = ttk.Entry(parent, textvariable=var_end_fpga_index, width=12)
    entry_end_fpga_index.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    lbl_base_name = ttk.Label(parent, text="Base name template")
    lbl_base_name.grid(row=row, column=0, sticky="w", pady=4)
    entry_base_name = ttk.Entry(parent, textvariable=var_base_name)
    entry_base_name.grid(row=row, column=1, sticky="ew", pady=4)
    row += 1

    ttk.Label(parent, text="Start index").grid(row=row, column=0, sticky="w", pady=4)
    entry_start_index = ttk.Entry(parent, textvariable=var_start_index, width=12)
    entry_start_index.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    ttk.Label(parent, text="End index").grid(row=row, column=0, sticky="w", pady=4)
    entry_end_index = ttk.Entry(parent, textvariable=var_end_index, width=12)
    entry_end_index.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    ttk.Label(parent, text="COM port").grid(row=row, column=0, sticky="w", pady=4)
    com_row = ttk.Frame(parent)
    com_row.grid(row=row, column=1, sticky="w", pady=4)
    cmb_com_port = ttk.Combobox(com_row, textvariable=var_com_port, width=12, state="normal")
    cmb_com_port.grid(row=0, column=0)
    ttk.Button(com_row, text="Refresh", command=on_refresh_com_ports).grid(
        row=0, column=1, padx=(8, 0)
    )
    row += 1

    ttk.Label(parent, text="Baud rate").grid(row=row, column=0, sticky="w", pady=4)
    ttk.Entry(parent, textvariable=var_baud, width=12).grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    ttk.Label(parent, text="Result directory").grid(row=row, column=0, sticky="w", pady=4)
    save_row = ttk.Frame(parent)
    save_row.grid(row=row, column=1, sticky="ew", pady=4)
    save_row.columnconfigure(0, weight=1)
    ttk.Entry(save_row, textvariable=var_save_dir).grid(row=0, column=0, sticky="ew")
    ttk.Button(save_row, text="Browse…", command=on_browse_dir).grid(
        row=0, column=1, padx=(8, 0)
    )
    row += 1

    ttk.Label(parent, text="Auto delay (s)").grid(row=row, column=0, sticky="w", pady=4)
    ttk.Entry(parent, textvariable=var_auto_delay, width=12).grid(
        row=row, column=1, sticky="w", pady=4
    )
    row += 1

    ttk.Label(parent, text="Flip-flop position").grid(row=row, column=0, sticky="w", pady=4)
    cmb_flipflop_position = ttk.Combobox(
        parent,
        textvariable=var_flipflop_position,
        width=12,
        state=tk.DISABLED,
        values=("DFF", "CFF", "BFF", "AFF"),
    )
    cmb_flipflop_position.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    ttk.Label(parent, text="MDIST / MUX pair").grid(row=row, column=0, sticky="w", pady=4)
    mdist_mux_row = ttk.Frame(parent)
    mdist_mux_row.grid(row=row, column=1, sticky="w", pady=4)
    ttk.Label(mdist_mux_row, text="MDIST").grid(row=0, column=0, sticky="w")
    cmb_mdist_value = ttk.Combobox(
        mdist_mux_row,
        textvariable=var_mdist_value,
        width=10,
        state=tk.DISABLED,
        values=("8", "7", "6", "5", "4", "3", "2"),
    )
    cmb_mdist_value.grid(row=0, column=1, sticky="w", padx=(6, 10))
    ttk.Label(mdist_mux_row, text="MUX").grid(row=0, column=2, sticky="w")
    cmb_mux_pair = ttk.Combobox(
        mdist_mux_row,
        textvariable=var_mux_pair,
        width=14,
        state=tk.DISABLED,
        values=("M0-M7",),
    )
    cmb_mux_pair.grid(row=0, column=3, sticky="w", padx=(6, 0))
    row += 1
    ttk.Label(parent, text="LDIST case").grid(row=row, column=0, sticky="w", pady=4)
    cmb_ldist_case = ttk.Combobox(
        parent,
        textvariable=var_ldist_case,
        width=30,
        state=tk.DISABLED,
        values=tuple(get_ldist_case_label(i) for i in get_ldist_case_ids_ordered()),
    )
    cmb_ldist_case.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    chk_loop_ff_only = ttk.Checkbutton(
        parent,
        text="Auto-loop FF positions (DFF -> CFF -> BFF -> AFF)",
        variable=var_loop_ff_only,
        onvalue=True,
        offvalue=False,
        state=tk.DISABLED,
        command=on_naming_mode_changed,
    )
    chk_loop_ff_only.grid(row=row, column=1, sticky="w", pady=4)
    row += 1
    chk_loop_mdist_only = ttk.Checkbutton(
        parent,
        text="Auto-loop MDIST and mapped MUX pairs (8 -> 2)",
        variable=var_loop_mdist_only,
        onvalue=True,
        offvalue=False,
        state=tk.DISABLED,
        command=on_naming_mode_changed,
    )
    chk_loop_mdist_only.grid(row=row, column=1, sticky="w", pady=4)
    row += 1
    chk_loop_ldist_only = ttk.Checkbutton(
        parent,
        text="Auto-loop LDIST cases",
        variable=var_loop_ldist_only,
        onvalue=True,
        offvalue=False,
        state=tk.DISABLED,
        command=on_naming_mode_changed,
    )
    chk_loop_ldist_only.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    ttk.Label(parent, text="Inital Values").grid(row=row, column=0, sticky="w", pady=4)
    cmb_r1_pair = ttk.Combobox(
        parent,
        textvariable=var_r1_pair_suffix,
        width=22,
        state=tk.DISABLED,
        values=R1_INIT_PAIR_SUFFIXES,
    )
    cmb_r1_pair.grid(row=row, column=1, sticky="w", pady=4)
    row += 1
    chk_r1_loop_all_pairs = ttk.Checkbutton(
        parent,
        text="Auto-loop all initial values (12 captures)",
        variable=var_r1_loop_all_pairs,
        onvalue=True,
        offvalue=False,
        state=tk.DISABLED,
        command=on_naming_mode_changed,
    )
    chk_r1_loop_all_pairs.grid(row=row, column=1, sticky="w", pady=4)
    row += 1

    ttk.Label(parent, text="File Name Preview:").grid(row=row, column=0, sticky="nw", pady=4)
    ttk.Label(
        parent,
        textvariable=var_filename_preview,
        wraplength=360,
        justify=tk.LEFT,
    ).grid(row=row, column=1, sticky="w", pady=4)

    return CaptureForm(
        var_base_name=var_base_name,
        var_start_index=var_start_index,
        var_end_index=var_end_index,
        var_file_naming_mode=var_file_naming_mode,
        var_fpga_index=var_fpga_index,
        var_end_fpga_index=var_end_fpga_index,
        var_com_port=var_com_port,
        var_baud=var_baud,
        var_save_dir=var_save_dir,
        var_vivado_bat_path=var_vivado_bat_path,
        var_vivado_project_path=var_vivado_project_path,
        var_vivado_tcl_bitstream=var_vivado_tcl_bitstream,
        var_vivado_bitstream_generate_name=var_vivado_bitstream_generate_name,
        var_vivado_bitstream_program=var_vivado_bitstream_program,
        var_vivado_tcl_program=var_vivado_tcl_program,
        var_auto_delay=var_auto_delay,
        var_filename_preview=var_filename_preview,
        var_flipflop_position=var_flipflop_position,
        var_mdist_value=var_mdist_value,
        var_mux_pair=var_mux_pair,
        var_loop_ff_only=var_loop_ff_only,
        var_loop_mdist_only=var_loop_mdist_only,
        var_loop_ldist_only=var_loop_ldist_only,
        var_ldist_case=var_ldist_case,
        var_r1_pair_suffix=var_r1_pair_suffix,
        var_r1_loop_all_pairs=var_r1_loop_all_pairs,
        entry_fpga_index=entry_fpga_index,
        entry_end_fpga_index=entry_end_fpga_index,
        entry_start_index=entry_start_index,
        entry_end_index=entry_end_index,
        cmb_flipflop_position=cmb_flipflop_position,
        cmb_mdist_value=cmb_mdist_value,
        cmb_mux_pair=cmb_mux_pair,
        cmb_ldist_case=cmb_ldist_case,
        cmb_r1_pair=cmb_r1_pair,
        chk_loop_ff_only=chk_loop_ff_only,
        chk_loop_mdist_only=chk_loop_mdist_only,
        chk_loop_ldist_only=chk_loop_ldist_only,
        chk_r1_loop_all_pairs=chk_r1_loop_all_pairs,
        cmb_com_port=cmb_com_port,
        lbl_base_name=lbl_base_name,
        entry_base_name=entry_base_name,
    )

from __future__ import annotations

from dataclasses import dataclass
from tkinter import ttk
from typing import Callable

from ui.views.capture_form import CaptureForm


@dataclass
class VivadoPanelWidgets:
    btn_generate_bitstream: ttk.Button
    btn_program_device: ttk.Button


def build_vivado_configuration(
    parent: ttk.Frame,
    form: CaptureForm,
    *,
    on_browse_bat: Callable[[], None],
    on_browse_project: Callable[[], None],
    on_browse_tcl_bitstream: Callable[[], None],
    on_browse_bitstream_program: Callable[[], None],
    on_browse_tcl_program: Callable[[], None],
    on_run_bitstream: Callable[[], None],
    on_run_program: Callable[[], None],
) -> VivadoPanelWidgets:
    parent.columnconfigure(1, weight=1)
    row = 0

    ttk.Label(parent, text="Vivado bat path").grid(row=row, column=0, sticky="w", pady=4)
    bat_row = ttk.Frame(parent)
    bat_row.grid(row=row, column=1, columnspan=2, sticky="ew", pady=4)
    bat_row.columnconfigure(0, weight=1)
    ttk.Entry(bat_row, textvariable=form.var_vivado_bat_path).grid(row=0, column=0, sticky="ew")
    ttk.Button(bat_row, text="Browse…", command=on_browse_bat).grid(row=0, column=1, padx=(8, 0))
    row += 1

    ttk.Label(parent, text="Vivado project (.xpr)").grid(row=row, column=0, sticky="w", pady=4)
    proj_row = ttk.Frame(parent)
    proj_row.grid(row=row, column=1, columnspan=2, sticky="ew", pady=4)
    proj_row.columnconfigure(0, weight=1)
    ttk.Entry(proj_row, textvariable=form.var_vivado_project_path).grid(
        row=0, column=0, sticky="ew"
    )
    ttk.Button(proj_row, text="Browse…", command=on_browse_project).grid(
        row=0, column=1, padx=(8, 0)
    )
    row += 1

    ttk.Label(parent, text="Generate Bitstream TCL").grid(row=row, column=0, sticky="w", pady=4)
    bs_row = ttk.Frame(parent)
    bs_row.grid(row=row, column=1, sticky="ew", pady=4)
    bs_row.columnconfigure(0, weight=1)
    ttk.Entry(bs_row, textvariable=form.var_vivado_tcl_bitstream).grid(row=0, column=0, sticky="ew")
    ttk.Button(bs_row, text="Browse…", command=on_browse_tcl_bitstream).grid(
        row=0, column=1, padx=(8, 0)
    )
    btn_generate_bitstream = ttk.Button(
        parent, text="Generate Bitstream", command=on_run_bitstream
    )
    btn_generate_bitstream.grid(row=row, column=2, sticky="ew", padx=(8, 0), pady=4)
    row += 1

    ttk.Label(parent, text="Bitstream output name (optional)").grid(
        row=row, column=0, sticky="w", pady=4
    )
    ttk.Entry(parent, textvariable=form.var_vivado_bitstream_generate_name).grid(
        row=row, column=1, columnspan=2, sticky="ew", pady=4
    )
    row += 1

    ttk.Label(parent, text="Bitstream to program (.bit)").grid(row=row, column=0, sticky="w", pady=4)
    bit_row = ttk.Frame(parent)
    bit_row.grid(row=row, column=1, columnspan=2, sticky="ew", pady=4)
    bit_row.columnconfigure(0, weight=1)
    ttk.Entry(bit_row, textvariable=form.var_vivado_bitstream_program).grid(
        row=0, column=0, sticky="ew"
    )
    ttk.Button(bit_row, text="Browse…", command=on_browse_bitstream_program).grid(
        row=0, column=1, padx=(8, 0)
    )
    row += 1

    ttk.Label(parent, text="Programming Device TCL").grid(row=row, column=0, sticky="w", pady=4)
    pr_row = ttk.Frame(parent)
    pr_row.grid(row=row, column=1, sticky="ew", pady=4)
    pr_row.columnconfigure(0, weight=1)
    ttk.Entry(pr_row, textvariable=form.var_vivado_tcl_program).grid(row=0, column=0, sticky="ew")
    ttk.Button(pr_row, text="Browse…", command=on_browse_tcl_program).grid(
        row=0, column=1, padx=(8, 0)
    )
    btn_program_device = ttk.Button(parent, text="Programming Device", command=on_run_program)
    btn_program_device.grid(row=row, column=2, sticky="ew", padx=(8, 0), pady=4)
    row += 1

    return VivadoPanelWidgets(
        btn_generate_bitstream=btn_generate_bitstream,
        btn_program_device=btn_program_device,
    )

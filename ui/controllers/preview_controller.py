from __future__ import annotations

from RealTermNaming import get_mdist_pairs
from ui.services.filename_preview_service import build_bitstream_name, build_preview_name
from ui.views.capture_form import CaptureForm


def effective_naming_mode(form) -> str:
    """Return the underlying scheme id ('scheme1', 'scheme3', 'scheme4') driven by
    the top-mode radio plus the Configurations sub-section checkboxes.

    Works against any form-like object exposing var_top_mode / var_enable_ff_mux /
    var_enable_init_values; duck-typed so unit tests can pass a SimpleNamespace.
    """
    if form.var_top_mode.get() == "reliability":
        return "scheme1"
    if bool(form.var_enable_init_values.get()):
        return "scheme4"
    return "scheme3"


class PreviewController:
    def __init__(self, form: CaptureForm) -> None:
        self._form = form

    def apply_naming_mode_ui(self) -> None:
        self._form.apply_naming_mode_ui()
        self.refresh_mdist_pairs()
        self.update_filename_preview()
        self.update_bitstream_name()

    def refresh_mdist_pairs(self) -> None:
        try:
            mdist_value = int(self._form.var_mdist_value.get().strip())
        except Exception:
            mdist_value = 8
        pairs = get_mdist_pairs(mdist_value)
        labels = [f"M{a}-M{b}" for a, b in pairs] or ["M0-M7"]
        self._form.cmb_mux_pair["values"] = labels
        if self._form.var_mux_pair.get() not in labels:
            self._form.var_mux_pair.set(labels[0])

    def _fpga_range_raw(self, mode: str) -> tuple[str, str]:
        # In Configurations modes the FPGA ID drives a single-FPGA run; in Reliability
        # we still expose the start/end range via the dedicated entries.
        if mode == "scheme1":
            return (
                self._form.var_fpga_index.get(),
                self._form.var_end_fpga_index.get(),
            )
        fpga_id = self._form.var_fpga_id.get()
        return fpga_id, fpga_id

    def update_filename_preview(self) -> None:
        try:
            mode = effective_naming_mode(self._form)
            fpga_start_raw, fpga_end_raw = self._fpga_range_raw(mode)
            preview = build_preview_name(
                naming_mode=mode,
                fpga_index_raw=fpga_start_raw,
                end_fpga_index_raw=fpga_end_raw,
                start_index_raw=self._form.var_start_index.get(),
                end_index_raw=self._form.var_end_index.get(),
                base_name=self._form.var_base_name.get(),
                flipflop_position=self._form.var_flipflop_position.get(),
                mdist_value_raw=self._form.var_mdist_value.get(),
                mux_pair_raw=self._form.var_mux_pair.get(),
                ff_loop_fixed_mux=self._form.var_loop_ff_only.get(),
                mdist_loop_fixed_mux=self._form.var_loop_mdist_only.get(),
                ldist_case_raw=self._form.var_ldist_case.get(),
                ldist_loop=self._form.var_loop_ldist_only.get(),
                r1_pair_suffix_raw=self._form.var_r1_pair_suffix.get(),
                r1_loop_all_pairs=self._form.var_r1_loop_all_pairs.get(),
            )
            self._form.var_filename_preview.set(preview)
        except Exception as exc:
            self._form.var_filename_preview.set(f"(invalid naming input: {exc})")

    def update_bitstream_name(self) -> None:
        if effective_naming_mode(self._form) != "scheme3":
            return
        try:
            name = build_bitstream_name(
                flipflop_position=self._form.var_flipflop_position.get(),
                mdist_value_raw=self._form.var_mdist_value.get(),
                mux_pair_raw=self._form.var_mux_pair.get(),
                ldist_case_raw=self._form.var_ldist_case.get(),
            )
            self._form.var_vivado_bitstream_generate_name.set(name)
        except Exception:
            pass

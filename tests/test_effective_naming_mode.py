from __future__ import annotations

import unittest
from types import SimpleNamespace

from ui.controllers.preview_controller import effective_naming_mode


class _Var:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


def _form(top: str, ff_mux: bool, init_values: bool) -> SimpleNamespace:
    return SimpleNamespace(
        var_top_mode=_Var(top),
        var_enable_ff_mux=_Var(ff_mux),
        var_enable_init_values=_Var(init_values),
    )


class EffectiveNamingModeTests(unittest.TestCase):
    def test_reliability_top_mode_returns_scheme1(self) -> None:
        self.assertEqual(effective_naming_mode(_form("reliability", True, False)), "scheme1")
        # Even if sub-checkbox flags are set, Reliability dominates.
        self.assertEqual(effective_naming_mode(_form("reliability", False, True)), "scheme1")

    def test_configurations_with_ff_mux_returns_scheme3(self) -> None:
        self.assertEqual(effective_naming_mode(_form("configurations", True, False)), "scheme3")

    def test_configurations_with_init_values_returns_scheme4(self) -> None:
        self.assertEqual(effective_naming_mode(_form("configurations", False, True)), "scheme4")

    def test_configurations_neither_falls_back_to_scheme3(self) -> None:
        # Defensive default while the user is between selections; read_config() still
        # raises if both checkboxes remain off at Connect/Capture time.
        self.assertEqual(effective_naming_mode(_form("configurations", False, False)), "scheme3")

    def test_init_values_takes_precedence_when_both_checked(self) -> None:
        # Mutex is enforced by the UI; this is a defensive precedence rule.
        self.assertEqual(effective_naming_mode(_form("configurations", True, True)), "scheme4")


if __name__ == "__main__":
    unittest.main()

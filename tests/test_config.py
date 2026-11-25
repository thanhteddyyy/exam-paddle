"""Tests for configuration loading, presets, and overrides."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from exam_padder.config import PresetName, load_config


def test_load_default_config() -> None:
    """Default config uses 300 DPI and the 'vua' preset across all block types."""
    cfg = load_config()
    assert cfg.dpi == 300
    assert cfg.ocr.enabled == "auto"
    assert cfg.ocr.downscale_dpi == 150
    assert cfg.input.two_column is False
    assert cfg.page.mode == "a4"
    assert cfg.slicing.snap_search_mm == 15.0
    assert cfg.padding.preset == "vua"

    per_type = cfg.padding.per_type
    assert set(per_type.keys()) == {
        "header",
        "section",
        "mcq",
        "true_false",
        "short_answer",
        "other",
    }
    assert per_type["header"].value == 0 and per_type["header"].unit == "mm"
    assert per_type["section"].value == 5 and per_type["section"].unit == "mm"
    assert per_type["mcq"].value == 2 and per_type["mcq"].unit == "lines"
    assert per_type["true_false"].value == 0.5 and per_type["true_false"].unit == "page"
    assert per_type["short_answer"].value == 0.5 and per_type["short_answer"].unit == "page"
    assert per_type["other"].value == 0 and per_type["other"].unit == "mm"


@pytest.mark.parametrize(
    ("preset", "mcq_val", "tf_val", "tf_new_page", "sa_val"),
    [
        ("gon", 1, 0.33, False, 0.33),
        ("vua", 2, 0.5, False, 0.5),
        ("rong", 4, 1, True, 0.75),
    ],
)
def test_load_presets(
    preset: PresetName,
    mcq_val: float,
    tf_val: float,
    tf_new_page: bool,
    sa_val: float,
) -> None:
    """Named presets load expected per-type values and page-break flags."""
    cfg = load_config(preset=preset)
    assert cfg.padding.preset == preset
    assert cfg.padding.per_type["mcq"].value == mcq_val
    assert cfg.padding.per_type["mcq"].unit == "lines"
    assert cfg.padding.per_type["true_false"].value == tf_val
    assert cfg.padding.per_type["true_false"].start_on_new_page is tf_new_page
    assert cfg.padding.per_type["short_answer"].value == sa_val


def test_per_type_partial_override() -> None:
    """Partial per_type override updates value while preserving unit from preset."""
    cfg = load_config(overrides={"padding": {"per_type": {"mcq": {"value": 3}}}})
    assert cfg.padding.per_type["mcq"].value == 3
    assert cfg.padding.per_type["mcq"].unit == "lines"
    assert cfg.padding.per_type["true_false"].value == 0.5


def test_question_overrides_and_user_yaml(tmp_path: Path) -> None:
    """User YAML config merges cleanly and supports per-question overrides."""
    user_yaml = tmp_path / "custom.yaml"
    user_yaml.write_text(
        """
dpi: 300
padding:
  preset: gon
  overrides:
    III-4:
      value: 1
      unit: page
      start_on_new_page: true
""".strip(),
        encoding="utf-8",
    )
    cfg = load_config(config_path=user_yaml)
    assert cfg.padding.preset == "gon"
    assert cfg.padding.per_type["mcq"].value == 1
    assert cfg.padding.overrides["III-4"].value == 1
    assert cfg.padding.overrides["III-4"].unit == "page"
    assert cfg.padding.overrides["III-4"].start_on_new_page is True


def test_invalid_preset_and_values() -> None:
    """Unknown preset, negative padding, and unknown fields raise validation errors."""
    with pytest.raises(ValueError, match="Unknown preset"):
        load_config(preset="invalid")  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        load_config(overrides={"padding": {"per_type": {"mcq": {"value": -1}}}})

    with pytest.raises(ValidationError):
        load_config(overrides={"unknown_top_key": True})

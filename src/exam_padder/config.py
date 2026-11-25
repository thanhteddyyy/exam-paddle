"""Configuration models and YAML/preset loader for Exam Padder."""

from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

BlockType = Literal["header", "section", "mcq", "true_false", "short_answer", "other"]
PaddingUnit = Literal["mm", "lines", "page"]
PresetName = Literal["gon", "vua", "rong", "custom"]
OcrMode = Literal["auto", "always", "never"]
DeskewMode = Literal["auto"] | bool
PageMode = Literal["a4", "continuous"]

DEFAULT_CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"
VALID_PRESETS: tuple[str, ...] = ("gon", "vua", "rong", "custom")


class PaddingRule(BaseModel):
    """Whitespace rule applied after a block."""

    model_config = ConfigDict(extra="forbid")

    value: float = Field(ge=0)
    unit: PaddingUnit
    start_on_new_page: bool = False


class OcrConfig(BaseModel):
    """OCR fallback settings."""

    model_config = ConfigDict(extra="forbid")

    enabled: OcrMode = "auto"
    downscale_dpi: int = Field(default=150, gt=0)
    lang: str = "vi"


class InputConfig(BaseModel):
    """Input preprocessing and layout hints."""

    model_config = ConfigDict(extra="forbid")

    two_column: bool = False
    deskew: DeskewMode = "auto"
    whiten_background: bool = False


class PageConfig(BaseModel):
    """Output page geometry settings."""

    model_config = ConfigDict(extra="forbid")

    mode: PageMode = "a4"
    margin_top_mm: float = Field(default=10.0, ge=0)
    margin_bottom_mm: float = Field(default=10.0, ge=0)
    fit_width: bool = False
    allow_split_tall_block: bool = True


class SlicingConfig(BaseModel):
    """Block slicing and whitespace snapping settings."""

    model_config = ConfigDict(extra="forbid")

    snap_search_mm: float = Field(default=15.0, ge=0)
    ink_threshold: float = Field(default=0.002, ge=0.0, le=1.0)
    trim_keep_mm: float = Field(default=1.5, ge=0)
    question_left_margin_tolerance: float = Field(default=0.04, ge=0.0, le=1.0)


class PaddingConfig(BaseModel):
    """Padding preset, line spacing, and overrides."""

    model_config = ConfigDict(extra="forbid")

    preset: PresetName = "vua"
    line_spacing_factor: float = Field(default=1.5, gt=0)
    fallback_line_height_mm: float = Field(default=7.0, gt=0)
    per_type: dict[BlockType, PaddingRule] = Field(default_factory=dict)
    overrides: dict[str, PaddingRule] = Field(default_factory=dict)


class AppConfig(BaseModel):
    """Top-level application configuration."""

    model_config = ConfigDict(extra="forbid")

    dpi: int = Field(default=300, gt=0)
    ocr: OcrConfig = Field(default_factory=OcrConfig)
    input: InputConfig = Field(default_factory=InputConfig)
    page: PageConfig = Field(default_factory=PageConfig)
    slicing: SlicingConfig = Field(default_factory=SlicingConfig)
    padding: PaddingConfig = Field(default_factory=PaddingConfig)


def _read_yaml_dict(path: Path) -> dict[str, Any]:
    """Read a YAML file and ensure its top-level value is a mapping."""
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}, got {type(data).__name__}")
    return data


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge two dictionaries without mutating inputs."""
    merged = deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def load_preset_dict(preset_name: str, config_dir: Path | None = None) -> dict[str, Any]:
    """Load per-type padding rules for a named preset."""
    if preset_name not in VALID_PRESETS:
        raise ValueError(f"Unknown preset '{preset_name}'. Expected one of {VALID_PRESETS}.")
    resolved_name = "vua" if preset_name == "custom" else preset_name
    cfg_dir = config_dir or DEFAULT_CONFIG_DIR
    preset_path = cfg_dir / "presets" / f"{resolved_name}.yaml"
    return _read_yaml_dict(preset_path)


def load_config(
    config_path: Path | None = None,
    preset: PresetName | None = None,
    overrides: dict[str, Any] | None = None,
    config_dir: Path | None = None,
) -> AppConfig:
    """Load default config, merge user YAML/overrides and preset rules, and validate."""
    cfg_dir = config_dir or DEFAULT_CONFIG_DIR
    raw = _read_yaml_dict(cfg_dir / "default.yaml")

    if config_path is not None:
        raw = _deep_merge(raw, _read_yaml_dict(config_path))
    if overrides is not None:
        raw = _deep_merge(raw, overrides)

    padding_section = raw.setdefault("padding", {})
    if not isinstance(padding_section, dict):
        raise ValueError("'padding' section in config must be a mapping.")

    if preset is not None:
        padding_section["preset"] = preset

    preset_name = padding_section.get("preset", "vua")
    if not isinstance(preset_name, str):
        raise ValueError("'padding.preset' must be a string.")

    base_per_type = load_preset_dict(preset_name, config_dir=cfg_dir)
    user_per_type = padding_section.get("per_type") or {}
    if not isinstance(user_per_type, dict):
        raise ValueError("'padding.per_type' must be a mapping.")

    padding_section["per_type"] = _deep_merge(base_per_type, user_per_type)
    logger.debug("Loaded configuration with preset=%s", preset_name)
    return AppConfig.model_validate(raw)

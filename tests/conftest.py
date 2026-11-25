"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.fixtures.make_synthetic_pdf import create_synthetic_exam_pdf


@pytest.fixture
def synthetic_pdf_path(tmp_path: Path) -> Path:
    """Create a fresh synthetic exam PDF in a temporary directory."""
    return create_synthetic_exam_pdf(tmp_path / "synthetic_exam.pdf")

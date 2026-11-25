"""Tests for the synthetic Vietnamese Math exam PDF fixture."""

from __future__ import annotations

import re
from pathlib import Path

import pymupdf

from tests.fixtures.make_synthetic_pdf import A4_HEIGHT_PT, A4_WIDTH_PT


def _norm_ws(text: str) -> str:
    """Collapse any Unicode whitespace (including NBSP) to regular spaces."""
    return re.sub(r"\s+", " ", text)


def test_synthetic_pdf_structure_and_text(synthetic_pdf_path: Path) -> None:
    """Synthetic PDF has 2 A4 pages, rich text layer, Vietnamese diacritics, and key markers."""
    assert synthetic_pdf_path.is_file()
    doc = pymupdf.open(synthetic_pdf_path)
    try:
        assert doc.page_count == 2
        pages_text = []
        for page in doc:
            assert abs(page.rect.width - A4_WIDTH_PT) < 1.0
            assert abs(page.rect.height - A4_HEIGHT_PT) < 1.0
            words = page.get_text("words")
            assert len(words) > 20
            pages_text.append(_norm_ws(page.get_text("text")))
    finally:
        doc.close()

    p1, p2 = pages_text
    assert "BỘ GIÁO DỤC VÀ ĐÀO TẠO" in p1
    assert "PHẦN I." in p1
    assert "PHẦN II." in p1
    assert "PHẦN III." in p1
    assert "Thí sinh trả lời từ câu 1 đến câu 12" in p1
    assert "Câu 1." in p1
    assert "Câu 3." in p1
    assert "a)" in p1 and "d)" in p1
    assert "Trang 1/2" in p1 and "Mã đề thi 0101" in p1

    assert "Câu 2." in p2
    assert "HẾT" in p2
    assert "Trang 2/2" in p2 and "Mã đề thi 0101" in p2

"""Generate a synthetic Vietnamese high-school Math exam PDF for testing."""

from __future__ import annotations

import argparse
from pathlib import Path

import pymupdf

A4_WIDTH_PT = 595.28
A4_HEIGHT_PT = 841.89
LEFT_MARGIN_X = 56.0
FOOTER_Y = 805.0

FONT_CANDIDATES: list[tuple[Path, Path]] = [
    (Path(r"C:\Windows\Fonts\times.ttf"), Path(r"C:\Windows\Fonts\timesbd.ttf")),
    (Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")),
    (Path(r"C:\Windows\Fonts\segoeui.ttf"), Path(r"C:\Windows\Fonts\segoeuib.ttf")),
    (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
    ),
    (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ),
]


def _find_unicode_fonts() -> tuple[Path, Path]:
    """Find a regular and bold TTF font pair with Vietnamese Unicode coverage."""
    for regular, bold in FONT_CANDIDATES:
        if regular.is_file() and bold.is_file():
            return regular, bold
    raise FileNotFoundError("No Unicode TTF font pair found on this system for synthetic PDF.")


def _write_line(
    page: pymupdf.Page,
    x: float,
    y: float,
    text: str,
    *,
    bold: bool = False,
    fontsize: float = 11.0,
) -> float:
    """Insert one line of text and return the next y position."""
    fontname = "vnb" if bold else "vn"
    page.insert_text((x, y), text, fontname=fontname, fontsize=fontsize)
    return y + fontsize * 1.45


def _draw_page1(page: pymupdf.Page) -> None:
    """Populate page 1 with header, Part I (3 MCQs), Part II (1 T/F), and Part III start."""
    y = 48.0
    y = _write_line(page, 145, y, "BỘ GIÁO DỤC VÀ ĐÀO TẠO", bold=True, fontsize=11.5)
    y = _write_line(
        page, 118, y, "KỲ THI TỐT NGHIỆP TRUNG HỌC PHỔ THÔNG NĂM 2025", bold=True, fontsize=11.0
    )
    y = _write_line(page, 215, y, "Môn thi: TOÁN — Mã đề thi: 0101", bold=True, fontsize=11.0)
    page.draw_line((LEFT_MARGIN_X, y), (A4_WIDTH_PT - LEFT_MARGIN_X, y), width=0.8)
    y += 18.0

    y = _write_line(
        page, LEFT_MARGIN_X, y, "PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.", bold=True
    )
    y = _write_line(
        page,
        LEFT_MARGIN_X,
        y,
        "Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.",
    )
    y += 6.0

    # MCQ 1-3 with horizontal A/B/C/D options on a single row
    mcqs = [
        (
            "Câu 1. Cho hàm số f(x) = x^3 - 3x + 2. Giá trị cực đại của hàm số đã cho bằng",
            ("A. 4.", "B. 0.", "C. -1.", "D. 1."),
        ),
        (
            "Câu 2. Tập nghiệm của bất phương trình log_2(x - 1) > 3 là",
            ("A. (9; +∞).", "B. (1; 9).", "C. (7; +∞).", "D. [9; +∞)."),
        ),
        (
            "Câu 3. Trong không gian Oxyz, vectơ pháp tuyến của mặt phẳng "
            "(P): 2x - y + 3z - 1 = 0 là",
            ("A. (2; -1; 3).", "B. (2; 1; 3).", "C. (-2; -1; 3).", "D. (2; -1; -1)."),
        ),
    ]
    option_xs = (72.0, 192.0, 312.0, 432.0)
    for stem, options in mcqs:
        y = _write_line(page, LEFT_MARGIN_X, y, stem)
        for opt_x, opt_text in zip(option_xs, options, strict=True):
            page.insert_text((opt_x, y), opt_text, fontname="vn", fontsize=11.0)
        y += 24.0

    # Part II
    y = _write_line(page, LEFT_MARGIN_X, y, "PHẦN II. Câu trắc nghiệm đúng sai.", bold=True)
    y = _write_line(
        page,
        LEFT_MARGIN_X,
        y,
        "Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, "
        "chọn đúng hoặc sai.",
    )
    y += 6.0
    y = _write_line(
        page,
        LEFT_MARGIN_X,
        y,
        "Câu 1. Một chất điểm chuyển động thẳng với vận tốc v(t) = 3t^2 - 6t + 4 (m/s).",
    )
    for sub in (
        "a) Gia tốc của chất điểm tại thời điểm t = 2 giây là 6 m/s^2.",
        "b) Vận tốc nhỏ nhất của chất điểm đạt được bằng 1 m/s.",
        "c) Quãng đường đi được trong 2 giây đầu tiên là 4 mét.",
        "d) Chất điểm chuyển động cùng chiều dương với mọi t >= 0.",
    ):
        y = _write_line(page, LEFT_MARGIN_X + 14.0, y, sub)

    y += 10.0
    # Part III starting near bottom of page 1, Câu 1 spans across to page 2
    y = _write_line(page, LEFT_MARGIN_X, y, "PHẦN III. Câu trắc nghiệm trả lời ngắn.", bold=True)
    y = _write_line(page, LEFT_MARGIN_X, y, "Thí sinh trả lời từ câu 1 đến câu 6.")
    y += 6.0
    y = _write_line(
        page,
        LEFT_MARGIN_X,
        y,
        "Câu 1. Cho hình chóp S.ABCD có đáy ABCD là hình vuông cạnh bằng 4, cạnh bên SA",
    )
    _write_line(
        page,
        LEFT_MARGIN_X,
        y,
        "vuông góc với mặt phẳng đáy và SA = 3 (tham khảo hình vẽ ở đầu trang sau).",
    )

    page.insert_text((210.0, FOOTER_Y), "Trang 1/2 - Mã đề thi 0101", fontname="vn", fontsize=10.0)


def _draw_page2(page: pymupdf.Page) -> None:
    """Populate page 2 with continuation of Part III Câu 1, Câu 2, HẾT, and footer."""
    y = 56.0
    y = _write_line(
        page,
        LEFT_MARGIN_X,
        y,
        "Tính khoảng cách từ điểm A đến mặt phẳng (SBD) (làm tròn đến hàng phần trăm).",
    )

    # Simple geometric diagram representing the pyramid S.ABCD
    base_y = y + 85.0
    a_pt = (130.0, base_y)
    b_pt = (100.0, base_y + 35.0)
    c_pt = (230.0, base_y + 35.0)
    d_pt = (260.0, base_y)
    s_pt = (130.0, y + 10.0)
    for p1, p2 in (
        (a_pt, b_pt),
        (b_pt, c_pt),
        (c_pt, d_pt),
        (d_pt, a_pt),
        (s_pt, a_pt),
        (s_pt, b_pt),
        (s_pt, c_pt),
        (s_pt, d_pt),
    ):
        page.draw_line(p1, p2, width=0.9)
    page.insert_text((s_pt[0] - 4, s_pt[1] - 4), "S", fontname="vnb", fontsize=10.0)
    page.insert_text((a_pt[0] - 12, a_pt[1] + 2), "A", fontname="vnb", fontsize=10.0)
    page.insert_text((b_pt[0] - 12, b_pt[1] + 8), "B", fontname="vnb", fontsize=10.0)
    page.insert_text((c_pt[0] + 4, c_pt[1] + 8), "C", fontname="vnb", fontsize=10.0)
    page.insert_text((d_pt[0] + 4, d_pt[1] + 2), "D", fontname="vnb", fontsize=10.0)

    y = base_y + 62.0
    y = _write_line(
        page,
        LEFT_MARGIN_X,
        y,
        "Câu 2. Một hộp chứa 5 viên bi đỏ và 7 viên bi xanh. Lấy ngẫu nhiên đồng thời 3 viên bi.",
    )
    y = _write_line(
        page,
        LEFT_MARGIN_X,
        y,
        "Xác suất để lấy được ít nhất 2 viên bi đỏ bằng bao nhiêu (làm tròn đến hàng phần trăm)?",
    )

    y += 28.0
    y = _write_line(page, 215.0, y, "------------ HẾT ------------", bold=True, fontsize=11.0)
    _write_line(
        page,
        92.0,
        y + 4.0,
        "Thí sinh không được sử dụng tài liệu. Cán bộ coi thi không giải thích gì thêm.",
        fontsize=10.0,
    )

    page.insert_text((210.0, FOOTER_Y), "Trang 2/2 - Mã đề thi 0101", fontname="vn", fontsize=10.0)


def create_synthetic_exam_pdf(output_path: Path) -> Path:
    """Create a 2-page A4 synthetic Vietnamese Math exam PDF at ``output_path``."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    regular_font, bold_font = _find_unicode_fonts()

    doc = pymupdf.open()
    try:
        for idx, drawer in enumerate((_draw_page1, _draw_page2)):
            page = doc.new_page(width=A4_WIDTH_PT, height=A4_HEIGHT_PT)
            page.insert_font(fontname="vn", fontfile=str(regular_font))
            page.insert_font(fontname="vnb", fontfile=str(bold_font))
            drawer(page)
            if idx not in (0, 1):
                raise RuntimeError("Unexpected page index")
        doc.save(output_path)
    finally:
        doc.close()
    return output_path


def main() -> None:
    """CLI entrypoint for generating the synthetic exam PDF."""
    parser = argparse.ArgumentParser(description="Generate synthetic Vietnamese Math exam PDF.")
    parser.add_argument(
        "output",
        nargs="?",
        default="out/synthetic_exam.pdf",
        help="Output PDF path (default: out/synthetic_exam.pdf)",
    )
    args = parser.parse_args()
    out = create_synthetic_exam_pdf(Path(args.output))
    print(f"Generated synthetic exam PDF: {out}")


if __name__ == "__main__":
    main()

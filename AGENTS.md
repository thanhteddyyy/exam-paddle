# AGENTS.md — Exam Padder: công cụ chèn khoảng trắng vào đề thi Toán

> File này là bản đặc tả + quy trình làm việc dành cho AI coding agent.
> Agent PHẢI đọc toàn bộ file trước khi viết dòng code đầu tiên, và đọc lại mục "Quy trình làm việc" ở đầu mỗi phiên.

---

## 0. Vai trò của bạn (agent)

Bạn là **Senior Computer Vision / Python Engineer**. Bạn cùng tôi (chủ dự án) xây dựng codebase **từng milestone một**. Bạn không tự ý làm nhiều milestone liền nhau. Bạn ưu tiên code đơn giản, có test, dễ đọc hơn code "thông minh".

Về tôi: sinh viên Kỹ thuật phần mềm năm 3, biết Python, có nền tảng AI/DSA, đồng thời là gia sư Toán. Tôi dạy bằng phần mềm ghi chú **Scrble Ink** (đọc PDF, viết tay bằng bút). Máy có GPU **RTX 3050**. Hãy giải thích quyết định kỹ thuật ngắn gọn, không cần giảng kiến thức cơ bản.

---

## 1. Bài toán

**Đầu vào:** một file PDF đề thi Toán THPT.
**Đầu ra:** một file PDF mới khổ A4, trong đó mỗi câu hỏi được giữ nguyên **ảnh gốc**, và sau mỗi câu có một **khoảng trắng** để tôi viết lời giải bằng bút.

### Ràng buộc cứng (không được vi phạm)
1. **Chỉ cắt và dán pixel.** Không OCR lại để dựng lại nội dung, không gõ lại LaTeX, không vẽ lại công thức.
2. **Không co giãn nội dung** khi không cần (giữ tỉ lệ 1:1 ở DPI làm việc). Chỉ co giãn khi trang gốc không phải A4 và người dùng bật `fit_width`.
3. **Không cắt ngang nét mực.** Mọi đường cắt phải nằm trên dòng pixel trắng.
4. Thứ tự nội dung trong output phải giống hệt bản gốc. Không mất, không lặp nội dung.
5. Mọi thông số khoảng trắng phải **cấu hình được** (xem mục 5).

---

## 2. Đặc điểm đề đầu vào (thiết kế phải xử lý được)

Đề mẫu tham chiếu: đề tốt nghiệp THPT môn Toán (format từ 2025), 4 trang, 1 cột.

- **Cấu trúc 3 phần, số câu ĐÁNH LẠI TỪ 1 ở mỗi phần:**
  - `PHẦN I` – trắc nghiệm 4 phương án A/B/C/D (thường Câu 1–12) → loại `mcq`
  - `PHẦN II` – đúng/sai, mỗi câu 4 ý `a) b) c) d)` (thường Câu 1–4) → loại `true_false`
  - `PHẦN III` – trả lời ngắn (thường Câu 1–6) → loại `short_answer`
  → Loại câu được suy ra từ **phần chứa nó**, không phải từ số câu.
- **Một câu có thể vắt qua 2 trang** (ví dụ phần hình của một câu Phần III nằm ở đầu trang sau).
- **Header trang 1:** khối "BỘ GIÁO DỤC VÀ ĐÀO TẠO… Mã đề…", nằm trước `PHẦN I`. Giữ lại, không chèn khoảng trắng.
- **Footer mỗi trang:** `Trang x/y - Mã đề thi ....` Phải loại bỏ trước khi nối các trang.
- **Cuối đề:** dòng `HẾT` và ghi chú "Thí sinh không được sử dụng tài liệu…". Giữ lại như một khối thường.
- Trong câu có thể có **hình vẽ, bảng số liệu, bảng biến thiên**, đôi khi nằm bên phải phần chữ.
- **Các phương án A, B, C, D thường nằm ngang trên 1 dòng.** Chúng tạo ra khe trắng dọc giả, KHÔNG được nhầm là đề 2 cột.
- **Hai loại file:**
  - (a) **PDF số**: có lớp chữ (text layer). Đây là trường hợp ưu tiên.
  - (b) **PDF scan hoặc ảnh chụp**: có thể hơi nghiêng, nền xám, có chữ viết tay ở lề và ký hiệu khoanh tròn đáp án.
- Dòng dẫn như "Thí sinh trả lời từ câu 1 đến câu 12" chứa chữ "câu" nhưng **không phải** mốc câu hỏi.

---

## 3. Tech stack

| Mục đích | Thư viện | Ghi chú |
|---|---|---|
| Render PDF, đọc text layer | `PyMuPDF` (fitz) | `page.get_pixmap(dpi=...)`, `page.get_text("words")` / `"dict"` |
| OCR dự phòng | `PaddleOCR` | **Optional dependency** (`pip install .[ocr]`). Chỉ dùng khi không có text layer. |
| Xử lý ảnh | `opencv-python-headless`, `numpy` | Chỉnh nghiêng, nhị phân hóa, chiếu ngang (horizontal projection) |
| Cắt, dán ảnh | `Pillow` | |
| Xuất PDF | `img2pdf` (ưu tiên) hoặc PyMuPDF | Kích thước trang đúng A4 = 595.28 × 841.89 pt |
| Chuẩn hóa tiếng Việt | `unidecode` | Bỏ dấu trước khi so regex |
| Cấu hình | `pydantic` v2 + `PyYAML` | |
| CLI | `typer` | |
| Web UI | `gradio` | |
| Test | `pytest` | |
| Lint/format | `ruff` | |

- Python **3.10+**. Dùng `pyproject.toml`, cài kiểu editable (`pip install -e .[dev]`).
- Dùng `pathlib` cho mọi đường dẫn (máy tôi có thể là Windows).
- **PaddleOCR:** API bản 2.x (`ocr.ocr(img, cls=True)`) và 3.x (`ocr.predict(img)` → `rec_texts`, `rec_polys`/`rec_boxes`) khác nhau. Trước khi viết adapter, **kiểm tra phiên bản đang cài** (`paddleocr.__version__`) và đọc docstring thật. Không viết theo trí nhớ. Ghi phiên bản đã pin vào `pyproject.toml`.
- OCR chạy trên **ảnh đã thu nhỏ** (mặc định tương đương 150 DPI). Tọa độ trả về phải nhân lại theo tỉ lệ về ảnh làm việc (300 DPI).

---

## 4. Kiến trúc

### 4.1 Nguyên tắc
- **Tách hai giai đoạn:**
  - **Analysis** (chậm): render → tìm mốc → chia khối. Kết quả được cache.
  - **Layout** (nhanh): áp khoảng trắng → dàn trang → xuất file.
  Đổi khoảng trắng **không được** chạy lại OCR.
- Mỗi module là hàm thuần (pure function) nhận vào và trả ra dataclass/pydantic model. Không dùng biến toàn cục.
- **Nguồn chữ là interface `TextSource`** gồm `PdfTextSource` và `PaddleOcrSource`. Phần còn lại của pipeline không biết chữ đến từ đâu.
- Mọi tọa độ nội bộ tính bằng **pixel của ảnh làm việc (DPI cấu hình, mặc định 300)**. Hàm đổi mm sang px nằm tập trung trong `units.py`.

### 4.2 Cấu trúc thư mục

```
exam-padder/
├── AGENTS.md                  # file này
├── README.md
├── pyproject.toml
├── configs/
│   ├── default.yaml
│   └── presets/{gon,vua,rong}.yaml
├── samples/                   # đề thật của tôi — .gitignore, KHÔNG commit
├── src/exam_padder/
│   ├── __init__.py
│   ├── config.py              # pydantic models cho config + load/merge preset
│   ├── models.py              # TextLine, Anchor, Block, AnalysisResult, PageLayout
│   ├── units.py               # mm↔px, line-height, page fraction → px
│   ├── render.py              # PDF → list[np.ndarray] (RGB), phát hiện text layer
│   ├── text_source/
│   │   ├── base.py            # Protocol TextSource
│   │   ├── pdf_text.py
│   │   └── paddle_ocr.py      # import lười (lazy import); báo lỗi rõ nếu chưa cài
│   ├── preprocess.py          # chỉnh nghiêng, làm trắng nền (chỉ cho bản scan)
│   ├── anchors.py             # chuẩn hóa, regex, phân loại, kiểm tra mốc
│   ├── stream.py              # bỏ header/footer trang, nối trang thành dải liên tục
│   ├── slicing.py             # dịch đường cắt về dòng trắng, cắt khối, trim, gán loại
│   ├── padding.py             # tính khoảng trắng (px) cho từng khối từ config + override
│   ├── layout.py              # dàn trang A4 / trang liên tục
│   ├── export.py              # xuất PDF, xuất ảnh khối để debug
│   ├── debug.py               # vẽ bbox, đường cắt, nhãn lên ảnh
│   ├── cache.py               # cache AnalysisResult theo hash(file + tham số analysis)
│   ├── pipeline.py            # analyze(), layout(), run()
│   └── cli.py
├── app/
│   └── gradio_app.py
└── tests/
    ├── conftest.py
    ├── fixtures/make_synthetic_pdf.py   # sinh PDF giả bằng PyMuPDF
    ├── test_units.py
    ├── test_anchors.py
    ├── test_stream.py
    ├── test_slicing.py
    ├── test_padding.py
    └── test_layout.py
```

### 4.3 Data models (gợi ý, được phép chỉnh nhưng phải báo tôi)

```python
class TextLine(BaseModel):
    text: str                    # nguyên văn
    norm: str                    # đã bỏ dấu, gộp khoảng trắng
    bbox: tuple[int, int, int, int]   # x0, y0, x1, y1 (px, ảnh làm việc)
    page: int
    source: Literal["pdf", "ocr"]
    conf: float | None = None

class Anchor(BaseModel):
    kind: Literal["question", "section", "footer", "end"]
    page: int
    bbox: tuple[int, int, int, int]
    section: Literal["I", "II", "III"] | None = None
    number: int | None = None        # số câu
    text: str

BlockType = Literal["header", "section", "mcq", "true_false", "short_answer", "other"]

class Block(BaseModel):
    id: str                          # "header", "S-II", "I-5", "II-3", "III-1", "end"
    type: BlockType
    y0: int; y1: int                 # trong hệ tọa độ dải liên tục (stream)
    warnings: list[str] = []

class AnalysisResult(BaseModel):
    dpi: int
    stream_width: int
    stream_height: int
    stream_png_path: Path            # dải liên tục, lưu ra đĩa (cache)
    blocks: list[Block]
    median_line_height_px: float
    warnings: list[str]
```

---

## 5. Cấu hình khoảng trắng (yêu cầu chính, PHẢI linh hoạt)

### 5.1 Đơn vị hỗ trợ
- `mm`: milimét trên trang A4 output.
- `lines`: số dòng. 1 dòng = `median_line_height_px` đo từ đề × `line_spacing_factor` (mặc định 1.5). Không đo được thì dùng `fallback_line_height_mm` (mặc định 7).
- `page`: phần trang A4. `0.5` = nửa trang = 148.5 mm.

### 5.2 Các tùy chọn
- `preset`: `gon` | `vua` | `rong` | `custom`.
- `per_type`: mỗi loại khối có `{value, unit, start_on_new_page}`.
- `overrides`: ghi đè theo id khối, ví dụ `"III-4": {value: 1, unit: page}`.
- Thứ tự ưu tiên: **override theo câu > per_type do người dùng chỉnh > preset > default**.

### 5.3 Preset mặc định

| Loại | gon | **vua (mặc định)** | rong |
|---|---|---|---|
| header | 0 mm | 0 mm | 0 mm |
| section | 3 mm | 5 mm | 8 mm |
| mcq | 1 lines | **2 lines** | 4 lines |
| true_false | 0.33 page | **0.5 page** | 1 page + `start_on_new_page` |
| short_answer | 0.33 page | **0.5 page** | 0.75 page |
| other | 0 mm | 0 mm | 0 mm |

### 5.4 `configs/default.yaml` (mẫu)

```yaml
dpi: 300
ocr:
  enabled: auto            # auto | always | never
  downscale_dpi: 150
  lang: vi
input:
  two_column: false        # chỉ bật thủ công
  deskew: auto             # auto (chỉ bản scan) | true | false
  whiten_background: false
page:
  mode: a4                 # a4 | continuous
  margin_top_mm: 10
  margin_bottom_mm: 10
  fit_width: false
  allow_split_tall_block: true
slicing:
  snap_search_mm: 15       # tìm dòng trắng trong phạm vi này phía trên mốc
  ink_threshold: 0.002     # tỉ lệ pixel mực tối đa để coi một dòng là "trắng"
  trim_keep_mm: 1.5        # chừa lại sau khi trim
  question_left_margin_tolerance: 0.04   # tỉ lệ so với chiều rộng trang
padding:
  preset: vua
  line_spacing_factor: 1.5
  fallback_line_height_mm: 7
  per_type: {}             # rỗng = lấy theo preset
  overrides: {}
```

---

## 6. Thuật toán chi tiết

### 6.1 Render & nguồn chữ
1. Render mỗi trang ở `dpi`. Ghi lại hệ số `scale = dpi / 72` để đổi tọa độ PDF (pt) sang px.
2. Trang có text layer khi `len(page.get_text("words")) > 20`. Nếu `ocr.enabled == auto`: có text layer thì dùng `PdfTextSource`, không có thì dùng `PaddleOcrSource`.
3. `PdfTextSource`: gom các từ thành dòng theo `(block_no, line_no)`, bbox dòng = hợp các bbox từ.
4. `PaddleOcrSource`: chạy trên ảnh downscale. Nếu phiên bản hỗ trợ trả tọa độ từng từ thì lấy, để xử lý trường hợp chữ viết tay dính đầu dòng.

### 6.2 Nhận diện mốc (`anchors.py`)
Chuẩn hóa: `norm = re.sub(r"\s+", " ", unidecode(text)).strip()`.

| kind | Regex trên `norm` | Điều kiện thêm |
|---|---|---|
| question | `^Cau\s*(\d{1,2})\s*[.:]` | Phân biệt hoa thường; `x0` cách lề trái vùng nội dung ≤ tolerance |
| section | `^PHAN\s+(III|II|I)\b` | |
| footer | `Trang\s*\d+\s*/\s*\d+` | Nằm trong 12% dưới cùng của trang |
| end | `^HET$` hoặc `^-+\s*HET\s*-+$` | |

- **Chống nhiễu chữ viết tay ở đầu dòng (bản OCR):** nếu `norm` không khớp ngay đầu nhưng `re.search(r"\bCau\s*\d{1,2}\s*[.:]", norm)` khớp và vị trí khớp nằm trong 15 ký tự đầu, thì vẫn nhận, đồng thời ghi warning. Nếu có tọa độ từng từ thì lấy `x0` của từ "Cau".
- **Lề trái vùng nội dung** = phân vị 5% của `x0` các dòng chữ trên trang.
- **Kiểm tra:**
  - Gán `section` cho mỗi mốc question theo mốc section gần nhất phía trước (theo thứ tự trang, rồi theo y).
  - Trong mỗi section, số câu phải là 1, 2, 3… liên tục. Thiếu, nhảy hoặc trùng thì giữ mốc nhưng ghi warning (không tự bịa mốc).
  - Không có mốc section nào thì phân loại theo nội dung khối (6.4).

### 6.3 Dải liên tục (`stream.py`)
- Với mỗi trang: vùng giữ lại là từ `top_cut` đến `bottom_cut`.
  - `bottom_cut` = dòng trắng ngay trên footer (nếu tìm thấy footer), nếu không thì chừa lề dưới mặc định.
  - `top_cut` = dòng pixel có mực đầu tiên trừ đi một ít lề.
- Nối dọc các vùng đã cắt thành một ảnh duy nhất. Lưu bảng ánh xạ `(page, y_page) → y_stream` để đổi tọa độ mốc.
- Nếu `two_column: true`: chia mỗi trang thành cột trái và cột phải trước khi nối (thứ tự: trái rồi phải). Rãnh cột phải là khe trắng dọc chạy suốt ≥ 80% chiều cao vùng chữ, nằm trong khoảng 35–65% chiều rộng trang.

### 6.4 Cắt khối (`slicing.py`)
1. Nhị phân hóa dải bằng Otsu, tính `ink_ratio[y]` cho từng dòng.
2. Với mỗi mốc question/section/end: bắt đầu từ `y0` của mốc, đi lên tối đa `snap_search_mm`, tìm **đoạn liên tiếp các dòng trắng** (ink_ratio ≤ threshold) gần mốc nhất. Đường cắt đặt ở **giữa đoạn trắng đó**. Không tìm được thì cắt tại `y0 - 2px` và ghi warning `"cut_through_ink"`.
3. Khối đầu tiên (từ y=0 đến mốc đầu tiên) là `header`.
4. Khối từ mốc section đến mốc question kế tiếp là `section`.
5. Gán loại khối question theo section: I → `mcq`, II → `true_false`, III → `short_answer`.
   Không có section thì đoán theo nội dung: có ≥ 3 dòng bắt đầu `a)`, `b)`, `c)`, `d)` → `true_false`; có `A.` và `B.` → `mcq`; còn lại → `short_answer`. Ghi warning `"type_guessed"`.
6. **Trim:** bỏ các dòng trắng ở trên và dưới mỗi khối, chừa lại `trim_keep_mm`.

### 6.5 Khoảng trắng (`padding.py`)
`resolve_padding(block, cfg, median_line_height_px) -> PaddingSpec(px: int, start_on_new_page: bool)` theo thứ tự ưu tiên ở mục 5.2.

### 6.6 Dàn trang (`layout.py`)
- **Chế độ `a4`:** kích thước trang (px) = A4 ở `dpi` (300 DPI → 2480 × 3508). Vùng nội dung bị trừ `margin_top/bottom`.
  - Khối có `start_on_new_page` và trang hiện tại chưa trống thì sang trang mới.
  - Khối không vừa phần còn lại của trang hiện tại thì sang trang mới.
  - Khối cao hơn cả vùng nội dung một trang: nếu `allow_split_tall_block` thì chia tại dòng trắng gần biên trang nhất, không thì co nhỏ cho vừa và ghi warning.
  - Sau khối là khoảng trắng: nếu khoảng trắng vượt quá phần còn lại của trang thì khối kế tiếp sang trang mới (phần còn lại để trắng, không mang khoảng trắng sang trang sau).
  - Căn ngang: giữ nguyên vị trí x như bản gốc (dải có cùng chiều rộng với trang gốc). Nếu trang gốc rộng khác A4: `fit_width` thì co giãn, không thì căn giữa.
- **Chế độ `continuous`:** mỗi trang output có chiều rộng A4, chiều cao tùy ý, chứa toàn bộ nội dung.
- Output của layout là `list[PIL.Image]` (RGB nền trắng) kèm metadata khối nằm ở trang nào, vị trí nào (để vẽ preview).

### 6.7 Xuất file (`export.py`)
- PDF: mỗi ảnh trang thành 1 trang A4 bằng `img2pdf` với `layout_fun` A4. Ảnh lưu PNG (không nén mất dữ liệu).
- Debug: `--debug-dir` xuất ảnh từng trang có vẽ bbox mốc (question = xanh lá, section = xanh dương, footer = đỏ), đường cắt và nhãn `id/type`. Xuất thêm ảnh từng khối và file `analysis.json`.

### 6.8 Tiền xử lý bản scan (`preprocess.py`)
- **Chỉnh nghiêng:** ước lượng góc bằng `minAreaRect` trên mực hoặc Hough lines, chỉ xoay nếu |góc| trong khoảng 0.3°–10°. Xoay với nền trắng.
- **Làm trắng nền** (tùy chọn): chia ảnh cho phiên bản làm mờ lớn (background division), sau đó cắt ngưỡng nhẹ để nền thành 255. **Không** nhị phân hóa ảnh output, vì phải giữ nét gốc.
- Ngoài phạm vi: nắn phối cảnh ảnh chụp nghiêng mạnh (gợi ý người dùng dùng app scan).

---

## 7. Lộ trình milestone

Mỗi milestone chỉ hoàn thành khi **đạt hết tiêu chí nghiệm thu** và tôi xác nhận.

### M0 — Khung dự án & kiểm tra môi trường
- Tạo cấu trúc thư mục, `pyproject.toml` (extras: `ocr`, `ui`, `dev`), `ruff`, `pytest`, `.gitignore` (gồm `samples/`, `.cache/`, `out/`).
- `config.py` load `default.yaml` và preset.
- Script `python -m exam_padder.cli doctor`: in phiên bản Python, PyMuPDF, OpenCV, PaddleOCR (nếu có), trạng thái CUDA/GPU của paddle.
- `tests/fixtures/make_synthetic_pdf.py`: sinh PDF A4 có header, `PHẦN I` với 3 câu trắc nghiệm (có dòng A. B. C. D. ngang), `PHẦN II` với 1 câu có a) b) c) d), `PHẦN III` với 2 câu, footer `Trang x/y`, một câu vắt qua trang, một dòng nhiễu "trả lời từ câu 1 đến câu 12".
- **Nghiệm thu:** `pip install -e .[dev]` chạy được; `pytest` xanh (test load config); `doctor` chạy được.

### M1 — Render + nguồn chữ + nhận diện mốc trên 1 trang (PoC)
- `render.py`, `text_source/pdf_text.py`, `text_source/paddle_ocr.py`, `anchors.py` (regex + phân loại, chưa kiểm tra liên trang), `debug.py`.
- CLI: `exam-padder detect input.pdf --page 1 --debug-dir out/`. In bảng mốc (kind, section, number, bbox, source) và lưu `debug.png`.
- **Nghiệm thu:** trên PDF giả, tìm đúng 100% mốc và không nhận nhầm dòng nhiễu. Có unit test cho regex gồm các ca: "Câu 1.", "Câu 12:", "Cau 3.", "Cáu 4.", "câu 1 đến câu 12" (phải loại), "19 Câu 1." (OCR nhiễu đầu dòng). Chạy được trên đề thật trong `samples/` và tôi xem `debug.png`.

### M2 — Mốc toàn tài liệu + kiểm tra hợp lệ
- Chạy cho mọi trang, gán section, kiểm tra số câu liên tục, sinh warnings.
- **Nghiệm thu:** test có các ca thiếu câu, trùng câu, không có section. In ra danh sách cuối cùng dạng `I-1 … I-12, II-1 … II-4, III-1 … III-6` cho đề thật.

### M3 — Dải liên tục
- `stream.py`: bỏ footer, nối trang, bảng ánh xạ tọa độ.
- **Nghiệm thu:** ảnh `stream.png` của đề thật không còn dòng "Trang x/y". Câu vắt trang liền mạch. Có test ánh xạ tọa độ.

### M4 — Cắt khối
- `slicing.py`: dịch đường cắt, chia khối, gán loại, trim. Xuất ảnh từng khối ra `out/blocks/`.
- **Nghiệm thu:** không khối nào bị cắt qua mực (test bằng cách kiểm tra `ink_ratio` tại đường cắt). Dòng tiêu đề PHẦN II/III là khối riêng. Tôi xem các ảnh khối của đề thật.

### M5 — Khoảng trắng + dàn trang + xuất PDF (chạy trọn vẹn bằng CLI)
- `units.py`, `padding.py`, `layout.py`, `export.py`, `pipeline.py`, `cache.py`.
- CLI: `exam-padder run input.pdf -o output.pdf [--preset vua] [--set padding.per_type.mcq.value=3] [--debug-dir out/]`.
- **Nghiệm thu:**
  - Test cho mm/lines/page → px và thứ tự ưu tiên override.
  - Test dàn trang: không khối nào bị chia khi thấp hơn 1 trang; `start_on_new_page` hoạt động; kích thước trang PDF = A4.
  - Lần chạy thứ 2 với preset khác dùng cache (không chạy lại analysis; in log thời gian).
  - Tôi mở `output.pdf` trên Scrble Ink và xác nhận.

### M6 — Hỗ trợ bản scan / ảnh chụp
- Hoàn thiện adapter PaddleOCR (đã kiểm tra phiên bản), chạy trên ảnh downscale, thêm `preprocess.py`.
- **Nghiệm thu:** tạo bản scan giả (render PDF giả → xoay 1.5° → thêm nhiễu và nền xám) và vẫn tìm đủ mốc. Chạy trên ảnh chụp đề thật của tôi, báo cáo câu nào thiếu hoặc sai.

### M7 — Giao diện Gradio
- `app/gradio_app.py`:
  - Upload PDF; bấm "Phân tích" (chạy analysis, có cache).
  - Chọn preset; mỗi loại câu có slider `value`, dropdown đơn vị (`mm`/`lines`/`page`), checkbox "bắt đầu trang mới".
  - Bảng (Dataframe) các khối: `id | type | warnings | padding override | đơn vị | trang mới`, sửa trực tiếp được.
  - Gallery xem trước các trang output, **cập nhật khi đổi khoảng trắng mà không chạy lại analysis**.
  - Gallery debug: dải có vẽ đường cắt và nhãn. Cho phép thêm, xóa đường cắt bằng cách nhập y hoặc chọn khối.
  - Tùy chọn: bật 2 cột, làm trắng nền, chế độ trang a4/continuous.
  - Nút "Xuất PDF" và "Lưu cấu hình thành preset" (ghi YAML).
- **Nghiệm thu:** toàn bộ luồng chạy được trên đề thật. Đổi slider thì preview cập nhật trong vài giây.

### M8 — Hoàn thiện
- Hiệu năng (xử lý song song từng trang nếu cần), README có ảnh trước/sau, đóng gói, log rõ ràng, xử lý lỗi thân thiện (PDF mã hóa, trang trống, không tìm thấy mốc nào).

---

## 8. Quy trình làm việc (BẮT BUỘC)

1. **Mỗi lần chỉ làm 1 milestone.** Khi bắt đầu, viết **kế hoạch ≤ 10 dòng** gồm file sẽ tạo/sửa, quyết định chính, rủi ro. Nếu có điểm mơ hồ làm thay đổi thiết kế thì **hỏi tôi trước**. Mơ hồ nhỏ thì tự chọn phương án hợp lý và ghi rõ đã chọn gì.
2. Viết code kèm test. Chạy `ruff check`, `ruff format`, `pytest` và **dán kết quả thật**. Không bao giờ báo "đã pass" khi chưa chạy.
3. Kết thúc milestone bằng một báo cáo ngắn:
   - Đã làm gì (danh sách file)
   - Lệnh để tôi tự chạy thử
   - Kết quả test
   - Những gì tôi cần kiểm tra bằng mắt (ví dụ mở `out/debug/page1.png`)
   - Hạn chế và câu hỏi mở
   Sau đó **dừng lại, chờ tôi xác nhận**.
4. Commit sau mỗi milestone với message dạng `M3: build continuous stream, strip footers` (nếu repo có git và tôi cho phép).
5. **Không tự thêm thư viện lớn ngoài stack** (layout model, LLM, PP-Structure…) khi chưa hỏi tôi.
6. Không được đọc nhầm API: với PyMuPDF, PaddleOCR, Gradio, khi không chắc thì kiểm tra phiên bản đã cài và docstring/`help()` thực tế.
7. Có lỗi thì tìm nguyên nhân gốc, không vá cho test pass. Nếu phải thay đổi đặc tả trong file này thì đề xuất cụ thể để tôi duyệt.
8. Không commit file trong `samples/` (đề thi có bản quyền và có chữ viết tay của học sinh).

## 9. Chuẩn code
- Type hints đầy đủ, docstring ngắn cho hàm public. Hàm ≤ ~50 dòng khi có thể.
- Dùng `logging` (không dùng `print`, trừ output của CLI).
- Hằng số "ma thuật" (ngưỡng, tỉ lệ) phải nằm trong config, không viết cứng trong code.
- Ảnh nội bộ là `np.ndarray` RGB `uint8`; chỉ đổi sang PIL ở `layout.py`/`export.py`.
- Tên biến, hàm, docstring bằng tiếng Anh. Thông báo trên UI và báo cáo cho tôi bằng tiếng Việt.

## 10. Ngoài phạm vi (hiện tại)
- Nhận diện nội dung câu hỏi, đáp án, chấm bài.
- Gõ lại LaTeX, dựng lại đề.
- Nắn phối cảnh ảnh chụp nghiêng mạnh, xóa chữ viết tay.
- Đề nhiều cột phức tạp hơn 2 cột.

---

**Câu lệnh khởi động cho agent:** "Đọc AGENTS.md. Tóm tắt lại bài toán trong 5 dòng để tôi xác nhận bạn hiểu đúng, rồi đưa kế hoạch cho Milestone 0."
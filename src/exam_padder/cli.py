"""Command-line interface for Exam Padder."""

from __future__ import annotations

import importlib.metadata
import platform
import sys

import typer

app = typer.Typer(no_args_is_help=True, help="Exam Padder CLI.")


def _pkg_version(dist_name: str, fallback: str | None = None) -> str:
    """Return installed distribution version or fallback string."""
    try:
        return importlib.metadata.version(dist_name)
    except importlib.metadata.PackageNotFoundError:
        return fallback or "not installed"


@app.callback()
def main() -> None:
    """Exam Padder — chèn khoảng trắng vào đề thi Toán PDF."""


@app.command()
def doctor() -> None:
    """Print Python, CV/PDF dependencies, and Paddle CUDA/GPU status."""
    typer.echo(f"Python: {platform.python_version()} ({sys.executable})")

    try:
        import pymupdf

        fitz_ver = getattr(pymupdf, "__version__", None) or _pkg_version("PyMuPDF")
        typer.echo(f"PyMuPDF: {fitz_ver} (MuPDF {pymupdf.version[1]})")
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        typer.echo(f"PyMuPDF: error ({exc})")

    try:
        import cv2

        typer.echo(f"OpenCV: {cv2.__version__}")
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        typer.echo(f"OpenCV: error ({exc})")

    try:
        import numpy as np
        import PIL
        import pydantic

        typer.echo(
            f"Core libs: numpy={np.__version__}, Pillow={PIL.__version__}, "
            f"pydantic={pydantic.__version__}"
        )
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        typer.echo(f"Core libs: error ({exc})")

    try:
        import paddleocr

        ocr_ver = getattr(paddleocr, "__version__", None) or _pkg_version("paddleocr")
        typer.echo(f"PaddleOCR: {ocr_ver}")
    except ImportError:
        typer.echo("PaddleOCR: not installed (optional: pip install -e .[ocr])")

    try:
        import paddle

        paddle_ver = getattr(paddle, "__version__", "unknown")
        cuda_compiled = paddle.device.is_compiled_with_cuda()
        if cuda_compiled:
            gpu_count = paddle.device.cuda.device_count()
            gpu_names = [paddle.device.cuda.get_device_name(i) for i in range(gpu_count)]
            gpu_info = f"available ({gpu_count}: {', '.join(gpu_names)})" if gpu_count else "none"
        else:
            gpu_info = "not compiled with CUDA"
        typer.echo(f"PaddlePaddle: {paddle_ver}, CUDA: {cuda_compiled}, GPU: {gpu_info}")
    except ImportError:
        typer.echo("PaddlePaddle: not installed (optional: pip install -e .[ocr])")


if __name__ == "__main__":
    app()

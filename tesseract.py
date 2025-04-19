from __future__ import annotations
from pathlib import Path
from typing import List
from PIL import Image
from tqdm import tqdm
from pytesseract import image_to_string
from pdf2image import convert_from_path

Image.MAX_IMAGE_PIXELS = None


def pdf_to_images(pdf_path: Path, dpi: int = 300) -> List['Image.Image']:
    """Render each PDF page to a Pillow image at the given DPI."""
    return convert_from_path(str(pdf_path), dpi=dpi)


def ocr_images(images: List['Image.Image'], *, lang: str = 'eng') -> List[str]:
    """Run Tesseract OCR on a list of Pillow images and return page‑wise text."""
    texts: List[str] = []
    for page_img in tqdm(images, desc='OCR', unit='page'):
        texts.append(image_to_string(page_img, lang=lang))
    return texts


def save_output(text_pages: List[str]):
    """Persist OCR results as text or JSON."""
    out_string = ''
    for i, page in enumerate(text_pages, 1):
        out_string += f'=== Page {i} ===\n'
        out_string += page.rstrip()
        out_string += '\n\n'

    return out_string


def tesseract_ocr(filename: str) -> None:
    images = pdf_to_images(filename, dpi=300)
    text_pages = ocr_images(images, lang='eng')
    return save_output(text_pages), 0
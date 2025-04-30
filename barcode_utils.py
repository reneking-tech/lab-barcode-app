# barcode_utils.py

import os
from barcode import Code128
from barcode.writer import ImageWriter

BARCODE_DIR = os.path.join("static", "barcodes")
os.makedirs(BARCODE_DIR, exist_ok=True)


def generate_barcode(data, filename):
    """
    Generates a barcode image and saves it as a PNG.
    Returns the full file path.
    """
    path_without_ext = os.path.join(BARCODE_DIR, filename)
    writer = ImageWriter()
    barcode = Code128(data, writer=writer)

    full_path = barcode.save(path_without_ext)  # returns path WITH extension
    return full_path

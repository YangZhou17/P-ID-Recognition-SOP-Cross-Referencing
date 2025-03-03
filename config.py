"""
Configuration file for OCR and image processing.
Defines constants for merging boxes and Tesseract OCR settings.
"""
MIN_BLOCK_DISTANCE = 10         # Minimum distance for merging boxes.
BOX_PADDING = 7                 # Extra padding around boxes during OCR.
MIN_HEIGHT_DIFF = 7             # Maximum height difference determining if boxes are on the same line.
MIN_HORI_DIFF_SAME_HEIGHT = 90  # Horizontal difference threshold for same-line boxes.

# OCR configuration for locating text blocks
FIRST_CONFIG = r'--oem 3 --psm 6'

# OCR configuration for actual text extraction
SECOND_CONFIG = (
    r'--oem 3 '
    r'--psm 6 '
    # r'-l eng '
    r'-c tessedit_char_whitelist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-&.\' " '
    r'-c preserve_interword_spaces=1'
)
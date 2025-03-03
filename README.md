# Diagram Analysis and Discrepancy Checker

This project provides an automated pipeline for processing Piping & Instrumentation Diagrams (P&IDs) PDFs. It converts PDFs into high-resolution images, extracts text boxes using OCR, compares extracted numerical values (e.g., PSIG and Temperature) against standard limits defined in an Standard Operating Procedure (SOP) document, and then annotates the images to highlight discrepancies.

---

## Features

- **OCR-Based Text Extraction:** Uses Tesseract OCR to identify and extract text boxes from images.
- **Discrepancy Checking:** Compares extracted numerical values against predefined limits.
- **Annotated Results:** Draws color-coded rectangles on images — green for values within limits and red for values exceeding limits.

---

## Prerequisites

- **Python 3.12**
- **Tesseract-OCR:** [Download and install Tesseract OCR](https://github.com/tesseract-ocr/tesseract). Make sure it’s in your system PATH or configure the path in your code.
- **Poppler:** Required for PDF-to-image conversion.  
  - **Ubuntu:** `sudo apt-get install poppler-utils`  
  - **Windows/Mac:** [Download Poppler](http://blog.alivate.com.au/poppler-windows/) and add to your PATH.

### Python Libraries

Install the required Python packages via pip:

```bash
pip install opencv-python pytesseract pdf2image python-docx
```

---

## Directory Structure

```
diagram-analysis/
├── data/
│   ├── p&id/           # Directory for PDF diagram files
│   └── sop/            # Directory for SOP DOCX files
├── check_discrepancy.py
├── config.py
├── extract_text_box.py
├── load_sop.py
├── main.py
├── pdf_to_image.py
└── README.md
```

---

## Usage

1. **Prepare Input Files:**
   - Place your PDF diagram file(s) in the `data/p&id/` directory.
   - Place your SOP DOCX file(s) in the `data/sop/` directory.

2. **Run the Program:**

   Execute the main script by running:

   ```bash
   python3 main.py "./data/p&id/diagram.pdf" "./data/sop/sop.docx"
   ```

3. **Output:**
   - Annotated images are saved in an output directory named after the PDF file name.
   - The console will also display the extracted limits and the comparison results for each processed image.

---

## Example Output

### Annotated Diagram Result

![Annotated Diagram](images/page_1_analyzed.png)

### OCR Text Extraction Result

![OCR Extraction](images/page_1.png)

---

## Customization

- **OCR Settings:**  
  Modify `first_config` and `second_config` in `config.py` to adjust Tesseract OCR performance based on your diagram quality.

- **Merging Parameters:**  
  Change parameters such as `MIN_BLOCK_DISTANCE` and `BOX_PADDING` in `config.py` to fine-tune how text boxes are merged.

- **Image Scaling:**  
  Change SCALE_FACTOR parameters in `config.py` to cater for different image resolutions.

---

## Possible Improvements

- **Better Lauout Analysis:**
  Locating components locations by grouping tesseract's text boxes can be improved by traning a YOLO model.

- **Graph Construction:**
  Thoughts are to connect modules based on horizontal/vertical alignment if can achieve higher component recognition quality.

---

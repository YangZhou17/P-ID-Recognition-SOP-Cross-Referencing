from pdf_to_image import pdf_to_images
from load_sop import *
from check_discrepancy import process_boxes_and_draw
from extract_text_box import extract_boxes_from_image
import json
import os

def main(diagram_file_path, sop_file_path):
    '''
    Main workflow:
      1. Extract limits from the SOP document.
      2. Convert a PDF diagram into images.
      3. Extract text boxes from each image and compare against limits.
      4. Annotate and save the processed images.
    '''
    # Extract limits from the SOP file.
    print("Extracting Limits From SOP File")
    limits = extract_limits_from_doc(sop_file_path)
    limit_mapping = create_mapping_from_limits(limits)
    print(json.dumps(limits, indent=4))

    # Convert the PDF diagram into image files.
    images = pdf_to_images(diagram_file_path, os.path.basename(diagram_file_path).split('.')[0])
    
    # Process each image.
    for img_path in images:
        print(f"Start Processing '{img_path}'.")
        print("Locating Text Blocks")
        boxes = extract_boxes_from_image(img_path)
        print("Comparing With SOP")
        result = process_boxes_and_draw(limit_mapping, boxes, img_path, header_y_cutoff=1000)
        print(f"Process Finished For '{img_path}'.")

if __name__ == "__main__":
    main("./data/p&id/diagram.pdf", "./data/sop/sop.docx")
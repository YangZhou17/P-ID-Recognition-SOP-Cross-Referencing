from config import *
import cv2
import pytesseract
import os

def boxes_overlap_or_close(box1, box2, min_distance):
    '''
    Check if two boxes overlap or are within a specified distance.
    '''
    x1, y1, w1, h1 = box1['x'], box1['y'], box1['w'], box1['h']
    x2, y2, w2, h2 = box2['x'], box2['y'], box2['w'], box2['h']

    # Expand the first box by min_distance on all sides.
    x1_exp = x1 - min_distance
    y1_exp = y1 - min_distance
    w1_exp = w1 + 2 * min_distance
    h1_exp = h1 + 2 * min_distance

    # Check for horizontal overlap
    if x1_exp > x2 + w2 or x2 > x1_exp + w1_exp:
        return False
    # Check for vertical overlap
    if y1_exp > y2 + h2 or y2 > y1_exp + h1_exp:
        return False
    return True

def merge_boxes(box1, box2):
    '''
    Merge two boxes into one that encompasses both.
    '''
    new_x = min(box1['x'], box2['x'])
    new_y = min(box1['y'], box2['y'])
    new_x2 = max(box1['x'] + box1['w'], box2['x'] + box2['w'])
    new_y2 = max(box1['y'] + box1['h'], box2['y'] + box2['h'])

    return {
        'x': new_x,
        'y': new_y,
        'w': new_x2 - new_x,
        'h': new_y2 - new_y
    }

def merge_close_boxes(old_boxes):
    '''
    Iteratively merge boxes that overlap or are very close.
    '''
    boxes = old_boxes
    merged_flag = True
    while merged_flag:
        merged_flag = False
        new_boxes = []
        skip_indices = set()
        for i in range(len(boxes)):
            if i in skip_indices:
                continue
            current_box = boxes[i]
            for j in range(i + 1, len(boxes)):
                if j in skip_indices:
                    continue

                # Check if boxes are on the same line or vertically aligned.
                same_line = (
                    (
                        abs(current_box['x'] + current_box['w'] - boxes[j]['x']) < MIN_HORI_DIFF_SAME_HEIGHT or
                        abs(boxes[j]['x'] + boxes[j]['w'] - current_box['x']) < MIN_HORI_DIFF_SAME_HEIGHT
                    ) and
                    abs(current_box['y'] - boxes[j]['y']) < MIN_HEIGHT_DIFF and
                    abs(current_box['h'] - boxes[j]['h']) < MIN_HEIGHT_DIFF
                )
                same_verti = (
                    (
                        abs(current_box['y'] + current_box['h'] - boxes[j]['y']) < MIN_HORI_DIFF_SAME_HEIGHT or
                        abs(boxes[j]['y'] + boxes[j]['h'] - current_box['y']) < MIN_HORI_DIFF_SAME_HEIGHT
                    ) and
                    abs(current_box['x'] - boxes[j]['x']) < MIN_HEIGHT_DIFF and
                    abs(current_box['w'] - boxes[j]['w']) < MIN_HEIGHT_DIFF
                )

                # Merge if boxes overlap/are close or aligned.
                if boxes_overlap_or_close(current_box, boxes[j], MIN_BLOCK_DISTANCE) or same_line or same_verti:
                    current_box = merge_boxes(current_box, boxes[j])
                    skip_indices.add(j)
                    merged_flag = True
            new_boxes.append(current_box)
        boxes = new_boxes
    return boxes


def extract_boxes_from_image(image_path):
    '''
    Extract and refine text boxes from an image using OCR.
    1. Load and resize the image.
    2. Convert to grayscale and apply thresholding.
    3. Run OCR to get initial boxes and merge close boxes.
    4. For each box, perform a second OCR pass on an expanded area.
    5. Save an annotated image and return the final boxes.
    '''
    # Load the image.
    image = cv2.imread(image_path)
    if image is None:
        raise IOError(f"Could not open or find the image '{image_path}'.")

    # Resize the image for better OCR results.
    width = int(image.shape[1] * SCALE_FACTOR)
    height = int(image.shape[0] * SCALE_FACTOR)
    resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)

    # Convert image to grayscale.
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # Run initial OCR to extract text box data.
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config=FIRST_CONFIG)
    boxes = []
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        text = data['text'][i].strip()
        if text != "":
            boxes.append({
                'x': data['left'][i],
                'y': data['top'][i],
                'w': data['width'][i],
                'h': data['height'][i],
                'text': text
            })

    # Merge boxes that are close or overlapping.
    boxes = merge_close_boxes(boxes)
    boxes = sorted(boxes, key=lambda b: b['x'])

    # Second round OCR on each box
    final_boxes = []
    for box in boxes:
        x, y, w, h = box['x'], box['y'], box['w'], box['h']

        # Expand the box by BOX_PADDING
        crop_x = max(0, x - BOX_PADDING)
        crop_y = max(0, y - BOX_PADDING - 5)
        crop_w = w + 2 * BOX_PADDING
        crop_h = h + 2 * BOX_PADDING
        crop = gray[
            crop_y : min(crop_y + crop_h, gray.shape[0]),
            crop_x : min(crop_x + crop_w, gray.shape[1])
        ]

        # Rotate the crop by 90° if needed
        if crop.shape[0] > crop.shape[1]:
            crop = cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)

        # Run OCR on the cropped region.
        new_text = pytesseract.image_to_string(crop, config=SECOND_CONFIG).strip()
        if len(new_text) < 2:
            continue

        # Annotate the image with the refined text.
        cv2.rectangle(resized, (x, y), (x + w, y + h), (255, 0, 0), 3)
        cv2.putText(resized, new_text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Save box with final OCR text
        final_boxes.append({
            'x': x,
            'y': y,
            'w': w,
            'h': h,
            'text': new_text
        })

    # Save the annotated image.
    filename = os.path.basename(image_path)
    parent_dir = os.path.dirname(os.path.dirname(image_path))
    parent_name = os.path.basename(parent_dir)
    output_dir_name = parent_name + "_boxes"
    out_dir = os.path.join(parent_dir, output_dir_name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    cv2.imwrite(out_path, resized)

    return final_boxes

# if __name__ == "__main__":
#     extract_boxes_from_image("./diagram/diagram_raw_images/page_1.png")
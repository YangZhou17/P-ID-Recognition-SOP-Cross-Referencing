import cv2
import re
from config import *
import os

def extract_number(text, marker):
    '''
    Extract the first integer that appears immediately before the given marker in the text.
    If no integer found, remove all symbols and try again
    '''
    # Split text into lines, if any line contains the marker, use that line.
    lines = text.split('\n')
    chosen_line = lines[0]
    for line in lines:
        if marker in line:
            chosen_line = line
            break
    
    # Build a regex to find digits immediately preceding the marker.
    pattern = r'(\d+)(?=' + re.escape(marker) + r')'

    # First attempt: search in the original string.
    match = re.search(pattern, chosen_line)
    if match:
        return int(match.group(1))

    # If not found, remove non-alphanumeric characters and try again.
    cleaned_string = re.sub(r'[^A-Za-z0-9]', '', chosen_line)
    match = re.search(pattern, cleaned_string)
    if match:
        return int(match.group(1))
    return None

def process_boxes_and_draw(limit_mapping, boxes, original_image_path, header_y_cutoff=1000):
    '''
    Process text boxes from an image:
      - Group header boxes and combine their text.
      - Compare diagram boxes against limit values.
      - Draw annotated rectangles on the image and save the result.
    '''
    # Load the image.
    image = cv2.imread(original_image_path)
    if image is None:
        raise IOError(f"Could not open or find the image '{original_image_path}'.")

    # Scale up the image for better OCR quality.
    scale_percent = 400
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    drawn_img = cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)

    # Separate header boxes (above cutoff and non-numeric) from diagram boxes.
    header_boxes = [
        b for b in boxes
        if b['y'] < header_y_cutoff and not b['text'].strip().isdigit()
    ]
    diagram_boxes = [
        b for b in boxes 
        if b['y'] >= header_y_cutoff and not (b['y'] >= 6500 and b['x'] >= 7000)
    ]

    # Group header boxes based on their vertical position.
    header_boxes_sorted = sorted(header_boxes, key=lambda b: b['y'])
    groups = []
    if header_boxes_sorted:
        for i in range(len(header_boxes_sorted)):
            found_group = False
            for j in range(len(groups)):
                mid = groups[j][0]['x'] + groups[j][0]['w'] / 2
                if (mid < header_boxes_sorted[i]['x'] + header_boxes_sorted[i]['w'] and
                    mid > header_boxes_sorted[i]['x']):
                    found_group = True
                    groups[j].append(header_boxes_sorted[i])
                    break
            if (found_group): continue

            groups.append([header_boxes_sorted[i]])

    # Combine each group of header boxes into a single bounding box.
    header_group_boxes = []
    for group in groups:
        min_x = min(b['x'] for b in group)
        min_y = min(b['y'] for b in group)
        max_x = max(b['x'] + b['w'] for b in group)
        max_y = max(b['y'] + b['h'] for b in group)
        combined_text = " ".join(b['text'] for b in group)
        if (len(combined_text) < 10): continue
        header_group_boxes.append({
            'x': min_x,
            'y': min_y,
            'w': max_x - min_x,
            'h': max_y - min_y,
            'text': combined_text
        })

    # Draw the header box on the image.
    for box in header_group_boxes:
        x, y, w, h, text = box['x'], box['y'], box['w'], box['h'], box['text']
        cv2.rectangle(drawn_img, (x, y), (x + w, y + h), (255, 0, 0), 6)
        cv2.putText(drawn_img, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Build a list of header strings from each group.
    header_strings = []
    for g in groups:
        # you can decide how you want to combine them. 
        # For example, just join them with spaces:
        combined_text = " ".join([box['text'] for box in g])
        if (len(combined_text) < 10): continue
        header_strings.append(combined_text)

    # Process each diagram box based on its content.
    for b in diagram_boxes:
        text_upper = b['text'].upper()
        # Process blocks containing 'PSIG'
        if "PSIG" in text_upper:
            value = extract_number(b['text'], "PSIG")
            if value is None:
                continue
            limit_value = 10000
            # Update limit_value from header mapping.
            for header in header_strings:
                if header[0:2] in limit_mapping:
                    if (limit_mapping[header[0:2]]["psig"] < limit_value):
                        limit_value = limit_mapping[header[0:2]]["psig"]
            print("=======================")
            print("Comparing PSIG:")
            print("Standard PSIG: " + str(limit_value))
            print("Actual PSIG: " + str(value))
            res = "PASSED" if value <= limit_value else "FAILED"
            print(res)
            print("=======================")
            color = (0, 255, 0) if value <= limit_value else (0, 0, 255)
            x, y, w, h = b['x'], b['y'], b['w'], b['h']
            cv2.rectangle(drawn_img, (x, y), (x + w, y + h), color, 6)
            cv2.putText(drawn_img, b['text'], (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        # Process blocks containing 'F'
        elif "F" in text_upper:
            value = extract_number(b['text'], "F")
            if value is None:
                continue
            limit_value = [float('-inf'), float('inf')]
            # Update temperature range from header mapping.
            for header in header_strings:
                if header[0:2] in limit_mapping:
                    temp_range = limit_mapping[header[0:2]]["temperature"]
                    if (temp_range[0] > limit_value[0]):
                        limit_value[0] = temp_range[0]
                    if (temp_range[1] < limit_value[1]):
                        limit_value[1] = temp_range[1]
            print("=======================")
            print("Comparing Temperature:")
            print("Standard Temperature Range: " + str(limit_value))
            print("Actual Temperature: " + str(value))
            res = "PASSED" if value >= limit_value[0] and value <= limit_value[1] else "FAILED"
            print(res)
            print("=======================")
            color = (0, 255, 0) if value >= limit_value[0] and value <= limit_value[1] else (0, 0, 255)
            x, y, w, h = b['x'], b['y'], b['w'], b['h']
            cv2.rectangle(drawn_img, (x, y), (x + w, y + h), color, 6)
            cv2.putText(drawn_img, b['text'], (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Construct the output file name and path.
    filename = os.path.basename(original_image_path).split('.')
    new_file_name = filename[0] + "_analyzed." + filename[1]
    parent_dir = os.path.dirname(os.path.dirname(original_image_path))
    parent_name = os.path.basename(parent_dir)
    output_dir_name = parent_name + "_analyzed"
    out_dir = os.path.join(parent_dir, output_dir_name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, new_file_name)
    print(out_path)
    cv2.imwrite(out_path, drawn_img)

    return header_strings
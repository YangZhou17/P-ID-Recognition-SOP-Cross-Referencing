import docx

def extract_limits_from_doc(file_path):
    '''
    Extract limits from SOP file.
    Reads tables (skipping header rows) and extracts:
      - Name from the first cell.
      - PSIG value from the second cell.
      - Temperature range from the third cell.
    '''
    doc = docx.Document(file_path)
    limits = []
    for table in doc.tables:
        cells = []
        for i in range(1, len(table.rows)):
            entry = {}
            for j in range(len(table.rows[i].cells)):
                text = table.rows[i].cells[j].text.strip()
                if (j == 0): entry["name"] = text
                if (j == 1): entry["psig"] = int(text)
                if (j == 2):
                    temp_range = text.split(" to ")
                    if (len(temp_range) == 1):
                        entry["temperature"] = [float('-inf'), float(temp_range[0])]
                    else:
                        entry["temperature"] = [float(temp_range[0]), float(temp_range[1])]
            limits.append(entry)
    return limits

def create_mapping_from_limits(limits):
    '''
    Create a mapping from header prefixes to limit entries.
    Maps:
      "F-" to the first limit,
      "V-" to the second limit,
      "E-" to the fourth limit,
      "AC" to the fifth limit.
    Can improve when achieving higher ocr tool accuracy
    '''
    mapping = {}
    if len(limits) >= 5:
        mapping["F-"] = limits[0]
        mapping["V-"] = limits[1]
        mapping["E-"] = limits[3]
        mapping["AC"] = limits[4]
    return mapping
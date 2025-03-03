from pdf2image import convert_from_path
import os

def pdf_to_images(pdf_path, diagram_folder):
    """
    Convert a PDF file into images, one per page and save them inside the specified diagram folder.

    :param pdf_path: Path to the PDF file.
    :param diagram_folder: Folder where the output folder will be created.
    :return: List of image file paths.
    """
    # Ensure the diagram folder exists
    if not os.path.exists(diagram_folder):
        os.makedirs(diagram_folder)

    # Create an output folder inside the diagram folder
    output_folder = os.path.join(diagram_folder, os.path.basename(pdf_path).split('.')[0] + "_raw_images")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Convert PDF to images
    images = convert_from_path(pdf_path)
    image_paths = []

    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths

if __name__ == "__main__":
    print(pdf_to_images("./data/p&id/diagram.pdf", "diagram"))

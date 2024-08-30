import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image

def save_bounding_box_with_margins_as_pdf(pdf_path, output_pdf_path, margin=100, dpi=300):
    # Open the PDF
    doc = fitz.open(pdf_path)
    temp_pdf_paths = []

    # Iterate through all pages
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Render the page to an image with higher DPI
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))  # Set DPI here
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Convert PIL image to OpenCV format
        open_cv_image = np.array(img)
        open_cv_image = open_cv_image[:, :, ::-1].copy()

        # Convert to grayscale
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize variables to store bounding box dimensions
        bounding_boxes = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            bounding_boxes.append((x, y, w, h))

        # Find the bounding box that covers all contours
        if bounding_boxes:
            min_x = min(b[0] for b in bounding_boxes)
            min_y = min(b[1] for b in bounding_boxes)
            max_x = max(b[0] + b[2] for b in bounding_boxes)
            max_y = max(b[1] + b[3] for b in bounding_boxes)

            # Increase the dimensions by adding a margin
            min_x = max(min_x - margin, 0)
            min_y = max(min_y - margin, 0)
            max_x = min(max_x + margin, open_cv_image.shape[1])
            max_y = min(max_y + margin, open_cv_image.shape[0])

            # Crop the image based on the new bounding box
            cropped_image = img.crop((min_x, min_y, max_x, max_y))

            # Create a new image with white background and larger size for margins
            new_width = cropped_image.width + 3 * margin
            new_height = cropped_image.height + 3 * margin
            new_image = Image.new("RGB", (new_width, new_height), (255, 255, 255))  # White background

            # Paste the cropped image onto the new image with margins
            new_image.paste(cropped_image, (margin, margin))

            # Save the image as a PDF page
            temp_pdf_path = f"temp_page_{page_num}.pdf"
            new_image.save(temp_pdf_path, "PDF")
            temp_pdf_paths.append(temp_pdf_path)

        else:
            print(f"Page {page_num + 1}: No contours found. No image saved.")

    # Merge all the temporary PDF pages into a single PDF
    pdf_writer = fitz.open()
    for temp_pdf_path in temp_pdf_paths:
        pdf_writer.insert_pdf(fitz.open(temp_pdf_path))

    # Save the result as a new PDF
    pdf_writer.save(output_pdf_path)
    pdf_writer.close()

    # Clean up temporary files
    import os
    for temp_pdf_path in temp_pdf_paths:
        os.remove(temp_pdf_path)

    doc.close()

    print(f"Saved new PDF with margins as: {output_pdf_path}")

save_bounding_box_with_margins_as_pdf('Grammatik-Aktiv.pdf',
                                      'Grammatik-Aktiv-study-mode.pdf', margin=500)
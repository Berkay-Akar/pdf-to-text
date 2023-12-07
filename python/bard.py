import fitz
import cv2
import pytesseract
from PIL import Image
import csv


def pdf_to_csv(pdf_file_path, csv_file_path):
    """
    Converts a PDF file to images page by page, performs OCR on each image, and saves the extracted text as a CSV file.

    Args:
        pdf_file_path: Path to the PDF file.
        csv_file_path: Path to save the extracted text as a CSV file.
    """

    # Open the PDF file
    doc = fitz.open(pdf_file_path)

    # Create a list to store the extracted text for each page
    extracted_text = []

    # Loop through each page of the PDF
    for page in doc:
        # Extract the page image
        image_list = page.get_image_list()
        if image_list:
            image_bytes = image_list[0].get_stream()
            image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        else:
            # Handle pages without images
            print(f"Page {page.number + 1} has no images.")
            extracted_text.append("")
            continue

        # Convert the image to grayscale and apply thresholding
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresholded_image = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )[1]

        # Convert the image to PIL format for Tesseract
        pil_image = Image.fromarray(thresholded_image)

        # Extract text using Tesseract
        text = pytesseract.image_to_string(pil_image)

        # Append the extracted text for the current page to the list
        extracted_text.append(text)

    # Write the extracted text to a CSV file
    with open(csv_file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Page", "Text"])
        for page_number, text in enumerate(extracted_text):
            writer.writerow([page_number + 1, text])

    # Print confirmation message
    print(f"Extracted text from PDF and saved to CSV file: {csv_file_path}")


# Example usage
pdf_file_path = "test.pdf"
csv_file_path = "extracted_text.csv"
pdf_to_csv(pdf_file_path, csv_file_path)

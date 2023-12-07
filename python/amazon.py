import fitz
import boto3
import io
import os


def pdf_to_images(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    images = []

    # Convert each page to an image
    for page in doc:
        pix = page.get_pixmap()
        img_bytes = io.BytesIO(pix.tobytes())
        images.append(img_bytes.getvalue())

    return images


def process_with_textract(
    images, aws_access_key_id, aws_secret_access_key, aws_region_name
):
    # Initialize the Textract client with provided credentials
    textract = boto3.client(
        "textract",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
    )

    # Send each image to Textract and store results
    results = []
    for image in images:
        response = textract.detect_document_text(Document={"Bytes": image})
        results.append(response)

    return results


def write_results_to_file(ocr_results, output_file_path):
    with open(output_file_path, "w") as file:
        for page_result in ocr_results:
            for item in page_result["Blocks"]:
                if item["BlockType"] == "LINE":
                    file.write(item["Text"] + "\n")


def main(
    pdf_path,
    aws_access_key_id,
    aws_secret_access_key,
    aws_region_name,
    output_file_path,
):
    images = pdf_to_images(pdf_path)
    ocr_results = process_with_textract(
        images, aws_access_key_id, aws_secret_access_key, aws_region_name
    )
    write_results_to_file(ocr_results, output_file_path)


if __name__ == "__main__":
    # Your AWS Credentials - Replace with your actual credentials
    # get key from .env file
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")

    pdf_path = "/Users/univenn/Documents/aws-textractor/test.pdf"  # Replace with your PDF file path
    output_file_path = "output.txt"
    main(
        pdf_path,
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        AWS_REGION_NAME,
        output_file_path,
    )

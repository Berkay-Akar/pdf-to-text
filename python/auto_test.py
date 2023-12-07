import fitz
import boto3
import io
import os


def pdf_to_images(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        images = []

        for page in doc:
            pix = page.get_pixmap()
            img_bytes = io.BytesIO(pix.tobytes())
            images.append(img_bytes.getvalue())

        doc.close()
        return images
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []


def process_with_textract(images, textract_client):
    results = []
    for image in images:
        try:
            response = textract_client.detect_document_text(Document={"Bytes": image})
            results.append(response)
        except Exception as e:
            print(f"Error with Textract OCR: {e}")

    return results


def write_results_to_file(ocr_results, output_file_path):
    try:
        with open(output_file_path, "w") as file:
            for page_result in ocr_results:
                for item in page_result["Blocks"]:
                    if item["BlockType"] == "LINE":
                        file.write(item["Text"] + "\n")
    except Exception as e:
        print(f"Error writing to file {output_file_path}: {e}")


def process_and_save_pdf(input_folder, output_folder, textract_client):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            images = pdf_to_images(pdf_path)

            if images:
                ocr_results = process_with_textract(images, textract_client)
                output_file_path = os.path.join(
                    output_folder, f"{os.path.splitext(filename)[0]}.txt"
                )
                write_results_to_file(ocr_results, output_file_path)

from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import auto_test  # Import your OCR script
import boto3
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"pdf", "zip"}


def save_pdf(file):
    # Ensure the 'uploads' directory exists
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    # Save the file in the 'uploads' folder
    filename = secure_filename(file.filename)
    filepath = os.path.join(uploads_dir, filename)
    file.save(filepath)
    return filepath


@app.route("/process-pdf", methods=["POST"])
def process_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file.filename.endswith(".zip"):
        import zipfile

        print("zip file found, extracting...")
        # Save the zip file to a temporary location
        zip_path = os.path.join(os.getcwd(), "uploads", secure_filename(file.filename))
        file.save(zip_path)

        # Extract the contents of the zip file
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(os.path.join(os.getcwd(), "uploads"))
            print("zip file extracted and the input folder is created")
        os.remove(zip_path)  # Remove the temporary zip file

    if file and allowed_file(file.filename):
        # Save the file in the input folder
        pdf_path = save_pdf(file)

        # Your AWS Credentials (loaded from environment variables)
        textract_client = boto3.client(
            "textract",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION_NAME"),
        )

        # Process and save the PDF
        input_folder = os.path.dirname(pdf_path)
        output_folder = "/Users/univenn/Documents/aws-textractor/outputs"  # Define the output folder path
        auto_test.process_and_save_pdf(input_folder, output_folder, textract_client)
        print("processed pdf", pdf_path)
        print("the pdf has been processed and saved to: ", output_folder)

        # Assuming only one file is processed, read the output
        output_file_path = os.path.join(
            output_folder, os.path.splitext(file.filename)[0] + ".txt"
        )
        if os.path.exists(output_file_path):
            with open(output_file_path, "r") as file:
                content = file.read()
            return jsonify({"content": content})
        else:
            return jsonify({"error": "File processing failed"}), 500


# Rest of the code remains the same

if __name__ == "__main__":
    app.run(debug=True)

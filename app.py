from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import amazon  # Import your OCR script

app = Flask(__name__)


@app.route("/process-pdf", methods=["POST"])
def process_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Process the file
        pdf_path = save_pdf(file)
        output_file_path = "output.txt"  # Define the output file path

        # Your AWS Credentials
        AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")

        # Use your OCR script's main function
        amazon.main(
            pdf_path,
            AWS_ACCESS_KEY_ID,
            AWS_SECRET_ACCESS_KEY,
            AWS_REGION_NAME,
            output_file_path,
        )

        with open(output_file_path, "r") as file:
            content = file.read()

        return jsonify({"content": content})


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"pdf"}


def save_pdf(file):
    # Ensure the 'uploads' directory exists
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    # Save the PDF and return the path
    filename = secure_filename(file.filename)
    filepath = os.path.join(uploads_dir, filename)
    file.save(filepath)
    return filepath


if __name__ == "__main__":
    app.run(debug=True)

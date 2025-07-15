from flask import Flask, request, jsonify, send_file
import os
import tempfile
import subprocess
import zipfile
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Route 1: Convert single DOCX to PDF
@app.route("/convert", methods=["POST"])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.lower().endswith('.docx'):
        return jsonify({"error": "Only .docx files are supported"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        docx_path = os.path.join(temp_dir, file.filename)
        file.save(docx_path)

        try:
            subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'pdf',
                '--outdir', temp_dir, docx_path
            ], check=True)

            pdf_filename = os.path.splitext(file.filename)[0] + '.pdf'
            pdf_path = os.path.join(temp_dir, pdf_filename)

            return send_file(pdf_path, mimetype='application/pdf', download_name='converted.pdf')
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "Conversion failed", "details": str(e)}), 500

# Route 2: Convert multiple files to PDFs and return as ZIP
@app.route("/convert-multiple", methods=["POST"])
def convert_multiple_to_zip():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist('files[]')
    if not files:
        return jsonify({"error": "No files received"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "converted_files.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                filename = secure_filename(file.filename)
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)

                ext = os.path.splitext(filename)[1].lower()
                output_pdf = os.path.splitext(filename)[0] + ".pdf"
                output_pdf_path = os.path.join(temp_dir, output_pdf)

                try:
                    subprocess.run([
                        'libreoffice', '--headless', '--convert-to', 'pdf',
                        '--outdir', temp_dir, input_path
                    ], check=True)
                    if os.path.exists(output_pdf_path):
                        zipf.write(output_pdf_path, arcname=output_pdf)
                except subprocess.CalledProcessError as e:
                    print(f"Error converting {filename}: {e}")
                    continue

        return send_file(zip_path, mimetype='application/zip', as_attachment=True, download_name='converted_files.zip')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

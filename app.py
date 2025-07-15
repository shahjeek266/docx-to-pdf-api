from flask import Flask, request, jsonify, send_file
import os
import tempfile
import subprocess
import zipfile
from werkzeug.utils import secure_filename
from flask_cors import CORS
from PyPDF2 import PdfMerger

app = Flask(__name__)
CORS(app)

@app.route("/convert", methods=["POST"])
def convert_docx():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.lower().endswith('.docx'):
        return jsonify({"error": "Only .docx files are supported"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        docx_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(docx_path)

        try:
            subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', temp_dir,
                docx_path
            ], check=True)

            pdf_filename = os.path.splitext(file.filename)[0] + '.pdf'
            pdf_path = os.path.join(temp_dir, pdf_filename)
            return send_file(pdf_path, mimetype='application/pdf', download_name='converted.pdf')
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "Conversion failed", "details": str(e)}), 500

@app.route("/convert-multiple", methods=["POST"])
def convert_multiple_docx():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist('files[]')
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir)

        converted_files = []

        for file in files:
            if not file.filename.lower().endswith('.docx'):
                continue

            filename = secure_filename(file.filename)
            docx_path = os.path.join(temp_dir, filename)
            file.save(docx_path)

            try:
                subprocess.run([
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', output_dir,
                    docx_path
                ], check=True)

                pdf_filename = os.path.splitext(filename)[0] + '.pdf'
                converted_files.append(os.path.join(output_dir, pdf_filename))
            except subprocess.CalledProcessError:
                continue

        if not converted_files:
            return jsonify({"error": "No files converted"}), 500

        zip_path = os.path.join(temp_dir, "converted_files.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in converted_files:
                zipf.write(file, os.path.basename(file))

        return send_file(zip_path, mimetype='application/zip', download_name='converted_files.zip')

@app.route("/merge-pdfs", methods=["POST"])
def merge_pdfs():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist('files[]')
    pdf_files = [f for f in files if f.filename.lower().endswith('.pdf')]
    if not pdf_files:
        return jsonify({"error": "Only PDF files are allowed"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "merged_output.pdf")
        merger = PdfMerger()

        try:
            for file in pdf_files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(temp_dir, filename)
                file.save(file_path)
                merger.append(file_path)

            merger.write(output_path)
            merger.close()

            return send_file(output_path, mimetype='application/pdf', as_attachment=True, download_name='merged_output.pdf')
        except Exception as e:
            return jsonify({"error": "Merging failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

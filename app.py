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
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            # Find any pdf in temp_dir after conversion
            pdf_files = [f for f in os.listdir(temp_dir) if f.lower().endswith('.pdf')]
            if not pdf_files:
                return jsonify({"error": "Conversion failed: No PDF created"}), 500

            pdf_path = os.path.join(temp_dir, pdf_files[0])  # take first PDF found
            return send_file(pdf_path, mimetype='application/pdf', download_name='converted.pdf')
        except subprocess.CalledProcessError as e:
            return jsonify({
                "error": "Conversion failed with CalledProcessError",
                "stdout": e.stdout.decode() if e.stdout else "",
                "stderr": e.stderr.decode() if e.stderr else "",
                "details": str(e)
            }), 500
        except Exception as e:
            return jsonify({"error": "Unexpected error: " + str(e)}), 500

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

@app.route('/combine-mixed', methods=['POST'])
def combine_mixed():
    if 'files' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files found"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_pdfs = []
        errors = []

        for f in files:
            original_filename = f.filename
            if not original_filename:
                errors.append("One file has no filename")
                continue

            filename = secure_filename(original_filename)
            base, ext = os.path.splitext(filename)
            ext = ext.lower()

            input_path = os.path.join(temp_dir, filename)
            f.save(input_path)

            try:
                if ext == '.docx':
                    # LibreOffice converts with .pdf extension, not _temp.pdf
                    subprocess.run([
                        'libreoffice', '--headless', '--convert-to', 'pdf',
                        '--outdir', temp_dir, input_path
                    ], check=True)

                    converted_pdf = os.path.join(temp_dir, base + '.pdf')
                    if os.path.exists(converted_pdf):
                        temp_pdfs.append(converted_pdf)
                    else:
                        errors.append(f"Conversion failed for {filename}")

                elif ext == '.txt':
                    content = open(input_path, 'r', encoding='utf-8').read()
                    pdf_path = os.path.join(temp_dir, base + '.pdf')
                    HTML(string=f"<pre>{content}</pre>").write_pdf(pdf_path)
                    temp_pdfs.append(pdf_path)

                elif ext in ['.jpg', '.jpeg', '.png']:
                    pdf_path = os.path.join(temp_dir, base + '.pdf')
                    img = Image.open(input_path).convert('RGB')
                    img.save(pdf_path)
                    temp_pdfs.append(pdf_path)

                elif ext == '.html':
                    pdf_path = os.path.join(temp_dir, base + '.pdf')
                    HTML(input_path).write_pdf(pdf_path)
                    temp_pdfs.append(pdf_path)

                elif ext == '.pdf':
                    temp_pdfs.append(input_path)

                else:
                    errors.append(f"Unsupported file type: {filename}")

            except Exception as e:
                errors.append(f"Error converting {filename}: {str(e)}")

        if not temp_pdfs:
            return jsonify({"error": "No convertible files", "details": errors}), 400

        try:
            combined_pdf_path = os.path.join(temp_dir, 'combined_output.pdf')
            merger = PdfMerger()
            for pdf_file in temp_pdfs:
                merger.append(pdf_file)
            merger.write(combined_pdf_path)
            merger.close()

            return send_file(combined_pdf_path, mimetype='application/pdf', download_name='combined_output.pdf')

        except Exception as e:
            return jsonify({"error": "Failed to merge PDFs", "details": str(e), "partial_errors": errors}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify, send_file
import os
import tempfile
import subprocess

app = Flask(__name__)

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
            # Run LibreOffice in headless mode to convert to PDF
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

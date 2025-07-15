from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import subprocess
from PIL import Image
from weasyprint import HTML

app = Flask(__name__)
CORS(app)  # Allow all origins

@app.route("/convert", methods=["POST"])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    supported = ['.docx', '.txt', '.html', '.jpg', '.jpeg', '.png']
    if ext not in supported:
        return jsonify({"error": f"Unsupported file type: {ext}"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, filename)
        file.save(input_path)
        output_path = os.path.join(temp_dir, "converted.pdf")

        try:
            if ext == '.docx':
                subprocess.run([
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', temp_dir,
                    input_path
                ], check=True)
                output_path = os.path.join(temp_dir, filename.replace(ext, '.pdf'))

            elif ext in ['.txt', '.html']:
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if ext == '.txt':
                    content = f"<pre>{content}</pre>"
                HTML(string=content).write_pdf(output_path)

            elif ext in ['.jpg', '.jpeg', '.png']:
                img = Image.open(input_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(output_path)

            else:
                return jsonify({"error": "Conversion not implemented"}), 400

            return send_file(output_path, mimetype="application/pdf", download_name="converted.pdf")

        except Exception as e:
            return jsonify({"error": "Conversion failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

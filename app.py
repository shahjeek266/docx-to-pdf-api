from flask import Flask, request, send_file, jsonify
import os
import tempfile
import subprocess

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename

    if not filename.lower().endswith('.docx'):
        return jsonify({"error": "Only .docx files are supported"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        docx_path = os.path.join(temp_dir, filename)
        file.save(docx_path)

        try:
            # Convert .docx to .pdf using LibreOffice
            subprocess.run([
                "libreoffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", temp_dir,
                docx_path
            ], check=True)

            pdf_filename = filename.rsplit(".", 1)[0] + ".pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)

            if not os.path.exists(pdf_path):
                return jsonify({"error": "PDF conversion failed"}), 500

            return send_file(pdf_path, mimetype="application/pdf", as_attachment=True, download_name="converted.pdf")
        
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Conversion error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

from flask import Flask, request, send_file, jsonify
import os
import tempfile
import mammoth
import pdfkit

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.endswith(".docx"):
        return jsonify({"error": "Only .docx files are supported"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        docx_path = os.path.join(temp_dir, file.filename)
        file.save(docx_path)

        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value

        html_path = os.path.join(temp_dir, "converted.html")
        with open(html_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)

        pdf_path = os.path.join(temp_dir, "converted.pdf")
        pdfkit.from_file(html_path, pdf_path)

        return send_file(pdf_path, download_name="converted.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

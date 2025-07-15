from flask import Flask, request, jsonify, send_file
import os
import tempfile
import shutil
import pythoncom
import comtypes.client

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert():
    pythoncom.CoInitialize()  # Fix for COM threading

    if 'file' not in request.files:
        pythoncom.CoUninitialize()
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename

    if not filename.lower().endswith('.docx'):
        pythoncom.CoUninitialize()
        return jsonify({"error": "Only .docx files are supported"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        docx_path = os.path.join(temp_dir, filename)
        pdf_path = os.path.join(temp_dir, 'converted.pdf')
        safe_pdf_path = os.path.join(tempfile.gettempdir(), f'converted_{os.getpid()}.pdf')

        file.save(docx_path)

        try:
            word = comtypes.client.CreateObject('Word.Application')
            word.Visible = False
            word.DisplayAlerts = 0
            doc = word.Documents.Open(docx_path)
            doc.SaveAs(pdf_path, FileFormat=17)
            doc.Close()
            word.Quit()

            # Copy the file to avoid permission error on deletion
            shutil.copy(pdf_path, safe_pdf_path)

            return send_file(safe_pdf_path, mimetype='application/pdf', download_name='converted.pdf')

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            pythoncom.CoUninitialize()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

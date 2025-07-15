
# 📄 Any File to PDF Converter – Web API (with WordPress Shortcode Integration)

A lightweight, open-source Flask API deployed on **Railway** that converts and merges documents and images into PDF files. This system powers a frontend WordPress site using custom shortcodes to provide user-friendly upload forms.

---

## 🚀 Features

- ✅ Convert `.docx` files to PDF  
- 📦 Convert multiple `.docx` files to PDFs (ZIP download)  
- 🔗 Merge multiple PDF files into one  
- 🧷 Combine and convert mixed file types (`.docx`, `.txt`, `.html`, `.jpg`, `.png`, `.pdf`) into a single merged PDF  
- ⚡ Powered by `LibreOffice`, `WeasyPrint`, `PyPDF2`, and `Pillow`  
- 🌐 Works with WordPress shortcodes on the frontend  
- 🎯 Deployed and tested via [Railway](https://railway.app/)  

---

## 📡 API Endpoints

All endpoints accept `POST` requests with `multipart/form-data`.

| Endpoint             | Description                                             | Input Field(s)       | Output Format        |
|----------------------|---------------------------------------------------------|----------------------|----------------------|
| `/convert`           | Convert a single `.docx` file to PDF                   | `file`               | PDF                  |
| `/convert-multiple`  | Convert multiple `.docx` files to individual PDFs      | `files[]`            | ZIP of PDFs          |
| `/merge-pdfs`        | Merge multiple `.pdf` files into one PDF              | `files[]`            | Single merged PDF    |
| `/combine-mixed`     | Merge & convert `.docx`, `.txt`, `.html`, `.jpg`, etc. | `files`              | Single merged PDF    |

---

## 📦 Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### requirements.txt

```
Flask==3.1.1
mammoth==1.9.1
pdfkit==1.0.0
PyMuPDF==1.26.3
Werkzeug==3.1.3
gunicorn==21.2.0
requests
flask-cors==3.0.10
pillow
weasyprint
```

### System Dependencies

- LibreOffice (required for `.docx` to PDF conversion)  
- Fonts (WeasyPrint requires standard system fonts)

---

## 🖥️ Local Development

```bash
python app.py
```

Server will run at: `http://localhost:5000`

---

## ☁️ Deployment on Railway

1. Create a new Railway project  
2. Upload your Flask app or connect via GitHub  
3. Set the start command:
   ```bash
   gunicorn app:app
   ```
4. Deploy and test the endpoints

---

## 🌐 WordPress Shortcode Integration

The backend API connects to WordPress via custom shortcodes. Each shortcode generates a file upload form with real-time feedback and download options.

### Example Shortcodes

```php
[docx_to_pdf_form]
[mixed_to_pdf_form]
```

Each shortcode provides:
- File upload fields  
- Progress messages and download links  
- AJAX-based interaction using JavaScript `fetch()`  

### Supported Forms

1. **Single `.docx` to PDF**
2. **Multiple `.docx` to ZIP of PDFs**
3. **Merge `.pdf` files**
4. **Combine and convert mixed types into a single PDF**

---

## 📂 Project Structure

```
.
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🧪 Example: `/combine-mixed` Endpoint

Supported file types:
- `.docx` ➜ PDF via LibreOffice
- `.txt` or `.html` ➜ PDF via WeasyPrint
- `.jpg`, `.jpeg`, `.png` ➜ PDF via Pillow
- `.pdf` ➜ Merged as-is

All files are converted to PDFs and merged into a **single output PDF**.

---

## 🛠️ Optimizations

- Uses `tempfile.TemporaryDirectory()` to handle secure, isolated file conversion
- Designed to support low-resource free deployments (like Railway)
- Fast PDF generation with optional enhancements (progress bar, loading UI)

---

## 👤 Author

**Shahmir Khan** – [shahmirkhan.net](https://shahmirkhan.net)

For questions, contributions, or freelance inquiries, open an issue or reach out via the website.

---

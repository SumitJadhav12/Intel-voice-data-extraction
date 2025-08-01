InvoiceIntel
Overview
InvoiceIntel is a Python-based application that extracts key fields from invoice images/PDFs using Tesseract OCR and displays structured data via a web interface.
Setup

Install Python 3.8+
Install Tesseract OCR:
Ubuntu: sudo apt-get install tesseract-ocr
macOS: brew install tesseract
Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki


Install dependencies:pip install flask pytesseract pillow pytest


Clone the repo and run:python app.py



API Specification

POST /invoices: Upload invoice image/PDF
Input: multipart/form-data with file
Output: JSON with invoice ID and extracted data


GET /invoices/{id}: Retrieve extracted invoice data
Output: JSON with extracted fields


POST /accounting/entries: Mock accounting integration
Input: JSON with invoice data
Output: JSON with status



UI Usage

Open http://localhost:5000 in a browser
Upload an invoice image
View extracted fields in a table
Data is automatically pushed to mock accounting endpoint

Testing
Run tests with:
pytest app.py

Sample Data

Sample invoices are in the samples/ directory
Includes 3 sample invoice images

Notes

Uses regex for parsing; no ML model implemented for simplicity
All tools are free and open-source
See prompt_log.md for parsing details
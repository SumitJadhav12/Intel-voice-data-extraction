from flask import Flask, request, jsonify, render_template
import os
import pytesseract
from PIL import Image
import re
import json
from datetime import datetime
import uuid
import pytest
from pdf2image import convert_from_path

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
EXTRACTED_DATA = {}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to extract text using Tesseract from image or PDF
def extract_text_from_file(file_path):
    try:
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path)
            text = ''
            for image in images:
                text += pytesseract.image_to_string(image)
            return text
        else:
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
    except Exception as e:
        return str(e)

# Helper function to parse invoice data with adaptive patterns
def parse_invoice(text):
    invoice_data = {
        'invoice_number': '',
        'date': '',
        'vendor': '',
        'line_items': [],
        'total': 0.0
    }

    # Dynamic patterns based on common invoice field variations
    patterns = {
        'invoice_number': r'(?:Invoice\s*#?|Invoice\s*Number|Order\s*No\.?|Ref\s*No\.?)\s*[:\s]*([\w\d-]+)',
        'date': r'(?:Date|Invoice\s*Date|Issue\s*Date|Due\s*Date)\s*[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        'vendor': r'(?:From|Vendor|Bill\s*To|Sold\s*To|Supplier|Company)\s*[:\s]*([^\n]+)',
        'total': r'(?:Total|Grand\s*Total|Amount\s*Due|Balance\s*Due)\s*[:\s]*\$?([\d,.]+\.?\d*)',
        'line_items': r'(\d+)\s+([^\d$\n]+)\s+\$?([\d,.]+\.?\d*)'
    }

    # Extract fields with fallback to text search
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not invoice_data['invoice_number']:
            match = re.search(patterns['invoice_number'], line, re.IGNORECASE)
            if match:
                invoice_data['invoice_number'] = match.group(1).strip()
        if not invoice_data['date']:
            match = re.search(patterns['date'], line, re.IGNORECASE)
            if match:
                invoice_data['date'] = match.group(1).strip()
        if not invoice_data['vendor']:
            match = re.search(patterns['vendor'], line, re.IGNORECASE)
            if match:
                invoice_data['vendor'] = match.group(1).strip()

    # Extract total
    total_match = re.search(patterns['total'], text, re.IGNORECASE)
    if total_match:
        total_str = total_match.group(1).replace(',', '')
        invoice_data['total'] = float(total_str)

    # Extract line items
    item_matches = re.finditer(patterns['line_items'], text, re.IGNORECASE)
    for match in item_matches:
        quantity = int(match.group(1))
        description = match.group(2).strip()
        price = float(match.group(3).replace(',', ''))
        invoice_data['line_items'].append({
            'quantity': quantity,
            'description': description,
            'price': price
        })

    return invoice_data

# Upload endpoint
@app.route('/invoices', methods=['POST'])
def upload_invoice():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save file
    invoice_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, f"{invoice_id}{os.path.splitext(file.filename)[1]}")
    file.save(file_path)

    # Extract and parse
    text = extract_text_from_file(file_path)
    invoice_data = parse_invoice(text)
    invoice_data['id'] = invoice_id
    EXTRACTED_DATA[invoice_id] = invoice_data

    return jsonify({'id': invoice_id, 'data': invoice_data}), 200

# Display API
@app.route('/invoices/<id>', methods=['GET'])
def get_invoice(id):
    if id in EXTRACTED_DATA:
        return jsonify(EXTRACTED_DATA[id]), 200
    return jsonify({'error': 'Invoice not found'}), 404

# Mock accounting integration
@app.route('/accounting/entries', methods=['POST'])
def accounting_entry():
    data = request.json
    # Mock processing
    return jsonify({'status': 'success', 'data': data}), 200

# Web UI
@app.route('/')
def index():
    return render_template('index.html')

# Test cases
def test_ocr_extraction():
    sample_text = """
    Order No.: ORD2025-001
    Due Date: 02/08/2025
    Supplier: ABC Corp
    1 Product X $15.00
    2 Product Y $25.00
    Amount Due: $40.00
    """
    data = parse_invoice(sample_text)
    assert data['invoice_number'] == 'ORD2025-001'
    assert data['date'] == '02/08/2025'
    assert data['vendor'] == 'ABC Corp'
    assert len(data['line_items']) == 2
    assert data['total'] == 40.00

if __name__ == '__main__':
    app.run(debug=True)
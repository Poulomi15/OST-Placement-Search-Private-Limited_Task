from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd
import re

app = Flask(__name__)

# Set the directory where CV files will be uploaded
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('extract_info', filename=filename))
    else:
        return redirect(request.url)

def extract_info_from_cv(file_path):
    # Open the CV file and extract text
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract email IDs using regular expression
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)

    # Extract phone numbers using regular expression
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    phones = re.findall(phone_pattern, text)

    return emails, phones, text

@app.route('/extract/<filename>')
def extract_info(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    emails, phones, text = extract_info_from_cv(file_path)

    # Create a Pandas DataFrame to store the information
    data = {'Email': emails, 'Phone': phones, 'Text': [text]}
    df = pd.DataFrame(data)

    # Export the DataFrame to an Excel file
    excel_filename = os.path.splitext(filename)[0] + '.xlsx'
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
    df.to_excel(excel_path, index=False)

    return redirect(url_for('download_excel', filename=excel_filename))

@app.route('/download/<filename>')
def download_excel(filename):
    return redirect(url_for('static', filename='uploads/' + filename))

if __name__ == '__main__':
    app.run(debug=True)

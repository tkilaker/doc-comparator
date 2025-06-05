import os
import tempfile
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from docx import Document
import diff_match_patch as dmp_module

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file using PyMuPDF"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_path):
    """Extract text from DOCX file using python-docx"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")

def compare_texts(text1, text2):
    """Compare two texts and return differences using diff-match-patch"""
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diffs)
    
    # Convert diffs to HTML format
    html_diff = []
    for op, data in diffs:
        if op == dmp_module.diff_match_patch.DIFF_INSERT:
            html_diff.append(f'<span class="diff-insert">{data}</span>')
        elif op == dmp_module.diff_match_patch.DIFF_DELETE:
            html_diff.append(f'<span class="diff-delete">{data}</span>')
        else:  # DIFF_EQUAL
            html_diff.append(data)
    
    return ''.join(html_diff)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare_documents():
    try:
        # Check if files were uploaded
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({'error': 'Please upload both files'}), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        # Check if files are selected
        if file1.filename == '' or file2.filename == '':
            return jsonify({'error': 'Please select both files'}), 400
        
        # Check file extensions
        if not (allowed_file(file1.filename) and allowed_file(file2.filename)):
            return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400
        
        # Save uploaded files temporarily
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
        
        file1.save(filepath1)
        file2.save(filepath2)
        
        try:
            # Extract text from both files
            if filename1.lower().endswith('.pdf'):
                text1 = extract_text_from_pdf(filepath1)
            else:  # .docx
                text1 = extract_text_from_docx(filepath1)
            
            if filename2.lower().endswith('.pdf'):
                text2 = extract_text_from_pdf(filepath2)
            else:  # .docx
                text2 = extract_text_from_docx(filepath2)
            
            # Compare texts
            diff_html = compare_texts(text1, text2)
            
            return jsonify({
                'success': True,
                'file1_name': filename1,
                'file2_name': filename2,
                'diff_html': diff_html
            })
        
        finally:
            # Clean up uploaded files
            if os.path.exists(filepath1):
                os.remove(filepath1)
            if os.path.exists(filepath2):
                os.remove(filepath2)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

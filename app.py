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

def normalize_text(text):
    """Aggressively normalizes text by removing all leading/trailing whitespace and blank lines."""
    import re
    
    # Remove soft hyphens and other invisible control characters
    text = text.replace('\xad', '')  # Soft hyphen
    text = text.replace('\u200b', '')  # Zero-width space
    text = text.replace('\u200c', '')  # Zero-width non-joiner
    text = text.replace('\u200d', '')  # Zero-width joiner
    text = text.replace('\ufeff', '')  # Byte order mark
    text = text.replace('\u2060', '')  # Word joiner
    
    # Replace non-breaking spaces and other unicode whitespace with regular spaces
    text = text.replace('\xa0', ' ')  # Non-breaking space
    text = text.replace('\u2009', ' ')  # Thin space
    text = text.replace('\u200a', ' ')  # Hair space
    text = text.replace('\u2007', ' ')  # Figure space
    text = text.replace('\u2008', ' ')  # Punctuation space
    text = text.replace('\u202f', ' ')  # Narrow no-break space
    text = text.replace('\u205f', ' ')  # Medium mathematical space
    text = text.replace('\u3000', ' ')  # Ideographic space
    
    # Use regex to replace any remaining unicode whitespace characters with regular spaces
    text = re.sub(r'[\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]', ' ', text)
    
    # Remove any remaining control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Split into lines and aggressively clean each line
    lines = text.splitlines()
    cleaned_lines = []
    
    for line in lines:
        # Strip both leading and trailing whitespace
        cleaned_line = line.strip()
        # Only keep non-empty lines
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    # Join with single newlines - this creates a canonical format
    return '\n'.join(cleaned_lines)

def compare_texts(text1, text2):
    """Compare two texts and return differences using diff-match-patch"""
    # Normalize both texts to ignore trailing whitespace and line ending differences
    normalized_text1 = normalize_text(text1)
    normalized_text2 = normalize_text(text2)
    
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(normalized_text1, normalized_text2)
    dmp.diff_cleanupSemantic(diffs)
    
    # Convert diffs to HTML format with simplified logic
    html_diff = []
    for op, data in diffs:
        if op == dmp_module.diff_match_patch.DIFF_INSERT:
            # Only show insertions that have actual content
            if data.strip():
                html_diff.append(f'<span class="diff-insert">{data}</span>')
        elif op == dmp_module.diff_match_patch.DIFF_DELETE:
            # Only show deletions that have actual content
            if data.strip():
                html_diff.append(f'<span class="diff-delete">{data}</span>')
        else:  # DIFF_EQUAL
            # Show unchanged text as-is
            html_diff.append(data)
    
    return ''.join(html_diff)

def clean_whitespace_for_display(text):
    """Clean up whitespace for better display"""
    if not text:
        return ''
    
    import re
    
    # Replace multiple consecutive newlines with maximum of 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Don't show text that's only whitespace unless it's a meaningful line break
    if not text.strip():
        return '\n' if '\n' in text else ''
    
    return text

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

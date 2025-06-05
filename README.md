# Document Comparator

A web-based tool that enables non-technical users to compare the textual content of two documents: one in PDF format and the other in DOCX format. The tool provides a simple, intuitive interface for uploading documents and displays differences in a clear, visually distinct format suitable for manual transcription.

## Features

- **Simple Web Interface**: Easy-to-use drag-and-drop file upload
- **Multiple Format Support**: Compare PDF and DOCX documents
- **Visual Difference Display**: Clear highlighting of added, deleted, and unchanged text
- **Responsive Design**: Works on desktop and mobile devices
- **File Validation**: Automatic validation of file types and sizes
- **Error Handling**: User-friendly error messages and feedback

## Requirements

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone or download this repository**

   ```bash
   git clone <repository-url>
   cd doc_comparator
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**

   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:

   ```
   http://localhost:5001
   ```

3. **Upload your documents**:

   - Click on the file input fields or drag and drop your files
   - Select one PDF file and one DOCX file (or any combination)
   - Maximum file size: 16MB per file

4. **Compare documents**:

   - Click the "Compare Documents" button
   - Wait for processing to complete
   - Review the highlighted differences

5. **Interpret the results**:
   - **Green highlighting**: Text that was added
   - **Red highlighting with strikethrough**: Text that was deleted
   - **Normal text**: Unchanged content

## File Support

- **PDF files**: `.pdf` extension
- **DOCX files**: `.docx` extension (Microsoft Word documents)

## Technical Details

### Backend

- **Framework**: Flask (Python web framework)
- **PDF Processing**: PyMuPDF for text extraction from PDF files
- **DOCX Processing**: python-docx for text extraction from Word documents
- **Difference Analysis**: Google's diff-match-patch library for robust text comparison

### Frontend

- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Responsive design with modern styling
- **JavaScript**: Asynchronous file upload and dynamic UI updates

### Project Structure

```
doc_comparator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── script.js     # Frontend functionality
└── uploads/              # Temporary file storage (auto-created)
```

## Security Features

- File type validation (only PDF and DOCX allowed)
- File size limits (16MB maximum)
- Secure filename handling
- Automatic cleanup of uploaded files
- Input sanitization

## Troubleshooting

### Common Issues

1. **"Module not found" errors**

   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **Port already in use**

   - The application runs on port 5001 by default
   - If the port is busy, modify the port in `app.py` or stop other services using port 5001

3. **File upload fails**

   - Check file size (must be under 16MB)
   - Ensure file format is PDF or DOCX
   - Try refreshing the page and uploading again

4. **Text extraction issues**
   - Some PDF files may have text as images (scanned documents) - these won't work
   - Ensure DOCX files are not corrupted
   - Try with different document files to isolate the issue

### Browser Compatibility

The application works best with modern browsers:

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Use Cases

This tool is particularly useful for:

- **Script Updates**: Actors comparing different versions of scripts
- **Document Revisions**: Reviewing changes between document versions
- **Content Migration**: Comparing content when moving between formats
- **Quality Assurance**: Verifying document conversions
- **Legal Documents**: Identifying changes in contracts or agreements

## Limitations

- Text-only comparison (images, formatting, and layout are ignored)
- Scanned PDFs (image-based) cannot be processed
- Very large documents may take longer to process
- Complex formatting in DOCX files is stripped during text extraction

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

"""
Fieldwise - WEB INTERFACE DEPLOYMENT GUIDE
Production-ready web application for automated construction takeoffs

STACK:
- Backend: Flask (Python)
- Frontend: HTML/CSS/JavaScript
- File Upload: Drag & drop
- Processing: Background jobs
- Export: Excel download
- Auth: Optional (add later)

DEPLOYMENT OPTIONS:
1. Railway (recommended - easiest)
2. Heroku
3. AWS/GCP
4. Self-hosted
"""

# ═══════════════════════════════════════════════════════════════
# STEP 1: INSTALL DEPENDENCIES
# ═══════════════════════════════════════════════════════════════

"""
requirements.txt:

flask==3.0.0
anthropic
google-cloud-vision
opencv-python-headless
numpy
Pillow
openpyxl
xlsxwriter
scikit-image
shapely
rich
flask-cors
werkzeug
"""

# ═══════════════════════════════════════════════════════════════
# STEP 2: FLASK BACKEND (app.py)
# ═══════════════════════════════════════════════════════════════

FLASK_APP = '''
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from integrated_agent import analyze_drawing
from excel_export import export_to_excel

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_drawing():
    """Upload and analyze drawing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    trade = request.form.get('trade', 'electrical')
    project_name = request.form.get('project_name', 'Project')
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Analyze
        analysis = analyze_drawing(filepath, trade)
        
        # Export to Excel
        excel_path = export_to_excel(analysis, filename, project_name)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'excel_file': excel_path
        })
    
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/api/download/<filename>')
def download_excel(filename):
    """Download Excel file"""
    return send_file(filename, as_attachment=True)

@app.route('/api/calibrate', methods=['POST'])
def calibrate_scale():
    """Calibrate drawing scale"""
    data = request.json
    # Store calibration in session or database
    return jsonify({'success': True})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
'''

# ═══════════════════════════════════════════════════════════════
# STEP 3: FRONTEND (index.html)
# ═══════════════════════════════════════════════════════════════

FRONTEND_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fieldwise - Automated Takeoff</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 40px;
            color: white;
            text-align: center;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; font-size: 1.1em; }
        .content { padding: 40px; }
        .upload-zone {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 60px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: #f8f9ff;
        }
        .upload-zone:hover { 
            border-color: #764ba2;
            background: #f0f2ff;
        }
        .upload-zone.dragover {
            border-color: #2ecc71;
            background: #e8f8f0;
        }
        .settings {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 30px 0;
        }
        select, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 10px;
            display: none;
        }
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Fieldwise</h1>
            <p class="subtitle">Automated Construction Takeoffs - Powered by AI</p>
        </div>
        
        <div class="content">
            <div class="upload-zone" id="uploadZone">
                <h2>📄 Drop Drawing Here or Click to Upload</h2>
                <p style="margin-top: 10px; opacity: 0.7;">Supports: PDF, PNG, JPG - All Trades</p>
                <input type="file" id="fileInput" accept=".pdf,.png,.jpg,.jpeg" style="display: none">
            </div>
            
            <div class="settings">
                <div>
                    <label>Trade:</label>
                    <select id="tradeSelect">
                        <option value="electrical">Electrical</option>
                        <option value="mechanical">HVAC/Mechanical</option>
                        <option value="plumbing">Plumbing</option>
                        <option value="fire_protection">Fire Protection</option>
                    </select>
                </div>
                <div>
                    <label>Project Name:</label>
                    <input type="text" id="projectName" placeholder="Enter project name">
                </div>
            </div>
            
            <div style="text-align: center;">
                <button id="analyzeBtn" style="display: none;">Analyze Drawing</button>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 20px; font-size: 18px;">Analyzing drawing...</p>
            </div>
            
            <div class="results" id="results">
                <h3>✅ Analysis Complete!</h3>
                <div id="analysisText" style="margin: 20px 0; white-space: pre-wrap;"></div>
                <button id="downloadBtn">Download Excel Takeoff</button>
            </div>
        </div>
    </div>
    
    <script>
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        let selectedFile = null;
        let excelFile = null;
        
        uploadZone.onclick = () => fileInput.click();
        
        fileInput.onchange = (e) => {
            selectedFile = e.target.files[0];
            uploadZone.innerHTML = `<h2>✓ ${selectedFile.name}</h2><p>Ready to analyze</p>`;
            analyzeBtn.style.display = 'inline-block';
        };
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        
        uploadZone.addEventListener('dragover', () => uploadZone.classList.add('dragover'));
        uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
        
        uploadZone.addEventListener('drop', (e) => {
            uploadZone.classList.remove('dragover');
            selectedFile = e.dataTransfer.files[0];
            uploadZone.innerHTML = `<h2>✓ ${selectedFile.name}</h2><p>Ready to analyze</p>`;
            analyzeBtn.style.display = 'inline-block';
        });
        
        analyzeBtn.onclick = async () => {
            loading.style.display = 'block';
            analyzeBtn.style.display = 'none';
            
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('trade', document.getElementById('tradeSelect').value);
            formData.append('project_name', document.getElementById('projectName').value || 'Project');
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    loading.style.display = 'none';
                    results.style.display = 'block';
                    document.getElementById('analysisText').textContent = data.analysis;
                    excelFile = data.excel_file;
                }
            } catch (error) {
                alert('Error: ' + error.message);
                loading.style.display = 'none';
                analyzeBtn.style.display = 'inline-block';
            }
        };
        
        document.getElementById('downloadBtn').onclick = () => {
            window.location.href = `/api/download/${excelFile}`;
        };
    </script>
</body>
</html>
'''

# ═══════════════════════════════════════════════════════════════
# STEP 4: DEPLOY TO RAILWAY (EASIEST)
# ═══════════════════════════════════════════════════════════════

RAILWAY_DEPLOY = """
1. Install Railway CLI:
   npm install -g @railway/cli

2. Login:
   railway login

3. Initialize project:
   railway init

4. Add environment variables:
   railway variables set GOOGLE_APPLICATION_CREDENTIALS=./google-vision-key.json
   railway variables set ANTHROPIC_API_KEY=your_key_here

5. Deploy:
   railway up

6. Get URL:
   railway domain

DONE! Your app is live at: https://your-app.railway.app
"""

# ═══════════════════════════════════════════════════════════════
# STEP 5: BATCH PROCESSING SCRIPT
# ═══════════════════════════════════════════════════════════════

BATCH_SCRIPT = '''
"""
Batch process multiple drawings
Usage: python batch_process.py /path/to/drawings electrical
"""

import sys
import os
from integrated_agent import analyze_drawing
from excel_export import export_to_excel
from pathlib import Path

def batch_process(folder_path, trade='electrical'):
    """Process all drawings in folder"""
    
    drawings = list(Path(folder_path).glob('*.png')) + \\
               list(Path(folder_path).glob('*.jpg')) + \\
               list(Path(folder_path).glob('*.pdf'))
    
    print(f"Found {len(drawings)} drawings to process")
    
    for i, drawing in enumerate(drawings, 1):
        print(f"\\n[{i}/{len(drawings)}] Processing: {drawing.name}")
        
        try:
            # Analyze
            analysis = analyze_drawing(str(drawing), trade)
            
            # Export
            excel_file = export_to_excel(analysis, drawing.stem, "Batch Project")
            
            print(f"✓ Complete: {excel_file}")
            
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py <folder> [trade]")
        sys.exit(1)
    
    folder = sys.argv[1]
    trade = sys.argv[2] if len(sys.argv) > 2 else 'electrical'
    
    batch_process(folder, trade)
'''

print("WEB INTERFACE DEPLOYMENT GUIDE CREATED")
print("Files to create:")
print("1. app.py (Flask backend)")
print("2. index.html (Frontend)")  
print("3. batch_process.py (Batch processing)")
print("4. requirements.txt")
print("\\nDeploy to Railway in 5 minutes!")

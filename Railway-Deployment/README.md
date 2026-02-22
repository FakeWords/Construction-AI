# Construction AI - Drawing Analysis Tool

AI-powered drawing analysis and material takeoff for electrical contractors.

## Features (V1)

- ✅ PDF upload (including Bluebeam files)
- ✅ Automatic panel detection
- ✅ Circuit counting
- ✅ Conduit run identification  
- ✅ Material takeoff with 15% overage
- ✅ Issue flagging (voltage drop, outdoor locations, etc.)
- ✅ Copy/paste report generation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Run Backend API

```bash
python main.py
```

API runs on `http://localhost:8000`

### 3. Open Web Interface

Open `index.html` in your browser

## How to Use

1. Drop PDF drawing files or click to browse
2. Click "Analyze Drawings"
3. View material counts, flagged issues, and notes
4. Copy report to clipboard or export as JSON

## Supported Formats

- Standard PDF files
- Bluebeam PDF files (.pdf with markup data)
- Multiple sheets in single PDF
- CAD-generated drawings with text

**Note:** Scanned drawings (image-only PDFs) require OCR - coming in next update.

## What It Detects

### Panels
- Distribution panels (MDP, SDP, LP, PP)
- Panel schedules
- Panel locations

### Circuits
- Circuit breaker counts
- Pole configurations
- Amperage ratings

### Conduit
- EMT, RGS, IMC, PVC, FMC
- Conduit sizes
- Run counts

### Issues Flagged
- ⚠️ High conduit count (voltage drop risk)
- 🔌 Transformers detected
- 🌧️ Outdoor/weatherproof locations
- ⚡ Ground level (strikable areas)
- 📋 High panel count

## Roadmap

**Week 1** (Current)
- [x] PDF parsing
- [x] Basic material detection
- [x] Web interface

**Week 2**
- [ ] Supplier pricing integration (Platt, Graybar)
- [ ] Cost estimates
- [ ] OCR for scanned drawings

**Week 3**
- [ ] Revision comparison (redline changes)
- [ ] Change tracking
- [ ] Material delta between revisions

**Week 4**
- [ ] NEC code lookup database
- [ ] Code reference tool
- [ ] Violation flagging

**Month 2**
- [ ] RFI tracking system
- [ ] Project organization
- [ ] Multi-project dashboard

**Month 3**
- [ ] Desktop application (Electron)
- [ ] Offline mode
- [ ] Enhanced UI

## Tech Stack

- **Backend:** Python + FastAPI
- **PDF Processing:** PyPDF2
- **Frontend:** HTML + Vanilla JS
- **Coming Soon:** OCR (Tesseract), ML detection

## API Endpoints

### `POST /analyze-drawing`
Upload single PDF, get analysis

**Request:**
- File: PDF (multipart/form-data)

**Response:**
```json
{
  "filename": "drawing.pdf",
  "pages": 15,
  "panels_detected": [...],
  "circuits_count": 48,
  "conduit_runs": [...],
  "materials": {
    "Panels": 3,
    "Circuit Breakers": 55,
    "EMT Conduit (10' sticks)": 46
  },
  "flagged_issues": ["⚠️ ..."],
  "notes": ["✓ ..."]
}
```

### `POST /batch-analyze`
Upload multiple PDFs

### `GET /health`
Health check

## Development

```bash
# Run backend with auto-reload
uvicorn main:app --reload

# Access API docs
http://localhost:8000/docs
```

## Notes

- Material estimates include 15% overage factor
- Detection patterns optimized for electrical drawings
- Works best with CAD-generated PDFs
- Bluebeam markup data preserved but not yet analyzed

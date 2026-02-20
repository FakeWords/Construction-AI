"""
Construction AI - Drawing Analysis & Material Takeoff Tool
Backend API for processing electrical construction drawings
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import PyPDF2
import io
import re
from datetime import datetime
from nec_validator import NECValidator, NECVersion, NEC_QUICK_REFERENCE

app = FastAPI(
    title="Construction AI",
    description="AI-powered drawing analysis and material takeoff for electrical contractors",
    version="1.0.0"
)

# CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DrawingAnalysis(BaseModel):
    filename: str
    pages: int
    trade: str
    code_book: str
    nec_version: str
    panels_detected: List[Dict]
    circuits_count: int
    conduit_runs: List[Dict]
    materials: Dict[str, int]
    flagged_issues: List[str]
    code_violations: List[Dict]
    cost_estimate: Optional[float]
    notes: List[str]
    timestamp: str


class MaterialDetector:
    """Detects electrical materials and components from drawing text"""
    
    def __init__(self):
        # Common electrical patterns
        self.panel_patterns = [
            r'PANEL\s+([A-Z0-9\-]+)',
            r'MDP|SDP|LP\d+|PP\d+',
            r'DISTRIBUTION\s+PANEL'
        ]
        
        self.circuit_patterns = [
            r'(\d+)\s*POLE',
            r'(\d+)P',
            r'(\d+)\s*AMP',
            r'CIRCUIT\s+(\d+)'
        ]
        
        self.conduit_patterns = [
            r'(\d+/?\d*)"?\s*(EMT|RGS|IMC|PVC|FMC)',
            r'(EMT|RGS|IMC|PVC)\s*(\d+/?\d*)"?'
        ]
        
        self.wire_patterns = [
            r'#(\d+)\s*(AWG|THHN|THWN)',
            r'(\d+/?\d*)\s*AWG'
        ]
    
    def detect_panels(self, text: str) -> List[Dict]:
        """Find all panel references"""
        panels = []
        for pattern in self.panel_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                panels.append({
                    "name": match.group(0),
                    "location": match.start()
                })
        return panels
    
    def detect_circuits(self, text: str) -> int:
        """Count circuit breakers"""
        count = 0
        for pattern in self.circuit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        return count
    
    def detect_conduit(self, text: str) -> List[Dict]:
        """Find conduit runs and sizes"""
        conduits = []
        for pattern in self.conduit_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                conduits.append({
                    "size": match.group(1) if len(match.groups()) > 0 else "unknown",
                    "type": match.group(2) if len(match.groups()) > 1 else "EMT",
                    "text": match.group(0)
                })
        return conduits
    
    def estimate_materials(self, panels: List, circuits: int, conduits: List) -> Dict[str, int]:
        """Rough material estimate with 15% overage"""
        materials = {}
        
        # Panels
        materials["Panels"] = len(panels)
        
        # Breakers (from circuits)
        materials["Circuit Breakers"] = int(circuits * 1.15)  # 15% overage
        
        # Conduit (assume 10' sticks)
        total_conduit = len(conduits) * 20  # Assume avg 20' per run
        materials["EMT Conduit (10' sticks)"] = int((total_conduit / 10) * 1.15)
        
        # Couplings (1 per stick)
        materials["EMT Couplings"] = materials["EMT Conduit (10' sticks)"]
        
        # Wire (rough estimate)
        materials["THHN Wire (feet)"] = int(circuits * 50 * 1.15)  # 50' avg per circuit
        
        return materials
    
    def flag_issues(self, text: str, panels: List, conduits: List) -> List[str]:
        """Flag potential problems"""
        issues = []
        
        # Check for long conduit runs
        if len(conduits) > 50:
            issues.append("⚠️ High conduit count detected - verify voltage drop calculations")
        
        # Check for transformers
        if re.search(r'TRANSFORMER|XFMR', text, re.IGNORECASE):
            issues.append("🔌 Transformer detected - verify primary/secondary sizing")
        
        # Check for outdoor/wet locations
        if re.search(r'OUTDOOR|EXTERIOR|WEATHERPROOF|WP', text, re.IGNORECASE):
            issues.append("🌧️ Outdoor location - consider weatherproof/rigid conduit instead of EMT")
        
        # Check for ground level
        if re.search(r'GROUND\s+LEVEL|SLAB|FLOOR', text, re.IGNORECASE):
            issues.append("⚡ Ground level installation - may require rigid conduit in strikable areas")
        
        # Check panel count
        if len(panels) > 20:
            issues.append("📋 High panel count - verify load calculations and service sizing")
        
        return issues


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF (including Bluebeam PDFs)"""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")


@app.get("/")
async def root():
    return {
        "service": "Construction AI",
        "version": "1.0.0",
        "status": "active",
        "description": "AI-powered drawing analysis for electrical contractors"
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/analyze-drawing", response_model=DrawingAnalysis)
async def analyze_drawing(
    file: UploadFile = File(...),
    trade: str = Query("electrical", description="Trade: electrical, mechanical, architectural, structural, fire_protection, low_voltage"),
    code_book: str = Query("NEC_2023", description="Code book version"),
    nec_version: NECVersion = Query(NECVersion.NEC_2023, description="NEC Code Version (deprecated, use code_book)")
):
    """
    Analyze construction drawing with trade-specific code compliance check
    
    Accepts: PDF files (including Bluebeam .pdf)
    Returns: Material takeoff, code violations, flagged issues, cost estimate
    Supports: Electrical, Mechanical, Architectural, Structural, Fire Protection, Low Voltage
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read file
    contents = await file.read()
    
    # Extract text
    text = extract_text_from_pdf(contents)
    
    if not text.strip():
        raise HTTPException(
            status_code=400, 
            detail="No text found in PDF. File may be scanned image - OCR coming soon."
        )
    
    # Analyze drawing
    detector = MaterialDetector()
    
    panels = detector.detect_panels(text)
    circuits = detector.detect_circuits(text)
    conduits = detector.detect_conduit(text)
    materials = detector.estimate_materials(panels, circuits, conduits)
    issues = detector.flag_issues(text, panels, conduits)
    
    # NEC Code Validation
    nec = NECValidator(nec_version)
    
    # Check outdoor requirements
    nec.violations.extend(nec.check_outdoor_requirements(text))
    
    # Check grounding
    nec.violations.extend(nec.check_grounding(text))
    
    # Check GFCI/AFCI for detected locations
    for panel in panels:
        gfci_check = nec.check_gfci_required(panel.get("name", ""))
        if gfci_check:
            nec.violations.append(gfci_check)
        
        afci_check = nec.check_afci_required(panel.get("name", ""))
        if afci_check:
            nec.violations.append(afci_check)
    
    # Get code compliance summary
    code_summary = nec.generate_code_summary()
    
    # Generate notes
    notes = []
    notes.append(f"✓ Analyzed as {trade.upper()} trade drawing")
    notes.append(f"✓ Code compliance: {code_book}")
    notes.append(f"✓ Detected {len(panels)} panels across drawing set")
    notes.append(f"✓ Counted {circuits} circuit references")
    notes.append(f"✓ Found {len(conduits)} conduit runs")
    notes.append("✓ Material estimates include 15% overage factor")
    if code_summary["critical_violations"] > 0:
        notes.append(f"⚠️ {code_summary['critical_violations']} CRITICAL code violations found - review immediately")
    if code_summary["warnings"] > 0:
        notes.append(f"⚠️ {code_summary['warnings']} code warnings flagged")
    
    # Rough cost estimate (placeholder - will add real pricing later)
    cost_estimate = None  # Will implement supplier pricing integration
    
    # Get page count
    pdf_file = io.BytesIO(contents)
    reader = PyPDF2.PdfReader(pdf_file)
    page_count = len(reader.pages)
    
    return DrawingAnalysis(
        filename=file.filename,
        pages=page_count,
        trade=trade,
        code_book=code_book,
        nec_version=nec_version.value,
        panels_detected=panels,
        circuits_count=circuits,
        conduit_runs=conduits,
        materials=materials,
        flagged_issues=issues,
        code_violations=code_summary["violations"],
        cost_estimate=cost_estimate,
        notes=notes,
        timestamp=datetime.now().isoformat()
    )


@app.get("/nec-lookup/{article}")
async def nec_lookup(article: str):
    """
    Quick NEC code reference lookup
    Example: /nec-lookup/210.8 returns GFCI requirements
    """
    article_clean = article.upper().strip()
    
    if article_clean in NEC_QUICK_REFERENCE:
        return {
            "article": article_clean,
            "description": NEC_QUICK_REFERENCE[article_clean],
            "found": True
        }
    
    # Partial match
    matches = {k: v for k, v in NEC_QUICK_REFERENCE.items() if article_clean in k}
    if matches:
        return {
            "article": article_clean,
            "matches": matches,
            "found": True
        }
    
    return {
        "article": article_clean,
        "description": "Article not found in quick reference",
        "found": False,
        "suggestion": "Try searching: 210.8 (GFCI), 210.12 (AFCI), 250 (Grounding), 310.16 (Ampacity)"
    }


@app.get("/nec-all")
async def nec_all_references():
    """Get all NEC quick references"""
    return {
        "total": len(NEC_QUICK_REFERENCE),
        "references": NEC_QUICK_REFERENCE
    }


@app.post("/batch-analyze")
async def batch_analyze(files: List[UploadFile] = File(...)):
    """
    Analyze multiple drawing files at once
    Useful for analyzing entire drawing sets
    """
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 files per batch")
    
    results = []
    for file in files:
        try:
            # Process each file
            contents = await file.read()
            text = extract_text_from_pdf(contents)
            
            detector = MaterialDetector()
            panels = detector.detect_panels(text)
            circuits = detector.detect_circuits(text)
            conduits = detector.detect_conduit(text)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "panels": len(panels),
                "circuits": circuits,
                "conduits": len(conduits)
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "total_files": len(files),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

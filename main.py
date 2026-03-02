"""
Fieldwise AI - Construction Intelligence Platform
Backend API - Complete Production Version
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List, Dict, Optional
import PyPDF2
import io
import re
import os
import shutil
from datetime import datetime

# Auth and Database
from database import (
    init_db, get_db, get_user_by_email, create_user,
    create_project, get_user_projects, get_project_by_id,
    delete_project, share_project, get_shared_projects, update_last_login
)
from auth import hash_password, verify_password, create_token, get_current_user, get_optional_user

# NEC + Timecard
from nec_validator import NECValidator, NECVersion, NEC_QUICK_REFERENCE
from timecard_scanner import TimeCardScanner
from timecard_excel import create_timecard_excel

# Integrated drawing agent
from integrated_agent import IntegratedDrawingAgent
from excel_export import export_to_excel
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(
    title="Fieldwise AI",
    description="AI-powered construction intelligence platform",
    version="2.0.0"
)
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="."), name="static")

app.state.max_upload_size = 100 * 1024 * 1024  # 100MB

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    try:
        init_db()
        print("[DB] Database initialized")
    except Exception as e:
        print(f"[DB] Database init failed: {e}")


# ═══════════════════════════════════════════════════════════════
# STATIC PAGES
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    with open("index.html", "r") as f:
        return Response(content=f.read(), media_type="text/html")

@app.get("/login")
async def login_page():
    with open("login.html", "r") as f:
        return Response(content=f.read(), media_type="text/html")

@app.get("/signup")
async def signup_page():
    with open("signup.html", "r") as f:
        return Response(content=f.read(), media_type="text/html")

@app.get("/projects")
async def projects_page():
    with open("projects.html", "r") as f:
        return Response(content=f.read(), media_type="text/html")

@app.get("/drawings")
async def drawings_page():
    with open("drawings.html", "r") as f:
        return Response(content=f.read(), media_type="text/html")

@app.get("/timecards")
async def timecards_page():
    with open("timecards.html", "r") as f:
        return Response(content=f.read(), media_type="text/html")

@app.get("/field")
async def field_page():
    with open("field.html", "r") as f:
        return Response(content=f.read(), media_type="text/html")

@app.get("/cart")
async def cart_page():
    import os
    path = os.path.join(os.path.dirname(__file__), "cart.html")
    with open(path, "r") as f:
        return Response(content=f.read(), media_type="text/html")
@app.get("/cart")
async def cart_page():
    with open("cart.html", "r") as f:
        return Response(content=f.read(), media_type="text/html")

@app.get("/api/nearby-suppliers")
async def nearby_suppliers(lat: float, lng: float):
    try:
        import googlemaps
        gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY", ""))
        suppliers = []
        search_terms = ["Graybar Electric", "Rexel", "Wesco electrical", "Home Depot"]
        for term in search_terms:
            results = gmaps.places_nearby(
                location=(lat, lng),
                radius=25000,
                keyword=term
            )
            for place in results.get('results', [])[:1]:
                dist_result = gmaps.distance_matrix(
                    origins=[(lat, lng)],
                    destinations=[place['geometry']['location']],
                    mode='driving'
                )
                distance = dist_result['rows'][0]['elements'][0].get('distance', {}).get('text', '')
                suppliers.append({
                    'name': place['name'],
                    'address': place.get('vicinity', ''),
                    'distance': distance
                })
        return {"suppliers": suppliers}
    except Exception as e:
        return {"suppliers": [], "error": str(e)}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    import anthropic as ant
    data = await request.json()
    messages = data.get("messages", [])
    system = data.get("system", "")
    
    client = ant.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system,
        messages=messages
    )
    return {"content": response.content[0].text}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ═══════════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/signup")
async def signup(request: Request):
    data = await request.json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    company = data.get("company", "").strip()

    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="Name, email and password required")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = hash_password(password)
    user = create_user(name, email, password_hash, company)
    token = create_token(user["id"])

    return {"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}


@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    update_last_login(user["id"])
    token = create_token(user["id"])

    return {"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}


@app.get("/api/me")
async def get_me(request: Request):
    user = get_current_user(request)
    return {"id": user["id"], "name": user["name"], "email": user["email"], "company": user["company"]}


# ═══════════════════════════════════════════════════════════════
# PROJECT ENDPOINTS
# ═══════════════════════════════════════════════════════════════
@app.post("/api/projects/create-blank")
async def create_blank_project(request: Request):
    user = get_current_user(request)
    data = await request.json()
    name = data.get("name", "").strip()
    trade = data.get("trade", "general")
    code_book = data.get("code_book", "NEC_2023")
    if not name:
        raise HTTPException(status_code=400, detail="Name required")
    project = create_project(
        user_id=user["id"],
        name=name,
        trade=trade,
        code_book=code_book,
        filename="",
        analysis="",
        excel_filename=""
    )
    return dict(project)

@app.get("/api/projects")
async def list_projects(request: Request):
    user = get_current_user(request)
    own = get_user_projects(user["id"])
    shared = get_shared_projects(user["email"])
    return {
        "projects": [dict(p) for p in own],
        "shared": [dict(p) for p in shared]
    }


@app.get("/api/projects/{project_id}")
async def get_project(project_id: int, request: Request):
    user = get_current_user(request)
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return dict(project)


@app.delete("/api/projects/{project_id}")
async def remove_project(project_id: int, request: Request):
    user = get_current_user(request)
    delete_project(project_id, user["id"])
    return {"success": True}


@app.post("/api/projects/{project_id}/share")
async def share_project_endpoint(project_id: int, request: Request):
    user = get_current_user(request)
    data = await request.json()
    email = data.get("email", "").strip().lower()
    permission = data.get("permission", "view")

    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    project = get_project_by_id(project_id)
    if not project or project["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    share_project(project_id, user["id"], email, permission)
    return {"success": True, "message": f"Project shared with {email}"}


# ═══════════════════════════════════════════════════════════════
# DRAWING ANALYZER
# ═══════════════════════════════════════════════════════════════

@app.post("/api/analyze-drawing")
async def analyze_drawing_endpoint(
    request: Request,
    file: UploadFile = File(...),
    trade: str = Form("electrical"),
    project_name: str = Form("Project"),
    code_book: str = Form("NEC_2023")
):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        agent = IntegratedDrawingAgent(file_path, trade, code_book)
        analysis = agent.analyze()

        excel_file = export_to_excel(analysis, file.filename, project_name)

        user = get_optional_user(request)
        project_id = None
        if user:
            project = create_project(
                user_id=user["id"],
                name=project_name,
                trade=trade,
                code_book=code_book,
                filename=file.filename,
                analysis=analysis,
                excel_filename=os.path.basename(excel_file)
            )
            project_id = project["id"]

        return JSONResponse({
            "success": True,
            "analysis": analysis,
            "excel_file": os.path.basename(excel_file),
            "project_id": project_id
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/download-excel/{filename}")
async def download_excel(filename: str):
    try:
        with open(filename, "rb") as f:
            content = f.read()
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# FIELD PHOTO TOOL
# ═══════════════════════════════════════════════════════════════

@app.post("/api/analyze-photo")
async def analyze_photo_endpoint(
    request: Request,
    file: UploadFile = File(...),
    question: str = Form("What is this equipment? Give me a complete material list, labor estimate, and cost range."),
    vertical_add: float = Form(0),
    pixels_per_foot: float = Form(None)
):
    import base64
    import json
    import anthropic as ant

    try:
        contents = await file.read()
        b64 = base64.standard_b64encode(contents).decode("utf-8")

        media_type = file.content_type or "image/jpeg"
        if not media_type.startswith("image/"):
            media_type = "image/jpeg"

        scale_context = ""
        if pixels_per_foot:
            scale_context = f"\nScale calibrated: {pixels_per_foot:.2f} pixels = 1 foot."
        if vertical_add > 0:
            scale_context += f"\nAdd {vertical_add} feet to each run for vertical drops."

        prompt = f"""You are an expert construction estimator with 20+ years experience.

Analyze this field photo and answer: {question}
{scale_context}

Respond in this EXACT JSON format (no markdown, no extra text):
{{
    "identification": "What you see - equipment type, condition, brand/model, size/rating",
    "materials": [
        {{"item": "Material name", "qty": 2, "unit": "EA"}},
        {{"item": "Another material", "qty": 50, "unit": "LF"}}
    ],
    "materials_text": "Plain text summary if structured list not applicable",
    "labor": "Labor estimate: X-Y hours. Task breakdown...",
    "cost_range": "$X,XXX - $X,XXX",
    "notes": "Code requirements, warnings, or important observations"
}}"""

        client_ant = ant.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        response = client_ant.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        result["success"] = True
        return JSONResponse(result)

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# ═══════════════════════════════════════════════════════════════
# TIMECARD ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/process-timecards")
async def process_timecards(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    scanner = TimeCardScanner()
    fte_entries = []
    contractor_entries = []

    for file in files:
        try:
            contents = await file.read()
            text = extract_text_from_pdf(contents)
            sheet_type = scanner.detect_sheet_type(text)
            entries = scanner.extract_time_entries(text)
            if sheet_type == "FTE":
                fte_entries.extend(entries)
            else:
                contractor_entries.extend(entries)
        except Exception as e:
            print(f"[TIMECARD] Error processing {file.filename}: {str(e)}")
            continue

    try:
        excel_bytes = create_timecard_excel(fte_entries, contractor_entries)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=timecards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Excel: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        text_extracted = ""
        for page in reader.pages:
            text_extracted += page.extract_text() + "\n"
        return text_extracted
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# PROJECT HUB — FILES
# ═══════════════════════════════════════════════════════════════

def get_gcs_client():
    from google.cloud import storage
    import json
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    if creds_json:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_info(json.loads(creds_json))
        return storage.Client(credentials=creds)
    return storage.Client()

@app.get("/api/projects/{project_id}/files")
async def list_project_files(project_id: int, request: Request):
    user = get_current_user(request)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM project_files WHERE project_id = %s ORDER BY uploaded_at DESC", (project_id,))
        files = cur.fetchall()
    return {"files": [dict(f) for f in files]}

@app.post("/api/projects/{project_id}/files")
async def upload_project_file(project_id: int, request: Request, file: UploadFile = File(...)):
    user = get_current_user(request)
    contents = await file.read()
    bucket_name = os.environ.get("GOOGLE_CLOUD_BUCKET", "fieldwise-ai-files")
    gcs_path = f"projects/{project_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    try:
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(contents, content_type=file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO project_files (project_id, name, gcs_path, size) VALUES (%s, %s, %s, %s)",
            (project_id, file.filename, gcs_path, len(contents))
        )
    return {"success": True}

@app.get("/api/files/download")
async def download_project_file(path: str, request: Request):
    user = get_current_user(request)
    bucket_name = os.environ.get("GOOGLE_CLOUD_BUCKET", "fieldwise-ai-files")
    try:
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(path)
        contents = blob.download_as_bytes()
        return Response(content=contents, media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={path.split('/')[-1]}"})
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/files/{file_id}")
async def delete_project_file(file_id: int, request: Request):
    user = get_current_user(request)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM project_files WHERE id = %s", (file_id,))
        f = cur.fetchone()
        if f:
            try:
                client = get_gcs_client()
                bucket = client.bucket(os.environ.get("GOOGLE_CLOUD_BUCKET", "fieldwise-ai-files"))
                bucket.blob(f["gcs_path"]).delete()
            except: pass
            cur.execute("DELETE FROM project_files WHERE id = %s", (file_id,))
    return {"success": True}


# ═══════════════════════════════════════════════════════════════
# PROJECT HUB — RFIs
# ═══════════════════════════════════════════════════════════════

@app.get("/api/projects/{project_id}/rfis")
async def list_rfis(project_id: int, request: Request):
    user = get_current_user(request)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM project_rfis WHERE project_id = %s ORDER BY created_at DESC", (project_id,))
        rfis = cur.fetchall()
    return {"rfis": [dict(r) for r in rfis]}

@app.post("/api/projects/{project_id}/rfis")
async def create_rfi(project_id: int, request: Request):
    user = get_current_user(request)
    data = await request.json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO project_rfis (project_id, rfi_number, subject, description, assigned_to, due_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (project_id, data.get("rfi_number"), data.get("subject"), data.get("description"),
             data.get("assigned_to"), data.get("due_date"), data.get("status", "open"))
        )
    return {"success": True}

@app.delete("/api/rfis/{rfi_id}")
async def delete_rfi(rfi_id: int, request: Request):
    user = get_current_user(request)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM project_rfis WHERE id = %s", (rfi_id,))
    return {"success": True}


# ═══════════════════════════════════════════════════════════════
# PROJECT HUB — NOTES
# ═══════════════════════════════════════════════════════════════

@app.get("/api/projects/{project_id}/notes")
async def list_notes(project_id: int, request: Request):
    user = get_current_user(request)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM project_notes WHERE project_id = %s ORDER BY created_at DESC", (project_id,))
        notes = cur.fetchall()
    return {"notes": [dict(n) for n in notes]}

@app.post("/api/projects/{project_id}/notes")
async def create_note(project_id: int, request: Request):
    user = get_current_user(request)
    data = await request.json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO project_notes (project_id, content, author_name) VALUES (%s, %s, %s)",
            (project_id, data.get("content"), user["name"])
        )
    return {"success": True}

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, request: Request):
    user = get_current_user(request)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM project_notes WHERE id = %s", (note_id,))
    return {"success": True}

@app.get("/admin/migrate")
async def run_migration():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_files (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                gcs_path VARCHAR(500) NOT NULL,
                size INTEGER,
                uploaded_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_rfis (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                rfi_number VARCHAR(50),
                subject VARCHAR(500) NOT NULL,
                description TEXT,
                assigned_to VARCHAR(255),
                due_date DATE,
                status VARCHAR(50) DEFAULT 'open',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_notes (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                author_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
    return {"success": True, "message": "Tables created"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

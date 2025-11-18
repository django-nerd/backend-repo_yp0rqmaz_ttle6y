import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Department, News, Event, Vacancy, Employee, Complaint

app = FastAPI(title="Government Services Portal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "Government Services Portal API"}

@app.get("/test")
def test_database():
    """Test endpoint to check DB connectivity and expose collections"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# --------- Public endpoints ---------

@app.get("/api/departments")
async def list_departments():
    items = get_documents("department")
    return items

@app.get("/api/departments/{name}")
async def get_department(name: str):
    items = get_documents("department", {"name": name})
    if not items:
        raise HTTPException(status_code=404, detail="Department not found")
    return items[0]

@app.get("/api/news")
async def list_news(limit: int = 20):
    items = get_documents("news")
    items.sort(key=lambda x: x.get("published_at") or x.get("created_at"), reverse=True)
    return items[:limit]

@app.get("/api/events")
async def list_events(limit: int = 50):
    items = get_documents("event")
    items.sort(key=lambda x: x.get("start_date") or x.get("created_at"))
    return items[:limit]

@app.get("/api/vacancies")
async def list_vacancies(limit: int = 50):
    items = get_documents("vacancy")
    items.sort(key=lambda x: x.get("closing_date") or x.get("created_at"))
    return items[:limit]

# Public complaint submission
@app.post("/api/complaints")
async def submit_complaint(payload: Complaint):
    complaint_id = create_document("complaint", payload)
    return {"id": complaint_id, "status": "received"}

# --------- Admin endpoints (simple, no auth for demo) ---------

@app.post("/api/admin/news")
async def create_news(payload: News):
    if payload.published_at is None:
        payload.published_at = datetime.utcnow()
    doc_id = create_document("news", payload)
    return {"id": doc_id}

@app.post("/api/admin/events")
async def create_event(payload: Event):
    doc_id = create_document("event", payload)
    return {"id": doc_id}

@app.post("/api/admin/vacancies")
async def create_vacancy(payload: Vacancy):
    doc_id = create_document("vacancy", payload)
    return {"id": doc_id}

@app.post("/api/admin/departments")
async def create_department(payload: Department):
    doc_id = create_document("department", payload)
    return {"id": doc_id}

# Simple stats for admin dashboard
@app.get("/api/admin/stats")
async def admin_stats():
    stats = {
        "employees": len(get_documents("employee")),
        "complaints": len(get_documents("complaint")),
        "news": len(get_documents("news")),
        "events": len(get_documents("event")),
        "vacancies": len(get_documents("vacancy")),
        "departments": len(get_documents("department")),
    }
    return stats

# Seed endpoint to create 30 departments if none exist
@app.post("/api/admin/seed-departments")
async def seed_departments():
    existing = get_documents("department")
    if existing:
        return {"seeded": False, "message": "Departments already exist", "count": len(existing)}

    names = [
        "Health", "Education", "Transport", "Finance", "Agriculture", "Tourism",
        "Defense", "Interior", "Foreign Affairs", "Justice", "Environment",
        "Energy", "Housing", "Labor", "Commerce", "Culture", "Science",
        "Technology", "Sports", "Women & Child", "Social Welfare", "Rural Development",
        "Urban Development", "Water Resources", "Information",
        "Public Works", "Planning", "Disaster Management", "Revenue", "Animal Husbandry"
    ]

    for n in names:
        dept = Department(
            name=f"Department of {n}",
            description=f"Responsible for {n.lower()} related policies and services.",
            services=["Citizen Support", "Policy Implementation", "Information & Guidance"],
        )
        create_document("department", dept)

    return {"seeded": True, "count": len(names)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

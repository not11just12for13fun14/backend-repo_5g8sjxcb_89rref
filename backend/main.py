import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timezone
from bson import ObjectId

from database import db
from schemas import Project, Skill, Testimonial, Certificate

app = FastAPI(title="Futuristic Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists and mount as static for serving uploaded files
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

security = HTTPBearer()

# Simple token-based auth for demo purposes. In production use proper session/JWT.
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "changeme-admin-token")


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or credentials.credentials != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


# Utilities
class IDModel(BaseModel):
    id: str


def to_dict(doc):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    # Normalize timestamps
    for k in ["created_at", "updated_at", "createdAt", "updatedAt"]:
        if k in d and hasattr(d[k], "isoformat"):
            try:
                d[k] = d[k].isoformat()
            except Exception:
                pass
    return d


@app.get("/")
def root():
    return {"message": "Portfolio API is running"}


@app.get("/schema")
def get_schema():
    return {
        "collections": [
            "user", "project", "skill", "testimonial", "certificate", "activitylog"
        ]
    }


@app.get("/test")
def test_database():
    status = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            status["database"] = "✅ Connected & Working"
            status["database_url"] = "✅ Set"
            status["database_name"] = getattr(db, "name", "✅ Connected")
            status["connection_status"] = "Connected"
            try:
                status["collections"] = db.list_collection_names()
            except Exception:
                pass
    except Exception as e:
        status["database"] = f"❌ Error: {str(e)[:80]}"
    return status


# ---------- Startup: Seed sample data if collections are empty ----------
@app.on_event("startup")
def seed_sample_data():
    if db is None:
        return
    try:
        # Only seed when empty to avoid duplicates
        needs_projects = db["project"].count_documents({}) == 0
        needs_skills = db["skill"].count_documents({}) == 0
        needs_testimonials = db["testimonial"].count_documents({}) == 0
        needs_certificates = db["certificate"].count_documents({}) == 0
        now = datetime.now(timezone.utc)
        if needs_projects:
            db["project"].insert_many([
                {
                    "title": "Nebula UI Kit",
                    "slug": "nebula-ui-kit",
                    "shortDesc": "A polished, animated component kit with glassmorphism and neon accents.",
                    "longDesc": "Built with React, Tailwind, and Framer Motion.",
                    "tech": ["React", "Tailwind", "Framer Motion"],
                    "tags": ["design", "components"],
                    "liveDemoUrl": "https://ui.example.com",
                    "githubUrl": "https://github.com/example/nebula",
                    "images": [
                        "https://images.unsplash.com/photo-1526932848701-1f216ce59f87?q=80&w=1200&auto=format&fit=crop"
                    ],
                    "featured": True,
                    "published": True,
                    "orderIndex": 0,
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "title": "Cosmic Commerce",
                    "slug": "cosmic-commerce",
                    "shortDesc": "Headless shop with 3D product previews and blazing-fast UX.",
                    "longDesc": "FastAPI backend + React storefront.",
                    "tech": ["FastAPI", "MongoDB", "React"],
                    "tags": ["ecommerce", "3d"],
                    "liveDemoUrl": "https://shop.example.com",
                    "githubUrl": "https://github.com/example/cosmic-commerce",
                    "images": [
                        "https://images.unsplash.com/photo-1547658719-da2b51169166?q=80&w=1200&auto=format&fit=crop"
                    ],
                    "featured": False,
                    "published": True,
                    "orderIndex": 1,
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "title": "Orbit Analytics",
                    "slug": "orbit-analytics",
                    "shortDesc": "Realtime dashboards with glowing charts and delightful micro-interactions.",
                    "longDesc": "Streaming insights with websockets and ECharts.",
                    "tech": ["WebSockets", "ECharts", "Tailwind"],
                    "tags": ["analytics", "dashboard"],
                    "liveDemoUrl": "https://dash.example.com",
                    "githubUrl": "https://github.com/example/orbit-analytics",
                    "images": [
                        "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?q=80&w=1200&auto=format&fit=crop"
                    ],
                    "featured": False,
                    "published": True,
                    "orderIndex": 2,
                    "created_at": now,
                    "updated_at": now,
                },
            ])
        if needs_skills:
            db["skill"].insert_many([
                {"name": "React", "level": 90, "category": "Frontend", "orderIndex": 0, "published": True, "deleted": False, "created_at": now, "updated_at": now},
                {"name": "FastAPI", "level": 85, "category": "Backend", "orderIndex": 1, "published": True, "deleted": False, "created_at": now, "updated_at": now},
                {"name": "MongoDB", "level": 80, "category": "Database", "orderIndex": 2, "published": True, "deleted": False, "created_at": now, "updated_at": now},
                {"name": "Tailwind CSS", "level": 88, "category": "Frontend", "orderIndex": 3, "published": True, "deleted": False, "created_at": now, "updated_at": now},
            ])
        if needs_testimonials:
            db["testimonial"].insert_many([
                {"name": "Ava Stone", "role": "Product Lead @ Nova", "quote": "Delivers stunning interfaces with impeccable attention to detail.", "orderIndex": 0, "published": True, "deleted": False, "created_at": now, "updated_at": now},
                {"name": "Leo Park", "role": "CTO @ Orbit Labs", "quote": "Reliable, fast, and creative — a joy to collaborate with.", "orderIndex": 1, "published": True, "deleted": False, "created_at": now, "updated_at": now},
            ])
        if needs_certificates:
            db["certificate"].insert_many([
                {"title": "Certified FastAPI Developer", "issuer": "FastAPI Academy", "issueDate": "2024-01", "image": "https://images.unsplash.com/photo-1557800636-894a64c1696f?q=80&w=1200&auto=format&fit=crop", "tags": ["backend"], "published": True, "deleted": False, "created_at": now, "updated_at": now},
                {"title": "MongoDB Essentials", "issuer": "MongoDB University", "issueDate": "2023-09", "image": "https://images.unsplash.com/photo-1556157382-97eda2d62296?q=80&w=1200&auto=format&fit=crop", "tags": ["database"], "published": True, "deleted": False, "created_at": now, "updated_at": now},
            ])
    except Exception:
        # Seeding should never break startup
        pass


# ---------- File Upload (local storage) ----------
@app.post("/api/admin/upload")
async def upload_file(file: UploadFile = File(...), _: bool = Depends(require_admin)):
    # Save to uploads dir with timestamped name
    ext = os.path.splitext(file.filename)[1]
    safe_ext = ext if len(ext) <= 10 else ext[:10]
    fname = f"{int(datetime.now().timestamp()*1000)}{safe_ext}"
    dest = os.path.join(UPLOAD_DIR, fname)
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)
    url = f"/uploads/{fname}"
    return {"url": url}


# ---------- Public Read Endpoints ----------
@app.get("/api/projects")
def list_projects(published: Optional[bool] = None, tag: Optional[str] = None, search: Optional[str] = None, page: int = 1, limit: int = 20):
    if db is None:
        raise HTTPException(500, "Database not configured")
    q = {"deleted": {"$ne": True}}
    if published is not None:
        q["published"] = published
    if tag:
        q["tags"] = {"$in": [tag]}
    if search:
        q["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"shortDesc": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}},
        ]
    cursor = db["project"].find(q).sort([("featured", -1), ("orderIndex", 1), ("created_at", -1)])
    total = db["project"].count_documents(q)
    items = [to_dict(x) for x in cursor.skip((page-1)*limit).limit(limit)]
    return {"items": items, "total": total, "page": page, "limit": limit}


@app.get("/api/projects/{slug}")
def get_project(slug: str):
    if db is None:
        raise HTTPException(500, "Database not configured")
    doc = db["project"].find_one({"slug": slug, "deleted": {"$ne": True}})
    if not doc:
        raise HTTPException(404, "Not found")
    return to_dict(doc)


@app.get("/api/skills")
def list_skills(category: Optional[str] = None, search: Optional[str] = None):
    if db is None:
        raise HTTPException(500, "Database not configured")
    q = {"deleted": {"$ne": True}, "published": True}
    if category:
        q["category"] = category
    if search:
        q["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}},
        ]
    items = [to_dict(x) for x in db["skill"].find(q).sort("orderIndex", 1)]
    return {"items": items}


@app.get("/api/testimonials")
def list_testimonials():
    if db is None:
        raise HTTPException(500, "Database not configured")
    q = {"deleted": {"$ne": True}, "published": True}
    items = [to_dict(x) for x in db["testimonial"].find(q).sort("orderIndex", 1)]
    return {"items": items}


@app.get("/api/certificates")
def list_certificates(tag: Optional[str] = None, search: Optional[str] = None):
    if db is None:
        raise HTTPException(500, "Database not configured")
    q = {"deleted": {"$ne": True}, "published": True}
    if tag:
        q["tags"] = {"$in": [tag]}
    if search:
        q["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"issuer": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}},
        ]
    items = [to_dict(x) for x in db["certificate"].find(q).sort("_id", -1)]
    return {"items": items}


# ---------- Admin CRUD Endpoints (token auth) ----------

# Create
@app.post("/api/admin/projects")
def create_project(payload: Project, _: bool = Depends(require_admin)):
    if db is None:
        raise HTTPException(500, "Database not configured")
    now = datetime.now(timezone.utc)
    data = payload.model_dump()
    data.update({"created_at": now, "updated_at": now})
    if db["project"].find_one({"slug": data.get("slug")}):
        raise HTTPException(400, "Slug already exists")
    _id = db["project"].insert_one(data).inserted_id
    db["activitylog"].insert_one({"user_email": "admin", "action": "create", "entity": "project", "entity_id": str(_id), "timestamp": now})
    return {"id": str(_id)}


@app.put("/api/admin/projects/{id}")
def update_project(id: str, payload: Project, _: bool = Depends(require_admin)):
    if db is None:
        raise HTTPException(500, "Database not configured")
    now = datetime.now(timezone.utc)
    data = payload.model_dump()
    data.update({"updated_at": now})
    res = db["project"].update_one({"_id": ObjectId(id)}, {"$set": data})
    if res.matched_count == 0:
        raise HTTPException(404, "Not found")
    db["activitylog"].insert_one({"user_email": "admin", "action": "update", "entity": "project", "entity_id": id, "timestamp": now})
    return {"ok": True}


@app.delete("/api/admin/projects/{id}")
def delete_project(id: str, hard: bool = False, _: bool = Depends(require_admin)):
    if db is None:
        raise HTTPException(500, "Database not configured")
    now = datetime.now(timezone.utc)
    if hard:
        db["project"].delete_one({"_id": ObjectId(id)})
    else:
        db["project"].update_one({"_id": ObjectId(id)}, {"$set": {"deleted": True, "updated_at": now}})
    db["activitylog"].insert_one({"user_email": "admin", "action": "delete", "entity": "project", "entity_id": id, "timestamp": now})
    return {"ok": True}


@app.post("/api/admin/skills")
def create_skill(payload: Skill, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    data = payload.model_dump()
    data.update({"created_at": now, "updated_at": now})
    _id = db["skill"].insert_one(data).inserted_id
    db["activitylog"].insert_one({"user_email": "admin", "action": "create", "entity": "skill", "entity_id": str(_id), "timestamp": now})
    return {"id": str(_id)}


@app.put("/api/admin/skills/{id}")
def update_skill(id: str, payload: Skill, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    data = payload.model_dump()
    data.update({"updated_at": now})
    res = db["skill"].update_one({"_id": ObjectId(id)}, {"$set": data})
    if res.matched_count == 0:
        raise HTTPException(404, "Not found")
    db["activitylog"].insert_one({"user_email": "admin", "action": "update", "entity": "skill", "entity_id": id, "timestamp": now})
    return {"ok": True}


@app.delete("/api/admin/skills/{id}")
def delete_skill(id: str, hard: bool = False, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    if hard:
        db["skill"].delete_one({"_id": ObjectId(id)})
    else:
        db["skill"].update_one({"_id": ObjectId(id)}, {"$set": {"deleted": True, "updated_at": now}})
    db["activitylog"].insert_one({"user_email": "admin", "action": "delete", "entity": "skill", "entity_id": id, "timestamp": now})
    return {"ok": True}


@app.post("/api/admin/testimonials")
def create_testimonial(payload: Testimonial, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    data = payload.model_dump()
    data.update({"created_at": now, "updated_at": now})
    _id = db["testimonial"].insert_one(data).inserted_id
    db["activitylog"].insert_one({"user_email": "admin", "action": "create", "entity": "testimonial", "entity_id": str(_id), "timestamp": now})
    return {"id": str(_id)}


@app.put("/api/admin/testimonials/{id}")
def update_testimonial(id: str, payload: Testimonial, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    data = payload.model_dump()
    data.update({"updated_at": now})
    res = db["testimonial"].update_one({"_id": ObjectId(id)}, {"$set": data})
    if res.matched_count == 0:
        raise HTTPException(404, "Not found")
    db["activitylog"].insert_one({"user_email": "admin", "action": "update", "entity": "testimonial", "entity_id": id, "timestamp": now})
    return {"ok": True}


@app.delete("/api/admin/testimonials/{id}")
def delete_testimonial(id: str, hard: bool = False, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    if hard:
        db["testimonial"].delete_one({"_id": ObjectId(id)})
    else:
        db["testimonial"].update_one({"_id": ObjectId(id)}, {"$set": {"deleted": True, "updated_at": now}})
    db["activitylog"].insert_one({"user_email": "admin", "action": "delete", "entity": "testimonial", "entity_id": id, "timestamp": now})
    return {"ok": True}


@app.post("/api/admin/certificates")
def create_certificate(payload: Certificate, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    data = payload.model_dump()
    data.update({"created_at": now, "updated_at": now})
    _id = db["certificate"].insert_one(data).inserted_id
    db["activitylog"].insert_one({"user_email": "admin", "action": "create", "entity": "certificate", "entity_id": str(_id), "timestamp": now})
    return {"id": str(_id)}


@app.put("/api/admin/certificates/{id}")
def update_certificate(id: str, payload: Certificate, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    data = payload.model_dump()
    data.update({"updated_at": now})
    res = db["certificate"].update_one({"_id": ObjectId(id)}, {"$set": data})
    if res.matched_count == 0:
        raise HTTPException(404, "Not found")
    db["activitylog"].insert_one({"user_email": "admin", "action": "update", "entity": "certificate", "entity_id": id, "timestamp": now})
    return {"ok": True}


@app.delete("/api/admin/certificates/{id}")
def delete_certificate(id: str, hard: bool = False, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    if hard:
        db["certificate"].delete_one({"_id": ObjectId(id)})
    else:
        db["certificate"].update_one({"_id": ObjectId(id)}, {"$set": {"deleted": True, "updated_at": now}})
    db["activitylog"].insert_one({"user_email": "admin", "action": "delete", "entity": "certificate", "entity_id": id, "timestamp": now})
    return {"ok": True}


# Bulk publish/unpublish
class BulkPublish(BaseModel):
    ids: List[str]
    published: bool


@app.post("/api/admin/projects/bulk-publish")
def bulk_publish_projects(payload: BulkPublish, _: bool = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    ids = [ObjectId(x) for x in payload.ids]
    db["project"].update_many({"_id": {"$in": ids}}, {"$set": {"published": payload.published, "updated_at": now}})
    return {"ok": True}


# Reordering
class ReorderPayload(BaseModel):
    ordered_ids: List[str]


@app.post("/api/admin/projects/reorder")
def reorder_projects(payload: ReorderPayload, _: bool = Depends(require_admin)):
    for idx, id in enumerate(payload.ordered_ids):
        db["project"].update_one({"_id": ObjectId(id)}, {"$set": {"orderIndex": idx}})
    return {"ok": True}


# Simple contact endpoint with basic rate limit in-memory (demo)
_rate_cache = {}


class ContactForm(BaseModel):
    name: str
    email: str
    message: str


@app.post("/api/contact")
async def contact(form: ContactForm, request: Request):
    ip = request.client.host if request.client else "unknown"
    now = datetime.now().timestamp()
    window = 60
    entry = _rate_cache.get(ip, [])
    entry = [t for t in entry if now - t < window]
    if len(entry) >= 3:
        raise HTTPException(429, "Too many requests")
    entry.append(now)
    _rate_cache[ip] = entry
    if db is not None:
        db["activitylog"].insert_one({
            "user_email": form.email,
            "action": "contact",
            "entity": "message",
            "entity_id": "-",
            "metadata": form.model_dump(),
            "timestamp": datetime.now(timezone.utc)
        })
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

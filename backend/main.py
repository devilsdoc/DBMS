"""
Main FastAPI Application Entrypoint
CSE Department Centralized Database-Driven Attendance Management System
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routers import (
    auth_routes,
    teacher_routes,
    tg_routes,
    student_routes,
    reports_routes,
    audit_routes
)
from backend.database import engine, get_db
from backend.services.defaulter_service import evaluate_and_generate_defaulter_alerts
from backend.dependencies import role_checker
from sqlalchemy.orm import Session
from fastapi import Depends

app = FastAPI(
    title="CSE Department Attendance Management & Monitoring System API",
    description="Role-Based Access Controlled (RBAC) Backend for HoD, Class Teachers, Course Teachers, Teacher Guardians, and Students.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (supports React / Next.js / Vite frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_routes.router)
app.include_router(teacher_routes.router)
app.include_router(tg_routes.router)
app.include_router(student_routes.router)
app.include_router(reports_routes.router)
app.include_router(audit_routes.router)

@app.post("/alerts/trigger-check", tags=["Defaulter Alerts"])
@app.post("/api/v1/alerts/trigger-check", tags=["Defaulter Alerts"])
def trigger_daily_defaulter_check(
    db: Session = Depends(get_db)
):
    """
    Simulates / triggers the daily 6:00 PM cron job.
    Evaluates all students and inserts Defaulter Alerts for any student < 75%.
    """
    return evaluate_and_generate_defaulter_alerts(db)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ONLINE",
        "system": "CSE Attendance Management System",
        "database": engine.url.drivername,
        "docs": "/docs",
        "timestamp": "2026-10-29T18:45:00"
    }

# Serve frontend build if dist folder exists
DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.isdir(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", tags=["Frontend"])
    async def serve_frontend(full_path: str):
        file_path = os.path.join(DIST_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(DIST_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return health_check()
else:
    @app.get("/", tags=["Health"])
    def root_health():
        return health_check()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
import os

from .config import settings
from .exceptions import http_exception_handler, validation_exception_handler, generic_exception_handler
from .routers import auth, teams, tasks, messages

app = FastAPI(
    title="TaskFlow API",
    description="소규모 팀 칸반 + 채팅 협업 앱 TaskFlow MVP API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(teams.router, prefix="", tags=["Teams"])
app.include_router(tasks.router, prefix="", tags=["Tasks"])
app.include_router(messages.router, prefix="", tags=["Messages"])

root_dir = os.path.dirname(os.path.dirname(__file__))

# 로컬: frontend/ 디렉토리, Vercel: public/ 디렉토리
for _static_dir, _mount_path in [
    (os.path.join(root_dir, "frontend", "js"), "/static/js"),
    (os.path.join(root_dir, "public", "static", "js"), "/static/js"),
]:
    if os.path.isdir(_static_dir):
        try:
            app.mount("/static/js", StaticFiles(directory=_static_dir), name="static_js")
        except Exception:
            pass
        break

_html_dir = None
for _candidate in [
    os.path.join(root_dir, "frontend"),
    os.path.join(root_dir, "public"),
]:
    if os.path.isdir(_candidate):
        _html_dir = _candidate
        break

if _html_dir:
    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(_html_dir, "login.html"))

    @app.get("/{page}.html", include_in_schema=False)
    async def serve_page(page: str):
        path = os.path.join(_html_dir, f"{page}.html")
        if os.path.isfile(path):
            return FileResponse(path)
        return FileResponse(os.path.join(_html_dir, "login.html"))

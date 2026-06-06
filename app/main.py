from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.db.database import Base, engine


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Agent Platform",
    description="AI Agent Platform with tool calling, memory, and task history",
    version="0.1.0",
)

app.include_router(chat_router, prefix="/api", tags=["Chat"])

static_dir = Path(__file__).parent / "static"
app.mount("/app", StaticFiles(directory=static_dir, html=True), name="app")


@app.get("/ui", include_in_schema=False)
def ui():
    return RedirectResponse(url="/app/")


@app.get("/")
def root():
    return {"message": "AI Agent Platform is running"}

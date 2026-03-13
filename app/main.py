from fastapi import FastAPI

from app.database import Base, engine
from app.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(
    title="Project Mark API",
    version="1.0"
)

# Register API routes
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Project Mark API is running"}
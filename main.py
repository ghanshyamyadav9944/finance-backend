from fastapi import FastAPI
from database import engine, Base
from routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Dashboard API",
    description="Zorvyn Fintech Backend Assignment",
    version="1.0.0"
)

app.include_router(router)

@app.get("/", tags=["Home"])
def home():
    return {"message": "Finance Backend Running!"}

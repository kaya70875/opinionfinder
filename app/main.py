from fastapi import FastAPI
from app.routes.transcripts import router as transcripts_router
from app.routes.jobs import router as jobs_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

app = FastAPI()

# CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the YouTube Transcript API!"}

app.include_router(transcripts_router, prefix="/api", tags=["transcripts"])
app.include_router(jobs_router, prefix="/api", tags=["jobs"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
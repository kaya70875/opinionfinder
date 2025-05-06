from fastapi import FastAPI
from app.routes import transcripts as transcripts_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_api_route(transcripts_router, prefix="/api", tags=["transcripts"])

@app.get("/")
async def root():
    return {"message": "Welcome to the YouTube Transcript API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
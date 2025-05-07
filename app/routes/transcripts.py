from fastapi import APIRouter
from fastapi import Query, Path, HTTPException
from fastapi.responses import StreamingResponse
from app.utils.writes import write_as_csv, write_as_text, write_as_json
from app.fetch import fetch

router = APIRouter()

@router.get("/transcripts/{channel_name}")
async def fetch_transcripts(
        channel_name : str = Path(description="Channel name to fetch transcripts from.", min_length=1, max_length=70),
        export_type: str = Query(default="json", description="Export type for transcripts. Options: 'json', 'txt', 'csv'")
        ):
    """
    Fetch transcripts for all videos from a channel.
    """
    try:
        if export_type not in ["json", "txt", "csv"]:
            raise HTTPException(status_code=400, detail="Invalid export type. Options: 'json', 'txt', 'csv'")
        
        # Call the fetch function from fetch.py
        transcripts = fetch(channel_name, export_type)

        if export_type == "txt":
            output = write_as_text(transcripts)

            return StreamingResponse(output, media_type="text/plain", headers={
                "Content-Disposition": "attachment; filename=transcripts.txt"
            })
        
        elif export_type == 'csv':
            output = write_as_csv(transcripts)

            return StreamingResponse(output, media_type="text/csv", headers={
                "Content-Disposition": "attachment; filename=transcripts.csv"
            })
        
        elif export_type == 'json':
            output = write_as_json(transcripts)

            return StreamingResponse(output, media_type="application/json", headers={
                "Content-Disposition": "attachment; filename=transcripts.json"
            })

        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
from fastapi import APIRouter
from fastapi import Query, Path, HTTPException
from fastapi.responses import StreamingResponse
from app.utils.writes import write_as_csv, write_as_text, write_as_json
from app.fetch import fetch_all_transcripts
from app.youtube_v3.v3_requests import get_video_ids_from_channel

router = APIRouter()

@router.get("/transcripts/{channel_name}")
async def fetch_transcripts(
        channel_name : str = Path(description="Channel name to fetch transcripts from.", min_length=1, max_length=70),
        export_type: str = Query(default="json", description="Export type for transcripts. Options: 'json', 'txt', 'csv'"),
        limit: int = Query(default=50, description="Limit the number of transcripts to fetch.", min_length=1, max_length=1000) # Adjusted to max_length for limit
        ):
    """
    Fetch transcripts for all videos from a channel.
    """
    try:
        if export_type not in ["json", "txt", "csv"]:
            raise HTTPException(status_code=400, detail="Invalid export type. Options: 'json', 'txt', 'csv'")
        
        video_ids = await get_video_ids_from_channel(channel_name, limit=limit)
        if not video_ids:
            raise HTTPException(status_code=404, detail="No video IDs found for the specified channel.")

        # Call the fetch function from fetch.py
        transcripts = await fetch_all_transcripts(video_ids, max_workers=30)
        if not transcripts:
            raise HTTPException(status_code=404, detail="No transcripts found for the specified video IDs.")

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
    
    
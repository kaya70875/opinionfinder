from fastapi import APIRouter
from fastapi import Query, Path, HTTPException
from fastapi.responses import StreamingResponse
from app.utils.writes import write_as_csv, write_as_text, write_as_json
from app.fetch import fetch_all_transcripts_with_metadata
from app.youtube_v3.v3_requests import fetch_channel
from app.user.limits import check_request_limits, update_user_limits
from app.user.utils import get_user_plan
from app.user.user_limits import USER_LIMITS
from app.utils.data_processing import clean_transcripts, calculate_estimated_token

router = APIRouter()

@router.get("/transcripts/{channel_name}")
async def fetch_transcripts(
        channel_name : str = Path(description="Channel name to fetch transcripts from.", min_length=1, max_length=70),
        export_type: str = Query(default="json", description="Export type for transcripts. Options: 'json', 'txt', 'csv'"),
        max_results: int = Query(default=None, description="Limit the number of transcripts to fetch."),
        allowed_metadata: str = Query(default='title', description="Allowed metadata values. Options : 'title | description | publishedAt'"),
        include_timing: bool = Query(default=True, description="Whether the include start and duration parameters or not.")
        ):
    """
    Fetch transcripts for all videos from a channel.
    """
    try:
        if export_type not in ["json", "txt", "csv"]:
            raise HTTPException(status_code=400, detail="Invalid export type. Options: 'json', 'txt', 'csv'")
        
        user_id = "681b72683e6372ca59e05893"

        # Set maximum allowed videos to fetch as default.
        user_plan = get_user_plan(user_id).lower().replace(' ', '_')
        user_limits = USER_LIMITS.get(user_plan, USER_LIMITS['free'])
        max_allowed = int(user_limits['max_videos'])
        if max_results is None:
            max_results = max_allowed
        if max_results > max_allowed:
            raise HTTPException(status_code=403, detail=f"Limit exceeds plan allowance ({max_allowed} max for {user_plan} users).")

        # Check request limits for the user
        check_request_limits(user_id, user_limits=user_limits)
        
        channel = await fetch_channel(channel_name, max_results)
        video_ids = channel.video_ids
        snippets = channel.metadata
        if not video_ids:
            raise HTTPException(status_code=404, detail="No video IDs found for the specified channel.")

        # Call the fetch function from fetch.py
        channel_data = await fetch_all_transcripts_with_metadata(video_ids, snippets)
        if not channel_data:
            raise HTTPException(status_code=404, detail="No channel_data found for the specified video IDs.")

        #Update user metrics
        update_user_limits(user_id, (data.transcript for data in channel_data))

        # Convert metadata to a list
        allowed_metadata_list = allowed_metadata.split(',')

        #Clean transcripts for final writing format.
        cleaned_data = clean_transcripts(channel_data)

        #Calculate estimated token
        estimated_token = calculate_estimated_token(cleaned_data)

        if export_type == "txt":
            output = write_as_text(cleaned_data, allowed_metadata_list, include_timing)

            return StreamingResponse(output, media_type="text/plain", headers={
                "Content-Disposition": "attachment; filename=transcripts.txt",
                "X-Estimated-Tokens": str(estimated_token)
            })
                
        
        elif export_type == 'csv':
            output = write_as_csv(cleaned_data, allowed_metadata_list, include_timing)

            return StreamingResponse(output, media_type="text/csv", headers={
                "Content-Disposition": "attachment; filename=transcripts.csv",
                "X-Estimated-Tokens": str(estimated_token)
            })
        
        elif export_type == 'json':
            output = write_as_json(cleaned_data, allowed_metadata_list, include_timing)

            return StreamingResponse(output, media_type="application/json", headers={
                "Content-Disposition": "attachment; filename=transcripts.json",
                "X-Estimated-Tokens": str(estimated_token)
            })

        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
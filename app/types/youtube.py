from pydantic import BaseModel
from app.types.thumbnails import Thumbnails

class Snippet(BaseModel):
    title: str
    description: str
    publishedAt: str
    channelId: str
    thumbnails: Thumbnails
    
class ChannelData(BaseModel):
    video_ids: list[str]
    metadata: list[Snippet]

class FetchAndMetaResponse(BaseModel):
    video_id: str
    transcript: list[dict]
    snippet: Snippet
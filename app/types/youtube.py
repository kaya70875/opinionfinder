from pydantic import BaseModel

class Snippet(BaseModel):
    title: str
    description: str
    publishedAt: str
    channelId: str
    
class ChannelData(BaseModel):
    video_ids: list[str]
    metadata: list[Snippet]

class FetchAndMetaResponse(BaseModel):
    video_id: str
    transcript: list[dict]
    snippet: Snippet
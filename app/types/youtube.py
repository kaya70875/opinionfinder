from pydantic import BaseModel

class Snippet(BaseModel):
    publishedAt: str
    channelId: str
    title: str
    description: str
    
class ChannelData(BaseModel):
    video_ids: list[str]
    metadata: list[Snippet]
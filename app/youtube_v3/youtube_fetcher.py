from app.types.youtube import ChannelData

class YoutubeV3:
    def __init__(self, api_key: str, channel_name: str):
        self.api_key = api_key
        self.channel_name = channel_name
    
    async def fetch_channel(self):
        pass

    async def _get_channel_id(self) -> str:
        pass

    async def _fetch_with_playlist_id(self, upload_playlist_id, max_results: int) -> ChannelData:
        pass

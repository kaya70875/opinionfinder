import httpx
#40 - 30
TIMEOUT = httpx.Timeout(30)
TRANSCRIPT_FETCH_TIMEOUT = httpx.Timeout(connect=2.0, read=2.0, write=2.0, pool=2.0)
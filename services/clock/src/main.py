from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/clock")
async def get_timestamp(response_type: str = "json"):
    now = datetime.now().isoformat()
    return PlainTextResponse(now) if response_type == "text" else {"timestamp": now}

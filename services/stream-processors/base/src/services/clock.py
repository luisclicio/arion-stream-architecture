import os
from datetime import datetime
from typing import Literal

import requests


class Clock:
    @staticmethod
    def now(source: Literal["system", "external"] = "external") -> datetime:
        if source == "system":
            return datetime.now()

        base_url = os.getenv("CLOCK_URL", "http://clock:8000")
        response = requests.get(f"{base_url}/clock?response_type=text")
        return datetime.fromisoformat(response.text)

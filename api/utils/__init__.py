from typing import Optional, Dict, Any
from datetime import datetime as dt


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class JsonException(Exception):
    def __init__(
        self,
        detail: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        self.detail = detail or {
            "status": False,
            "error": f"An unexpected error occurred.Please try again later",
        }
        self.status_code = status_code or 500
        self.headers = headers or {"Content-Type": "application/json"}

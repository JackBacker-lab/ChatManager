from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ActionStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    INVALID_INPUT = "invalid_input"
    PERMISSION_DENIED = "permission_denied"
    SKIPPED = "skipped"


class Log(BaseModel):
    chat_id: int
    status: ActionStatus
    action_name: str
    called_by_id: int
    msg_text: str
    msg_link: str | None = None
    target_id: int | None = None
    details: str | None = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

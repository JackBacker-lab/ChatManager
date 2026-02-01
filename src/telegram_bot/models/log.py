from datetime import datetime

from pydantic import BaseModel, Field


class Log(BaseModel):
    chat_id: int
    status: str
    action: str
    action_by_id: int
    text: str
    link: str | None = None
    target_id: int | None = None
    reason: None | str = None
    details: None | str = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    )

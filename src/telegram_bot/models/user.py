from pydantic import BaseModel


class UserDTO(BaseModel):
    id: int
    full_name: str
    username: str | None = None
    link: str | None = None
    updated_at: str | None = None

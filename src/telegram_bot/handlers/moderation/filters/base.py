from dataclasses import dataclass
from enum import Enum, auto


@dataclass(frozen=True)
class FilterError:
    code: str
    message: str


class FilterStatus(Enum):
    OK = auto()
    SKIPPED = auto()
    FAILED = auto()


@dataclass
class FilterResult:
    triggered: bool
    reason: str
    status: FilterStatus = FilterStatus.OK
    score: float | None = None
    error: FilterError | None = None


@dataclass
class MessageContext:
    """Normalized message data for filters."""

    chat_id: int
    user_id: int
    text: str

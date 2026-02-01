"""Configuration models for all moderation filters.

Minimal values in all configs > 0 to prevent unexpected errors.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

# Domain-specific scalar types, that represent safe operational ranges.
Ratio = Annotated[float, Field(ge=0.1, le=1.0)]
TextLength = Annotated[int, Field(ge=1, le=1000)]
Languages = list[Annotated[str, Field(pattern=r"^(ru|ua|en)$")]]
Repeats = Annotated[int, Field(ge=1, le=100)]


class BaseConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)


class AICensorshipConfig(BaseConfig):
    enabled: bool = False
    threshold: Ratio = 0.7


class CensorshipConfig(BaseConfig):
    enabled: bool = True
    max_norm_text_len: TextLength = 500

    # Small algorithm-specific margin (sliding window overlap),
    # intentionally kept narrow to prevent O(n²) behavior on long texts.
    window_len_margin: Annotated[int, Field(ge=1, le=10)] = 2
    similarity: Ratio = 0.85
    languages: Languages = ["ru", "ua", "en"]
    ai: AICensorshipConfig = AICensorshipConfig()


class FloodConfig(BaseConfig):
    enabled: bool = True
    message_limit: Repeats = 5

    # Time window in seconds for flood detection.
    time_window: Annotated[int, Field(ge=1, le=100)] = 10

    # Telegram/aiogram-specific limitation:
    # mute durations < 30s are treated as permanent restrictions.
    # This constraint is intentional and MUST NOT be lowered.
    # See: https://docs.aiogram.dev/en/dev-3.x/api/methods/restrict_chat_member.html#module-aiogram.methods.restrict_chat_member
    mute_time: Annotated[int, Field(ge=30, le=100)] = 30


class CapsConfig(BaseConfig):
    enabled: bool = True
    ratio: Ratio = 0.7
    min_length: TextLength = 10


class LinksConfig(BaseConfig):
    enabled: bool = True
    whitelist: list[str] = Field(default_factory=list)


class UserMentionsConfig(BaseConfig):
    enabled: bool = True
    max: Repeats = 5


class GibberishConfig(BaseConfig):
    enabled: bool = True

    min_length_low_variety: TextLength = 20
    min_unique_chars: Repeats = 5

    max_special_chars_repeat_len: Repeats = 3
    max_any_char_repeat_len: Repeats = 5

    min_length_consonant_check: TextLength = 25
    consonant_ratio_threshold: Ratio = 0.7

    # Phrase-related limits operate on word sequences,
    # not raw text length, therefore Repeats is used intentionally.
    phrase_min_words_count: Repeats = 3
    phrase_max_words_count: Repeats = 30
    max_phrase_repeats: Repeats = 5

    @field_validator("phrase_max_words_count")
    def validate_phrase_limits(cls, v: int, info: ValidationInfo) -> int:
        min_val = info.data.get("phrase_min_words_count", 1)
        if v < min_val:
            raise ValueError(
                f'"phrase_max_words_count" ({v}) must be'
                '>= "phrase_min_words_count" ({min_val})'
            )
        return v


class SpamConfig(BaseConfig):
    enabled: bool = True
    caps: CapsConfig = CapsConfig()
    links: LinksConfig = LinksConfig()
    user_mentions: UserMentionsConfig = UserMentionsConfig()
    gibberish: GibberishConfig = GibberishConfig()


class FiltersConfig(BaseConfig):
    censorship: CensorshipConfig = CensorshipConfig()
    spam: SpamConfig = SpamConfig()
    flood: FloodConfig = FloodConfig()

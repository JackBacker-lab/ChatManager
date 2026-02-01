import re


def parse_duration(duration: str) -> int:
    """Return the duration in seconds or 0 if duration is invalid.

    Support seconds, minutes, hours, and days as units.
    """
    match = re.fullmatch(r"(\d+)([smhd])", duration.lower())
    if not match:
        return 0

    value, unit = int(match[1]), match[2]
    return value * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]

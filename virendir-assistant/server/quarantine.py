_QUARANTINE_ACTIVE = False


def in_quarantine() -> bool:
    """Return True if quarantine mode is active.

    Honors the environment variable VIREN_QUARANTINE as an override
    (any non-empty value means quarantine is on).
    """
    import os
    if os.getenv("VIREN_QUARANTINE", ""):
        return True
    return _QUARANTINE_ACTIVE


def set_quarantine(active: bool) -> None:
    """Set quarantine mode on/off for this process lifetime."""
    global _QUARANTINE_ACTIVE
    _QUARANTINE_ACTIVE = bool(active)
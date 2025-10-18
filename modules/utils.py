"""
Common utility functions used across the pipeline
Consolidates duplicate code patterns
"""
from typing import Dict, Any


def normalize_spokesperson(analysis: Dict) -> Dict:
    """
    Normalize spokesperson data - handle both dict and list formats

    Gemini sometimes returns spokesperson as a list (when multiple people),
    sometimes as a dict (when one person). We normalize to always use the first/primary person.

    Args:
        analysis: Analysis dict containing spokesperson data

    Returns:
        Normalized spokesperson dict
    """
    spokesperson = analysis.get('spokesperson', {})

    # If it's a list, take the first spokesperson
    if isinstance(spokesperson, list):
        if len(spokesperson) > 0:
            return spokesperson[0]
        else:
            return {}
    # If it's already a dict, use it
    elif isinstance(spokesperson, dict):
        return spokesperson
    # Fallback to empty dict
    else:
        return {}


def safe_get(data: Dict, *keys, default=None) -> Any:
    """
    Safely navigate nested dictionaries

    Args:
        data: Dictionary to navigate
        *keys: Sequence of keys to traverse
        default: Default value if key path not found

    Returns:
        Value at key path or default

    Example:
        safe_get(data, 'user', 'profile', 'name', default='Unknown')
    """
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current if current is not None else default


def format_timestamp(seconds: float) -> str:
    """
    Format seconds into MM:SS timestamp

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to max length with suffix

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

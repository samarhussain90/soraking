"""
Unified JSON persistence layer
Consolidates 29 duplicate JSON operations across modules
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


def save_json(data: Any, file_path: str, indent: int = 2, ensure_dir: bool = True) -> None:
    """
    Save data to JSON file

    Args:
        data: Data to save (dict, list, etc.)
        file_path: Path to JSON file
        indent: Indentation level for pretty printing
        ensure_dir: Create parent directories if they don't exist

    Raises:
        IOError: If file cannot be written
    """
    path = Path(file_path)

    if ensure_dir:
        path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        json.dump(data, f, indent=indent, default=str)


def load_json(file_path: str, default: Optional[Any] = None) -> Any:
    """
    Load data from JSON file

    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid

    Returns:
        Loaded data or default value
    """
    path = Path(file_path)

    if not path.exists():
        return default

    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠ Failed to load {file_path}: {e}")
        return default


def append_to_json_array(item: Any, file_path: str, ensure_dir: bool = True) -> None:
    """
    Append item to JSON array file (creates if doesn't exist)

    Args:
        item: Item to append
        file_path: Path to JSON array file
        ensure_dir: Create parent directories if they don't exist
    """
    # Load existing array or create new
    data = load_json(file_path, default=[])

    if not isinstance(data, list):
        raise ValueError(f"File {file_path} does not contain a JSON array")

    # Append item
    data.append(item)

    # Save back
    save_json(data, file_path, ensure_dir=ensure_dir)


def update_json_field(file_path: str, **updates) -> None:
    """
    Update specific fields in a JSON object file

    Args:
        file_path: Path to JSON file
        **updates: Field updates as keyword arguments

    Example:
        update_json_field('config.json', status='completed', timestamp=datetime.now())
    """
    # Load existing data or create new dict
    data = load_json(file_path, default={})

    if not isinstance(data, dict):
        raise ValueError(f"File {file_path} does not contain a JSON object")

    # Update fields
    data.update(updates)

    # Save back
    save_json(data, file_path)


def backup_json(file_path: str, backup_dir: Optional[str] = None) -> str:
    """
    Create timestamped backup of JSON file

    Args:
        file_path: Path to JSON file to backup
        backup_dir: Optional backup directory (defaults to same dir with .backup suffix)

    Returns:
        Path to backup file
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")

    # Determine backup location
    if backup_dir:
        backup_path = Path(backup_dir)
    else:
        backup_path = path.parent / '.backups'

    backup_path.mkdir(parents=True, exist_ok=True)

    # Create timestamped backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_path / f"{path.stem}_{timestamp}.json"

    # Copy file
    data = load_json(file_path)
    save_json(data, str(backup_file))

    return str(backup_file)


class JSONCache:
    """Simple file-based JSON cache"""

    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get cached value"""
        cache_file = self.cache_dir / f"{key}.json"
        return load_json(str(cache_file), default=default)

    def set(self, key: str, value: Any) -> None:
        """Set cached value"""
        cache_file = self.cache_dir / f"{key}.json"
        save_json(value, str(cache_file))

    def delete(self, key: str) -> bool:
        """Delete cached value"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
            return True
        return False

    def clear(self) -> int:
        """Clear all cached values"""
        count = 0
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
            count += 1
        return count

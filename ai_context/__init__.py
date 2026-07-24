__version__ = "1.0.0"

import json
from pathlib import Path


CONFIG_FILE = ".contractconfig"

DEFAULT_CONFIG = {
    "lang": "en",
    "version": __version__,
}

LANG_META = {
    "en": {"label": "English", "flag": "EN"},
    "zh": {"label": "中文", "flag": "CN"},
}


def load_config(ai_dir: str) -> dict:
    """Load contract config from .ai/.contractconfig, or return defaults."""
    path = Path(ai_dir) / CONFIG_FILE
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            pass
    return dict(DEFAULT_CONFIG)


def save_config(ai_dir: str, config: dict) -> None:
    """Save contract config to .ai/.contractconfig."""
    path = Path(ai_dir) / CONFIG_FILE
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

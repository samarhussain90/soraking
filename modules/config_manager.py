"""
Unified Configuration Manager
Consolidates configuration from 4+ sources into single interface
Priority: ENV → Database → Defaults
"""
import os
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """
    Centralized configuration management

    Load hierarchy:
    1. Environment variables (highest priority)
    2. Database settings (via SettingsManager, if available)
    3. Default values (fallback)
    """

    # SORA API CONFIGURATION
    SORA_DEFAULTS = {
        'model': 'sora-2',  # sora-2 or sora-2-pro
        'resolution': '1792x1024',  # 16:9 widescreen
        'seconds': 12,  # Video duration
        'audio_mode': 'automatic',  # automatic, music, none
        'audio_mix': 'balanced'  # balanced, music_focused, dialogue_focused
    }

    # GEMINI ANALYSIS CONFIGURATION
    GEMINI_DEFAULTS = {
        'model': 'gemini-2.0-flash-exp',
        'temperature': 0.3,
        'max_output_tokens': 8000
    }

    # AGGRESSION PRESETS
    AGGRESSION_PRESETS = {
        'soft': {
            'name': 'Soft (Calm & Educational)',
            'intensity': 0.3,
            'tone': 'calm, educational',
            'pacing': 'relaxed',
            'call_to_action': 'gentle invitation'
        },
        'medium': {
            'name': 'Medium (Balanced)',
            'intensity': 0.6,
            'tone': 'confident, helpful',
            'pacing': 'steady',
            'call_to_action': 'clear offer'
        },
        'aggressive': {
            'name': 'Aggressive (Urgent)',
            'intensity': 0.85,
            'tone': 'urgent, exciting',
            'pacing': 'fast-paced',
            'call_to_action': 'strong urgency'
        },
        'ultra': {
            'name': 'Ultra (Explosive)',
            'intensity': 1.0,
            'tone': 'explosive, shocking',
            'pacing': 'rapid-fire',
            'call_to_action': 'extreme FOMO'
        }
    }

    # FILE PATHS
    BASE_DIR = Path(__file__).parent.parent
    OUTPUT_DIR = BASE_DIR / 'output'
    VIDEOS_DIR = OUTPUT_DIR / 'videos'
    LOGS_DIR = OUTPUT_DIR / 'logs'
    TEMP_DIR = OUTPUT_DIR / 'temp'

    def __init__(self, use_database: bool = True):
        """
        Initialize configuration manager

        Args:
            use_database: Whether to load from database (requires SettingsManager)
        """
        self._db_settings = None
        self._use_database = use_database

        # Try to load from database
        if use_database:
            try:
                from modules.settings_manager import get_settings_manager
                self._db_settings = get_settings_manager()
            except Exception as e:
                print(f"⚠ Could not load database settings: {e}")
                self._db_settings = None

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value with priority hierarchy

        Args:
            section: Config section (e.g., 'sora', 'gemini')
            key: Config key
            default: Default value if not found

        Returns:
            Configuration value
        """
        # Priority 1: Environment variable
        env_key = f"{section.upper()}_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Priority 2: Database settings
        if self._db_settings:
            try:
                if section == 'sora':
                    db_value = self._db_settings.get_sora_config().get(key)
                    if db_value is not None:
                        return db_value
                elif section == 'gemini':
                    db_value = self._db_settings.get_gemini_prompts().get(key)
                    if db_value is not None:
                        return db_value
                elif section == 'aggression':
                    presets = self._db_settings.get_aggression_presets()
                    if key in presets:
                        return presets[key]
            except:
                pass

        # Priority 3: Defaults
        if section == 'sora':
            return self.SORA_DEFAULTS.get(key, default)
        elif section == 'gemini':
            return self.GEMINI_DEFAULTS.get(key, default)
        elif section == 'aggression':
            return self.AGGRESSION_PRESETS.get(key, default)

        return default

    def get_sora_config(self) -> Dict[str, Any]:
        """Get complete Sora configuration"""
        config = {}
        for key in self.SORA_DEFAULTS:
            config[key] = self.get('sora', key)
        return config

    def get_gemini_config(self) -> Dict[str, Any]:
        """Get complete Gemini configuration"""
        config = {}
        for key in self.GEMINI_DEFAULTS:
            config[key] = self.get('gemini', key)
        return config

    def get_aggression_preset(self, level: str) -> Optional[Dict]:
        """Get aggression preset by level"""
        return self.get('aggression', level)

    def get_all_aggression_presets(self) -> Dict:
        """Get all aggression presets"""
        if self._db_settings:
            try:
                return self._db_settings.get_aggression_presets()
            except:
                pass
        return self.AGGRESSION_PRESETS.copy()

    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key"""
        return os.getenv('OPENAI_API_KEY', '')

    @property
    def gemini_api_key(self) -> str:
        """Get Gemini API key"""
        return os.getenv('GEMINI_API_KEY', '')

    @property
    def do_spaces_access_key(self) -> str:
        """Get DigitalOcean Spaces access key"""
        return os.getenv('DO_SPACES_ACCESS_KEY', '')

    @property
    def do_spaces_secret_key(self) -> str:
        """Get DigitalOcean Spaces secret key"""
        return os.getenv('DO_SPACES_SECRET_KEY', '')

    @property
    def supabase_url(self) -> str:
        """Get Supabase URL"""
        return os.getenv('SUPABASE_URL', '')

    @property
    def supabase_key(self) -> str:
        """Get Supabase key"""
        return os.getenv('SUPABASE_KEY', '')

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate that required API keys are configured

        Returns:
            Dict of key names and their configured status
        """
        return {
            'openai': bool(self.openai_api_key),
            'gemini': bool(self.gemini_api_key),
            'spaces_access': bool(self.do_spaces_access_key),
            'spaces_secret': bool(self.do_spaces_secret_key),
            'supabase_url': bool(self.supabase_url),
            'supabase_key': bool(self.supabase_key)
        }

    def ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.OUTPUT_DIR, self.VIDEOS_DIR, self.LOGS_DIR, self.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Singleton instance
_config_manager = None


def get_config_manager(use_database: bool = True) -> ConfigManager:
    """
    Get singleton ConfigManager instance

    Args:
        use_database: Whether to use database for configuration

    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(use_database=use_database)
    return _config_manager

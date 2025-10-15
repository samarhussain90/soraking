"""
Configuration management for the Ad Cloning Platform
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    IDEOGRAM_API_KEY = os.getenv('IDEOGRAM_API_KEY')
    PORT = int(os.getenv('PORT', 3000))

    # Project paths
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / 'output'
    ANALYSIS_DIR = OUTPUT_DIR / 'analysis'
    VIDEOS_DIR = OUTPUT_DIR / 'videos'
    LOGS_DIR = OUTPUT_DIR / 'logs'
    TEMPLATES_DIR = BASE_DIR / 'templates'

    # Sora settings
    SORA_MODEL = 'sora-2-pro'  # Using Sora 2 Pro for better quality and character consistency
    SORA_RESOLUTION = '1792x1024'  # Higher resolution (Sora 2 Pro supports up to 1792x1024)
    SORA_DURATION = '12'  # Max duration per clip

    # Sora pricing (per second)
    SORA_2_COST_PER_SECOND = 0.064  # $0.064/second for Sora 2
    SORA_2_PRO_COST_PER_SECOND = 0.32  # $0.32/second for Sora 2 Pro

    # Note: Sora 2 Pro supports 1792x1024, but Sora 2 only supports 1280x720 (landscape) or 720x1280 (portrait)

    # Video settings
    DEFAULT_AD_DURATION = 48  # Total ad length in seconds
    SCENES_PER_AD = 4  # 4 scenes × 12s = 48s

    # Gemini settings
    GEMINI_MODEL = 'gemini-2.5-pro'

    # Sora 2 Pro Audio Settings
    AUDIO_ENABLED = True  # Enable audio generation in prompts
    AUDIO_MIX = 'cinematic'  # Audio quality: 'standard' or 'cinematic'

    # Text Overlay Defaults
    TEXT_FONT_PRIMARY = 'Bebas Neue'  # For large callouts (prices, big numbers)
    TEXT_FONT_SECONDARY = 'Montserrat Black'  # For CTAs and secondary text
    TEXT_SIZE_LARGE = '120pt'  # Price reveals, shocking statements
    TEXT_SIZE_MEDIUM = '80pt'  # Questions, hooks
    TEXT_SIZE_SMALL = '60pt'  # CTAs, supporting text
    TEXT_COLORS = {
        'urgent': 'red',
        'highlight': 'yellow',
        'cta': 'white',
        'price': 'green',
        'default': 'white'
    }

    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.OUTPUT_DIR, cls.ANALYSIS_DIR, cls.VIDEOS_DIR,
                         cls.LOGS_DIR, cls.TEMPLATES_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate_api_keys(cls):
        """Validate that all required API keys are present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        return True

# Create directories on import
Config.create_directories()

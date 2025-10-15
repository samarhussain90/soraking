"""
Settings Manager
Manages system settings and prompts stored in Supabase
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from modules.supabase_client import SupabaseClient


class SettingsManager:
    """Manages settings stored in Supabase with caching"""

    def __init__(self):
        """Initialize settings manager"""
        self.client = SupabaseClient()
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = timedelta(minutes=5)  # Cache for 5 minutes

    def get_setting(
        self,
        category: str,
        key: str,
        use_cache: bool = True
    ) -> Optional[Dict]:
        """
        Get a single setting by category and key

        Args:
            category: Setting category (e.g., 'aggression_preset', 'system_prompt')
            key: Setting key (e.g., 'soft', 'gemini_analysis')
            use_cache: Whether to use cached value

        Returns:
            Setting value as dict, or None if not found
        """
        cache_key = f"{category}:{key}"

        # Check cache
        if use_cache and cache_key in self._cache:
            cache_time = self._cache_time.get(cache_key)
            if cache_time and datetime.now() - cache_time < self._cache_ttl:
                return self._cache[cache_key]

        # Fetch from database
        try:
            response = self.client.supabase.table('settings')\
                .select('*')\
                .eq('category', category)\
                .eq('key', key)\
                .execute()

            if response.data and len(response.data) > 0:
                setting = response.data[0]
                # Cache the result
                self._cache[cache_key] = setting
                self._cache_time[cache_key] = datetime.now()
                return setting

            return None

        except Exception as e:
            print(f"Error fetching setting {category}:{key}: {e}")
            return None

    def get_settings_by_category(
        self,
        category: str,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Get all settings for a category

        Args:
            category: Setting category
            use_cache: Whether to use cached values

        Returns:
            List of settings
        """
        cache_key = f"category:{category}"

        # Check cache
        if use_cache and cache_key in self._cache:
            cache_time = self._cache_time.get(cache_key)
            if cache_time and datetime.now() - cache_time < self._cache_ttl:
                return self._cache[cache_key]

        # Fetch from database
        try:
            response = self.client.supabase.table('settings')\
                .select('*')\
                .eq('category', category)\
                .order('key')\
                .execute()

            settings = response.data or []

            # Cache the result
            self._cache[cache_key] = settings
            self._cache_time[cache_key] = datetime.now()

            return settings

        except Exception as e:
            print(f"Error fetching settings for category {category}: {e}")
            return []

    def get_all_settings(self) -> List[Dict]:
        """
        Get all settings

        Returns:
            List of all settings
        """
        try:
            response = self.client.supabase.table('settings')\
                .select('*')\
                .order('category', 'key')\
                .execute()

            return response.data or []

        except Exception as e:
            print(f"Error fetching all settings: {e}")
            return []

    def update_setting(
        self,
        category: str,
        key: str,
        value: Any,
        description: Optional[str] = None
    ) -> bool:
        """
        Update a setting value

        Args:
            category: Setting category
            key: Setting key
            value: New value (will be converted to JSONB)
            description: Optional new description

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure value is a dict for JSONB storage
            if not isinstance(value, dict):
                value = {'value': value}

            update_data = {
                'value': value,
                'updated_at': datetime.now().isoformat()
            }

            if description:
                update_data['description'] = description

            response = self.client.supabase.table('settings')\
                .update(update_data)\
                .eq('category', category)\
                .eq('key', key)\
                .execute()

            # Clear cache for this setting
            cache_key = f"{category}:{key}"
            if cache_key in self._cache:
                del self._cache[cache_key]
                del self._cache_time[cache_key]

            # Clear category cache
            category_cache_key = f"category:{category}"
            if category_cache_key in self._cache:
                del self._cache[category_cache_key]
                del self._cache_time[category_cache_key]

            return True

        except Exception as e:
            print(f"Error updating setting {category}:{key}: {e}")
            return False

    def create_setting(
        self,
        category: str,
        key: str,
        value: Any,
        description: Optional[str] = None
    ) -> bool:
        """
        Create a new setting

        Args:
            category: Setting category
            key: Setting key
            value: Setting value (will be converted to JSONB)
            description: Optional description

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure value is a dict for JSONB storage
            if not isinstance(value, dict):
                value = {'value': value}

            insert_data = {
                'category': category,
                'key': key,
                'value': value
            }

            if description:
                insert_data['description'] = description

            response = self.client.supabase.table('settings')\
                .insert(insert_data)\
                .execute()

            # Clear category cache
            category_cache_key = f"category:{category}"
            if category_cache_key in self._cache:
                del self._cache[category_cache_key]
                del self._cache_time[category_cache_key]

            return True

        except Exception as e:
            print(f"Error creating setting {category}:{key}: {e}")
            return False

    def delete_setting(
        self,
        category: str,
        key: str
    ) -> bool:
        """
        Delete a setting

        Args:
            category: Setting category
            key: Setting key

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.supabase.table('settings')\
                .delete()\
                .eq('category', category)\
                .eq('key', key)\
                .execute()

            # Clear cache
            cache_key = f"{category}:{key}"
            if cache_key in self._cache:
                del self._cache[cache_key]
                del self._cache_time[cache_key]

            category_cache_key = f"category:{category}"
            if category_cache_key in self._cache:
                del self._cache[category_cache_key]
                del self._cache_time[category_cache_key]

            return True

        except Exception as e:
            print(f"Error deleting setting {category}:{key}: {e}")
            return False

    def clear_cache(self):
        """Clear all cached settings"""
        self._cache = {}
        self._cache_time = {}

    # Convenience methods for specific settings

    def get_gemini_prompt(self) -> str:
        """Get the Gemini analysis system prompt"""
        setting = self.get_setting('system_prompt', 'gemini_analysis')
        if setting and 'value' in setting:
            return setting['value'].get('prompt', '')
        return ''

    def get_aggression_presets(self) -> Dict[str, Dict]:
        """
        Get all aggression presets

        Returns:
            Dict with keys: soft, medium, aggressive, ultra
        """
        settings = self.get_settings_by_category('aggression_preset')
        presets = {}
        for setting in settings:
            presets[setting['key']] = setting['value']
        return presets

    def get_aggression_preset(self, level: str) -> Optional[Dict]:
        """Get a specific aggression preset"""
        setting = self.get_setting('aggression_preset', level)
        if setting and 'value' in setting:
            return setting['value']
        return None

    def get_sora_config(self) -> Dict:
        """Get Sora technical configuration"""
        setting = self.get_setting('sora_config', 'technical_specs')
        if setting and 'value' in setting:
            return setting['value']
        return {
            'resolution': '4K',
            'aspect_ratio': '1792x1024',
            'default_style': 'engaging',
            'default_color_grade': 'cinematic',
            'audio_mix': 'cinematic'
        }


# Singleton instance
_settings_manager = None

def get_settings_manager() -> SettingsManager:
    """Get or create settings manager singleton"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


# Test function
if __name__ == "__main__":
    manager = get_settings_manager()

    print("Testing Settings Manager\n" + "="*50)

    # Test getting Gemini prompt
    print("\n1. Gemini Prompt:")
    prompt = manager.get_gemini_prompt()
    print(f"Length: {len(prompt)} characters")
    print(f"Preview: {prompt[:100]}...")

    # Test getting aggression presets
    print("\n2. Aggression Presets:")
    presets = manager.get_aggression_presets()
    for level, preset in presets.items():
        print(f"  - {level}: {preset.get('name', 'N/A')}")

    # Test getting Sora config
    print("\n3. Sora Config:")
    config = manager.get_sora_config()
    print(f"  Resolution: {config.get('resolution')}")
    print(f"  Aspect Ratio: {config.get('aspect_ratio')}")

    print("\n" + "="*50)
    print("Settings Manager test complete!")

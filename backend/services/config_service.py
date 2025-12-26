import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from config import Settings, get_settings
from services.provider_registry import get_all_cloud_providers, get_openrouter_models

SETTINGS_FILE = Path(__file__).parent.parent / "settings.json"

class ConfigService:
    """Manages user settings via settings.json, merged with .env secrets"""

    def __init__(self):
        self.env_settings = get_settings()
        self.user_settings = self._load_user_settings()
        # Auto-migrate old settings format if needed
        self._migrate_if_needed()

    def _load_user_settings(self) -> Dict[str, Any]:
        """Load settings.json, return empty dict if not found"""
        if not SETTINGS_FILE.exists():
            return {}
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_user_settings(self, updates: Dict[str, Any]) -> bool:
        """Save updates to settings.json"""
        try:
            # Merge with existing settings
            current = self._load_user_settings()
            self._deep_merge(current, updates)

            # Write to file
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(current, f, indent=2)

            # Reload in-memory settings
            self.user_settings = current
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def _deep_merge(self, base: dict, updates: dict):
        """Recursively merge updates into base"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in base:
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get_llm_config(self) -> Dict[str, Any]:
        """Get merged LLM configuration"""
        # Check if using new format
        if "llm" in self.user_settings and "provider_type" in self.user_settings["llm"]:
            llm_settings = self.user_settings["llm"]
            provider_type = llm_settings["provider_type"]

            config = {
                "provider_type": provider_type
            }

            if provider_type == "cloud":
                cloud_provider = llm_settings.get("cloud_provider")
                config["cloud_provider"] = cloud_provider

                # Get provider-specific config
                if "cloud_service_config" in llm_settings:
                    provider_config = llm_settings["cloud_service_config"].get(cloud_provider, {})
                    config.update(provider_config)

                    # Get API key from api_keys or env
                    if cloud_provider == "openrouter":
                        config["api_key"] = self.get_api_key("openrouter") or self.env_settings.openrouter_api_key
                    elif cloud_provider == "openai":
                        config["api_key"] = self.get_api_key("openai") or ""

            else:  # local
                local_config = llm_settings.get("local", {})
                config.update(local_config)

            return config

        # Fallback to old format / env defaults
        env = get_settings()
        return {
            "provider": env.llm_provider,
            "base_url": env.llm_base_url,
            "model": env.openrouter_model,
            "api_key": env.openrouter_api_key,
            "max_tokens": env.openrouter_max_tokens,
            "temperature": env.openrouter_temperature,
            "top_p": env.openrouter_top_p,
            "frequency_penalty": env.openrouter_frequency_penalty,
            "presence_penalty": env.openrouter_presence_penalty,
            "repetition_penalty": env.openrouter_repetition_penalty
        }

    def get_embedding_config(self) -> Dict[str, str]:
        """Get embedding model configuration"""
        default = {"model": self.env_settings.embedding_model}
        if "embedding" in self.user_settings:
            default.update(self.user_settings["embedding"])
        return default

    def _migrate_if_needed(self):
        """Auto-migrate old settings format to new format"""
        if "llm" not in self.user_settings:
            return

        llm_settings = self.user_settings["llm"]

        # Check if already using new format
        if "provider_type" in llm_settings:
            return

        # Check if using old format
        if "provider" not in llm_settings:
            return

        print("Migrating settings to new format...")
        old_provider = llm_settings["provider"]

        # Map old provider to new structure
        provider_map = {
            "openrouter": ("cloud", "openrouter"),
            "openai-compatible": ("cloud", "custom"),
            "local": ("local", None)
        }

        if old_provider not in provider_map:
            print(f"Unknown provider {old_provider}, skipping migration")
            return

        provider_type, cloud_provider = provider_map[old_provider]

        # Build new structure
        new_llm_config = {
            "provider_type": provider_type
        }

        if provider_type == "cloud":
            new_llm_config["cloud_provider"] = cloud_provider
            new_llm_config["cloud_service_config"] = {}

            # Copy config to appropriate cloud provider
            config_data = {
                "model": llm_settings.get("model", ""),
                "temperature": llm_settings.get("temperature", 0.7),
                "max_tokens": llm_settings.get("max_tokens", 1024)
            }

            # Add OpenRouter-specific params if applicable
            if cloud_provider == "openrouter":
                config_data.update({
                    "top_p": llm_settings.get("top_p", 0.9),
                    "frequency_penalty": llm_settings.get("frequency_penalty", 0.2),
                    "presence_penalty": llm_settings.get("presence_penalty", 0.0),
                    "repetition_penalty": llm_settings.get("repetition_penalty", 1.1)
                })
            # Add base_url for custom provider
            elif cloud_provider == "custom":
                config_data["base_url"] = llm_settings.get("base_url", "")

            new_llm_config["cloud_service_config"][cloud_provider] = config_data

        else:  # local
            new_llm_config["local"] = {
                "base_url": llm_settings.get("base_url", "http://localhost:8080"),
                "temperature": llm_settings.get("temperature", 0.7),
                "max_tokens": llm_settings.get("max_tokens", 1024)
            }

        # Save migrated settings
        self.user_settings["llm"] = new_llm_config
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.user_settings, f, indent=2)

        print("Migration complete!")

    def get_cloud_providers(self) -> list:
        """Get available cloud providers"""
        return get_all_cloud_providers()

    def get_openrouter_models(self) -> list:
        """Get available OpenRouter models"""
        api_key = self.get_api_key("openrouter") or self.env_settings.openrouter_api_key
        return get_openrouter_models(api_key)

    def get_api_keys(self) -> Dict[str, bool]:
        """Get API key status (not the keys themselves, just whether they're set)"""
        api_keys = self.user_settings.get("api_keys", {})
        return {
            "openrouter": bool(api_keys.get("openrouter")),
            "openai": bool(api_keys.get("openai")),
            "github_token": bool(api_keys.get("github_token")),
            "openweather_api_key": bool(api_keys.get("openweather_api_key")),
            "crypto_api_key": bool(api_keys.get("crypto_api_key"))
        }

    def get_api_key(self, service: str) -> Optional[str]:
        """Get a specific API key"""
        api_keys = self.user_settings.get("api_keys", {})
        return api_keys.get(service)

    def save_api_keys(self, keys: Dict[str, str]) -> bool:
        """Save API keys (only saves non-empty values)"""
        if "api_keys" not in self.user_settings:
            self.user_settings["api_keys"] = {}

        # Only update keys that are provided and non-empty
        for key, value in keys.items():
            if value:  # Only save if not empty
                self.user_settings["api_keys"][key] = value

        return self.save_user_settings(self.user_settings)

# Singleton instance
_config_service: Optional[ConfigService] = None

def get_config_service() -> ConfigService:
    global _config_service
    if _config_service is None:
        _config_service = ConfigService()
    return _config_service

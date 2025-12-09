from typing import Optional, Dict

_tokens: Dict[str, Dict[str, str]] = {}

def set_token(provider: str, user_id: str, access_token: str, refresh_token: Optional[str] = None):
    user_tokens = _tokens.setdefault(user_id, {})
    user_tokens[f"{provider}_access_token"] = access_token
    if refresh_token:
        user_tokens[f"{provider}_refresh_token"] = refresh_token

def get_token(provider: str, user_id: str) -> Optional[str]:
    return _tokens.get(user_id, {}).get(f"{provider}_access_token")

def has_token(provider: str, user_id: str) -> bool:
    return get_token(provider, user_id) is not None

def token_summary(user_id: str) -> Dict[str, bool]:
    return {
        "google": has_token("google", user_id),
        "drive": has_token("google", user_id),
        "gmail": has_token("google", user_id),
        "slack": has_token("slack", user_id),
        "notion": has_token("notion", user_id),
    }


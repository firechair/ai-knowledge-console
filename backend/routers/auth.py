from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import httpx
from urllib.parse import urlencode
import json
from config import get_settings
from services.oauth_tokens import set_token

router = APIRouter()

DEFAULT_USER = "default_user"

def get_google_auth_url(state: str | None = None) -> str:
    cfg = get_settings()
    redirect_uri = f"{cfg.app_base_url}/api/auth/google/callback"
    params = {
        "client_id": cfg.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/drive.readonly",
        "access_type": "offline",
        "prompt": "consent"
    }
    if state:
        params["state"] = state
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

@router.get("/google/login")
async def google_login(state: str | None = None):
    cfg = get_settings()
    if not cfg.google_client_id or not cfg.google_client_secret:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")
    return RedirectResponse(get_google_auth_url(state))

@router.get("/gmail/login")
async def gmail_login(state: str | None = None):
    # Alias to Google OAuth login for Gmail
    return await google_login(state)

@router.get("/drive/login")
async def drive_login(state: str | None = None):
    # Alias to Google OAuth login for Drive
    return await google_login(state)

@router.get("/google/callback")
async def google_callback(code: str, state: str | None = None):
    cfg = get_settings()
    redirect_uri = f"{cfg.app_base_url}/api/auth/google/callback"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": cfg.google_client_id,
                "client_secret": cfg.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = resp.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        if access_token:
            set_token("google", DEFAULT_USER, access_token, refresh_token)
        if state:
            try:
                obj = json.loads(state)
                return_url = obj.get("return_url")
                if return_url:
                    return RedirectResponse(return_url)
            except Exception:
                pass
        if getattr(cfg, "frontend_base_url", None):
            return RedirectResponse(f"{cfg.frontend_base_url}/#/connectors")
        return {"status": "success", "provider": "google", "authorized": bool(access_token)}

def get_slack_auth_url(state: str | None = None) -> str:
    cfg = get_settings()
    redirect_uri = f"{cfg.app_base_url}/api/auth/slack/callback"
    params = {
        "client_id": cfg.slack_client_id,
        "scope": "channels:history,groups:history,search:read",
        "user_scope": "",
        "redirect_uri": redirect_uri,
    }
    if state:
        params["state"] = state
    return f"https://slack.com/oauth/v2/authorize?{urlencode(params)}"

@router.get("/slack/login")
async def slack_login(state: str | None = None):
    cfg = get_settings()
    if not cfg.slack_client_id or not cfg.slack_client_secret:
        raise HTTPException(status_code=400, detail="Slack OAuth not configured")
    return RedirectResponse(get_slack_auth_url(state))

@router.get("/slack/callback")
async def slack_callback(code: str, state: str | None = None):
    cfg = get_settings()
    redirect_uri = f"{cfg.app_base_url}/api/auth/slack/callback"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "client_id": cfg.slack_client_id,
                "client_secret": cfg.slack_client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
        data = resp.json()
        access_token = data.get("access_token") or (data.get("authed_user") or {}).get("access_token")
        if access_token:
            set_token("slack", DEFAULT_USER, access_token)
        if state:
            try:
                obj = json.loads(state)
                return_url = obj.get("return_url")
                if return_url:
                    return RedirectResponse(return_url)
            except Exception:
                pass
        if getattr(cfg, "frontend_base_url", None):
            return RedirectResponse(f"{cfg.frontend_base_url}/#/connectors")
        return {"status": "success", "provider": "slack", "authorized": bool(access_token)}

def get_notion_auth_url(state: str | None = None) -> str:
    cfg = get_settings()
    redirect_uri = f"{cfg.app_base_url}/api/auth/notion/callback"
    params = {
        "client_id": cfg.notion_client_id,
        "response_type": "code",
        "owner": "user",
        "redirect_uri": redirect_uri,
    }
    if state:
        params["state"] = state
    return f"https://api.notion.com/v1/oauth/authorize?{urlencode(params)}"

@router.get("/notion/login")
async def notion_login(state: str | None = None):
    cfg = get_settings()
    if not cfg.notion_client_id or not cfg.notion_client_secret:
        raise HTTPException(status_code=400, detail="Notion OAuth not configured")
    return RedirectResponse(get_notion_auth_url(state))

@router.get("/notion/callback")
async def notion_callback(code: str, state: str | None = None):
    cfg = get_settings()
    redirect_uri = f"{cfg.app_base_url}/api/auth/notion/callback"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.notion.com/v1/oauth/token",
            auth=(cfg.notion_client_id, cfg.notion_client_secret),
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/json"},
        )
        data = resp.json()
        access_token = data.get("access_token")
        if access_token:
            set_token("notion", DEFAULT_USER, access_token)
        if state:
            try:
                obj = json.loads(state)
                return_url = obj.get("return_url")
                if return_url:
                    return RedirectResponse(return_url)
            except Exception:
                pass
        if getattr(cfg, "frontend_base_url", None):
            return RedirectResponse(f"{cfg.frontend_base_url}/#/connectors")
        return {"status": "success", "provider": "notion", "authorized": bool(access_token)}

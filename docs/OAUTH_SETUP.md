# OAuth Setup Guide

This guide explains how to configure OAuth credentials for Gmail, Google Drive, Slack, and Notion.

## Understanding OAuth

**Important**: OAuth credentials are **application credentials**, not user credentials.

- **You** (developer/admin) set up credentials **once**
- **End users** connect **their own** accounts through the UI
- Each user's tokens are stored separately

## Google (Gmail + Drive)

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to **APIs & Services > OAuth consent screen**

### 2. Configure OAuth Consent Screen

1. Choose **External** (or Internal for Google Workspace)
2. Fill in app information:
   - App name: "AI Knowledge Console"
   - User support email: your email
   - Developer contact: your email
3. Add scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/drive.readonly`
4. Save and continue

### 3. Create OAuth Credentials

1. Go to **Credentials** tab
2. Click **Create Credentials > OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Name: "AI Knowledge Console"
5. Authorized redirect URIs:
   ```
   http://localhost:8000/api/auth/google/callback
   ```
   (Add production URL when deploying)
6. Click **Create**
7. **Copy** Client ID and Client Secret

### 4. Enable APIs

1. Go to **API Library**
2. Enable:
   - Gmail API
   - Google Drive API

### 5. Add to .env

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

---

## Slack

### 1. Create Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click **Create New App**
3. Choose **From scratch**
4. App name: "AI Knowledge Console"
5. Select your workspace

### 2. Configure OAuth & Permissions

1. In left sidebar, click **OAuth & Permissions**
2. Under **Redirect URLs**, add:
   ```
   http://localhost:8000/api/auth/slack/callback
   ```
3. Under **Scopes > Bot Token Scopes**, add:
   - `search:read`
   - `channels:history`
   - `groups:history`

### 3. Get Credentials

1. In left sidebar, click **Basic Information**
2. Under **App Credentials**:
   - Copy **Client ID**
   - Copy **Client Secret**

### 4. Add to .env

```env
SLACK_CLIENT_ID=your_client_id_here
SLACK_CLIENT_SECRET=your_client_secret_here
```

---

## Notion

### 1. Create Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click **+ New integration**
3. Name: "AI Knowledge Console"
4. Associated workspace: select your workspace
5. Type: **Public integration**

### 2. Configure OAuth

1. Under **OAuth Domain & URIs**:
   - Redirect URI:
     ```
     http://localhost:8000/api/auth/notion/callback
     ```

### 3. Get Credentials

1. Copy **OAuth client ID**
2. Copy **OAuth client secret**

### 4. Add to .env

```env
NOTION_CLIENT_ID=your_oauth_client_id_here
NOTION_CLIENT_SECRET=your_oauth_secret_here
```

---

## Testing the OAuth Flow

### 1. Start the Application

```bash
cd backend
source .venv/bin/activate
uvicorn app:app --reload

# In another terminal
cd frontend
npm run dev
```

### 2. Authorize Services (Manual Setup)

1. Open `http://localhost:5173`
2. Go to **Connectors** tab
3. Click **Authorize** for the service:
   - **Gmail/Drive**: Opens Google consent; they use Google OAuth under the hood.
   - **Slack**: Opens Slack OAuth consent.
   - **Notion**: Opens Notion OAuth consent.
4. Grant permissions and you’ll be redirected back to the app.
5. The connector shows **Configured**, then you can toggle **Enabled**.

### 3. Enable and Test

1. Toggle service to **Enabled**
2. Go to **Chat** tab
3. Enter a search query in the tool parameter field
4. Ask the LLM a question that requires that data

**Example**:
- Enable Gmail
- Set query: "from:boss@company.com subject:report"
- Ask: "What did my boss say about the quarterly report?"
- LLM searches your emails and answers based on results

---

## Verification (Redirects)

You can confirm the redirects with quick checks:

**Google (Gmail/Drive)**
- Login: `curl -s -D - "http://localhost:8000/api/auth/google/login?state=%7B%22return_url%22%3A%22http%3A%2F%2Flocalhost%3A5173%2F%23%2Fconnectors%22%7D" | grep -i '^location'`
- Gmail alias: `curl -s -D - "http://localhost:8000/api/auth/gmail/login?..." | grep -i '^location'`
- Drive alias: `curl -s -D - "http://localhost:8000/api/auth/drive/login?..." | grep -i '^location'`
- Expect: a redirect to `accounts.google.com` with `redirect_uri=http://localhost:8000/api/auth/google/callback` and `state` pointing back to the Connectors tab.

**Slack**
- When configured: `curl -s -D - "http://localhost:8000/api/auth/slack/login?..." | grep -i '^location'` shows a redirect to Slack.
- When not configured: returns `400` JSON with `{"detail":"Slack OAuth not configured"}`.

**Notion**
- When configured: `curl -s -D - "http://localhost:8000/api/auth/notion/login?..." | grep -i '^location'` shows a redirect to Notion.
- When not configured: returns `400` JSON with `{"detail":"Notion OAuth not configured"}`.

---

## Production Deployment

### Update Redirect URIs

In each service's OAuth settings, add your production URLs:

**Google**:
```
https://your-domain.com/api/auth/google/callback
```

**Slack**:
```
https://your-domain.com/api/auth/slack/callback
```

**Notion**:
```
https://your-domain.com/api/auth/notion/callback
```

### Update .env

```env
APP_BASE_URL=https://your-domain.com
FRONTEND_BASE_URL=https://your-domain.com
```

---

## Security Notes

1. **Never commit** `.env` file to git
2. **Rotate secrets** if exposed
3. **Use HTTPS** in production
4. **Implement user sessions** instead of `user_id=default_user` in production
5. **Store tokens** in a database (currently in-memory)

---

## Troubleshooting

**"Redirect URI mismatch"**  
→ Ensure redirect URI in provider settings matches exactly

**"Invalid client"**  
→ Double-check CLIENT_ID and CLIENT_SECRET in .env

**"Access denied"**  
→ User denied permissions, they need to re-authorize

**"Tokens not working"**  
→ Restart backend after changing .env to reload settings

**"Authorize returns JSON or doesn’t go back to UI"**
→ Ensure the frontend was launched with `VITE_API_URL` pointing to the backend (e.g., `VITE_API_URL=http://localhost:8000 npm run dev`). The app now sends a `state` with `return_url` and the backend callbacks redirect to `FRONTEND_BASE_URL` (or the `state` URL) after token exchange.

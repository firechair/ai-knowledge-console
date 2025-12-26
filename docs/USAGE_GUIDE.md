# Usage Guide

This guide demonstrates practical use cases and scenarios for the AI Knowledge Console, showing you how to leverage different features for various needs.

## Table of Contents
- [New Features Guide](#new-features-guide)
- [Core RAG Usage](#core-rag-usage)
- [Conversations Management](#conversations-management)
- [External API Tools](#external-api-tools)
- [OAuth-Integrated Services](#oauth-integrated-services)
- [Advanced Scenarios](#advanced-scenarios)
- [Best Practices](#best-practices)

---

## New Features Guide

Learn how to use the latest productivity enhancements added to the AI Knowledge Console.

### Conversation Management

**Search Your Conversation History**

All your past conversations are automatically saved and searchable.

**How to use**:
1. Go to the Chat tab
2. Look for the conversation list on the left side
3. Use the search box to find conversations by content
4. Click any conversation to load its full history

**Example Workflow**:
```
Scenario: You remember discussing Python best practices last week,
          but can't remember the specifics.

Step 1: Type "Python best practices" in the conversation search
Step 2: See list of matching conversations with previews
Step 3: Click the relevant conversation to reload it
Step 4: Continue where you left off!
```

**Key Features**:
- **Real-time search**: Results update as you type
- **Content-based**: Searches through all messages, not just titles
- **Auto-refresh**: List updates every 30 seconds with new conversations
- **Preview**: See conversation titles and first message preview

### Document Preview

**Preview Files Before Uploading**

Verify file contents before processing to avoid mistakes.

**How to use**:
1. Go to the Documents tab
2. Click "Choose File" or drag-and-drop
3. Preview appears automatically
4. Review the content:
   - **Text files (.txt)**: First 500 characters shown
   - **PDF files**: filename and size displayed
   - **Word files (.docx)**: filename and size displayed
5. Click "Confirm Upload" to proceed or "Cancel" to choose another file

**Example Workflow**:
```
Scenario: You have multiple versions of a contract and want to
          upload the latest one.

Step 1: Select what you think is the latest file
Step 2: Preview shows: "This contract dated January 2024..."
Step 3: Realize it's the old version
Step 4: Click "Cancel"
Step 5: Select the correct file instead
Step 6: Preview confirms: "This contract dated November 2024..."
Step 7: Click "Confirm Upload" to proceed
```

**Benefits**:
- Prevent uploading wrong files
- Verify text extraction quality for PDFs
- Catch file corruption early
- Confirm file contents match expectations

### Keyboard Shortcuts

**Navigate Faster with Keyboard**

Use keyboard shortcuts for efficient navigation without touching the mouse.

**Available Shortcuts**:

| Shortcut | Action | Use Case |
|----------|--------|----------|
| `Cmd/Ctrl + 1` | Go to Chat tab | Quick return to conversation |
| `Cmd/Ctrl + 2` | Go to Documents tab | Upload files quickly |
| `Cmd/Ctrl + 3` | Go to Connectors tab | Configure integrations |
| `Cmd/Ctrl + 4` | Go to Settings tab | Adjust preferences |
| `Escape` | Clear conversation selection | Start fresh chat |

**Example Workflow**:
```
Typical Power User Flow:
1. Cmd+2 - Jump to Documents
2. Upload a new file
3. Cmd+1 - Jump back to Chat
4. Ask questions about the new document
5. Cmd+3 - Check a connector status
6. Cmd+1 - Return to chat
7. Escape - Start new conversation
```

**Accessibility**: All keyboard shortcuts also work for screen reader users and keyboard-only navigation.

###Conversation Context Tips

**Making the Most of Conversation Memory**

The AI remembers your entire conversation history within a session.

**Best Practices**:

**Do**:
- Use "+ New Conversation" when switching topics completely
- Keep related questions in the same conversation
- Reference previous answers: "Based on what you just said about X..."

**Don't**:
- Mix unrelated topics in one conversation
- Forget to start new conversations for new documents

**Example - Good Conversation Flow**:
```
Conversation 1 (Project Alpha):
You: "What are the requirements for Project Alpha?"
AI: [Lists requirements from docs]
You: "What's the timeline?" ← AI knows you mean Project Alpha
AI: [Provides timeline]
You: "Any risks?" ← Still contextually aware
AI: [Lists risks]

[Start new conversation for different topic]

Conversation 2 (Budget Analysis):
You: "Show me the Q4 budget breakdown"
AI: [Fresh context, focused on budget]
```

---

## Model Management Workflows

### Downloading a Local LLM Model

**Scenario:** You want to download a local model for offline inference.

**Steps:**
1. Navigate to **Settings** tab in the UI
2. Select **Models** section
3. Click **Download LLM Model**
4. Enter HuggingFace repository (e.g., `TheBloke/Llama-2-7B-GGUF`)
5. Enter filename (e.g., `llama-2-7b.Q4_K_M.gguf`)
6. Monitor download progress
7. Model appears in "Local Models" list when complete
8. Configure LLM settings to use the downloaded model

**What Happens:**
- ModelManager downloads GGUF file from HuggingFace
- Progress tracked in real-time
- Model stored in `MODELS_DIR` (default: `./models`)
- Ready to use with local llama.cpp server

**Tips:**
- Choose quantized models (Q4_K_M, Q5_K_M) for better performance
- Check model size before downloading (some are >10GB)
- Use TheBloke's repositories for quality GGUF models

---

### Switching LLM Providers

**Scenario:** Switch from local llama.cpp to cloud provider (OpenRouter).

**Steps:**
1. Navigate to **Settings** → **LLM Configuration**
2. Toggle provider type to **Cloud**
3. Select **OpenRouter** from cloud providers dropdown
4. Enter your OpenRouter API key
5. Select model (e.g., `x-ai/grok-4.1-fast`, `anthropic/claude-3.5-sonnet`)
6. Adjust temperature and max_tokens if desired
7. Click **Save Configuration**
8. Chat interface now uses OpenRouter

**Switching Back to Local:**
1. Toggle provider type to **Local**
2. Configure local LLM URL (default: `http://localhost:8080`)
3. Save configuration

**What Happens:**
- ConfigService updates settings.json
- LLMService switches provider immediately
- No restart required
- Settings persist across sessions

**Tips:**
- Keep both local and cloud API keys configured
- Use local for privacy-sensitive chats
- Use cloud for better quality when internet is available
- Monitor OpenRouter costs at their dashboard

---

### Exporting Conversations

**Scenario:** Export a conversation as PDF for sharing with your team.

**Steps:**
1. Complete your conversation in the Chat interface
2. In the chat input, type: *"Generate a PDF summary of this conversation"*
3. The AI creates a downloadable PDF file
4. Click the download link in the response
5. PDF opens with formatted conversation history

**Available Formats:**
- **PDF**: Professional formatting, ideal for sharing
- **Markdown**: Plain text with formatting, ideal for documentation
- **HTML**: Web-ready version, ideal for embedding

**Example Prompts:**
- "Create a PDF of this conversation"
- "Export this chat as Markdown"
- "Generate an HTML version of our discussion"
- "Make a PDF with bullet-point summary of key decisions"

**What Happens:**
- LLM recognizes file generation request
- FileService generates file in requested format
- File stored in `static/generated/`
- Absolute URL returned for download
- Click link to download instantly

**Tips:**
- Request specific formatting (e.g., "with bullet points")
- Ask for summaries to condense long conversations
- Generated files persist until manually deleted
- Works in Docker and local setups

---

### Managing API Keys

**Scenario:** Add GitHub token for commit search integration.

**Steps:**
1. Navigate to **Settings** → **API Keys**
2. Find **GitHub** in the list
3. Enter your Personal Access Token
4. Click **Save**
5. Status indicator shows "Configured"
6. GitHub tool is now available in Chat settings

**Removing API Keys:**
1. Navigate to API Keys section
2. Click **Delete** next to the service
3. Confirms removal and disables integration

**What Happens:**
- ConfigService stores key in settings.json
- Connector becomes available immediately
- Key used for API calls to external service
- Status validation shows if key is working

**Supported Services:**
- **OpenRouter**: Cloud LLM provider
- **GitHub**: Repository commit search
- **OpenWeather**: Weather data
- **OAuth Services**: Configured separately via Connectors tab

**Tips:**
- Use environment variables for production deployments
- Rotate keys periodically for security
- Test connection after adding keys
- Check status indicators for validation

---

## Core RAG Usage

The primary function of the AI Knowledge Console is to let you chat with your documents using Retrieval-Augmented Generation.

### Scenario 1: Research Paper Analysis

**Use Case**: You have multiple research papers and want to extract insights across them.

**Steps**:
1. Upload your PDF papers via the Documents page
2. Wait for indexing to complete
3. Ask questions like:
   - "What are the main findings across all papers?"
   - "Compare the methodologies used in these studies"
   - "What are the key limitations mentioned?"

**How It Works**:
- Documents are chunked into semantic sections
- Your question is converted to an embedding
- Relevant chunks are retrieved from ChromaDB
- LLM generates an answer based only on retrieved context

**Example Conversation**:
```
You: "Summarize the key findings from the papers"
AI: Based on the uploaded documents, the main findings include:
    1. [Finding from Paper A, page 5]
    2. [Finding from Paper B, section 3]...
    
You: "What methodology was most common?"
AI: The most frequently used methodology across the papers was...
```

### Scenario 2: Code Documentation

**Use Case**: Internal codebase documentation that you need to reference frequently.

**Steps**:
1. Upload `.txt` or `.docx` files containing API docs, architecture notes
2. Enable conversation memory for context-aware follow-ups
3. Ask specific implementation questions

**Example Questions**:
- "How do I authenticate with the payment API?"
- "What's the rate limit for the user endpoint?"
- "Show me example request/response for creating an order"

---

## API Key Setup Tutorial

To use the external tools, you'll need to obtain API keys. Here is a step-by-step guide for each provider.

### 1. GitHub Personal Access Token
**Purpose**: Fetch commit data from repositories.

1. Go to **[GitHub Settings > Developer settings](https://github.com/settings/apps)**.
2. Click **Personal access tokens** → **Tokens (classic)**.
3. Click **Generate new token** → **Generate new token (classic)**.
4. Fill in:
   - **Note**: "AI Knowledge Console"
   - **Expiration**: 90 days (recommended)
   - **Scopes**: Check only **`repo`** (gives read access).
5. Click **Generate token** and copy it immediately (starts with `ghp_...`).

### 2. OpenWeather API Key
**Purpose**: Get real-time weather data.

1. Go to **[OpenWeatherMap](https://openweathermap.org/)** and sign in/up.
2. Click your username (top right) → **My API keys**.
3. You will see a **Default** key, or create a new one named "AI Console".
4. Copy the 32-character key.
   - *Note: New keys take ~10 minutes to activate.*

### 3. CoinGecko & Hacker News
**Good news**: These APIs are **public and free**. No keys required!
- **CoinGecko**: Rate limited to ~50 calls/min (plenty for personal use).
- **Hacker News**: Completely open API.

### 4. OAuth APIs (Gmail, Drive, Slack, Notion)
For these services, you need to create an OAuth App in their respective developer consoles.
Detailed step-by-step instructions are available in the **[OAuth Setup Guide](oauth_setup.md)**.

---

## External API Tools

The application includes optional API integrations for real-time data.

### Scenario 3: Track Open Source Projects

**Use Case**: Monitor recent commits in GitHub repositories you're following.

**Setup**:
1. Add `GITHUB_TOKEN` to `.env`
2. Enable "GitHub" connector in the UI

**Usage**:
```
You: "Show me recent commits in facebook/react"
AI: Here are the latest commits:
    - abc1234: Fix SSR hydration bug (by @johndoe, 2 hours ago)
    - def5678: Update docs for hooks API (by @janedoe, 5 hours ago)...
```

**Combined with Documents**:
```
You: "Compare React's recent changes with what's mentioned in my architecture doc"
AI: The recent React commits focus on SSR improvements, which aligns with 
    the concerns mentioned on page 3 of your architecture document...
```

### Scenario 4: Cryptocurrency Research

**Use Case**: Research crypto investments while referencing your personal notes.

**Setup**:
1. Enable "Crypto" connector (no API key needed)
2. Upload your investment research documents

**Usage**:
```
You: "What's the current price of bitcoin?"
AI: Bitcoin is currently $43,250 USD (€39,800 EUR), down 2.3% in 24h

You: "How does this compare to my price target in my notes?"
AI: According to your notes (file: crypto-targets.docx), your target 
    buy price for Bitcoin was $42,000. Current price is 3% higher...
```

### Scenario 5: Developer News Digest

**Use Case**: Stay updated on tech news while working on projects.

**Setup**:
1. Enable "Hacker News" connector

**Usage**:
```
You: "What are the top Hacker News stories today?"
AI: Top stories:
    1. "New Python 3.12 Performance Improvements" (450 points, 120 comments)
    2. "WebAssembly in Production: Lessons Learned"...
    
You: "Are any of these related to the technologies in my project docs?"
AI: Yes! The Python 3.12 story is highly relevant. Your project 
    documentation mentions using Python 3.11, and the article discusses...
```

---

## OAuth-Integrated Services

For advanced integrations requiring OAuth authentication.

### Scenario 6: Email-Powered Insights

**Use Case**: Analyze patterns in your emails or find specific information.

**Setup**:
1. Configure Gmail OAuth (see [OAuth Setup Guide](oauth_setup.md))
2. Authorize via the Connectors page
3. Enable Gmail tool and set `gmail_query` parameter

**Example Queries**:
```
You: "Find emails from john@company.com about the Q4 project"
AI: Found 5 emails from john@company.com related to Q4:
    - "Re: Q4 Project Timeline" (Nov 15)
    - "Budget Approval for Q4" (Nov 20)...
    
You: "Summarize the main concerns John raised"
AI: Based on the emails, John's primary concerns were:
    1. Timeline risks due to resource constraints
    2. Budget overruns in infrastructure costs...
```

**Parameters**:
- Set `gmail_query` to Gmail search syntax: `from:john@company.com subject:Q4`

### Scenario 7: Drive Document Search

**Use Case**: Search across Google Drive files without leaving the chat.

**Setup**:
1. Configure Google Drive OAuth
2. Authorize and enable Drive tool
3. Set `drive_query` parameter

**Example Queries**:
```
You: "Find spreadsheets about marketing campaigns"
AI: Found 3 spreadsheets:
    - "2024 Marketing Budget.xlsx" (Modified: Dec 1)
    - "Campaign Performance Q3.xlsx" (Modified: Nov 28)...
    
You: "What metrics are tracked in the Campaign Performance sheet?"
AI: Based on the file metadata and your uploaded docs, the standard 
    metrics for campaign tracking include CTR, conversion rate...
```

### Scenario 8: Slack Conversation Context

**Use Case**: Reference team discussions in Slack channels.

**Setup**:
1. Configure Slack OAuth
2. Authorize workspace access
3. Set `slack_query` parameter

**Example Queries**:
```
You: "What did the team say about the API redesign?"
AI: Recent Slack messages mention:
    - @sarah: "We should prioritize backwards compatibility" (#engineering)
    - @mike: "Timeline is tight, let's scope it down" (#product)...
```

### Scenario 9: Notion Knowledge Base

**Use Case**: Search your team's Notion documentation.

**Setup**:
1. Configure Notion OAuth
2. Authorize workspace
3. Set `notion_query` parameter

**Example Queries**:
```
You: "Find onboarding docs for new engineers"
AI: Found 2 Notion pages:
    - "Engineering Onboarding Checklist" (Updated: Nov 25)
    - "Dev Environment Setup Guide" (Updated: Nov 18)...
```

---

## Advanced Scenarios

### Scenario 10: Multi-Source Research

**Use Case**: Combine information from documents, APIs, and OAuth services.

**Example Workflow**:
```
1. Upload: Contract documents, project specs
2. Enable: GitHub, Gmail, Slack
3. Query: "Based on our contract terms, project docs, recent GitHub commits,
          and team Slack discussions, what are the risks for the Dec 15 deadline?"
          
AI: I've analyzed multiple sources:
    
    Contract Terms (contract.pdf, page 4):
    - Delivery deadline: Dec 15 with 10% late penalty
    
    Project Specs (specs.docx):
    - 8 remaining features listed as "critical"
    
    GitHub Activity:
    - Only 3 of 8 features have commits in the last week
    - Commit velocity is down 40% vs. last month
    
    Slack Discussions (#project-alpha):
    - @sarah mentioned "backend integration blocked" (2 days ago)
    - @mike noted "2 team members out sick" (yesterday)
    
    Risk Assessment:
    HIGH RISK. Current velocity suggests missing deadline by 1-2 weeks.
    Recommend: 1) Scope reduction, 2) Deadline renegotiation, or 
               3) Additional resources.
```

### Scenario 11: Competitive Analysis

**Use Case**: Track competitors and correlate with your strategy docs.

**Setup**:
- Upload: Your strategy documents
- Enable: Hacker News, GitHub (for open-source competitors)

**Example Query**:
```
You: "What are our competitors doing lately, and how does it compare 
      to our roadmap?"
      
AI: Competitor Activity:
    
    From Hacker News:
    - CompetitorX launched AI features (300 upvotes, trending)
    - Users praising their UX improvements in comments
    
    From GitHub (competitor-public-repo):
    - Recent commits show focus on mobile optimization
    - New ML model for recommendations
    
    Your Roadmap (roadmap-2024.docx):
    - AI features planned for Q1 2025 (you're behind)
    - Mobile optimization not mentioned (gap identified)
    
    Recommendation: Consider accelerating AI features timeline.
```

---

## Best Practices

### Document Organization

**Do**:
- Break large documents into logical sections
- Use descriptive filenames (e.g., `marketing-strategy-2024.pdf` vs `doc1.pdf`)
- Upload related documents together for better cross-referencing

**Don't**:
- Upload duplicate documents (wastes vector storage)
- Use scanned images without OCR (text won't be indexed)

### Query Techniques

**Effective Questions**:
- "Summarize the key points from section 3"
- "Compare approach A and approach B mentioned in the docs"
- "What are the requirements for X?"

**Less Effective**:
- "Tell me everything" (too broad)
- "Is this good?" (requires context you haven't given)
- Single-word queries without context

### Conversation Memory

When enabled, the AI remembers your conversation history:

```
You: "What's the project timeline?"
AI: According to your docs, the project runs Jan-June 2024.

You: "What are the milestones?" ← AI knows you mean the same project
AI: The timeline document lists these milestones:
    - Phase 1: Jan-Feb (Design)
    - Phase 2: Mar-Apr (Development)...
```

### Tool Parameters

Set these in the Sidebar to filter API queries:

- **GitHub**: Search specific repos (`org/repo`)
- **Gmail**: Use Gmail search syntax (`from:user@domain.com after:2024-01-01`)
- **Drive**: Filter by file type or folder
- **Slack**: Target specific channels or date ranges
- **Notion**: Search by workspace or page type

### Performance Tips

1. **Upload Strategy**: Upload most relevant docs first, test queries, then add more
2. **Chunk Size**: Default settings work for most docs; adjust if answers lack context
3. **Query Specificity**: More specific queries = better retrieval = better answers
4. **Tool Selection**: Only enable tools you're actively using to reduce latency

---

## Troubleshooting Common Scenarios

### "I can't find information I know is in my documents"

**Possible Causes**:
1. Document wasn't fully indexed (check Documents page)
2. Query doesn't match vocabulary used in doc (try rephrasing)
3. Chunk size too small (info split across multiple chunks)

**Solutions**:
- Rephrase query using exact terms from document
- Ask "What topics are covered in my documents?" to see what's indexed
- Try more specific queries with page numbers or section names

### "External tool isn't returning data"

**Checklist**:
1. Is the tool enabled in Connectors?
2. Is the API key configured (if required)?
3. Are parameters set correctly? (check Sidebar)
4. For OAuth: Is authorization status "Authorized"?

### "Answers are generic/not using my documents"

This means retrieval isn't finding relevant chunks.

**Fix**:
- Check Documents page - are files successfully uploaded?
- Try: "List all documents you have access to"
- Use more specific queries that match document content

### Repetitive or stuttering responses

**Symptoms**:
- Output like `HiHi!! How How can can I I help help...`.

**Cause**:
- Streaming deltas can duplicate initial tokens, and some models stutter when sampling without penalties.

**Resolution**:
- Client-side normalization collapses duplicate words/punctuation.
- For finer control, tune LLM payload parameters (OpenRouter): `temperature`, `top_p`, `frequency_penalty`, `presence_penalty`, `repetition_penalty`, `max_tokens` via backend configuration.

---

## Real-World Workflow Examples

### Student Research Workflow
1. Upload course materials + research papers
2. Enable Hacker News for latest developments
3. Query: "Explain [concept] using my lecture notes and recent news"

### Developer Documentation Workflow
1. Upload API docs, internal wiki exports
2. Enable GitHub for live repo data
3. Query: "How do I implement [feature] according to our docs, and show recent examples from our codebase"

### Business Analysis Workflow
1. Upload contracts, financial reports, market research
2. Enable Gmail (for client communications) + Slack (for team discussions)
3. Query: "Summarize client concerns from emails and how the team is addressing them in Slack"

### Content Creator Workflow
1. Upload brand guidelines, content calendars
2. Enable Hacker News + Twitter/social (if integrated)
3. Query: "What topics are trending that align with our brand voice?"

---

## Next Steps

- **Customize Tools**: Enable only the integrations you need
- **Iterate on Queries**: Refine your questions based on initial responses
- **Combine Sources**: The real power is in cross-referencing documents with live data
- **Save Useful Queries**: Document query patterns that work well for your use case

For technical setup details, see:
- [OAuth Setup Guide](oauth_setup.md) - Configure Gmail, Drive, Slack, Notion
- [Architecture](architecture.md) - Understand how the system works
## Conversations Management

Manage and organize your chats:

### Create & Open
- Click **New** in the Conversations tab to create a conversation and jump to Chat.
- Click **Open** on any conversation to hydrate Chat with its full history.

### Rename
- Click **Rename**, edit the title inline, then **Save**. Titles help you quickly identify sessions.

### Delete
- Delete a single conversation from its row.
- Use **Delete All** to remove every conversation (with confirmation).

### Notes
- Chat persists locally (messages, `use documents` setting) via `localStorage` and hydrates from the backend when opening a conversation.
- The server stores conversation history in SQLite at `backend/conversations.db`.
### Authorize Connectors (OAuth)

**Purpose**: Connect your accounts so the app can use Gmail, Drive, Slack, and Notion data.

**Steps**:
- Ensure `.env` includes `APP_BASE_URL=http://localhost:8000` and `FRONTEND_BASE_URL=http://localhost:5173`.
- Start frontend with backend URL: `VITE_API_URL=http://localhost:8000 npm run dev`.
- Open `http://localhost:5173`, go to **Connectors**.
- Click **Authorize** for the desired service:
  - Gmail/Drive → Google consent screen
  - Slack → Slack consent screen
  - Notion → Notion consent screen
- After granting consent, you’re redirected back to the Connectors page.
- Status shows **Configured**; toggle to **Enabled** to use in chat.

# Usage Guide

This guide demonstrates practical use cases and scenarios for the AI Knowledge Console, showing you how to leverage different features for various needs.

## Table of Contents
- [New Features Guide](#new-features-guide)
- [Core RAG Usage](#core-rag-usage)
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
1. Configure Gmail OAuth (see [OAuth Setup Guide](OAUTH_SETUP.md))
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
- [OAuth Setup Guide](OAUTH_SETUP.md) - Configure Gmail, Drive, Slack, Notion
- [Architecture](ARCHITECTURE.md) - Understand how the system works

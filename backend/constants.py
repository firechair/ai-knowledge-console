"""
Application-wide constants for the AI Knowledge Console backend.

Centralizes all magic numbers, configuration defaults, and error messages
for easier maintenance and consistency across the application.
"""

# ============================================================================
# LLM Configuration Constants
# ============================================================================

DEFAULT_TEMPERATURE = 0.7
"""Default sampling temperature for LLM generation (0.0-1.0)"""

DEFAULT_MAX_TOKENS = 1024
"""Default maximum tokens to generate in LLM responses"""

MIN_TEMPERATURE = 0.0
"""Minimum allowed temperature value"""

MAX_TEMPERATURE = 1.0
"""Maximum allowed temperature value"""

MAX_TOKENS_LIMIT = 4096
"""Hard limit on maximum tokens (prevents excessive API costs)"""


# ============================================================================
# Vector Store / RAG Configuration
# ============================================================================

DEFAULT_CHUNK_SIZE = 500
"""Default text chunk size for document processing (characters)"""

DEFAULT_CHUNK_OVERLAP = 50
"""Default overlap between chunks for context continuity"""

DEFAULT_SIMILARITY_RESULTS = 5
"""Default number of similar chunks to retrieve from vector store"""

MIN_CHUNK_SIZE = 100
"""Minimum chunk size (smaller makes search less effective)"""

MAX_CHUNK_SIZE = 2000
"""Maximum chunk size (larger reduces retrieval precision)"""


# ============================================================================
# Document Processing Constants
# ============================================================================

SUPPORTED_FILE_TYPES = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'text/plain': '.txt'
}
"""Mapping of MIME types to file extensions for supported documents"""

SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.txt']
"""List of supported file extensions"""

MAX_FILE_SIZE_MB = 25
"""Maximum file size in megabytes"""

MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
"""Maximum file size in bytes (computed from MB)"""


# ============================================================================
# Conversation / Chat Constants
# ============================================================================

MAX_CONVERSATION_HISTORY = 6
"""Maximum messages to include in context (last 6 = 3 conversation turns)"""

CONVERSATION_TITLE_LENGTH = 50
"""Maximum length for conversation title (truncated from first message)"""

CONVERSATION_PREVIEW_LENGTH = 100
"""Maximum length for conversation preview text"""


# ============================================================================
# External API Configuration
# ============================================================================

GITHUB_API_BASE = "https://api.github.com"
"""Base URL for GitHub API"""

COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
"""Base URL for CoinGecko cryptocurrency API"""

OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
"""Base URL for OpenWeather API"""

HACKERNEWS_API_BASE = "https://hacker-news.firebaseio.com/v0"
"""Base URL for Hacker News API"""


# ============================================================================
# Rate Limiting Constants
# ============================================================================

DEFAULT_RATE_LIMIT = 100
"""Default number of requests allowed per time window"""

DEFAULT_RATE_WINDOW_SEC = 60
"""Default time window for rate limiting (seconds)"""


# ============================================================================
# WebSocket Configuration
# ============================================================================

WS_RECONNECT_MAX_ATTEMPTS = 5
"""Maximum WebSocket reconnection attempts before giving up"""

WS_RECONNECT_BASE_DELAY = 1000
"""Base delay in milliseconds for WebSocket reconnection (exponential backoff)"""

WS_RECONNECT_MAX_DELAY = 30000
"""Maximum delay in milliseconds between reconnection attempts"""


# ============================================================================
# Database Configuration
# ============================================================================

DB_DEFAULT_PATH = "backend/conversations.db"
"""Default path for SQLite conversation database"""

DB_QUERY_TIMEOUT_MS = 5000
"""Database query timeout in milliseconds"""


# ============================================================================
# Error Messages
# ============================================================================

ERROR_FILE_TOO_LARGE = f"File size exceeds maximum allowed ({MAX_FILE_SIZE_MB}MB)"
"""Error message for files exceeding size limit"""

ERROR_UNSUPPORTED_FILE = "Unsupported file type. Supported formats: PDF, DOCX, TXT"
"""Error message for unsupported file types"""

ERROR_LLM_UNAVAILABLE = "LLM service is currently unavailable. Please try again later."
"""Error message when LLM service cannot be reached"""

ERROR_DOCUMENT_NOT_FOUND = "Document not found in vector store"
"""Error message when requested document doesn't exist"""

ERROR_CONVERSATION_NOT_FOUND = "Conversation not found"
"""Error message when requested conversation doesn't exist"""

ERROR_INVALID_TEMPERATURE = f"Temperature must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE}"
"""Error message for invalid temperature values"""

ERROR_INVALID_MAX_TOKENS = f"Max tokens must be between 1 and {MAX_TOKENS_LIMIT}"
"""Error message for invalid max tokens values"""

ERROR_EMPTY_PROMPT = "Prompt cannot be empty"
"""Error message for empty/whitespace-only prompts"""

ERROR_NO_API_KEY = "API key not configured for this service"
"""Error message when required API key is missing"""

ERROR_RATE_LIMIT_EXCEEDED = f"Rate limit exceeded. Maximum {DEFAULT_RATE_LIMIT} requests per {DEFAULT_RATE_WINDOW_SEC} seconds."
"""Error message when user exceeds rate limit"""


# ============================================================================
# HTTP Status Code Constants
# ============================================================================

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503

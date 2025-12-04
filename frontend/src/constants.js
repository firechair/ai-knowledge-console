/**
 * Application-wide constants for the AI Knowledge Console frontend.
 * 
 * Centralizes configuration, magic numbers, and UI constants for easier
 * maintenance and consistency across components.
 */

// ============================================================================
// API Configuration
// ============================================================================

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api';


// ============================================================================
// WebSocket Configuration
// ============================================================================

export const WS_RECONNECT_DELAY = 1000; // Base delay in ms
export const WS_MAX_RECONNECT_ATTEMPTS = 5;
export const WS_MAX_DELAY = 30000; // 30 seconds max delay


// ============================================================================
// File Upload Configuration
// ============================================================================

export const MAX_FILE_SIZE_MB = 25;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export const SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.txt'];

export const SUPPORTED_MIME_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
];

export const FILE_PREVIEW_MAX_LENGTH = 500; // Characters to show in preview


// ============================================================================
// UI Configuration
// ============================================================================

export const TOAST_DURATION = 3000; // Toast notification duration (ms)
export const DEBOUNCE_DELAY = 300; // Debounce delay for search inputs (ms)
export const PAGINATION_SIZE = 20; // Items per page
export const CONVERSATION_REFRESH_INTERVAL = 30000; // Auto-refresh conversations (ms)


// ============================================================================
// Tool Parameter Defaults
// ============================================================================

export const DEFAULT_TOOL_PARAMS = {
    github_repo: 'facebook/react',
    crypto_symbol: 'bitcoin',
    weather_city: 'London',
    max_hackernews_stories: 5
};


// ============================================================================
// Keyboard Shortcuts
// ============================================================================

export const SHORTCUTS = {
    // Tab navigation
    CHAT_TAB: { key: '1', modifierKey: true, description: 'Go to Chat' },
    DOCUMENTS_TAB: { key: '2', modifierKey: true, description: 'Go to Documents' },
    CONNECTORS_TAB: { key: '3', modifierKey: true, description: 'Go to Connectors' },
    SETTINGS_TAB: { key: '4', modifierKey: true, description: 'Go to Settings' },

    // Actions
    NEW_CONVERSATION: { key: 'n', modifierKey: true, description: 'New conversation' },
    SEARCH: { key: 'k', modifierKey: true, description: 'Search conversations' },
    ESCAPE: { key: 'Escape', modifierKey: false, description: 'Clear selection' }
};


// ============================================================================
// Message Display
// ============================================================================

export const MAX_MESSAGE_LENGTH = 10000; // Characters
export const STREAMING_DELAY = 50; // Delay between token renders (ms)


// ============================================================================
// Conversation List
// ============================================================================

export const CONVERSATION_TITLE_LENGTH = 50;
export const CONVERSATION_PREVIEW_LENGTH = 100;
export const CONVERSATIONS_PER_PAGE = 50;


// ============================================================================
// Error Messages
// ============================================================================

export const ERROR_MESSAGES = {
    FILE_TOO_LARGE: `File size exceeds ${MAX_FILE_SIZE_MB}MB`,
    UNSUPPORTED_FILE: `Supported formats: ${SUPPORTED_FILE_TYPES.join(', ')}`,
    NETWORK_ERROR: 'Network error - please check your connection',
    SERVER_ERROR: 'Server error - please try again later',
    UPLOAD_FAILED: 'Upload failed - please try again',
    CONNECTION_LOST: 'Connection lost - attempting to reconnect',
    RATE_LIMITED: 'Too many requests - please wait a moment',
    INVALID_INPUT: 'Please enter a valid message',
    EMPTY_MESSAGE: 'Message cannot be empty'
};


// ============================================================================
// Success Messages
// ============================================================================

export const SUCCESS_MESSAGES = {
    UPLOAD_COMPLETE: 'Document uploaded successfully',
    DOCUMENT_DELETED: 'Document deleted successfully',
    SETTINGS_SAVED: 'Settings saved successfully',
    CONNECTOR_CONFIGURED: 'Connector configured successfully',
    CONNECTION_RESTORED: 'Connection restored'
};


// ============================================================================
// Loading Messages
// ============================================================================

export const LOADING_MESSAGES = {
    UPLOADING: 'Uploading document...',
    PROCESSING: 'Processing...',
    CONNECTING: 'Connecting...',
    GENERATING: 'Generating response...',
    SEARCHING: 'Searching conversations...'
};


// ============================================================================
// Connection Status
// ============================================================================

export const CONNECTION_STATUS = {
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    DISCONNECTED: 'disconnected',
    ERROR: 'error'
};


// ============================================================================
// Theme / Styling Constants
// ============================================================================

export const THEME_COLORS = {
    PRIMARY: '#3B82F6',    // Blue
    SUCCESS: '#10B981',    // Green
    WARNING: '#F59E0B',    // Amber
    ERROR: '#EF4444',      // Red
    INFO: '#6366F1'        // Indigo
};


// ============================================================================
// Animation Durations
// ============================================================================

export const ANIMATION = {
    FAST: 150,
    NORMAL: 300,
    SLOW: 500
};


// ============================================================================
// Z-Index Layers
// ============================================================================

export const Z_INDEX = {
    BASE: 1,
    DROPDOWN: 10,
    MODAL: 100,
    TOAST: 1000,
    TOOLTIP: 10000
};


// ============================================================================
// Breakpoints (for responsive design)
// ============================================================================

export const BREAKPOINTS = {
    SM: 640,
    MD: 768,
    LG: 1024,
    XL: 1280,
    '2XL': 1536
};

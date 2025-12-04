# AI Knowledge Console - Frontend

React + Vite application for the AI Knowledge Console, providing a modern, accessible interface for document management, RAG chat, and API integrations.

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **State Management**: React Query (@tanstack/react-query)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **WebSocket**: Native WebSocket API

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── App.jsx                  # Main app shell with tab navigation
│   │   ├── Chat.jsx                 # Chat interface with WebSocket streaming
│   │   ├── DocumentUpload.jsx       # File upload with preview
│   │   ├── Connectors.jsx           # API/OAuth configuration
│   │   ├── Settings.jsx             # App settings
│   │   ├── ConversationList.jsx     # Conversation history browser
│   │   └── ErrorBoundary.jsx        # React error protection
│   ├── utils/
│   │   └── api.js                   # API client utilities
│   ├── constants.js                 # App constants and configuration
│   └── main.jsx                     # App entry point
├── public/                          # Static assets
└── package.json                     # Dependencies
```

## Key Components

### App.jsx
Main application shell with tab-based navigation.

**Features**:
- Tab navigation (Chat, Documents, Connectors, Settings)
- Keyboard shortcuts (Cmd+1-4)
- Global state management
- Error boundary integration

### Chat.jsx
Real-time chat interface with conversation management.

**Features**:
- WebSocket streaming with automatic reconnection
- Conversation memory
- Document context toggleable
- External tool integration
- Loading states and error handling

### ConversationList.jsx
Browse and search conversation history.

**Features**:
- Real-time search
- Auto-refresh every 30 seconds
- Conversation previews
- Click to load conversation

### DocumentUpload.jsx
Upload documents with preview functionality.

**Features**:
- File preview before upload
  - Text files: First 500 characters
  - PDF/DOCX: File metadata
- Confirm/cancel workflow
- Upload progress indication

### ErrorBoundary.jsx
Catches React errors to prevent app crashes.

**Features**:
- Friendly error message for users
- Detailed error info in development
- Reload page button
- Automatic error logging

## Constants & Configuration

All configuration values are centralized in `src/constants.js`:

### API Configuration
```javascript
import { API_BASE_URL, WS_BASE_URL } from './constants';
```

### File Upload Limits
```javascript
import { MAX_FILE_SIZE_MB, SUPPORTED_FILE_TYPES } from './constants';
```

### UI Constants
```javascript
import { 
  DEBOUNCE_DELAY,           // Search debouncing
  CONVERSATION_REFRESH_INTERVAL,  // Auto-refresh timing
  ANIMATION                 // Animation durations
} from './constants';
```

### Error Messages
```javascript
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from './constants';
```

## Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables
```env
# Optional: Override API URL
VITE_API_URL=http://localhost:8000/api

# Optional: Override WebSocket URL
VITE_WS_URL=ws://localhost:8000/api
```

## Keyboard Shortcuts

The app includes keyboard shortcuts for efficient navigation:

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + 1` | Go to Chat tab |
| `Cmd/Ctrl + 2` | Go to Documents tab |
| `Cmd/Ctrl + 3` | Go to Connectors tab |
| `Cmd/Ctrl + 4` | Go to Settings tab |
| `Escape` | Clear conversation selection |

## Accessibility

The application follows WCAG 2.1 Level A guidelines:

- **Keyboard Navigation**: Full keyboard support with visible focus indicators
- **ARIA Labels**: Proper ARIA roles and labels throughout
- **Screen Reader**: Compatible with screen readers
- **Semantic HTML**: Uses proper HTML5 semantic elements
- **Color Contrast**: Meets WCAG AA standards

## State Management

### Server State (React Query)
- Document lists
- Conversation history
- Connector status
- Auto-refresh and caching

### Local State (useState)
- UI state (tab selection, modals)
- Form inputs
- Temporary data

### WebSocket State
- Connection status
- Reconnection logic
- Message streaming

## API Integration

### REST Endpoints
```javascript
// Example: Upload document
const response = await fetch(`${API_BASE_URL}/documents/upload`, {
  method: 'POST',
  body: formData
});
```

### WebSocket Streaming
```javascript
import { createChatSocket } from './utils/api';

const ws = createChatSocket();
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle streaming tokens
};
```

## Adding New Components

### 1. Create Component
```javascript
// src/components/MyComponent.jsx
export default function MyComponent() {
  return <div>My Component</div>;
}
```

### 2. Add to App.jsx
```javascript
import MyComponent from './components/MyComponent';

// Use in render
<MyComponent />
```

### 3. Add Constants (if needed)
```javascript
// src/constants.js
export const MY_COMPONENT_SETTING = 'value';
```

## Styling

### Tailwind CSS
All styling uses Tailwind CSS utility classes:

```javascript
<div className="flex items-center gap-2 p-4 bg-blue-50 rounded-lg">
  {/* Content */}
</div>
```

### Custom Styles
For component-specific styles, use inline Tailwind classes or add to `index.css`.

## Testing

```bash
# Run tests (if configured)
npm test

# Type checking (if using TypeScript)
npm run typecheck
```

## Performance

### Optimizations Applied
- Code splitting with dynamic imports
- React Query caching
- Debounced search inputs
- Lazy loading of components
- WebSocket connection pooling

### Build Optimizations
- Tree shaking
- Minification
- Gzip compression
- Asset optimization

## Troubleshooting

### WebSocket Connection Issues
```javascript
// Check connection status in Chat component
if (connectionStatus !== 'connected') {
  // Shows reconnection UI automatically
}
```

### CORS Issues
Ensure backend CORS is configured to allow frontend origin:
```env
# Backend .env
allowed_origins=http://localhost:5173,http://localhost:3000
```

### Build Errors
```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

## Deployment

### Production Build
```bash
npm run build
# Output: dist/ directory
```

### Deploy with Docker
The `dist/` folder is served by Nginx in production:
```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
```

### Environment Configuration
Production API URLs are configured via environment variables:
```env
VITE_API_URL=/api  # Relative URL for Nginx proxy
```

## Contributing

When adding new features:

1. **Add constants** to `src/constants.js`
2. **Add ARIA labels** for accessibility
3. **Handle loading/error states** properly
4. **Add keyboard shortcuts** if applicable
5. **Update this README** with new components

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

See main project LICENSE file.

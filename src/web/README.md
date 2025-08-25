# Terry the Tube - Frontend Architecture

This directory contains the complete frontend implementation for Terry the Tube's web interface. The frontend is built with modern TypeScript and follows a clean, modular architecture using reactive state management and WebSocket-based real-time communication.

## Architecture Overview

The frontend uses a **Component-Based Architecture** with centralized state management:

```
┌─────────────────────────────────────────────────────┐
│                 HTML Template                        │
│  (main-template.html + web_templates.py)           │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│              App Controller                          │
│         (app-controller.ts)                         │
│  • Application orchestration                        │
│  • Event coordination                               │
│  • Global error handling                            │
└─────────┬─────────────────────────┬─────────────────┘
          │                         │
┌─────────▼─────────┐    ┌─────────▼─────────────────┐
│   UI Controller   │    │    State Manager          │
│ (ui-controller.ts)│    │  (state-manager.ts)       │
│ • DOM manipulation│    │ • Reactive state          │
│ • Visual updates  │    │ • Change notifications    │
│ • User feedback   │    │ • Data persistence        │
└─────────┬─────────┘    └─────────┬─────────────────┘
          │                        │
          └────────┬───────────────┘
                   │
┌─────────────────▼───────────────────────────────────┐
│             WebSocket Manager                       │
│          (websocket-manager.ts)                     │
│  • Real-time server communication                  │
│  • Connection health monitoring                    │
│  • Automatic reconnection                          │
└─────────────────────────────────────────────────────┘
```

## Core Components

### 1. **App Controller** (`app-controller.ts`)
- **Purpose**: Main application orchestrator
- **Responsibilities**:
  - Initialize all subsystems
  - Coordinate component interactions
  - Handle user actions (recording, text chat, personality selection)
  - Manage global error boundaries
- **Key Features**:
  - Modern ES6+ patterns (destructuring, arrow functions, optional chaining)
  - Defensive error handling with rollback states
  - Event delegation and listener management

### 2. **State Manager** (`state-manager.ts`)
- **Purpose**: Centralized reactive state management
- **Responsibilities**:
  - Store application state
  - Notify listeners of state changes
  - Batch UI updates for performance
  - Provide typed state access
- **Key Features**:
  - Nested state path access (`connection.status`, `ui.recording`)
  - Reactive subscriptions with automatic cleanup
  - Render queue optimization with `requestAnimationFrame`
  - Type-safe state operations

### 3. **UI Controller** (`ui-controller.ts`)
- **Purpose**: Centralized DOM manipulation and rendering
- **Responsibilities**:
  - Update visual elements based on state changes
  - Handle user interactions
  - Manage toast notifications and error display
  - Control message rendering and animations
- **Key Features**:
  - Element caching for performance
  - Incremental message updates (no full re-renders)
  - Toast notification system
  - Responsive UI state management

### 4. **WebSocket Manager** (`websocket-manager.ts`)
- **Purpose**: Real-time communication with backend
- **Responsibilities**:
  - Establish and maintain WebSocket connections
  - Handle message serialization/deserialization
  - Monitor connection health
  - Implement reconnection logic with exponential backoff
- **Key Features**:
  - Automatic reconnection with retry limits
  - Connection quality monitoring
  - Ping/pong heartbeat system
  - Error resilience and graceful degradation

## State Architecture

The application uses a **reactive state management system** with three main state branches:

### Connection State
```typescript
connection: {
  status: 'connected' | 'connecting' | 'disconnected' | 'error',
  ws: WebSocket | null,
  reconnectAttempts: number,
  quality: 'good' | 'fair' | 'poor',
  lastPing: number | null
}
```

### UI State
```typescript
ui: {
  recording: boolean,
  textChatEnabled: boolean,
  personalityOverlayVisible: boolean,
  loadingStates: {
    generatingResponse: boolean,
    generatingAudio: boolean,
    sendingMessage: boolean
  },
  errors: ErrorInfo[]
}
```

### Data State
```typescript
data: {
  messages: Message[],
  currentStatus: string,
  selectedPersonality: string | null,
  personalityInfo: PersonalityInfo | null,
  availablePersonalities: PersonalityInfo[]
}
```

## Communication Flow

### 1. **User Interaction Flow**
```
User Action → App Controller → State Update → UI Controller → DOM Update
```

### 2. **WebSocket Communication Flow**
```
Backend State Change → WebSocket Message → State Manager → UI Controller → Visual Update
```

### 3. **Voice Recording Flow**
```
Hold Button → Start Recording → WebSocket → Backend Processing → State Update → UI Feedback
```

## File Structure

```
src/web/
├── README.md                    # This documentation
├── main-template.html           # HTML template with placeholders
├── styles.css                   # Complete CSS styling
├── types.ts                     # TypeScript type definitions
├── app-controller.ts            # Main application controller
├── state-manager.ts             # Reactive state management
├── ui-controller.ts             # DOM manipulation and rendering
├── websocket-manager.ts         # WebSocket communication
├── web_interface.py             # Python backend interface
├── web_server.py               # HTTP server for static content
├── web_templates.py            # Template processing and injection
├── websocket_server.py         # WebSocket server implementation
└── dist/                       # Compiled JavaScript output
    ├── app-controller.js
    ├── state-manager.js
    ├── ui-controller.js
    ├── websocket-manager.js
    └── types.js
```

## Key Features

### 🎯 **Modern JavaScript/TypeScript**
- ES6+ features throughout (destructuring, arrow functions, optional chaining)
- Full TypeScript typing for type safety
- Module-based architecture
- Async/await patterns for cleaner code

### 🔄 **Reactive State Management**
- Centralized state with path-based access
- Automatic UI updates on state changes
- Performance optimization with render queuing
- Type-safe state operations

### 🌐 **Real-time Communication**
- WebSocket-based bidirectional communication
- Automatic reconnection with exponential backoff
- Connection health monitoring
- Message queuing and error handling

### 📱 **Responsive Design**
- Mobile-first responsive layout
- Touch-friendly controls
- Progressive enhancement
- Accessible interface elements

### 🎨 **Modern UI/UX**
- CSS Custom Properties for theming
- Smooth animations and transitions
- Toast notifications for user feedback
- Loading states and progress indicators

## Build Process

The frontend uses a **hybrid build system**:

1. **TypeScript Compilation**: `.ts` files are compiled to JavaScript in the `dist/` directory
2. **Template Injection**: Python backend injects compiled JavaScript into HTML template
3. **Style Integration**: CSS is embedded directly into the template
4. **Runtime Assembly**: Complete HTML page is served with all assets inline

## Browser Compatibility

- **Modern Browsers**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Features Used**: WebSockets, ES6+ JavaScript, CSS Grid/Flexbox, CSS Custom Properties
- **Fallbacks**: Graceful degradation for connection failures, error boundaries for JavaScript errors

## Development Workflow

1. **Edit TypeScript**: Modify `.ts` files in `src/web/`
2. **Compile**: TypeScript is compiled to `dist/` directory
3. **Test**: Run application and test in browser
4. **Debug**: Use browser DevTools, console logging, and error boundaries

## Performance Considerations

- **Element Caching**: DOM elements are cached to avoid repeated queries
- **Render Batching**: UI updates are batched using `requestAnimationFrame`
- **Incremental Updates**: Messages are added incrementally, not re-rendered entirely
- **Connection Pooling**: Single WebSocket connection shared across components
- **Memory Management**: Event listeners are properly cleaned up

## Error Handling

The frontend implements **comprehensive error handling**:

- **Global Error Boundaries**: Catch and handle JavaScript errors
- **WebSocket Error Recovery**: Automatic reconnection and fallback states
- **User Feedback**: Toast notifications for all error conditions
- **State Rollback**: Failed operations roll back to previous valid state
- **Graceful Degradation**: Application continues working with reduced functionality

## Security Considerations

- **Input Validation**: All user inputs are validated before sending
- **XSS Prevention**: Content is properly escaped in DOM updates
- **CSRF Protection**: State-changing operations require valid WebSocket connection
- **Error Information**: Error messages don't leak sensitive server information
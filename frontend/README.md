# LlamaIndex Chat Frontend

ChatGPT-style React frontend for the LlamaIndex Chat application.

## Features

- ChatGPT-inspired UI design
- Real-time streaming chat (WebSocket)
- Conversation history sidebar
- Source citations display
- Dark/light theme support
- Responsive design

## Tech Stack

- React 19
- TypeScript
- Vite
- TanStack Query (React Query)
- Axios

## Getting Started

### Install Dependencies

```bash
npm install
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```
VITE_API_URL=http://localhost:8000
```

### Run Development Server

```bash
npm run dev
```

Frontend will start at: http://localhost:5173

## Project Structure

```
frontend/src/
├── pages/
│   └── ChatPage.tsx        # Main chat interface
├── utils/
│   └── api.ts              # API client
├── styles/
│   └── globals.css         # Global styles
├── App.tsx                 # App component
└── main.tsx                # Entry point
```

## Usage

1. Start the backend server (see backend README)
2. Start the frontend: `npm run dev`
3. Open http://localhost:5173
4. Click "New Chat" to start a conversation
5. Type your message and press Enter or click Send

## API Integration

The frontend connects to the backend API at `VITE_API_URL`.

Key endpoints used:
- `POST /api/chat/sessions` - Create session
- `GET /api/chat/sessions` - List sessions
- `POST /api/chat/message` - Send message
- `WS /ws/chat/{session_id}` - Streaming chat

## Building for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Customization

### Styling

Edit `src/styles/globals.css` to customize colors and theme.

### API URL

Change `VITE_API_URL` in `.env` to point to your backend.

## Troubleshooting

### CORS Errors

Make sure the backend CORS configuration includes your frontend URL.

### WebSocket Connection Failed

Check that the backend is running and WebSocket endpoint is accessible.

### API Calls Failing

Verify `VITE_API_URL` is correct and backend is running.

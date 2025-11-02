# Trading Dashboard Frontend

React TypeScript frontend for the AI-powered trading dashboard.

## Features

- 🔐 User authentication (login/register)
- 📊 Dashboard interface
- 🎨 Dark theme optimized for trading
- 📱 Responsive design
- 🔄 Real-time API integration

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will be available at http://localhost:3000

### Building for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── contexts/       # React contexts (Auth, etc.)
├── pages/          # Page components
├── App.tsx         # Main app component
└── index.tsx       # Entry point
```

## API Integration

The frontend communicates with the Python FastAPI backend running on port 8000. The proxy configuration in package.json handles API requests during development.

## Authentication

Uses JWT tokens stored in localStorage with automatic token refresh and protected routes.
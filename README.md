# Polymarket Dashboard

A real-time dashboard for viewing Polymarket market data, including market statistics and historical data visualization.

## Features

- Display of current and live markets
- Market metrics:
  - Trading volume
  - Open interest
  - Number of traders
- Historical open interest chart
- Real-time market data updates

## Project Structure

```
polymarket-dashboard/
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   ├── pyproject.toml    # Python dependencies
│   └── .env             # Backend environment variables
└── frontend/             # React frontend
    ├── src/             # Source code
    ├── package.json     # Node.js dependencies
    └── .env            # Frontend environment variables
```

## Setup Instructions

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
poetry install
```

2. Configure environment variables:
- Copy `.env.example` to `.env` (if not already present)
- Update any necessary configuration

3. Start the backend server:
```bash
poetry run uvicorn app.main:app --reload
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Configure environment variables:
- Copy `.env.example` to `.env` (if not already present)
- Update the backend API URL if necessary

3. Start the development server:
```bash
npm run dev
```

## API Documentation

The backend provides the following API endpoints:

- `GET /api/markets` - Get current markets with statistics
- `GET /api/markets/{market_id}/history` - Get historical open interest data

## Technologies Used

- Backend:
  - FastAPI (Python)
  - Poetry for dependency management
  - aiohttp for async HTTP requests

- Frontend:
  - React with TypeScript
  - Tailwind CSS for styling
  - shadcn/ui for UI components
  - Recharts for data visualization

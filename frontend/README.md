# Frontend Rebuild (Phase 1)

This folder contains the rebuilt UI based on Vue3 + Element Plus.

## Phase status

- Phase 1: login + layout shell ✅
- Phase 2: network / upgrade / artifacts / jobs view modules ✅ (style-matched component structure)

## Run

```bash
cd frontend
npm install
npm run dev
```

Open: http://127.0.0.1:5173

## API base

- Default: `http://127.0.0.1:5000/api/v1`
- Override with env:

```bash
VITE_API_BASE=http://127.0.0.1:5000/api/v1 npm run dev
```

# API Integration

- Base URL from env: `VITE_API_URL`
- Use axios instance from `src/lib/api.ts` — never raw fetch
- JWT token stored in memory (not localStorage)
- Refresh token flow handled by axios interceptor
- All API calls go through React Query with keys like `['documents', id]`
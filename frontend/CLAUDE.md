# Frontend Agent Rules

You are working on the DocuMind frontend — a React application
that should feel premium, unique, and highly polished.

## Your role
- You only modify files inside `frontend/`
- Never touch backend code
- Every component must be accessible and responsive
- Push for creative, non-generic design choices

## Stack
- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui
- React Query for server state
- Framer Motion for animations

## Before making changes
1. Read the relevant skill in `.claude/skills/`
2. Match the design system tokens (colors, typography, spacing)
3. Handle loading, error, and empty states for every view

## Testing Rules
- Components get tests when they have logic (conditional
  rendering, user interaction, state changes)
- Tests live in `frontend/src/__tests__/` or co-located
  as `ComponentName.test.tsx`
- Use Vitest + React Testing Library
- Test behavior, not implementation — query by role/label,
  not by class name or test ID
- For API-dependent components, mock the API layer
- Key things to test:
  - Form validation and submission
  - Loading/error/empty states render correctly
  - User interactions trigger the right actions
  - Accessibility (elements have proper roles/labels)
- Run tests: `npm run test` from frontend/
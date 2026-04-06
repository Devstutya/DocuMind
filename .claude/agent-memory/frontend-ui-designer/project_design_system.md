---
name: DocuMind Design System
description: Color palette, typography, spacing tokens, component patterns, and animation conventions established during Phase 5 UI polish.
type: project
---

## Color palette

Deep navy + electric violet brand identity. Avoids generic blue SaaS look.

- **navy-*** — dark backgrounds, sidebar shell (`navy-950` sidebar bg)
- **violet-*** — primary accent, CTAs, active states, brand elements (`violet-600` primary)
- **surface-*** — light neutral scale for cards, inputs, text (`surface-50` page bg, `surface-200` borders)

Semantic:
- Success: `emerald-500 / emerald-50`
- Error: `red-500 / red-50`
- Warning: `amber` (not yet used)

## Typography

Font: **Inter** (Google Fonts, 300–800 weight range).
Custom size: `text-2xs` = 0.625rem / 1rem line-height (used for timestamps, labels, badges).

## Component patterns

### Cards
`bg-white rounded-2xl border border-surface-200 shadow-card` — standard white card.
`shadow-card` is a custom token: subtle multi-layer shadow.

### Inputs
`bg-surface-50 border border-surface-200 rounded-xl focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400`

### Primary button
`bg-violet-600 hover:bg-violet-700 text-white rounded-xl font-semibold active:scale-[0.98]`

### Nav items (sidebar)
Active: `bg-violet-600/20 text-violet-300`
Inactive: `text-navy-400 hover:bg-navy-800 hover:text-navy-100`

## Animation keyframes (in tailwind.config.js)

- `animate-fade-up` — 0.3s ease-out entrance (new messages)
- `animate-fade-in` — 0.2s opacity fade (alerts, empty states)
- `bounce-dot` — custom typing indicator (NOT Tailwind's animate-bounce)
  Applied inline via `style={{ animation: 'bounce-dot 1.2s ...', animationDelay }}` on 3 dots

## Drag-and-drop upload

DocumentUpload uses `dragActive` state → adds `scale-[1.01] shadow-glow-violet border-violet-400` to zone.
Drop events are on the `<label>` element wrapping the hidden `<input type="file">`.

## Sidebar

Width: `w-60`. Background: `navy-950`. Uses `Brain` lucide icon as logo mark.
Active indicator: small `w-1 h-1 rounded-full bg-violet-400` dot on the right.

## Why: avoid generic blue SaaS
User wants distinctive, premium feel. Navy/violet palette was chosen to signal intelligence and depth.
How to apply: do not revert to indigo-600 / blue-50 default patterns. Maintain navy sidebar + violet accent system.

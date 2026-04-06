---
name: DocuMind Dark UI System
description: Confirmed dark UI palette — card/component backgrounds, text color conventions, and classes to avoid for the navy+violet design system
type: project
---

DocuMind uses a strict dark UI — navy-950 page backgrounds, navy-800/900 cards, white/gray-100 primary text.

**Why:** The original components mixed `bg-white`, `bg-surface-50` and `text-surface-*` classes (light-theme defaults) into a dark-navy layout, causing invisible text. A full contrast audit was done to align every component to the dark system.

**How to apply:** Follow these conventions in all new and modified components:

### Background hierarchy
- Page/shell: `bg-navy-950`
- Cards/panels: `bg-navy-800` or `bg-navy-900`
- Nested items/rows: `bg-navy-900` (inside navy-800 card) or `bg-navy-800` (inside navy-900 card)
- Inputs/selects: `bg-navy-800` or `bg-navy-900` with `border-navy-600` or `border-navy-700`
- Drop zones: `bg-navy-800 border-navy-700`
- Hover states: `hover:bg-navy-700/50` or `hover:bg-navy-800/80`

### Text color conventions
- Headings / primary text: `text-white` or `text-gray-100`
- Body / secondary text: `text-navy-300` or `text-navy-200`
- Muted / metadata: `text-navy-400`
- Very muted (timestamps, hints): `text-navy-500`
- Labels (uppercase tracking): `text-navy-300`
- Input text: `text-gray-100`, placeholder: `text-navy-500`

### Dividers and borders
- Card borders: `border-navy-700`
- Section dividers: `divide-navy-700` or `border-navy-700`
- Top/bottom bars: `border-navy-800`

### Accent elements (violet)
- Icon backgrounds: `bg-violet-600/15` or `bg-violet-600/20` with `border-violet-500/20`
- Icon color: `text-violet-400`
- Active nav state: `bg-violet-600/20 text-violet-300`
- Stat card icon bg (violet accent): `bg-violet-600/20 text-violet-300 border-violet-600/30`

### Error/success states (dark variants)
- Error: `bg-red-900/30 border border-red-700/50 text-red-300`
- Success: `bg-emerald-900/30 border border-emerald-700/50 text-emerald-300`
- Error delete button: `text-red-400 hover:text-red-300 hover:bg-red-900/30`

### Classes to NEVER use inside the dark layout
- `bg-white`, `bg-surface-0` through `bg-surface-200`
- `text-surface-700`, `text-surface-800`, `text-surface-900`
- `text-navy-600`, `text-navy-700` (near-invisible on navy-950)
- `bg-violet-50`, `bg-red-50`, `bg-emerald-50` (light tints)
- `border-surface-*`, `divide-surface-*`

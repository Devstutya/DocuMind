/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand — deep navy
        navy: {
          50:  '#eef1f8',
          100: '#d5dcef',
          200: '#aab9df',
          300: '#7e96cf',
          400: '#5273be',
          500: '#3655ae',
          600: '#2a4292',
          700: '#1e3076',
          800: '#152159',
          900: '#0c1438',
          950: '#070c22',
        },
        // Accent — electric violet
        violet: {
          50:  '#f3eeff',
          100: '#e3d4fe',
          200: '#c7aafd',
          300: '#a97ffc',
          400: '#8b54fb',
          500: '#7c3aed',
          600: '#6d28d9',
          700: '#5b21b6',
          800: '#4c1d95',
          900: '#3b1472',
        },
        // Neutral scale — slightly warm grey
        surface: {
          0:   '#ffffff',
          50:  '#f8f8fb',
          100: '#f1f0f7',
          200: '#e4e3ef',
          300: '#cccade',
          400: '#9e9bb8',
          500: '#6e6b8a',
          600: '#514e6b',
          700: '#38364d',
          800: '#232235',
          900: '#14131f',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '1rem' }],
      },
      boxShadow: {
        'glow-violet': '0 0 0 3px rgba(124, 58, 237, 0.25)',
        'glow-navy':   '0 0 0 3px rgba(30, 48, 118, 0.25)',
        'card':        '0 1px 3px 0 rgba(12,20,56,0.08), 0 4px 12px 0 rgba(12,20,56,0.04)',
        'card-hover':  '0 4px 16px 0 rgba(12,20,56,0.12), 0 1px 4px 0 rgba(12,20,56,0.06)',
        'panel':       '0 0 0 1px rgba(204,202,222,0.6), 0 2px 8px 0 rgba(12,20,56,0.06)',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      transitionDuration: {
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
      },
      animation: {
        'bounce-dot': 'bounce-dot 1.2s ease-in-out infinite',
        'fade-up':    'fade-up 0.3s ease-out',
        'fade-in':    'fade-in 0.2s ease-out',
      },
      keyframes: {
        'bounce-dot': {
          '0%, 80%, 100%': { transform: 'translateY(0)', opacity: '0.4' },
          '40%':            { transform: 'translateY(-6px)', opacity: '1' },
        },
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

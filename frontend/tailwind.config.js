/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'calc-primary': '#1e293b',
        'calc-secondary': '#334155',
        'calc-accent': '#3b82f6',
        'calc-success': '#10b981',
        'calc-warning': '#f59e0b',
        'calc-error': '#ef4444',
      },
      gridTemplateColumns: {
        'calc': 'repeat(4, 1fr)',
        'calc-scientific': 'repeat(6, 1fr)',
      }
    },
  },
  plugins: [],
}
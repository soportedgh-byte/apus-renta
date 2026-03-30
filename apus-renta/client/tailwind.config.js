/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#1B4F72', light: '#D6EAF8', dark: '#154360' },
        accent: '#2E86C1',
        dark: '#2C3E50',
        success: '#27AE60',
        danger: '#E74C3C',
        warning: '#F39C12',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};

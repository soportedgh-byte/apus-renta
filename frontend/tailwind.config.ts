import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Colores institucionales
        des: {
          DEFAULT: '#1A5276',
          light: '#2471A3',
          dark: '#154360',
          50: '#EBF5FB',
          100: '#D6EAF8',
          200: '#AED6F1',
          300: '#85C1E9',
          400: '#5DADE2',
          500: '#1A5276',
          600: '#154360',
          700: '#11344D',
          800: '#0D2539',
          900: '#091626',
        },
        dvf: {
          DEFAULT: '#1E8449',
          light: '#27AE60',
          dark: '#196F3D',
          50: '#EAFAF1',
          100: '#D5F5E3',
          200: '#ABEBC6',
          300: '#82E0AA',
          400: '#58D68D',
          500: '#1E8449',
          600: '#196F3D',
          700: '#145A32',
          800: '#0E4526',
          900: '#09301A',
        },
        oro: {
          DEFAULT: '#C9A84C',
          light: '#D4B96A',
          dark: '#A88B3D',
          50: '#FDF8EC',
          100: '#FAF0D4',
          200: '#F5E1A9',
          300: '#EFD27E',
          400: '#EAC353',
          500: '#C9A84C',
          600: '#A88B3D',
          700: '#876E2E',
          800: '#665120',
          900: '#453411',
        },
        fondo: {
          DEFAULT: '#0F1419',
          light: '#1A2332',
          dark: '#0A0E12',
        },
        tarjeta: {
          DEFAULT: '#1A2332',
          light: '#243044',
          dark: '#131A26',
        },
        barra: {
          DEFAULT: '#0A0F14',
          light: '#111921',
          dark: '#060A0E',
        },
      },
      fontFamily: {
        titulo: ['Georgia', 'Cambria', 'Times New Roman', 'serif'],
        interfaz: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        codigo: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      animation: {
        'pulso-suave': 'pulso-suave 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'deslizar-entrada': 'deslizar-entrada 0.3s ease-out',
        'aparecer': 'aparecer 0.5s ease-out',
        'cursor-parpadeo': 'cursor-parpadeo 1s step-end infinite',
      },
      keyframes: {
        'pulso-suave': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        'deslizar-entrada': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'aparecer': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'cursor-parpadeo': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;

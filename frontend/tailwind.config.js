/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#f97316',
          dark: '#c2410c',
        },
        surface: {
          DEFAULT: '#ffffff',
          warm: '#fff0dc',
        },
        bg: '#fff8ef',
        charcoal: '#1f1b16',
        cheddar: '#fbbf24',
        ketchup: '#b91c1c',
        lettuce: '#3f7d20',
      }
    },
  },
  plugins: [],
}

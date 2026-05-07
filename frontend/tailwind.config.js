/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        keGray: '#1e293b',        /* slate-800 */
        keDark: '#0f172a',        /* slate-900 */
        keTerracotta: '#c2410c',  /* orange-700 / clay */
        keWheat: '#fde047',       /* yellow-300 / gold */
        keYellow: '#fbbf24',      /* amber-400 - Official Eye Color */
        keBlue: '#3b82f6',        /* keeping for safety if needed */
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/container-queries'),
  ],
}

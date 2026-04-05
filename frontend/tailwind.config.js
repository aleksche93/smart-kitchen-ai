/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neoGray: '#1e293b',        /* slate-800 */
        neoDark: '#0f172a',        /* slate-900 */
        neoTerracotta: '#c2410c',  /* orange-700 / clay */
        neoWheat: '#fde047',       /* yellow-300 / gold */
        neoBlue: '#3b82f6',        /* keeping for safety if needed */
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}

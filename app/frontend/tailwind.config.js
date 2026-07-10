/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        chunk: {
          text: '#3b82f6',
          table: '#10b981',
          picture: '#f59e0b',
        },
      },
    },
  },
  plugins: [],
}

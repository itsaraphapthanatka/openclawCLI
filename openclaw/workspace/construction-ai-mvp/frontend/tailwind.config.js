/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'traffic-green': '#22c55e',
        'traffic-yellow': '#eab308',
        'traffic-red': '#ef4444',
      },
    },
  },
  plugins: [],
}

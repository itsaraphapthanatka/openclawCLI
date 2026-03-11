module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
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
};

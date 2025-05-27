/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Colors from naive-ui theme - matching exactly your theme.vue
        'primary': {
          DEFAULT: '#df691a',
          'hover': '#e98b39',
          'pressed': '#c65a11',
          'suppl': '#f0ad4e',
        },
        'secondary': {
          DEFAULT: '#5bc0de',
        },
        // Background colors from naive-ui theme
        'background': {
          DEFAULT: '#0f2537', // bodyColor
          'soft': '#142d42',   // cardColor
          'mute': '#1c3a50',   // popoverColor
        },
        // Button colors (default gray buttons)
        'btn-default': {
          DEFAULT: '#4e5d6c',
          'hover': '#5f7080',
          'pressed': '#3d4b59',
        },
        // Text colors from naive-ui theme
        'text': {
          'light': '#ffffff',      // textColorBase
          'light-muted': '#aab2bd', // placeholderColor
          'dark': '#212529',
          'dark-muted': 'rgba(33, 37, 41, 0.7)',
        },
        // Border colors from naive-ui theme
        'border': {
          DEFAULT: '#3b4c5a',  // borderColor/dividerColor
          'hover': '#5bc0de',  // scrollbarColorHover
        },
        // Input colors
        'input': {
          DEFAULT: '#1a3246',  // inputColor/actionColor
        },
      },
    },
  },
  plugins: [],
}

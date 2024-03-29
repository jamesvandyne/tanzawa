module.exports = {
  content: [
     '../apps/**/*.html',
      '../apps/**/forms.py',
    '../apps/**/forms/**/*.py',
    '../apps/interfaces/public/**/*.py',
      'src/**/*.js',
   ],
  theme: {
    colors: {
      'white': '#ffffff',
      'transparent': 'transparent',
      'current': 'currentColor',
      'primary': {
        DEFAULT: "#fbf7ef", // bg-bianca-500
      },
      'secondary': {
          DEFAULT: "#78695b", // negroni-900
          '600': '#e2ded7',  // bianca-600
          '700': '#b8a18c', // 'negroni-700
          '900': '#78695b'  // negroni-900
      },
      'bianca': {
        '50': '#fffffe',
        '100': '#fffefd',
        '200': '#fefdfb',
        '300': '#fdfcf9',
        '400': '#fcf9f4',
        '500': '#fbf7ef',
        '600': '#e2ded7',
        '700': '#bcb9b3',
        '800': '#97948f',
        '900': '#7b7975'
      },
      'negroni': {
        '50': '#fffdfc',
        '100': '#fefbf8',
        '200': '#fdf5ee',
        '300': '#fbefe3',
        '400': '#f8e2cf',
        '500': '#f5d6ba',
        '600': '#ddc1a7',
        '700': '#b8a18c',
        '800': '#938070',
        '900': '#78695b'
      },
      'malachite': {
        '50': '#f4fef7',
        '100': '#e9fdef',
        '200': '#c8fad6',
        '300': '#a7f6bd',
        '400': '#64f08c',
        '500': '#22e95a',
        '600': '#1fd251',
        '700': '#1aaf44',
        '800': '#148c36',
        '900': '#11722c'
      },
    },
    extend: {
      fontSize: {
        '5xl': ['5em', {
          lineHeight: '1em'
        }]
      },
      spacing: {
        '99': '45rem',
      },
    },
  },
  plugins: [],
}

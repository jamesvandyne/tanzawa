module.exports = {
  content: [
    './../../../../apps/templates/base_public.html',
    './../../../../apps/templates/registration/login.html',
    '../../../../apps/templates/public/**/*.html',
    '../../../../src/public_controllers/*.js',
  ],
  theme: {
    colors: {
      'white': '#ffffff',
      'black': '#000000',
      'transparent': 'transparent',
      'current': 'currentColor',
      'primary': {
        DEFAULT: '#dddddd',
        '600': '#CCCCCC',
        '800': '#BFBFBF',
      },
      'secondary': {
        DEFAULT: '#999CFC',
        '600': '#97948f',  // bianca-800
        '800': '#7476d6',
        '900': '#1a1c64',
      },
      },
    extend: {
      spacing: {
        '99': '45rem',
      },
    },
    variants: {
      extend: {},
    },
  },
};

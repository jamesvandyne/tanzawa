module.exports = {
  content: [
    './../../../../apps/templates/base_public.html',
    '../../../../apps/templates/public/**/*.html',
    '../../../../src/public_controllers/*.js',
  ],
  theme: {
    colors: {
      'white': '#ffffff',
      'transparent': 'transparent',
      'current': 'currentColor',
      'primary': "#dddddd",
      'secondary': "#999CFC",
      },
    extend: {
       colors: {
       } ,
      spacing: {
        '99': '45rem',
      },
    },
    variants: {
      extend: {},
    },
  },
};

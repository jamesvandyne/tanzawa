const path = require('path');

module.exports = {
  entry: './src/application.js',
  output: {
    filename: 'app.js',
    path: path.resolve(__dirname, '../static/js/'),
      // path: '.../static/js/'
  },
};
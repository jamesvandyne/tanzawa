const path = require('path');

module.exports = {
  entry: ['./src/application.js', '@hotwired/turbo', 'form-request-submit-polyfill'],
  output: {
    filename: 'app.js',
    path: path.resolve(__dirname, '../static/js/'),
  },
};
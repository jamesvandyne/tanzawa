const path = require('path');

const adminConfig = {
  entry: ['./src/application.js', '@hotwired/turbo', 'form-request-submit-polyfill'],
  output: {
    filename: 'app.js',
    path: path.resolve(__dirname, '../static/js/'),
  },
  optimization: {
    minimize: false,
  }
};

const publicConfig = {
  entry: ['./src/public.js'],
  output: {
    filename: 'public.js',
    path: path.resolve(__dirname, '../static/js/'),
  },
  optimization: {
    minimize: true,
  }
};

module.exports = [adminConfig, publicConfig];

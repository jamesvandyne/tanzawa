const path = require('path');

const adminConfig = {
  entry: ['./src/application.js', '@hotwired/turbo', 'form-request-submit-polyfill'],
  output: {
    filename: 'app.js',
    path: path.resolve(__dirname, '../static/js/'),
  },
  optimization: {
    minimize: true,
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


const tailwindConfig = {
  entry: "./css/style.css",
  output: {
    path: path.resolve(__dirname, "../static/tailwind/"),
    filename: "style.css",
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          "style-loader",
          { loader: "css-loader", options: { importLoaders: 1 } },
          "postcss-loader",
        ],
      },
    ],
  },
  // Optional for webpack-dev-server
  devServer: {
    watchContentBase: true,
    contentBase: path.resolve(__dirname, "dist"),
    open: true,
  },
}

module.exports = [adminConfig, publicConfig, tailwindConfig];

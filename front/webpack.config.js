const path = require('path');
const fs = require('fs');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

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
  entry: "./css/index.js",
  output: {
    path: path.resolve(__dirname, "../static/tailwind/"),
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "style.css"
    }),
  ],
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
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
};


/* Build a webpack config file each theme */
const themes = fs.readdirSync('./themes/');
const themeConfigs = [];
const outputPathParts = ["../static/themes/"];

for (const themeDirectory of themes) {
  // themeDirectory: /full/path/to/code/front/platinum
  let themeName = path.basename(themeDirectory); // platinum
  let outputPath = path.resolve(...outputPathParts, themeName);  // ../static/themes/platinum/
  let themeDirectoryPathParts = [__dirname, "themes", themeName];  // front/themes/platinum
  let entryPoint = path.resolve(...themeDirectoryPathParts,  "index.js"); // front/themes/platinum/index.js
  let themeConfig = {
    entry: entryPoint,  // front/themes/platinum/index.js
    output: {
      path: outputPath  // ../static/themes/platinum/
    },
    plugins: [
        new MiniCssExtractPlugin({
        filename: 'style.css'
      })
    ],
    module: {
      rules: [
        {
          test: /\.css$/,
          use: [
            MiniCssExtractPlugin.loader,
            { loader: "css-loader", options: { importLoaders: 1 } },
            { loader: "postcss-loader",
              options: {
                postcssOptions: {
                  plugins: () => [
                      require('postcss-import'),
                      require("tailwindcss")( {config:`./themes/${themeName}/tailwind.config.js` }),
                      require("autoprefixer")
                  ]
                }
              }
            },
          ],
        },
      ],
    }
  };
  themeConfigs.push(themeConfig);
}


module.exports = [adminConfig, publicConfig, tailwindConfig, ...themeConfigs];

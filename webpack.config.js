const path = require('path');
const webpack = require("webpack");
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: path.resolve(__dirname, 'src/index'),
  output: {
    path: path.resolve(__dirname, 'build'),
    filename: "main.js"
  },
  resolve: {
    enforceExtension: false,
    extensions: [".jsx", ".js"],
    modules: ["node_modules"],
    alias: {
      '../../theme.config$': path.join(__dirname, 'semantic/theme.config')
    }
  },
  module: {
    rules: [{
        test: /\.jsx$/,
        exclude: /node_modules/,
        use: {
	    loader: 'babel-loader',
	    options: {
	        presets: ['@babel/preset-react', '@babel/preset-env']
	    }
	}
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
	    loader: 'babel-loader',
	    options: {
	        presets: ['@babel/preset-react', '@babel/preset-env']
	    }
	}
      },
      {
        test: /\.less$/,
        use: [{
          loader: "style-loader"
        }, {
            loader: "css-loader"
        }, {
            loader: "less-loader"
        }],
      },
      {
        test: /\.css$/,
        loader: "style-loader!css-loader",
      },
      {
        test: [/\.bmp$/, /\.gif$/, /\.jpe?g$/, /\.png$/],
        loader: require.resolve('url-loader'),
        options: {
          limit: 10000,
          name: 'images/[name].[ext]',
        },
      },
      {
        test: [/\.eot$/, /\.ttf$/, /\.svg$/, /\.woff$/, /\.woff2$/],
        loader: require.resolve('file-loader'),
        options: {
          name: 'fonts/[name].[ext]',
        }
      },
      {
        test: /\.jsx$/,
        enforce: "pre",
        loader: "eslint-loader",
        exclude: /node_modules/,
      }
    ]
  },
  performance: {
    hints: false,
  },
  plugins: [
    new webpack.EnvironmentPlugin(['NODE_ENV']),
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, 'src/templates/index.template.ejs'),
      inject: 'body',
      filename: 'index.html'
    })
  ],
  devServer: {
    proxy: {
      '/dashboard/**': {
        target: 'http://localhost:5000',
      },
      '/profile/**': {
        target: 'http://localhost:5000',
      },
      '/flamegraph/**': {
        target: 'http://localhost:5000',
      },
    },
  },
};

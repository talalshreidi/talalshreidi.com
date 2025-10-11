const flowbite = require('flowbite/plugin');

module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {},
  },
  plugins: [flowbite],
}
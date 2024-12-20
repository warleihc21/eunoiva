/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.html', // Adicione os caminhos dos seus arquivos HTML
    './src/**/*.js',   // Adicione os caminhos dos seus arquivos JS
    './src/**/*.jsx',  // Se estiver usando React ou outro framework
    './src/**/*.ts',   // Se estiver usando TypeScript
    './src/**/*.tsx',  // Se estiver usando TypeScript com React
  ],
  theme: {
    extend: {
      aspectRatio: {
        'square': '1 / 1', // Proporção para quadrados
      },
    },
  },
  plugins: [],
};
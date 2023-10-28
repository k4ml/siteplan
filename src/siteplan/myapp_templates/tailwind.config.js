/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './myapp/fe/**/*.js',
    './myapp/templates/**/*.html'
  ],
  theme: {
    extend: {
      colors: {
        primary: {"700":"#3D4A3E","800":"#133331"},
        light: {"200":"#F8FFF8","300":"#EDFEEE"},
        myapp: {"300":"#B1FCD0","400":"#8BF433","500":"#09E665"},
        link: {"700":"#00A99C"}
      },
      fontSize: {
        "text-xl": "1.25rem",
        "text-3xl": "2.0rem",
        "text-4xl": "2.5rem"
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('windstrap')
  ],
}

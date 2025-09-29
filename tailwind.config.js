module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './apps/**/templates/**/*.js',
    './scripts/**/*.js'
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['Playfair Display', 'serif'],
        sans: ['Inter', 'sans-serif']
      }
    }
  },
  safelist: [
    'visible','hidden','flex','items-center','justify-center','opacity-0','opacity-100','scale-105',
    'bg-black/60','bg-black/40','drop-shadow-lg','max-w-xs','max-w-[70%]','translate-x-1/2','-translate-x-1/2'
  ],
  plugins: []
}


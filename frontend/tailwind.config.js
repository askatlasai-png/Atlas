// tailwind.config.js
import typography from "@tailwindcss/typography";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],

  safelist: [
    { pattern: /(text|bg|border)-(blue|emerald|amber|violet)-(50|100|200|600|700|800)/ },
	  'prose',
	  'prose-sm',
	  'prose-md',
	  'prose-lg',
	  'prose-xl',
	  'prose-invert',
	  'max-w-none',
  ],

  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', "ui-sans-serif", "system-ui"],
        display: ['"Plus Jakarta Sans Display"', '"Plus Jakarta Sans"', "system-ui"],
      },
    },
  },

  plugins: [typography()],
};

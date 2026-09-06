import daisyui from "daisyui";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./templates/**/*.html", "./frontend/src/**/*.{js,css}"],
  safelist: ["bg-primary/10", "bg-secondary/10", "bg-accent/10", "bg-violet-500/10", "bg-primary/15", "bg-secondary/15", "bg-accent/15", "text-primary", "text-secondary", "text-accent", "text-violet-500"],
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"] },
      colors: { ink: "#172033", mist: "#f5f7fb" },
      boxShadow: { soft: "0 14px 40px rgba(23, 32, 51, .08)" },
      keyframes: { "toast-progress": { from: { width: "100%" }, to: { width: "0%" } } },
    }
  },
  daisyui: {
    themes: [{ clinic: { primary: "#315efb", secondary: "#16b8a6", accent: "#f59e0b", neutral: "#172033", "base-100": "#ffffff", "base-200": "#f5f7fb", "base-content": "#172033" } }],
  },
  plugins: [daisyui]
};

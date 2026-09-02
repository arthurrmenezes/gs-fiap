/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Ford brand blue scale. 900 is the iconic deep Ford Blue (#00095B);
        // 500 is the interactive/signal blue used for CTAs and links.
        ford: {
          50: "#EEF3FE",
          100: "#D8E3FC",
          200: "#B4C8F8",
          300: "#85A4F1",
          400: "#5179E6",
          500: "#2C56D6",
          600: "#1C3DB4",
          700: "#152E8C",
          800: "#0D1E66",
          900: "#00095B",
          950: "#00052F",
        },
        // Neutral "graphite" scale for surfaces, text, borders.
        graphite: {
          25: "#FBFCFD",
          50: "#F5F7FA",
          100: "#ECEFF4",
          200: "#DDE2EA",
          300: "#C3CAD6",
          400: "#9AA4B4",
          500: "#6B7686",
          600: "#4C5666",
          700: "#363E4C",
          800: "#222934",
          900: "#141922",
        },
        // Status semantics for spec reconciliation states.
        signal: {
          ok: "#0F8A4F",
          okbg: "#E7F5EE",
          conflict: "#B26A00",
          conflictbg: "#FBF0DD",
          anomaly: "#C5221F",
          anomalybg: "#FBE9E8",
          na: "#6B7686",
          nabg: "#F0F2F5",
          low: "#3D5573",
          lowbg: "#E9EFF6",
        },
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "monospace"],
      },
      letterSpacing: {
        brand: "-0.02em",
      },
      boxShadow: {
        card: "0 1px 2px rgba(16, 24, 40, 0.04), 0 1px 3px rgba(16, 24, 40, 0.06)",
        elevated:
          "0 4px 6px -2px rgba(16, 24, 40, 0.04), 0 12px 24px -6px rgba(16, 24, 40, 0.10)",
        ring: "0 0 0 4px rgba(44, 86, 214, 0.12)",
      },
      backgroundImage: {
        "ford-header":
          "linear-gradient(112deg, #00052F 0%, #00095B 46%, #0D1E66 100%)",
        "grid-faint":
          "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.4s cubic-bezier(0.16, 1, 0.3, 1) both",
        shimmer: "shimmer 1.6s infinite",
      },
    },
  },
  plugins: [],
};

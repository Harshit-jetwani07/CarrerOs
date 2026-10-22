import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#14171F",
        "ink-soft": "#1C2029",
        line: "rgba(0,0,0,0.06)",
        "line-dark": "rgba(255,255,255,0.08)",
        paper: "#F6F7F9",
        surface: "#FFFFFF",
        slate: {
          DEFAULT: "#6B7280",
          light: "#9CA3AF",
        },
        cobalt: {
          DEFAULT: "#3652FF",
          dark: "#2540D6",
          light: "#EEF1FF",
        },
        gold: {
          DEFAULT: "#D4A72C",
          light: "#FBF3DD",
        },
        rust: {
          DEFAULT: "#C1502E",
          light: "#FBEAE4",
        },
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)", "sans-serif"],
        body: ["var(--font-plex-sans)", "sans-serif"],
      },
      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "16px",
        xl: "24px",
      },
      boxShadow: {
        panel: "0 22px 60px rgba(0, 0, 0, 0.28)",
        subtle: "0 1px 2px rgba(0, 0, 0, 0.04)",
      },
      backgroundImage: {
        "grid-dark": "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
        "glow-cobalt": "radial-gradient(circle at center, rgba(54,82,255,0.22), transparent 68%)",
      },
    },
  },
  plugins: [],
};

export default config;

"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

export function ThemeToggle({ compact = false }: { compact?: boolean }) {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const stored = window.localStorage.getItem("careeros-theme");
    const next = stored === "dark";
    setDark(next);
    document.documentElement.classList.toggle("theme-dark", next);
  }, []);
  function toggle() {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("theme-dark", next);
    window.localStorage.setItem("careeros-theme", next ? "dark" : "light");
  }
  return <button type="button" onClick={toggle} className={`theme-toggle ${compact ? "theme-toggle-compact" : ""}`} aria-label={dark ? "Switch to light mode" : "Switch to dark mode"} title={dark ? "Light mode" : "Dark mode"}>{dark ? <Sun size={17} /> : <Moon size={17} />}<span className="hidden sm:inline">{dark ? "Light" : "Dark"}</span></button>;
}

"use client";

import { Moon, Sun, Monitor } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ModeToggle() {
  const { theme, setTheme, systemTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const current = theme === "system" ? systemTheme : theme;

  if (!mounted) {
    return (
      <button
        type="button"
        aria-label="Toggle theme"
        className="relative flex size-9 items-center justify-center rounded-full border bg-transparent"
      >
        <Sun className="size-4" />
      </button>
    );
  }

  const cycleTheme = () => {
    if (theme === "light") setTheme("dark");
    else if (theme === "dark") setTheme("system");
    else setTheme("light");
  };

  return (
    <button
      type="button"
      onClick={cycleTheme}
      aria-label={`Theme: ${theme}. Click to cycle.`}
      className="group hover:bg-muted relative flex size-9 items-center justify-center overflow-hidden rounded-full border bg-transparent transition-colors"
    >
      <Sun
        className={`absolute size-4 transition-all duration-300 ${
          current === "dark"
            ? "scale-0 rotate-90 opacity-0"
            : "scale-100 rotate-0 opacity-100"
        }`}
      />
      <Moon
        className={`absolute size-4 transition-all duration-300 ${
          current === "dark"
            ? "scale-100 rotate-0 opacity-100"
            : "scale-0 -rotate-90 opacity-0"
        }`}
      />
      {theme === "system" && (
        <Monitor className="text-muted-foreground absolute size-3 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
      )}
    </button>
  );
}

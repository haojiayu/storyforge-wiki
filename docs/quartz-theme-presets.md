# Quartz Theme Presets for Worldbuilding Wiki

Paste one of these into `quartz.config.ts` under `configuration`.

## 1) Fantasy Parchment

```ts
configuration: {
  pageTitle: "The Ember Chronicle",
  baseUrl: "YOUR_USERNAME.github.io/my-world-wiki",
  theme: {
    typography: {
      header: "Cinzel",
      body: "EB Garamond",
      code: "JetBrains Mono",
    },
    colors: {
      lightMode: {
        light: "#faf4eb",
        lightgray: "#e8dcc8",
        gray: "#b8a99a",
        darkgray: "#4a3728",
        dark: "#2c1810",
        secondary: "#8b4513",
        tertiary: "#a0522d",
        highlight: "rgba(139,69,19,0.15)",
      },
      darkMode: {
        light: "#1a1208",
        lightgray: "#2d2010",
        gray: "#6b5744",
        darkgray: "#c4a882",
        dark: "#e8d5b0",
        secondary: "#cd853f",
        tertiary: "#daa520",
        highlight: "rgba(205,133,63,0.15)",
      },
    },
  },
}
```

## 2) Dark Arcane

```ts
configuration: {
  pageTitle: "Codex of Veiled Stars",
  baseUrl: "YOUR_USERNAME.github.io/my-world-wiki",
  theme: {
    typography: {
      header: "Cormorant Garamond",
      body: "Inter",
      code: "JetBrains Mono",
    },
    colors: {
      lightMode: {
        light: "#f6f5fb",
        lightgray: "#e4e2f2",
        gray: "#9990bf",
        darkgray: "#3f355f",
        dark: "#1b1730",
        secondary: "#5f4bb6",
        tertiary: "#7f67d9",
        highlight: "rgba(95,75,182,0.14)",
      },
      darkMode: {
        light: "#0d0b18",
        lightgray: "#1a1630",
        gray: "#6a5ca6",
        darkgray: "#b8afe3",
        dark: "#ece9ff",
        secondary: "#8d7cff",
        tertiary: "#6be6ff",
        highlight: "rgba(141,124,255,0.20)",
      },
    },
  },
}
```

## 3) Sci-Fi Neon

```ts
configuration: {
  pageTitle: "Neon Frontier Atlas",
  baseUrl: "YOUR_USERNAME.github.io/my-world-wiki",
  theme: {
    typography: {
      header: "Space Grotesk",
      body: "Inter",
      code: "JetBrains Mono",
    },
    colors: {
      lightMode: {
        light: "#f7fcff",
        lightgray: "#dff3fb",
        gray: "#8ab8cc",
        darkgray: "#24556b",
        dark: "#0f2430",
        secondary: "#00a3ff",
        tertiary: "#00d4b8",
        highlight: "rgba(0,163,255,0.16)",
      },
      darkMode: {
        light: "#071118",
        lightgray: "#0f1f2b",
        gray: "#4f7d93",
        darkgray: "#9fd7ef",
        dark: "#e5f7ff",
        secondary: "#00c2ff",
        tertiary: "#00f5d4",
        highlight: "rgba(0,194,255,0.22)",
      },
    },
  },
}
```

## Quick Font Setup

If you use custom fonts, add matching imports in your Quartz setup (or swap to already-installed fonts).

# packages/ui/

**Shared shadcn/ui component library (55+ components)**

## OVERVIEW

Shared UI primitive components for the monorepo, exported via `@chat-kasir/ui`.

## STRUCTURE

```
src/
├── components/     # 55+ shadcn/ui components (.tsx files)
├── hooks/          # Shared React hooks
├── lib/            # Utilities (e.g., cn())
├── styles/          # globals.css
└── components.json  # shadcn registry config
```

## EXPORTS

Import from `@chat-kasir/ui/components/*`:
```tsx
import { Button } from "@chat-kasir/ui/components/button";
import { Card } from "@chat-kasir/ui/components/card";
```

## CONVENTIONS

- **Styling**: Tailwind CSS via PostCSS + `@tailwindcss/postcss`
- **Linting**: Ultracite (biome-based)
- **Components**: PascalCase file names matching shadcn standard

## NOTES

- shadcn components use Tailwind CSS with shadcn design tokens

## ADD COMPONENTS

```bash
npx shadcn@latest add accordion dialog -c packages/ui
```

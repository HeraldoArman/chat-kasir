# apps/web/src/

**Next.js 16 frontend application**

## OVERVIEW

Next.js 16 frontend using App Router, PWA-enabled, with shadcn/ui components.

## STRUCTURE

```
src/
├── app/              # App Router (layout.tsx, page.tsx, manifest.ts)
├── components/       # App-specific components (header, mode-toggle, etc.)
└── index.css         # Entry CSS
```

## ENTRY POINTS

- `app/page.tsx` - Home route (`/`)
- `app/layout.tsx` - Root layout wrapping all pages
- `app/manifest.ts` - PWA manifest (metadata route)

## CONVENTIONS

- **Framework**: Next.js 16 (App Router)
- **UI**: shadcn/ui imported from `@chat-kasir/ui`
- **Env vars**: `@t3-oss/env-nextjs` + Zod validation via `packages/env`
- **Themes**: `next-themes` for dark/light mode

## PWA

- Next.js PWA via `next.config.ts` with manifest at `/manifest`
- PWA assets generated via: `cd apps/web && bun run generate-pwa-assets`

## ANTI-PATTERNS

- No tests configured yet

## COMMANDS

```bash
bun run dev:web      # Start on port 3001
bun run build        # Next.js production build
```

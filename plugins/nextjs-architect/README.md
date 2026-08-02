# nextjs-architect

Industry-standard engineering patterns for Next.js and React, enforced as a workflow rather than
offered as advice.

## The iron law

**SERVER FIRST, ALWAYS.**

Every component is a Server Component until you prove it needs client interactivity. Business logic
never lives in `app/` — only routing files. Every component with state has a test. No `any`.

## What is in the plugin

A single skill, no agents or commands. The core is `SKILL.md`; 22 reference files hold the
detail and are loaded on demand.

| Part | Covers |
|---|---|
| **Phased workflow** | Plan → detection → architecture → implementation → verification, with gates between them |
| **TypeScript verification gate** | Enforced `tsc` / `eslint` commands rather than a claim that types are fine |
| **Architecture** | Server Components, feature-based structure (FSD), logic/view separation, monorepos |
| **Runtime** | Error boundaries, Suspense streaming, forms with Server Actions, auth middleware, file uploads, the data access layer |
| **Routing** | Parallel, intercepting, PPR, `template.tsx` |
| **Delivery** | SEO metadata and JSON-LD, testing with Vitest/RTL/Playwright, Storybook, theming, i18n, CI/CD, Docker |
| **Quality** | Naming conventions, design system tokens, UI states, security headers, observability, review checklist |

## Installation

```bash
/plugin marketplace add haflingmax/haflingmax-claude-skills
/plugin install nextjs-architect@haflingmax-claude-skills
```

## When it triggers

Any task touching Next.js, React, or React+Vite — creating components, pages, routes, tests or
Storybook stories, and equally reviewing, auditing or refactoring an existing architecture.

Not for backend-only work with no React involvement, React Native, static sites without React, or
non-JavaScript template frameworks.

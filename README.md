# haflingmax-skills

Curated skills for software engineering, business analysis, and strategic planning — battle-tested patterns that make Claude Code agents more effective.

## Installation

### 1. Add as marketplace

```bash
/plugin marketplace add haflingmax/haflingmax-claude-skills
```

### 2. Install the plugin

```bash
/plugin install haflingmax-skills@haflingmax-haflingmax-claude-skills
```

Or via CLI:

```bash
claude plugin install haflingmax-skills@haflingmax-haflingmax-claude-skills
```

After installation, skills are available automatically. Claude Code detects and invokes
them based on your task context.

## Skills

### nextjs-architect

Enforces industry-standard engineering patterns for Next.js and React projects.

**Iron Law:** SERVER FIRST, ALWAYS.

**Covers:** Server Components, feature-based architecture (FSD), logic/view separation,
error boundaries, Suspense streaming, forms with Server Actions, auth middleware,
file uploads, data access layer, advanced routing (parallel, intercepting, PPR),
SEO, testing (Vitest/RTL/Playwright), Storybook, theming, i18n, CI/CD, Docker.

**Triggers on:** Any task involving Next.js, React, or React+Vite projects.

## Structure

```
.claude-plugin/
  plugin.json                     # Plugin manifest

skills/
  nextjs-architect/
    SKILL.md                      # Behavioral core (266 lines)
    references/
      component-patterns.md       # Hook+view, file structure, Storybook, testing
      error-suspense.md           # Error boundaries, Suspense, streaming
      forms-auth.md               # Forms, auth, file uploads, Server Action limits
      data-patterns.md            # DAL, generateStaticParams, ISR, pooling, use()
      advanced-routing.md         # Parallel/intercepting routes, PPR, template.tsx
      seo-scripts.md              # Metadata, JSON-LD, sitemap, next/script
      theming.md                  # Light/dark mode
      i18n.md                     # Internationalization
      semantic-variants.md        # Variant/intent component system
      storybook-docker.md         # Storybook containerization
      cicd-pipeline.md            # GitHub Actions CI/CD
      review-checklist.md         # Project audit checklist
```

## Adding New Skills

Create a new directory under `skills/` with a `SKILL.md`:

```
skills/
  my-new-skill/
    SKILL.md              # Required — YAML frontmatter + instructions
    references/           # Optional — deep-dive content loaded on demand
```

Skills are auto-discovered by Claude Code — no need to register them in `plugin.json`.

## License

MIT

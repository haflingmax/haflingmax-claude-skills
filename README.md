# haflingmax-skills

Curated skills for software engineering, business analysis, and strategic planning — battle-tested patterns that make Claude Code agents more effective.

## Installation

### 1. Add as marketplace

```bash
/plugin marketplace add haflingmax/haflingmax-claude-skills
```

### 2. Install the plugin

```bash
/plugin install nextjs-architect@haflingmax-claude-skills
```

Or via CLI:

```bash
claude plugin install nextjs-architect@haflingmax-claude-skills
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

### model-from-reference

Discipline for building a 3D model that has to match 2D reference art — character, prop, mannequin,
vehicle.

**Iron Law:** MEASUREMENT BELONGS IN VERIFICATION, NEVER IN THE OPERATION.

A cross-section's bounding box is identical for an ellipse and a rounded rectangle: width and depth
agree to the millimetre while one is an oval and the other is a box with corners. Measurement is
blind to form by construction, so the eye judges form and measurement only guards proportion.

**Covers:** the six-beat step cycle, the three-look inspection (surface, edge flow, vertex
placement) with mandatory top view and orbit, polygon budget from purpose, markup as tool rather
than blueprint, phases M1–M6, the operation catalogue, limb openings cut along the mesh's own
lines, stencil inversion instead of blind convergence, and thirty verified Blender traps.

**Ships with:** three inspector agents, a `/model-review` command that renders the mandatory frame
set and runs all three looks, and `pp_blender.py` — a session toolkit for rings by connectivity,
pixel measurement of the reference, frame scale, perception channels and topology counters.

**Triggers on:** modelling from reference, blockout, box modelling, edge flow for a joint,
silhouette matching — and especially "it matches the numbers but looks wrong".

Install:

```bash
/plugin install model-from-reference@haflingmax-claude-skills
```

## Structure

```
.claude-plugin/
  marketplace.json                # Marketplace manifest, lists both plugins

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

plugins/
  model-from-reference/           # Self-contained plugin, own manifest
    .claude-plugin/plugin.json
    agents/
      surface-inspector.md        # Judges form: arc, curvature breaks, oval or box
      edge-flow-inspector.md      # Judges loop routing, poles, density gradient
      vertex-inspector.md         # Judges vertex placement and the mirror seam
    commands/
      model-review.md             # Render the mandatory set, run all three looks
    skills/
      model-from-reference/
        SKILL.md                  # The law, the step cycle, the traps
        references/
          work-rules.md           # R1–R8: scene, budget, one part per iteration, markup
          step-cycle.md           # Six beats, the fix loop, limits, rollback
          measure-vs-eye.md       # Rule 5 and every sub-rule — when measurement lies
          phases.md               # M1–M6, operation catalogue, checks, budget
          blender.md              # Operation-to-tool mapping and 30 verified traps
        scripts/
          pp_blender.py           # Session toolkit for Blender
```

Two layouts coexist here. `nextjs-architect` is declared with `source: "./"`, so the repository root
is its plugin root. Anything added at the root — `agents/`, `commands/` — would silently become part
of it, so a plugin that ships those lives in its own directory under `plugins/` with its own
manifest.

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

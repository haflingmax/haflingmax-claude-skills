# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is a **Claude Code plugin marketplace**, not an application. It ships
agent-facing instructions (Markdown) — there is no runtime, no build step, no
test suite. The "product" is the prose that other Claude Code instances load
at session start. Treat changes to `SKILL.md` files the way you'd treat
changes to production prompts: small wording shifts change agent behavior.

There are **no build / lint / test commands**. Verification is by reading the
content and, where possible, running the skill against the kind of task it
claims to cover.

## Repository layout

```
.claude-plugin/marketplace.json   # Marketplace manifest — registers plugins
.claude/                          # Local Claude Code state — gitignored
skills/<plugin-name>/SKILL.md     # Root-layout plugin: skill only
skills/<plugin-name>/references/  # Deep-dive content loaded on demand
plugins/<plugin-name>/            # Self-contained plugin: own manifest + components
README.md                         # User-facing install instructions
```

**Two layouts coexist, and which one to use is forced, not a preference.**

`nextjs-architect` is declared with `"source": "./"` — the repository root *is* its plugin root.
Auto-discovery for such a plugin scans `<root>/commands`, `<root>/agents`, `<root>/skills/*/SKILL.md`,
`<root>/hooks/`, `<root>/.mcp.json`. So anything placed at the root becomes part of it.

That is fine for a plugin that ships only a skill. It breaks the moment a second plugin needs
agents, commands or hooks: put them at the root and they silently join `nextjs-architect`. Such a
plugin therefore lives in its own directory with its own `.claude-plugin/plugin.json`, and the
marketplace entry points at that directory:

```json
{ "name": "model-from-reference", "source": "./plugins/model-from-reference" }
```

A subdirectory source is the standard form — the official Anthropic marketplace uses it for all 276
of its entries. Auto-discovery does not recurse, so the two layouts do not see each other.

Two directories are easy to confuse and the `.gitignore` carries a load-bearing
comment about it:

- **`.claude-plugin/`** — the plugin/marketplace manifest. **Tracked.** Edit when adding plugins.
- **`.claude/`** — local Claude Code session state. **Gitignored.** Never commit.

## Marketplace vs. plugin manifest

Root `.claude-plugin/` holds `marketplace.json` — a *marketplace* manifest declaring several
plugins under one `plugins: []` array. There is no `plugin.json` at the repo root, which is why the
`nextjs-architect` entry carries `"strict": false`: that flag waives the per-plugin manifest
requirement. A plugin in its own directory ships a real `.claude-plugin/plugin.json` and does not
need the flag.

The `skills: []` field in a marketplace entry is only needed when the plugin has no manifest of its
own — it tells the loader where to look. A plugin with a manifest has its `skills/`, `agents/` and
`commands/` discovered automatically from its root; listing them adds nothing.

## Adding a new skill or plugin

**Skill only, no agents or commands** — the root layout is enough:

1. `mkdir skills/<skill-name>` (kebab-case)
2. Create `SKILL.md` with required YAML frontmatter:
   ```yaml
   ---
   name: <skill-name>          # must match directory name
   description: >              # the trigger text Claude sees — be specific
     Use when ...
   ---
   ```
3. Put deep-dive content in `skills/<skill-name>/references/*.md` and link to
   it from `SKILL.md` (loaded on demand to keep the core small).
4. If it belongs to a new plugin, add an entry to `.claude-plugin/marketplace.json`
   with `skills: ["./skills/<skill-name>"]`.

**Anything shipping agents, commands, hooks or scripts** — own directory, or it contaminates
`nextjs-architect`:

1. `mkdir -p plugins/<plugin-name>/{.claude-plugin,skills/<skill-name>,agents,commands}`
2. Write `plugins/<plugin-name>/.claude-plugin/plugin.json` — `name` must equal the marketplace
   entry's `name`.
3. Add the entry: `{ "name": "<plugin-name>", "source": "./plugins/<plugin-name>" }`. No `skills`
   array, no `strict`.
4. Inside `SKILL.md`, reference siblings by skill-relative path (`references/foo.md`). Anywhere
   else — commands, hooks, scripts — use `${CLAUDE_PLUGIN_ROOT}`, since relative paths there
   resolve against the user's working directory, not the plugin.

## Skill authoring conventions

This repo distinguishes two skill classes, and the tradeoff is documented at
the bottom of `skills/nextjs-architect/SKILL.md` (lines 375–380):

- **Discipline skills** (e.g. `superpowers:test-driven-development`) — ~500 words.
  Short, rigid, technique-focused. Hot path is the *process*, not domain facts.
- **Reference skills** (e.g. `nextjs-architect`) — may exceed 500 words when
  detection logic, architecture rules, and version-specific guidance must live
  in the core because they can't be deferred without breaking the workflow.
  This skill is ~1,600 words and 12 reference files (~7,000 words) — that's
  intentional, not a bug.

When writing or editing a SKILL.md:

- The `description` field is the trigger. It must be specific enough that
  Claude knows when to invoke (and when *not* to). Vague descriptions = misfires.
- Use phased gates (`Phase 0 → Phase 1 → ...`) and explicit `<HARD-GATE>` /
  `Gate:` markers when the workflow must be ordered. `nextjs-architect/SKILL.md`
  is the reference example.
- Prefer named cross-references to sub-skills (`superpowers:writing-plans`)
  over inlining their content.
- Tables for rules, fenced code for examples, `<Good>` / `<Bad>` blocks for
  contrasting patterns. The agent parses these reliably.

## Current skills

- **nextjs-architect** — Next.js / React / React+Vite architecture skill.
  Iron law: "Server first, always." Four-phase workflow with mandatory plan,
  detection, architecture, implementation, verification gates. Triggers on
  any task touching React or Next.js components, routes, tests, or Storybook.
  Root layout, `source: "./"`, `strict: false`.

- **model-from-reference** — building a 3D model that must match 2D reference art.
  Iron law: "Measurement belongs in verification, never in the operation" — a
  bounding box is identical for an ellipse and a rounded rectangle, so measurement
  is blind to form by construction and only the eye can judge it. Six-beat step
  cycle, three-look inspection with mandatory top view and orbit. Ships three
  inspector agents, a `/model-review` command and a Blender session toolkit, so it
  lives under `plugins/` with its own manifest. Triggers on blockout, box modelling,
  edge flow at a joint, silhouette matching — and especially "it matches the numbers
  but looks wrong".

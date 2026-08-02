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
.claude-plugin/marketplace.json          # Marketplace manifest — registers plugins
.claude/                                 # Local Claude Code state — gitignored
plugins/<plugin-name>/                   # One self-contained plugin, one directory
  .claude-plugin/plugin.json             #   its own manifest
  LICENSE                                #   travels with the plugin
  skills/<skill-name>/SKILL.md           #   the skill (YAML frontmatter + body)
  skills/<skill-name>/references/        #   deep-dive content loaded on demand
  skills/<skill-name>/scripts/           #   executables, if any
  agents/  commands/  hooks/             #   optional components
README.md                                # User-facing install instructions
CLAUDE.md                                # This file
```

**One layout, no exceptions.** Every plugin lives in `plugins/<name>/` with its own manifest, and
its marketplace entry points at that directory:

```json
{ "name": "<plugin-name>", "source": "./plugins/<plugin-name>" }
```

This used to be split: `nextjs-architect` was declared with `"source": "./"`, making the repository
root its plugin root. That form works but is a trap, and nothing in the official Anthropic
marketplace uses it — 0 of its 276 entries. Two reasons it was abandoned here:

- **A root-sourced plugin owns everything at the root.** Auto-discovery scans `<root>/commands`,
  `<root>/agents`, `<root>/skills/*/SKILL.md`, `<root>/hooks/`. Add a second plugin's agents at the
  root and they silently join the first one.
- **Installing it copies the whole repository** into that plugin's cache — the other plugin's files,
  the README, the licence, this file. Verified in the cache: dead weight, not a malfunction, but
  it grows with every plugin added.

It also needed `"strict": false` in the marketplace entry, which waives the per-plugin manifest
requirement. With a real `plugin.json` the flag is unnecessary — and its absence is the signal that
the plugin is properly formed.

Two directories are easy to confuse and the `.gitignore` carries a load-bearing
comment about it:

- **`.claude-plugin/`** — the plugin/marketplace manifest. **Tracked.** Edit when adding plugins.
- **`.claude/`** — local Claude Code session state. **Gitignored.** Never commit.

## Marketplace vs. plugin manifest

Two manifests, two jobs, and the distinction matters when something fails to load.

- **`.claude-plugin/marketplace.json`** at the repo root — the *marketplace*. Lists plugins under
  one `plugins: []` array. Edit it when adding a plugin.
- **`plugins/<name>/.claude-plugin/plugin.json`** — the *plugin*. Its `name` must equal the
  marketplace entry's `name`; a mismatch is the usual cause of "installs but nothing appears".

A marketplace entry needs neither a `skills: []` array nor `"strict": false`. Both exist for
plugins that have no manifest of their own: `skills` tells the loader where to look, `strict: false`
waives the manifest requirement. With a proper `plugin.json`, `skills/`, `agents/`, `commands/` and
`hooks/` are discovered automatically from the plugin root, and listing them adds nothing.

## Adding a plugin

1. ```
   mkdir -p plugins/<plugin-name>/{.claude-plugin,skills/<skill-name>}
   cp LICENSE plugins/<plugin-name>/
   ```
   Add `agents/`, `commands/`, `hooks/` only if you actually ship them.
2. Write `plugins/<plugin-name>/.claude-plugin/plugin.json` — `name` matching the marketplace entry,
   plus `description`, `version`, `author`, `keywords`.
3. Create `skills/<skill-name>/SKILL.md` with the required frontmatter:
   ```yaml
   ---
   name: <skill-name>          # must match its directory name
   description: >              # the trigger text Claude sees — be specific
     Use when ...
   ---
   ```
4. Put deep-dive content in `skills/<skill-name>/references/*.md` and link to it from `SKILL.md`
   (loaded on demand, which is what keeps the core small).
5. Add the marketplace entry:
   `{ "name": "<plugin-name>", "source": "./plugins/<plugin-name>" }`.

**Paths inside a plugin.** From `SKILL.md`, reference siblings skill-relatively — `references/foo.md`,
`scripts/tool.py`. Everywhere else — commands, agents, hooks — use `${CLAUDE_PLUGIN_ROOT}`, because
a relative path there resolves against the *user's* working directory, not the plugin's. This is the
single most common runtime bug in a plugin that validates cleanly.

## Skill authoring conventions

This repo distinguishes two skill classes, and the tradeoff is documented in the
footnote at the bottom of `plugins/nextjs-architect/skills/nextjs-architect/SKILL.md`:

- **Discipline skills** (e.g. `superpowers:test-driven-development`) — ~500 words.
  Short, rigid, technique-focused. Hot path is the *process*, not domain facts.
- **Reference skills** (e.g. `nextjs-architect`) — may exceed 500 words when
  detection logic, architecture rules, and version-specific guidance must live
  in the core because they can't be deferred without breaking the workflow.
  That skill is ~4,500 words with 22 reference files (~20,000 words) — intentional,
  not a bug.
- **model-from-reference** sits between the two: ~3,000 words of core against five
  references (~3,350 lines). The core carries a law and a cycle; everything
  procedural defers.

If you quote a size here, re-count it. These numbers were stale by a factor of three
before anyone noticed, because nothing checks them.

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
  Skill only — no agents, commands or scripts.

- **model-from-reference** — building a 3D model that must match 2D reference art.
  Iron law: "Measurement belongs in verification, never in the operation" — a
  bounding box is identical for an ellipse and a rounded rectangle, so measurement
  is blind to form by construction and only the eye can judge it. Six-beat step
  cycle, three-look inspection with mandatory top view and orbit. Ships three
  inspector agents, a `/model-review` command and a Blender session toolkit. Triggers
  on blockout, box modelling, edge flow at a joint, silhouette matching — and
  especially "it matches the numbers but looks wrong".

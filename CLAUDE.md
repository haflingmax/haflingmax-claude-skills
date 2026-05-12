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
skills/<plugin-name>/SKILL.md     # The skill itself (YAML frontmatter + body)
skills/<plugin-name>/references/  # Deep-dive content loaded on demand
README.md                         # User-facing install instructions
```

Two directories are easy to confuse and the `.gitignore` carries a load-bearing
comment about it:

- **`.claude-plugin/`** — the plugin/marketplace manifest. **Tracked.** Edit when adding plugins.
- **`.claude/`** — local Claude Code session state. **Gitignored.** Never commit.

## Marketplace vs. plugin manifest

The README references `.claude-plugin/plugin.json`, but this repo actually
uses `.claude-plugin/marketplace.json` — a *marketplace* manifest that can
declare multiple plugins under one `plugins: []` array. Each plugin entry's
`skills: []` field points to skill directories. If you add a plugin, edit
`marketplace.json`; if you add a skill *inside* an existing plugin, no manifest
edit is needed — skills are auto-discovered from the directory listed in
`plugins[].skills`.

## Adding a new skill

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
4. If the skill belongs to a new plugin, add a plugin entry to
   `.claude-plugin/marketplace.json` with `skills: ["./skills/<skill-name>"]`.

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

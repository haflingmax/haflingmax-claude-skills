# How rules are made, matured and retired

This file covers the process that produced every other rule in this skill: how a rule is added, how
it earns the right to be believed, how it is worded so that it can be checked at all, and the
sub-step cycle that the rules themselves refer to. Read it when you are about to write a new rule,
change an existing one, or extend this skill to a work type it does not yet cover — and read it if a
rule elsewhere in this set mentions the sub-step cycle and you want to know what those five states
are.

It is deliberately separate from the rules themselves. The rules say what to do; this says how the
set stays honest as it grows.

---

## Rules are added one at a time

Write it → apply it → look at what happened → approve, reword, or reject.

Never in batches. An unverified rule guarantees nothing, and ten unverified rules manufacture a
false sense of order — the set looks disciplined while none of it has been tested. That feeling is
worse than having no rules, because it stops you looking.

### The lifecycle of a rule

```
draft  ──applied──>  under verification  ──it worked──>  approved
                            │
                            └──it did not──>  reword  ──or──>  rejected
```

| Status | Meaning |
|--------|---------|
| `draft` | Formulated and applied in real work, but not yet carried through a full build from first setup to delivery |
| `under verification` | Being applied in current work; results are being collected |
| `approved` | Applied in practice and produced the intended effect |
| `rejected` | Applied and did not work; the reason is recorded in the change log |

**A rule is not working until it has been verified in practice** — including rules a human dictated.
Verification matters more than formulation. Practice almost always changes something: a missing
input turns up, a step proves redundant, a check fires falsely. Those findings go into the rule
itself and into the file's change log, so the next reader sees what the rule cost and why it is
worded the way it is.

This is why the rules in this skill carry their failure stories. A rule stripped of the failure it
came from reads as a platitude, and platitudes are abandoned the moment following them is
inconvenient.

### The sub-step cycle

A rule is carried out in sub-steps. Each sub-step passes five states **in order**, and the next
sub-step does not begin until the current one is closed:

| State | What happens |
|-------|--------------|
| **Studied** | The data needed for the decision is gathered: measurements, constraints, the options and what each costs |
| **Agreed** | The decision is presented with its justification and accepted by the user |
| **Recorded** | The decision is written down — in a rule if it is general, in the task if it belongs to this piece of work |
| **Performed** | The action is carried out |
| **Checked** | The result is measured and presented; divergences are examined, not passed over in silence |

**"Recorded" is the state that gets skipped**, and skipping it is expensive in a specific way: a
decision taken verbally and acted on immediately becomes indistinguishable from a guess two
sub-steps later. Nobody can tell whether it was chosen deliberately or simply happened — so nobody
can revisit it, and it silently hardens into an assumption.

Note the scope: this five-state cycle governs any sub-step of the work that carries a decision —
the phases M1–M6, and equally the choice of method under R8, which runs before M1. The six-beat
cycle in [step-cycle.md](step-cycle.md) applies to a step *inside* the "performed" state.

---

## Requirements on the wording

A rule must be **checkable**: it has an observable sign of compliance and an observable sign of
violation. "Work carefully" is not a rule. "Publish the inventory before the first operation" is.

A rule is worded **generally**. If a number tied to one particular piece of work appears in it, or a
list that is true of only one object, that is the sign the rule is being fitted to the work in front
of you. Move that content to the task and leave the *method of obtaining it* in the rule.

Both requirements exist for the same reason: a rule that cannot be checked cannot be falsified, and
a rule that cannot be falsified will be believed long after it has stopped being true.

## The boundary of a rule

Each rule has one job. A question that does not bear on that job does not belong in it, however
important the question is in itself — it goes into the queue as a separate rule.

A rule that has swollen stops being checkable: when it fires, you cannot tell which part of it did
the work, and when it fails you cannot tell which part failed.

---

## Template for a new rule

```markdown
### R<N> — <short title>

**Status:** `draft`

**Statement.** One or two sentences. What to do, or what not to do.

**Why.** Which failure mode this prevents. Reference A<N> if there is one.

**Procedure.** Numbered steps, executable literally.

**How to check.** A command, a script, or an observable sign. Not "by eye" if it can be measured.

**Done when:** a checkable condition.
**Violated if:** concrete signs of violation.
```

## Structure of a work-type file

1. **Header** — what work type this is, and where it applies.
2. **Rules in force** — R1, R2, … to the template above.
3. **Failure modes** — A1, A2, … the things the rules exist to prevent. These are not rules; they
   are descriptions of the mistakes the rules grew out of. Each rule points at the failure mode it
   closes.
4. **Queue of rules under discussion** — topics with no rule yet. Taken one at a time.
5. **Change log** — what changed and why, including findings from applying the rules.

## Extending this skill to a new work type

The rules in this skill are organised in three layers, and a new work type joins at the top:

| Layer | File | Answers |
|-------|------|---------|
| Work type | [work-rules.md](work-rules.md) | Which method to use, and the rules that hold whatever the method |
| Method | [step-cycle.md](step-cycle.md), [measure-vs-eye.md](measure-vs-eye.md), [phases.md](phases.md) | How that method is worked, independent of any editor |
| Editor | [blender.md](blender.md) | Which tool performs each operation, and what it does wrong |

A new work type gets its own file at the work-type layer, written to the structure above, and a row
in the routing table in `SKILL.md`. Do not duplicate the method layer — point at it. If the new work
type needs a method this set does not describe, that method gets its own file at the middle layer,
and only then does the work-type file reference it.

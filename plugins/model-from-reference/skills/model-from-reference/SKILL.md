---
name: model-from-reference
description: >
  Use when building or fixing a 3D model that has to match 2D reference art — character, prop,
  mannequin, vehicle: blockout, box modelling, matching a silhouette to concept art or a turnaround,
  edge flow at a limb joint, cutting an armhole or a leg opening, deciding a polygon budget.
  Especially when a mesh "matches every measurement but still looks wrong", is "in tolerance but
  reads wrong", when "the numbers agree" and the form does not, when a surface looks faceted or
  boxy, when something "looks off" and the user cannot see what — in any language, including
  Russian ("сходится с артом, а выглядит не так"). Applies to Blender and any polygon modeller with
  subdivision. Not for CAD or hard-surface work driven by dimensioned drawings, where the
  dimensions are the authority and this skill's central law inverts.
---

# Model From Reference

## Scope, before anything else

This skill is for form that is **judged by eye against art**. If your authority is a dimensioned
drawing — CAD, hard-surface engineering, anything where a number *is* the specification — stop
here: the central law below inverts for you, and the gates further down would forbid exactly the
right thing to do. Also not for sculpting with dynamic topology where retopology comes later (the
ring discipline does not apply), procedural generation with no reference art, or texturing,
shading, rigging and animation.

## The one law

**Measurement belongs in verification. Never in the operation.**

> Where an operation goes is found **by eye, on the reference**. Measurement passes judgment
> afterwards.

This is the rule the whole method exists to protect, because building-from-a-table-of-sections
keeps coming back in disguise: first as a method, then as a plan, then as a list of operations
with numbers inside their wording. Banning one disguise does not stop the next one. Only the
ordering does.

**Why it matters — the failure it prevents.** A cross-section's bounding box is identical for an
ellipse and for a rounded rectangle. Width and depth agree to the millimetre while one is a
smooth oval and the other is a box with corners. Measurement cannot tell them apart; it is blind
to form by construction. In practice this produced a torso whose front and side silhouettes both
matched the art within 5 mm of an 8 mm tolerance, and which — seen from above — was a flat slab
with two hard corners and a longitudinal ridge running its whole height.

So:

- **Measurement answers** "have the proportions drifted" — a part must not end up half as wide or
  a hand's width too low. Its answer is coarse by nature.
- **The eye answers** "is the form right" — and that is the only answer that counts.

**"The numbers agree" is neither an argument in an inspection nor an objection to its finding.**
If the eye names a break and measurement is silent, the eye is right; the silence is a property of
measurement, not an excuse for the form. The converse also holds: a finding about *size* is
verified by measurement before you act on it (see [measure-vs-eye.md](references/measure-vs-eye.md),
§5.4).

Catching yourself thinking *"just this once — the numbers are obviously fine"* is the signal, not
the exception. Stop, re-read the self-check below, and rewrite the operation's wording.

## Self-check before every operation

Re-read your own wording of the operation. If its location can be determined **without looking at
the reference** — from a table of measurements, a plan, a guide object, a zone or level number, a
fraction of the part's height — the operation is worded wrongly and gets rewritten before it is
performed.

The location marker has to be something visible on the reference: a change in the character of the
form, a drawn line, the point where width stops growing, the start of a surface turn.

- Right: "continue the shell downward to where the reference's profile stops widening."
- Wrong: "continue the shell down to level 1041 and set the ring to 283 × 179."

Only two things may be fixed by number before an operation: the **part's boundaries** (a contract
with the neighbouring part) and the **overall bounding box** — three numbers. The height at which
the maximum occurs is *not* included: where the part is widest is found by eye. Intermediate
sections are never an exception, not as a bound, not as a hint, not as a reference.

## The unit of work is a step

> A step is **one topological operation**, plus shaping exactly the geometry whose composition
> that operation changed, taken to "cannot be done better at this density", and closed by
> inspection.

Moving vertices is not a step — it is the content of a step. A markup block (head, chest, pelvis)
is too coarse to be a step; it is 3–6 steps.

**One form feature at a time, to a finish.** The temptation is constant: several places look wrong
at once and the hand reaches to fix them in one pass. The reason not to is not tidiness — it is
that inspection answers "what is wrong *in this zone*". Change three zones in one pass and a
finding cannot be traced to its cause; rollback loses meaning, and the fix loop stops converging
because every pass changes the conditions for its neighbours.

## The six-beat cycle

Every step passes six beats. A beat may not be skipped silently and may not be performed
retroactively.

| Beat | What happens |
|------|--------------|
| **1 — name** | One sentence: what we are doing and what it settles. No numbers in the wording. |
| **2 — operate** | Create a rollback point, then perform exactly one topological operation. |
| **3 — shape** | Place vertices **one ring at a time**. Each vertex gets its own place. |
| **4 — inspect** | Three separate looks. Unbounded fix loop. Details below. |
| **5 — verify** | Take the gauge **off the final surface** — subdivision on, never off the cage — and compare with the nearest markup measurement, **against the form tolerance, not the measurement tolerance**. One or two numbers, not a table. |
| **6 — decide** | Close the step / accept the divergence deliberately / re-shape / roll back. |

Beat 5's two qualifications are not pedantry. A cage reading is simply invalid under an
approximating subdivision scheme — and it reads low, so the error hides inside the numbers
themselves. And the measurement tolerance says with what precision the *reference* was gauged, not
how closely the model must follow it; holding form to it means driving the model to the error of
the source.

**Batch formulas over the whole mesh are forbidden.** Scale, projection, a per-height correction
factor — these deform existing form without creating new form. You cannot get an oval from a
square by scaling, and the bounding measurements will agree anyway, because a square and an oval
have the same width and depth.

**Converging several rings at once is a batch operation in disguise.** It looks innocent: each
ring has its own target from the reference, vertices are placed one by one, no shared formula.
But the rings are corrected in a loop, through each other, and nobody looks between passes. The
result is the same as a formula: every ring's gauge agrees at once and the form between them has
been checked by no one. Proven expensively and repeatedly — converging six rings produced a
collar around a head; five produced a shelf on the hips; seven produced a waist on a neck. Every
time the measurements were in tolerance and a human found the defect much later.

Convergence is allowed **inside one step** — over the geometry the step's operation changed and
its immediate neighbours. *Sign of violation:* more than four rings in one convergence loop, or a
height range covering more than one form feature.

## Beat 4 — inspection, in detail

This beat is where the method earns its keep, and it is the beat most often executed wrongly.

### The mandatory frames

**Two orthographic views are not enough**, for two independent reasons.

- Without **the view from above**, a section's shape is invisible from every angle, and a box lives
  on undetected where an oval was intended.
- Without **an orbit**, ridges that stand edge-on to the orthographic cameras are invisible — a
  fold running down the outer arm shows in neither the front nor the side view.

And a third thing worth knowing before you go hunting: **a concavity is not recoverable from two
orthographic silhouettes at all, in principle.** It does not affect either outline, so two views
give you the convex hull at best. If the form you are chasing is a hollow, the information was
never in those two views — look for it in the reference's shading, or in a third view.

### Three separate looks, every time

| Look | What it judges | Channel |
|------|----------------|---------|
| **Surface** | Does the contour run as one continuous arc? Any straight insert that then breaks? Bulges, hollows, ripples? Does it sit on the reference? | smooth shading, reflective/striped matcap, silhouette fill |
| **Edge flow** | How the form is made: loop routing, poles, density gradient, the mirror seam | the cage drawn over the smoothed result |
| **Vertex placement** | Distribution along rings and along meridians, spikes, the seam | the cage plus the reflective channel |

A smooth surface can sit on a bad mesh and the reverse. A vertex-placement defect is invisible on
the surface entirely — it shows up later, at densification or deformation.

The reflective channel is not optional decoration: a curvature break shows there **at zero
positional error**, and essentially nowhere else. It is the single most-cited defect class in this
whole method.

### How to ask the inspection

The inspection returns exactly what it was asked about, so the wording of the request is part of
the check, not a preamble to it.

1. **Do not say what was just built or how it should read.** Saying it up front turns inspection
   into confirmation: the looker seeks the named thing, finds it, and stops. Name the zone by
   coordinates, not by meaning.
2. **Do not hand out indulgences in advance.** "Don't count this as a defect" closes exactly the
   zone the inspection was for. Known defects outside the operation's zone are filtered **after**
   the inspection, when findings are reviewed.
3. **Ask about the arc directly.** "Are there bumps and creases" is a question about position, and
   a curvature break answers "no". Ask instead: does the contour run as one continuous arc; is
   there a stretch where it is straight and then breaks; is there a band along which the character
   of the highlight changes.
4. **Attach the reference itself, and a close-up.** A defect a fraction of a millimetre deep is
   invisible on a frame where the part occupies a seventh of the height. And without the reference
   the looker judges against generic anatomy — that is, against a different task. Proven
   expensively: three consecutive rejections demanded a triceps, shoulder blades and an olecranon
   from a smooth shop-window mannequin that has none and must not — and one of those phantom
   findings was acted on, a 13.7 mm olecranon sculpted and then carved back off.

Corollary: **open the reference yourself before handing a zone to inspection.** Silhouette objects
in the scene and the markup are derivatives; they show neither the character of the surface nor
what is actually drawn on the reference.

*Violated if:* the request names what was built; an indulgence was granted; the arc question was
not asked; the zone was shown only in a wide shot; **the reference was not attached**.

### The fix loop is mandatory and unbounded

> operation → inspection in three looks → if bad, fix → inspection in three looks again → …

The loop does not end until the result is judged right. The number of passes is not fixed in
advance.

- Inspection runs **after every operation**, not after a series.
- A fix after a bad inspection leads to a **new inspection**, not to the next operation — even if
  the fix looks obvious and small.
- The result is judged right when **none of the three looks** names a defect in the affected zone.
- "The numbers are clean" is not grounds to close an operation.

## Hard gates

<HARD-GATE>
Do not perform an operation whose location can be found from a table of measurements, a plan, a
guide object, a zone or level number, or a fraction of the part's height. Rewrite the wording first.

Do not run beat 4 with fewer than four viewpoints — front, side, top, orbit — and fewer than four
surface channels — silhouette fill, smooth shading, the reflective channel, and the model drawn over
the reference — plus the cage over the smoothed result and a close-up of the zone. The canonical sets live in phases.md §11.1 and
§11.2. A contour's shape is read on the silhouette channel and on no other; whether it matches the art is
read on the model-over-reference overlay and on no other.

Do not send a zone to inspection without the reference attached.

Do not close a step on measurements, and do not close it on the inspection alone. All four must
hold: the fix loop has closed, meaning none of the three looks names a defect in the affected zone;
the form has been taken as far as this density allows; the operation's own check has passed; and any
remaining divergence is either inside the form tolerance assigned at M2 (measure-vs-eye.md §7) —
never the tighter measurement tolerance the reference was read with — or explained by density and
written into
the journal with its number.

Do not gauge off the cage. Take the reading from the final surface, with subdivision applied.

Do not run a convergence *loop* over more than four rings, or over a height range spanning more than
one form feature. This bans groping, not arithmetic: a closed-form solve — inverting the subdivision
stencil for a chain of rings whose targets the eye has already placed — is not a loop and is not
limited by ring count. What still bounds it is the step's scope: the chain solved is the geometry
this operation changed plus its immediate neighbours. Prefer a solve exactly because it does not
iterate.

Do not apply a formula — scale, projection, a per-height factor — over geometry the step's operation
did not change, and never let a formula originate a form. A computation may undo a transform whose
effect is known exactly; it may not decide where the form goes.

Do not begin a second form feature before the first is closed.

Do not make a cut that leaves an odd segment count on a ring crossing the plane of symmetry: an odd
ring has no vertex on the plane, the halves do not meet, and the flow skews.
</HARD-GATE>

## Traps that cost the most in practice

Each of these was hit, diagnosed and written down; the section reference says where the full
account lives.

- **A partial ring's bounding box is not the section's semi-axis** — [measure-vs-eye.md](references/measure-vs-eye.md) §5.13.
  Around an opening (armhole, leg opening) a ring holds only part of the section. Deriving an
  angular parameter or a semi-axis from `max(x)` over that ring throws vertices to the full width.
  This broke a mesh twice in one session — once blowing a ring from a 40 mm radius to 245 mm.
- **Select rings with `pp.rings()`, never by a coordinate range** — [blender.md](references/blender.md) §6.23a.
  The coordinate version holds until the first slanted loop, then silently takes the wrong vertices.
- **A convergence loop must compare against the reference, not against a target it moves itself** —
  [measure-vs-eye.md](references/measure-vs-eye.md) §5.11. A loop that corrects its own target
  converges to itself and reports success. Sign: the "worst" figure stops falling monotonically and
  starts wandering.
- **A stencil is inverted, not groped for** — [measure-vs-eye.md](references/measure-vs-eye.md) §5.11a.
  For a tube's ring, the limit surface equals `(prev + 4·current + next) / 6`. That is an equation:
  a chain of rings with known targets is a tridiagonal system, solved in one sweep. Groping at it
  pass by pass failed three times; the sweep landed seven rings at once, first try, to 0.9 mm.
  The targets came from the reference and the solve only undid the stencil — it originated no form,
  and being a solve rather than a loop, the four-ring gate does not bind it.
- **A push that does not move the surface means something else holds that height** —
  [measure-vs-eye.md](references/measure-vs-eye.md) §5.12. Not "push harder". Find which vertex is
  actually outermost there first. Four passes of pushing grew a spike the subdivision then ate,
  while the eye still saw it.
- **Cut a limb opening along the mesh's own lines** — [measure-vs-eye.md](references/measure-vs-eye.md) §5.10.
  Cutting along a drawn seam runs diagonally across the grid and makes a staircase — one pole per
  step. The same opening as a rectangle in (ring, column) coordinates gives exactly four poles, and
  they land where they belong. The drawn seam is decoration: it belongs in texture or a shallow
  groove, not in topology.
- **A supporting-loop pair made by accident** — [blender.md](references/blender.md) §6.32. Ring
  spacings of 25 mm, then 7.5, then 7.5 hold a hard crease. Read the ladder of spacings before
  blaming the shape.
- **Interpolate profiles shape-preservingly** — [measure-vs-eye.md](references/measure-vs-eye.md) §5.14.
  A natural cubic spline through sparse markup levels overshoots; it put a 158.5 mm half-width
  between neighbours of 139.5 and 143.3 and lumped a shoulder. Fritsch–Carlson (PCHIP) cannot.
- **Keep guides on for the working zone only** — [measure-vs-eye.md](references/measure-vs-eye.md) §6.
  All guides visible at once turns the markup into a permanently open table, and verification
  quietly becomes construction.

## Where to read next

Read the file that matches what you are about to do. Do not read all of them.

| File | Read it when |
|------|--------------|
| [step-cycle.md](references/step-cycle.md) | Running the cycle: the six beats in full, the fix loop, limits, rollback points, the step journal — and §2, who judges what, when the human is shown a stage rather than a step |
| [measure-vs-eye.md](references/measure-vs-eye.md) | Anything involving numbers: the whole of rule 5 and its sub-rules — boundary vs section, hidden surfaces, smoothing targets, creases, stencil inversion — plus §6 what markup may and may not be used for, and §§7–8 the full list of what is and is not settled before the first polygon |
| [work-rules.md](references/work-rules.md) | Starting a project: empty scene, polygon budget from purpose, one part per iteration, scene setup for the reference, per-part metrics, markup — how it is produced and handed off — and choosing the method |
| [phases.md](references/phases.md) | Planning a build, or standing at a phase boundary: M1–M6 including part acceptance and the joint contract, the operation catalogue, perception channels, the density test, budget exhaustion, input data changing mid-work |
| [blender.md](references/blender.md) | Working in Blender: how each operation maps to tools, the session toolkit, the executable two-pass inspection procedure, and 36 traps, 26 of them verified against the source |
| [rule-process.md](references/rule-process.md) | Writing a rule, changing one, or extending this skill to a work type it does not cover: the rule lifecycle and statuses, the sub-step cycle the other files refer to, what makes a rule checkable, and the template |
| `scripts/pp_blender.py` | The session toolkit — rings by connectivity, reference pixel measurement, frame scale, perception channels, orbit, topology counters. Import it once per session; it survives across calls. |
| `/model-review`, and the three inspector agents | Beat 4, already implemented: the command renders the mandatory frame set and dispatches `surface-inspector`, `edge-flow-inspector` and `vertex-inspector` with the reference attached |

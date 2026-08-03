# The step cycle

This file is the operating manual for the unit of work. It covers what the box modelling method is
and is not (§1), who judges what — the builder every step, the human every stage (§2), what counts
as a step and when a step is finished (§3), the six beats every step passes through, including the
mandatory unbounded fix loop and the pass limits (§4), rollback and rollback points (§13), and
the step journal (§14). Read it before running the cycle for the first time on a build, and again
whenever a step refuses to close. The rest of the source regulation lives in the other reference
files — §§5–8 in [measure-vs-eye.md](measure-vs-eye.md), §§9–12 and §§15–17 in
[phases.md](phases.md) — alongside the work-type rules R1–R8 in [work-rules.md](work-rules.md) and
the Blender mapping in [blender.md](blender.md); cross-references below point to them by name.

**Regulation.** Describes the logic of the build, the unit of work, the step cycle, the order of
phases and the rules of verification. It is not tied to any particular editor: there are no tool
names, buttons or modes here. How operations map onto the capabilities of a particular editor is
described in a separate **editor mapping document**:

| Editor | Document |
|--------|----------|
| Blender 5.1+ via the MCP server | [blender.md](blender.md) |

**Status:** `draft` — the regulation was assembled from sources and from a review of three failed
attempts and has been applied to a real build; no build has yet been carried through under it from
first setup to delivery. The statuses are defined in [rule-process.md](rule-process.md).

**Terms.** To *engage* a transform is to turn its effect on the geometry on, reversibly. To *bake*
it is to turn its result into the mesh itself, irreversibly. The distinction matters: almost the
whole build runs with transforms engaged and not baked.

---

## 1. What this method is

**What it does.** The shell is grown out of a simple form: volume by volume, edge by edge. Half of
the part is built, relative to the plane of symmetry; the form is judged on the smoothed surface
while the work goes on. Setup — see [phases.md](phases.md), §9, M1.

**When it applies.** When the method-choice rule selected it — **R8** in
[work-rules.md](work-rules.md); the same rule holds the signs on which the method is recommended,
and the alternatives that were rejected.

**What this method does not do.** It does not build form from a table of sections. Lofting a shell
through a set of rings gives a regular lattice: edge loops run across the form rather than along
it, poles land wherever they happen to, and the places where the surface folds back under itself
are not described at all. Measured markup justifies the bounding measurements, but it does not
generate form.

**How the method is carried out.** The unit of work is a **step** (§3). Steps run in a cycle (§4)
and add up to **stages**, which are presented to the human (§2).

---

## 2. Roles: who judges what

Take every step to the human and the work stalls; take nothing until the end and the error surfaces
when everything has to be redone.

### 2.1 The builder judges every step themselves

After **every** step the builder looks at the form with their own eyes: changes the viewpoint,
rotates the figure, switches perception channels (see [phases.md](phases.md), §11). They make the
decision "step closed / re-shape / roll back" themselves, and do not show the human intermediate
pictures.

Checking against orthographic views alone is **forbidden**: fixating on the three projections masks
errors visible only from an arbitrary angle, and form usually falls apart at three-quarter view.

### 2.2 The human judges stages

A **stage** is a set of steps after which the form has moved into a new quality, and after which
rolling back past that boundary would mean redoing the whole stage.

Acceptance follows **R3** (see [work-rules.md](work-rules.md)): the human says "accepted" or gives
corrections; corrections are a new pass over the same stage, not a move to the next one.

What is specific to this method:

- the unit of acceptance within a part is the **stage**;
- stage boundaries are assigned in the plan (see [phases.md](phases.md), M2, item 6) and **do not
  move as the work goes on**: a stage whose boundary was assigned after the fact is a report on
  what has already been done, not an acceptance;
- M3 is one stage; each of M4's three passes is a separate stage.

What the presentation contains — as a delta to R3: front, side and three-quarter views; the
wireframe over the smoothed surface; a report on divergences from the markup (how much to check —
see [phases.md](phases.md), §11.3); an actual polygon report against the part's share of the R2
range; the list of steps **from the journal** (§14).

### 2.3 What the builder does not do

- Does not ask the human about what they are obliged to see for themselves.
- Does not present as an achievement a step they have not inspected with rotation.
- Does not delegate the judgment of the quality of the form to numbers: numbers answer the question
  "did it agree", not "is it good".

---

## 3. The unit of work is the step

> **A step is one topological operation, plus the shaping of exactly the geometry whose composition
> that operation changed, taken to the state "cannot be done better at this density", and closed by
> a check.**

A **topological operation** is one that changes the composition of the mesh: continue the shell,
cut a loop, run a loop along a form line, close an end cap, collapse density, delete a region. The
full catalogue — see [phases.md](phases.md), §10.1. Two rows of that catalogue — setting up
mirroring and engaging subdivision — are marked as *not* steps: they touch no geometry, and beat 3
is not performed on them.

**What is not a step:**

| Not a step | Why | What it is instead |
|------------|-----|--------------------|
| Moving a vertex or a group of vertices | Does not change the composition of the mesh | The content of a step: inside one step vertices are moved as many times as you please |
| Flattening a section, bowing a surface inward, creating a surface turn | These are goals of shaping, not operations | Shaping tasks — see [phases.md](phases.md), §10.4 |
| A markup block (head, pelvis, chest) | Too coarse; several changes in the character of the form live inside it | 3–6 steps |
| A whole phase | This is a set of stages | See [phases.md](phases.md), §9 |

**When a step is finished.** The criterion is an event, not a count: a step is closed when the
geometry it affected looks as good as it can **at the current density**, from every viewpoint.

- **Too early to close:** the form still responds to the vertices you have.
- **Time to close, and possibly to add density next:** to move the form you have to work on an ever
  smaller region, and neighbouring areas get spoiled while you do.
- **A cancelling sign, observable only after density has been added:** the model has started to look
  lumpy — density was added prematurely; roll back per [phases.md](phases.md), §11.5.

These are the same three signs the density test turns on; it is stated once, for the decision to
add density, in [phases.md](phases.md), §11.4.

**There is no numeric norm of "so many operations between checks".** The only measure of frequency
confirmed by practice is time: come back to rotating the model every few minutes, even in the
middle of a step.

---

## 4. The step cycle

Every step passes through six beats. A beat may not be skipped **silently** and may not be
performed after the fact. Skipping is permitted only where the beat itself explicitly allows it,
and only with the reason noted in the journal.

**How this relates to the overall process.** The step is an internal unit of phases M3–M4. The
sub-step cycle of the surrounding process (studied → agreed → recorded → performed → checked;
defined in [rule-process.md](rule-process.md)) applies to phases M1–M6 as wholes; the six-beat
cycle applies to a step inside the "performed" state.

### Beat 1 — name

In one sentence: what we are doing and what it settles. The wording contains no numbers and does
not let the location be determined without looking at the reference (see
[measure-vs-eye.md](measure-vs-eye.md), §5).

Right: "continue the shell downward to the place where, on the reference's profile, the growth in
width stops."
Wrong: "continue the shell down to level 1041 and bring the ring out to 283 × 179."

### Beat 2 — perform the operation

Create the **step's rollback point** (§13), then perform exactly one topological operation.

### Beat 3 — shape

**The unit of shaping is the ring, not the mesh.** Vertices are placed one ring at a time, from the
top down: each vertex of the ring is assigned its own place, rather than a common law of
displacement. After a ring — an inspection (beat 4 in miniature, and over the same four mandatory viewpoints:
from the front, from the side, from above, by orbit — see [phases.md](phases.md), §11.1). Move on **only if the correction is right**; if it is not, the ring is placed again from
scratch.

**A batch formula over the whole mesh is forbidden** (A15). Scale, projection, a per-height
correction factor — all of these deform form that already exists without creating new form: scaling
will not get you an oval out of a square, and the bounding measurements will agree all the same,
because a square and an oval have the same width and depth. A formula is admissible in two cases only, and neither of them is giving form: where the formula
**is** the goal of the operation — a uniform thickening, say — and where it **inverts a transform
whose effect is known exactly**, putting the cage where the limit surface lands on a target the eye
already placed (see [measure-vs-eye.md](measure-vs-eye.md), §5.11a and §6). Never as a way to "give
it form".

Move the vertices only of the geometry **whose composition beat 2's operation changed**:

- for adding operations — the new geometry;
- for collapsing and deleting operations — the geometry left at the site of the operation, and its
  immediate neighbouring ring.

Everything beyond that region is a separate step with its own check.

**Converging several rings at once is a batch operation.** The move looks innocent: each ring has
its own target taken from the reference, the vertices are placed one by one, there is no shared
formula. But the rings are corrected in a loop, through one another, and between passes nobody
looks. The result is the same as with a formula: the bounding measurements of every ring agree at
once, and the form between them has been checked by no one.

Proven expensively, and more than once. Converging six rings at once produced a collar around the
whole head; converging five produced a shelf on the hips; converging seven produced a waist on a
neck. Every time all the measurements were in tolerance, and the defect was found by the human or
by a separate inspection much later.

**Rule:** convergence is admissible **inside one step**, that is, over the geometry whose
composition its operation changed, and that geometry's immediate neighbours. A loop that spans
several changes in the character of the form — the chest and the shoulder girdle, the neck and the
shoulder, the pelvis and the lower body — is forbidden. Between zones a closure of the step is
placed: an inspection, and only then the next zone.

**Sign of violation:** more than four rings in one convergence *loop*, or its height range covering
more than one form feature from the topology plan.

The sign is groping, not ring count. Where the relation between cage and limit surface is linear,
the chain is a tridiagonal system and is **solved** in one sweep rather than approached; a solve is
not a loop and the four-ring sign does not apply to it — see
[measure-vs-eye.md](measure-vs-eye.md), §5.11a.

### 3.1 One block at a time, and to a finish

The temptation is constant: several places where the form is wrong are visible at once, and the
hand reaches to correct them in a single pass. It must not be done, and the reason is not tidiness
but the way checking works.

An inspection answers the question "what is wrong **in this zone**". When three zones have been
changed in one pass, the inspection's finding cannot be tied to a cause: it is unclear which
correction produced it, and rollback loses its meaning — everything would have to be rolled back.
The fix loop (beat 4) stops converging, because every pass changes the conditions for the
neighbours.

**Rule:** one block is taken, brought to the state "cannot be done better at this density", closed
by an inspection — and only after that does the next one begin. A markup block (chest, pelvis,
shoulders) is by itself too coarse; within it, zones are separated out by form features, as in M2.

**Violated if:** correction of a second zone was begun before the first was closed; if one step in
the journal covers several form features; if after an inspection it is impossible to say which
correction produced the finding.

### Beat 4 — inspect

Mandatory: two orthographic views, **the view from above** and **an orbit**. Orthographic views are
not enough. The set of four is defined in [phases.md](phases.md), §11.1, and the perception channels
in §11.2 of the same file; that is where both live. How the set is executed against the server is
[blender.md](blender.md), §6, "Inspection in two passes".

Proven expensively, and it is the failure the whole method exists to prevent. A torso was built
whose front and side silhouettes both agreed with the reference to within 5 mm against a form
tolerance of 8 mm — every level in tolerance, on both orthographic views, for weeks. Seen from
above, the same torso was a flat slab: the back ran as a straight line meeting the sides at two
hard corners, and a longitudinal ridge ran its whole height. Two independent inspections named it
in one word — a box — and both said "rebuild, not repair".

Nothing was wrong with the measurements. They could not see it: a bounding box is identical for an
ellipse and for a rounded rectangle, so width and depth agree to the millimetre while one is an
oval and the other is a box. The top view had never been taken, because the numbers agreed.

**An inspection runs in two passes, and these are different checks.**

| Pass | What it looks at | With what |
|------|------------------|-----------|
| **Surface** | the form: **does the contour run as one continuous arc**, is there a break, a straight insert, bulges, hollows; does it sit on the reference | smooth shading, the reflective channel, silhouette fill, and the model drawn over the reference |
| **Mesh** | how the form is made: edge flow, vertex distribution, poles, the seam | the wireframe over the smoothed result |

**The eye judges the form. Measurement is a coarse guard of proportions, and nothing more.**

This is not a caveat but a division of authority, and the two must not be confused in either
direction:

- **measurement answers** the question "have the proportions drifted" — a part must not turn out
  twice as narrow or a hand's width lower. Its answer is coarse by nature: the bounding measurement
  of a section is the same for an ellipse and for a rounded rectangle, and the position of a point
  says nothing about how the surface arrived at it;
- **the eye answers** the question "is the form right" — and that is the only answer that counts.
  The figure is built by visual judgment, not fitted to a table.

Hence the rule that is worth more than all the others in this section: **"the numbers agree" is
neither an argument in an inspection nor an objection to its finding.** If the eye names a break and
measurement is silent, the eye is right, and the silence of measurement is a property of
measurement, not an excuse for the form. The converse also holds: a finding of the eye about
**size** is verified by measurement before the correction (see
[measure-vs-eye.md](measure-vs-eye.md), §5.4).

Proven expensively. The contour of a neck agreed with the reference to within two millimetres over
its whole height, and the surface was breaking all the same: the rate of change of width jumped by
a factor of seventeen in a single step at the transition into the head. Measurement could not see
this, by construction. The inspection should have seen it and did not — because it was not asked
about it (see below).

**How to put the question to an inspection.** An inspection returns exactly what it was asked
about, so the wording of the request is part of the check, not something that precedes it.

1. **Do not describe what has just been done and how it is supposed to read.** Saying it up front
   turns the inspection into a confirmation: the looker seeks the named thing, finds it, and stops
   there. The zone is named by coordinates, not by meaning: "the band from such-and-such height to
   such-and-such", not "the undercut that was built".
2. **Do not hand out indulgences in advance.** "Don't count this one as a defect" closes exactly
   the zone the inspection was set up for. Known defects outside the operation's zone are filtered
   out **after** the inspection, when the findings are reviewed, not before it.
3. **Ask about the arc directly.** "Are there bulges and kinks" is a question about position, and to
   a break in curvature it answers "no". What must be asked is: does the contour run as one
   continuous arc; is there a stretch where it is straight and then breaks; is there a band on the
   surface along which the character of the highlight changes.
4. **Provide the reference and a close-up.** A defect a fraction of a millimetre in size is visible
   to no one on a frame where the part occupies a seventh of the height. The operation's zone is
   captured separately and close up.

   **The reference itself is given, not a paraphrase.** Without it the looker judges against generic
   human anatomy — that is, against somebody else's task. Proven expensively: three inspections in a
   row demanded a triceps, shoulder blades, epicondyles and an olecranon from a blank, and three
   times wrote REJECTED for their absence. The reference turned out to be a photograph of a **smooth
   shop-window mannequin with parting lines**, which has none of that and must not. Some of the
   remarks were acted on — a 13.7 mm olecranon was sculpted — and that was an invention against the
   reference, which then had to be removed.

   From the same: **before handing a zone over for inspection, open the reference yourself.** The
   silhouette objects in the scene and the markup are derivatives; they show neither the character
   of the surface nor what is actually drawn on the reference.

**Violated if:** the request to the inspection names what was built; an indulgence was granted for a
zone; the arc question was not asked; the operation's zone was shown only in a wide shot; **the
reference was not attached**.

The passes do not substitute for each other: a bad mesh can carry a smooth surface, and the
reverse. A defect in the placement of vertices is not visible on the surface at all — it will show
up later, at densification or deformation.

**The mesh is harder to look at than the surface**, so it gets not one look but two, with different
questions: one about **edge flow and topology**, the other about **the placement of vertices and the
seam**. Each question is asked separately and explicitly — a general look of "how's the mesh" misses
both.

### The fix loop — mandatory and unbounded

> **operation → inspection in three looks → if bad, a fix → inspection in three looks again → …**
>
> The loop does not end until the result is judged right. The number of passes is not limited in
> advance.

Rules of the loop:

1. **Inspection follows every operation**, not a series of them. An operation without an inspection
   is not closed, and the next one may not be started.
2. **An inspection is three looks**: the surface, edge flow, the placement of vertices. All three,
   every time.
3. **Numbers do not replace an inspection.** Measurements and counters are an input to the
   inspection, not a verdict: they see neither a kink in a vault, nor a pole sitting on curvature,
   nor a crowding of vertices at a narrow end. "The numbers are clean" is not grounds to close an
   operation.
4. **A fix after a bad inspection leads to a new inspection**, not to the next operation. Even if
   the fix looks obvious and small.
5. **It is the builder who judges the result right**, but only when none of the three looks names a
   defect in the affected zone. Known defects outside the operation's zone do not hold the loop —
   they are written down and wait for their own operation.

**Violated if:** an operation was closed without an inspection; the inspection was done with one
look instead of three; the result was judged right because the numbers agreed; after a fix the loop
continued with the next operation without a repeat inspection.

### Beat 5 — verify

If the step touched a zone where markup measurements exist, take the bounding measurement **off the
final surface** (with subdivision engaged, not off the cage) and compare it with the nearest
measurement. One or two numbers, not a table.

The comparison is made against the **form tolerance** (see
[measure-vs-eye.md](measure-vs-eye.md), §7), not against the measurement tolerance: a measurement
says with what precision the reference was gauged, not how closely the model is obliged to follow
it.

The beat is skipped explicitly, with a note in the journal, in two cases: "there are no
measurements in this zone" and "surface turn" (see [phases.md](phases.md), M2, item 1a).

### Beat 6 — decide

One of four:

- **close the step** — the fix loop (beat 4) has closed: none of the three looks names a defect in
  the affected zone. The form has been taken as far as this density allows **and** the operation's
  own check has been passed (see [phases.md](phases.md), §10.1). The divergence from the
  measurement is then either within the **form tolerance** — the one set at M2, not the measurement
  tolerance the reference was read with (see [measure-vs-eye.md](measure-vs-eye.md), §7) — or
  **explained by density**: on a coarse mesh a section cannot
  coincide with the measurement, and to chase the coincidence is to drive the form to fit a number
  before its time. An explanation by density is written into the journal with the size of the
  divergence and is closed at the step where density grew; it cannot be left unaccounted for;
- **accept the divergence deliberately** — with the reason written into the journal; the procedure
  is in [measure-vs-eye.md](measure-vs-eye.md), §5.4;
- **re-shape** — return to beat 3; this is not a new step, but the number of returns is written into
  the journal and is limited (§4.1);
- **roll back** — the operation was the wrong one, or in the wrong place; roll back per §13.

The decision is the builder's.

### 4.1 Limits

The three limits — the number of returns to beat 3 within one step, the number of **passes** over a
stage, and the number of **repair passes** at M5 — are assigned by **a single decision at M2, item
7** (see [phases.md](phases.md)). This document sets no specific numbers: they belong to the task,
not to the method.

**Signs on which the limit counts as reached ahead of time:** corrections go back and forth;
improving one viewpoint breaks another; each successive correction is smaller than the last and the
picture does not change.

**Reaching the limit on a step** means the cause is not in the affected geometry, and gives three
ways out, in this order:

1. the density test fired (see [phases.md](phases.md), §11.4) — the step is closed and the next step
   adds density;
2. the neighbouring geometry is at fault — the step is rolled back, and a separate step on the
   neighbouring zone comes next;
3. neither one nor the other — roll back to the step that built the zone (see
   [phases.md](phases.md), §11.5).

**Reaching the limit on a stage's passes** means that what is wrong is not the stage but the
decision that preceded it: return to the previous accepted stage or to the topology plan, and
present the reason to the human.

---

## 13. Rollback and rollback points

- **A stage's rollback point** — at every accepted stage (M6).
- **A step's rollback point** — created at beat 2, before the operation is performed, and it lives
  until the next stage is closed. It also provides the "before" state for the checks that require
  one.
- You cannot repair the consequences without rolling back the cause: a correction laid on top of a
  wrong step makes rollback impossible.
- A rollback restores the point in full. The ban on selective rollback applies to hand-editing
  individual vertices, not to returning to a step's rollback point.
- A rollback is not a failure of the work but a regular beat of it (§4, beat 6).

---

## 14. The step journal

The journal is kept as the work goes on and is a **mandatory artefact of the phase**. Without it
three requirements of this regulation cannot be met: the list of steps at the gate (§2.2), the
return to the last step that touched a zone (see [phases.md](phases.md), §11.5), and the self-check
of wordings for numbers before acting (see [phases.md](phases.md), §16.B).

The entry is created at beat 6 of every step, **before the next one begins**, and contains:

- the step number and the stage;
- **the beat 1 wording, verbatim**;
- the operation, per the catalogue in [phases.md](phases.md), §10.1;
- the zone and the geometry the step affected;
- the result of beat 5 — the measurement and its number, or a note of an explicit skip with its
  reason;
- the beat 6 decision and the number of returns to beat 3;
- the name of the rollback point, if the step closed a stage;
- a note of any change of input data (see [phases.md](phases.md), §15.3).

**Violated if:** a step was closed without an entry; the stage's list of steps was assembled from
memory before the gate; the journal cannot answer which step touched a given zone.

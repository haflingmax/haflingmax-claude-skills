# Phases, operations and checks

This file covers the build itself: the six phases M1–M6 and what each one settles, the catalogue of
topological operations and how an operation must be worded, the checks that close a step, and what
happens when a whole phase or the polygon budget fails. Read it when you are planning a build or
standing at a phase boundary — not while you are inside a step; the step cycle, the limits, rollback
points and the journal live in [step-cycle.md](step-cycle.md); rule 5 and all its sub-rules, and
§§6–8 (markup, what is settled before the first polygon, what may not be settled in advance), in
[measure-vs-eye.md](measure-vs-eye.md); the project-level rules cited here as R2, R3, R5–R8 and A6
in [work-rules.md](work-rules.md); and the mapping from operations to a specific editor's tools in
[blender.md](blender.md). Two terms from the source's own glossary are used throughout: to *engage*
a transform is to turn its effect on the geometry on, reversibly; to *bake* it is to turn its result
into the mesh itself, irreversibly. Almost the whole build runs with transforms engaged and not
baked.

---

## 9. Build phases

| Phase | What it settles |
|-------|-----------------|
| M1 | **Setup** |
| M2 | **Topology plan** |
| M3 | **Blockout: volumes** |
| M4 | **Refinement: sections, concavities, density** |
| M5 | **Part acceptance** |
| M6 | **Saving and delivery** |

The phases run strictly in order.

**"In passes over the whole part" is a requirement on phases, not on steps.** Growing the shell
inside M3 goes volume by volume, but M3 does not count as passed until every zone has been brought
to the same level of large-scale form. What is forbidden is moving to fine form in one region before
the large form is in place everywhere: fine form built on a wrong large form is thrown away
entirely.

### M1 — Setup

**What it settles.** Brings the scene to a state in which building is possible. No geometry is
created here.

**Procedure.**

1. **Inspect the whole scene.** Stray objects left over from earlier attempts are presented as a
   list and deleted only after consent: they may look like working data while resting on stale
   numbers.
2. **Align the markup's axis of symmetry with the plane of symmetry.** If the axis from the markup
   is offset relative to the reference's centre, it is the **reference** that moves, not the model:
   the model has to be symmetric about zero, or mirroring and markup will diverge by the size of
   the offset across the whole part.
   Moving the reference is a change of placement under R5. After the move, the instrumental check
   of R5, item 8, is repeated, a new measurement is published, and the human confirms the placement
   again. Moving the reference silently after R5 has been accepted is forbidden.
3. **Fix the zero point in depth** — as a number. Without it there is nothing to compare depth
   measurements against.
4. **Check that the R5 report (§§4–8) has been published and confirmed by the human**, and that the
   placement has not changed since that confirmation. View consistency and its threshold are held
   in R5 and are not reassigned here.
5. **Build guides from the approved markup — one per measurement**, each showing width and depth at
   its own height, grouped by block.
   A guide belongs to a **measurement, not to a ring**: it fixes neither the number of rings nor
   their heights, and the correspondence "one measurement = one ring" is never established, at any
   phase.
   A guide must: (a) be visible in the working view; (b) carry no polygons and enter neither the
   delivery nor the polygon count (R2); (c) not be caught up by editing operations on the model.
   Guides made of geometry are forbidden — they land in the polygon count and in surface
   measurements. If geometry is the only carrier available, it lives in a separate set excluded
   from delivery and from the count, and locked against selection; the concrete object type comes
   from the editor-correspondence document ([blender.md](blender.md)).
   While building, only the guides of **the zone being worked on** are switched on; the rest are
   hidden.
6. **Overlay the guides on the references in both views.** A divergence larger than the measurement
   tolerance means that markup and reference describe different placement states: the divergence is
   presented to the human and building does not start. Moving the guides or the reference silently
   is forbidden.
7. **Set the properties of the transforms** — through requirements on the result, not through
   settings:
   - **Mirroring** must deliver two properties: (a) vertices lying on the plane of symmetry do not
     leave it; (b) the halves close into a single shell with no doubled vertices on the seam.
   - Mirroring acts on the geometry **before** subdivision: subdivision is computed over the closed
     symmetric shell, otherwise the seam is subdivided as if it were a border.
   - **Subdivision** is the approximating Catmull-Clark scheme. During work the low-density control
     cage is deformed while the subdivided surface is judged, and additionally (c) subdivision can
     be switched off at any moment without losing edits, and (d) the control cage is visible at the
     same time as the subdivided result.
   - The form is judged at **the same subdivision level that will go into the delivery**, never
     higher: a higher level masks a deficient cage. The value itself — L — is assigned at M2 from
     the delivery form, so what M1 records here is the principle plus the checkable property that
     follows from it: **the viewport level and the render level are equal**. The number is engaged
     at M3, together with the first volume.

   How these properties are provided — by an option, a mode, a node or an ordering of operations —
   is settled by the editor-correspondence document; the chosen means is recorded in the report.
   Subdivision itself is engaged at M3 in any case (§10.3, item 2). If the editor does not allow
   *mirroring* to be configured before any geometry exists either, that too is recorded in the
   report and engaged at the moment the first volume is created.
8. **Split the scene's contents** into three independently switchable and independently lockable
   sets: references, guides, model.
9. **Publish the report**: scene contents, position of the axis, the zero point in depth, the
   transform properties and the chosen means of providing them.
10. **Get the human's confirmation of the report.** Building does not start before confirmation.

**Done when:** stray objects have been removed; the axis is aligned and the placement re-confirmed
under R5; the zero point is set; guides are built one per measurement and overlaid on the reference
without divergence; mirroring is set up; the transform properties are recorded, including the
equality of the viewport and render subdivision levels; the report is published and confirmed.
Subdivision is **not** engaged here — its level is assigned at M2 and engaged at M3.
**Violated if:** something was deleted without presenting a list; the axis was aligned by moving the
model instead of the reference; the reference was moved without re-confirming R5; guides were built
one per ring; the guides of the whole part were switched on while building; guides were made of
geometry that lands in the count; building started without confirmation of the report.

### M2 — Topology plan

**What it settles.** The rules of the game for the whole build (see
[measure-vs-eye.md](measure-vs-eye.md), §7). No geometry is created here.

**Procedure.**

1. **Check whether the form is a function of height.** First and most important. For each height,
   look at how many surfaces the markup describes. If at even one height there are two, the part
   cannot be built as a stack of horizontal rings, and increasing their number will not help.
   Sign in the data: a measurement noticeably smaller than the silhouette in the same view at the
   same height, **and not explained by a neighbouring part caught in the silhouette**. Sign on the
   reference: the surface turns back on itself.
   **Failure branch:** a suspicion not confirmed on the reference does not count as a surface-turn
   zone.
1a. **If no stack-of-rings zones are left at all**, the part as a whole is not described by a set of
   horizontal sections. This is not a markup error. The consequences are declared before the
   blockout: beat 5 is skipped in these zones under the note "surface turn"; estimating the number
   of rings is replaced by an estimate from surface area and the required density; the zone's
   measurements go into the excluded list (item 7 of this same procedure); at M5 verification runs against the part boundaries
   and the overall bounding measurement.
   If no metric control is left at all, the part is presented to the human with the question of
   returning to R8: a form not described by bounding measurements is a direct indication in favour
   of sculpting.
   **Violated if:** the branch was not declared and verification quietly shrank to zero
   measurements.
2. **Split the part into zones by method of construction**, not by markup blocks: stack-of-rings
   zones; surface-turn zones; part boundaries.
   Zone boundaries are recorded as **a form feature on the reference** — where the surface turns;
   where the stack of rings ends; along the part boundary — **and not as heights**. A zone-boundary
   height, if it is recorded at all, is marked as a forecast for the budget and is forbidden in the
   wording of an operation.
3. **Assign the subdivision level L** (from the delivery form) and the **girth requirement**: at the
   most demanding section the final surface must carry no fewer than N faces around its girth, N
   from the calculation in R6, item 11. This is an acceptance criterion, verified by gauging the
   finished surface, and **not** a segment count assigned to the cage: segments arise from cuts, and cuts are
   not assigned in advance (see [measure-vs-eye.md](measure-vs-eye.md), §8).
4. **Estimate the polygon count — as a forecast, not as a quota.** The estimate is needed only to
   check the budget and is given as **one number per part**.
   It must be computed **from surface area and the required face size**, not by decomposing the mesh
   into rings and segments: arithmetic of the form "so many rings by so many segments" is a loft
   model, and once it is in the plan it reads as a build instruction. Face size follows from the
   girth requirement: the perimeter of the most demanding section divided by N.
   During the build nothing is checked against the forecast; a divergence of fact from forecast is
   not a violation. Only going outside the bounds of the R2 range is re-negotiated.
5. **Choose the policies**: **the delivery form** — the cage, or subdivision baked at level L —
   end-cap closing scheme, poles, density-transition scheme, hard edges, symmetry branch (§15.1).
   The delivery form is decided **here and recorded**, because item 3 above already consumes it to
   assign L, the hard-edge policy depends on it (edge creases are usable if the subdivision is baked
   before delivery **or** the interchange format carries creases), and M6 checks what it hands over
   against it.
   **Write down the parity requirement at the seam** in the same place, and as a constraint on
   operations — "a cut that produces an odd ring at the seam is forbidden" — never as a segment
   count. The check below looks for exactly this wording.
6. **Assign the stage boundaries** (see [step-cycle.md](step-cycle.md), §2.2).
7. **Assign the limits** (see [step-cycle.md](step-cycle.md), §4.1) and write out the **list of
   measurements excluded from the final verification**.
8. **Recompute the polygons from the plan and check them against the R2 range.** A plan that does
   not fit the range is not approved: it is the plan that gets fixed, not the budget.

**How to check.** By reading the plan, not by counting geometry — there is none yet. The parity
requirement at the seam is written down **as a constraint on operations** ("a cut that produces an
odd ring at the seam is forbidden"), not as a segment count; the forecast is inside the R2 range; no
zone has been left without an assigned method of construction; all policies are chosen; stage
boundaries and limits are named.

**Done when:** zones are marked out by form features, the delivery form and the level L that
follows from it are recorded, policies are assigned, the forecast fits the range, stage boundaries
and limits are named, the plan is approved.
**Violated if:** the function-of-height check was not performed; the delivery form was left
undecided while L was assigned anyway; the plan assigns a cage segment
count or a ring count as a decomposition of the mesh;
ring heights or section bounding measurements have appeared in the plan **in any form and under any
name** — forecast, reference figure, zone boundaries, guideline.
The only numbers admissible in the plan: the part boundaries, the part's overall bounding
measurement, the required number of faces around the girth at the most demanding section (N), the
subdivision level L, the bounds of the polygon range, the one-number-per-part polygon forecast of
item 4, and a total ring forecast not tied to heights.

### M3 — Blockout: volumes

**What it settles.** The large-scale form and the proportions of the whole part. The phase's
acceptance criterion is **silhouette and proportions**; mesh density and beauty of topology are
deliberately not a criterion at this phase.

**How it is run.** In steps, per [step-cycle.md](step-cycle.md), §§3–4. The typical order is §10.3.
The phase constitutes one stage.

**Done when:** subdivision has been engaged at the level L assigned at M2, with the viewport level
equal to the render level; zero open edges; all the large volumes are in place; the part is
recognisable from a silhouette fill alone; the overall bounding measurement is in tolerance; the
transforms are not baked; the stage has been accepted by the human.
**Violated if:** one region was taken to a finish while the rest lagged behind; the transforms were
baked; the actual polygon count is outside the R2 range; the blockout was run by markup blocks.

### M4 — Refinement: sections, concavities, density

**What it settles.** Everything that does not follow from two silhouettes.

**The unit of work within a pass is the same step** (see [step-cycle.md](step-cycle.md), §3): the
sections pass and the concavities pass are performed as steps whose topological operation produces
the carrying geometry; the form itself is built up by moving vertices inside that same step (§10.4).

**Three passes over the whole part, strictly in this order. Each pass is a separate stage.**

1. **The sections pass** — take the form away from a solid of revolution: flattenings wherever the
   section is not an ellipse. The source is the three-quarter view and volumetric perception, not
   measurements.
   Flattening displaces the section's extreme points, so after the pass the bounding measurement is
   restored **to the value gauged off this same model immediately before the flattening**, not to a
   measurement from the markup. Verification against the measurement is a separate beat 5, after
   the restoration. If the measurement still does not agree after restoration, that is a form
   divergence: it is fixed per [measure-vs-eye.md](measure-vs-eye.md), §5.2 or §5.4, not with an
   extra compensating shift.
2. **The concavities pass.** Two classes are kept apart: concavities that reach the silhouette line
   (checked in the corresponding view against the reference), and concavities that do not change the
   silhouette (checked only volumetrically and in three-quarter view; a change of silhouette after
   them is a sign that a bounding shift was made instead of a concavity).
3. **The density pass** — targeted cuts there and only there where the density test (§11.4) has
   fired, and collapsing where the density is excessive.

**Done when:** the three passes have been performed strictly in order and each accepted as a stage;
the bounding measurement has been restored and re-gauged after the sections pass; every cut has a
fired density test behind it; the form does not read as a solid of revolution when orbited.
**Violated if:** passes were mixed; a cut was made without a density test; the silhouette changed
after the pass of concavities that do not change the silhouette.

### M5 — Part acceptance

**What it settles.** Moving on to the next part.

**What is presented.** As in [step-cycle.md](step-cycle.md), §2.2, except that verification against
the markup runs over **all measurements**, not only the affected ones, and the joint contract is
added.

**The joint contract.** Together with the part's acceptance, a contract is published and filed with
the task for every joint: the plane or line of the boundary; the end cap's bounding measurement —
width and depth; the number of **cage** segments around the girth at the end cap — the built count,
not the girth requirement N, which is measured in faces on the final surface; the direction of
edge flow across the boundary; whether the parts are welded into a single mesh or stay separate. An
accepted part's contract is a mandatory input to the neighbour's M2.

**The joint check** is performed at the M5 of the second part of the pair: the end caps' bounding
measurements agree within the measurement tolerance; the cage segment counts agree; there is neither a
gap nor interpenetration in three views.
**Failure branch:** what gets fixed is the part being built now, not the one already accepted; if it
cannot be fixed, the accepted part is reopened by an explicit decision of the human.

**Decisions the human may take** when a divergence is presented: accept the divergence, entering the
measurement into the excluded list; order a rollback to the stage that built the zone plus a new
pass; change the tolerance, with a re-check of all previously accepted zones. Silence is not
acceptance.

**Done when:** the full verification has been performed; every divergence is either within
tolerance, or disputed per [measure-vs-eye.md](measure-vs-eye.md), §5.4, or accepted by the human;
the joint contract is published; for the second part of a pair, the joint check has passed.
**Violated if:** the repair pass limit was exhausted without presenting it to the human; a
divergence was quietly fudged away; a part was accepted without publishing the contract.

### M6 — Saving and delivery

A rollback point is created at **every accepted stage**, not only at the end of the phase. The
point's name names the stage.

**What leaves the phase — in the delivery form decided at M2** (see
[measure-vs-eye.md](measure-vs-eye.md), §7):

- **if the delivery form is the cage** — the part as a cage, transforms engaged but not baked;
- **if the delivery form is baked subdivision** — baked here, at level L, and not before: baking
  earlier takes away the ability to re-shape the proportions in one movement (§16.A). Baking is one
  of the two ways to make edge creases usable; the other is an interchange format that carries
  creases itself (see [measure-vs-eye.md](measure-vs-eye.md), §7). Creases are unfit only in the
  remaining case — an unsubdivided cage in a format without crease support.

Either way the phase also hands over: a polygon report taken **off the result of the transforms**,
never off the cage, checked against the part's share of the R2 range; measurements taken only off
the final surface; boundary contracts; rollback points; the step journal.

**Done when:** there is a rollback point at every accepted stage, the point's name names the stage,
what was handed over matches the delivery form decided at M2, and everything listed has been handed
over.
**Violated if:** there is one point per phase; the rollback is selective; the polygon report was
taken off the cage; the delivery form differs from the one decided at M2, or subdivision was baked
before this phase.

---

## 10. Operations

### 10.1 Catalogue of topological operations

| Operation | When it is used | Check afterwards | What it is not |
|-----------|-----------------|------------------|----------------|
| **Set up mirroring** (M1) | Before any geometry, as the first act of setup — not a step | Deferred: there is no geometry to check at M1, so the check falls due at the first step that creates any. Then — the seam closes with no gap and no ridge; no seam vertex leaves the plane; there are no doubled vertices on the seam | Not a bake: mirroring lives to M6 and leaves engaged, unless the delivery form decided at M2 says otherwise. Beat 3 is not performed — no geometry is affected |
| **Engage subdivision** (M3) | Together with the first volume, at the level L assigned at M2. Not at M1: L does not exist yet — M1 only records the principle and the checkable property that viewport level equals render level | The subdivided envelope, not the cage, sits inside the silhouette; viewport level equals render level and both equal L | Not a bake: from this moment every gauge is taken off the result. Beat 3 is not performed |
| **Create the primary volume** | Once, at the start, in the riskiest zone of the part (§10.3) | If the volume spans the whole part, its bounding measurement follows the part's overall bounding measurement ([measure-vs-eye.md](measure-vs-eye.md), §5.3). If the volume occupies a single zone, its bounding measurement is **not given as a number at all**: the volume is placed against the reference's silhouette in both views and corrected by eye. A zone's local bounding measurement never enters the operation's brief under any circumstances. Check: the volume is inscribed in its zone's contour in both views and nowhere goes outside it | Not an attempt at likeness: the task is to occupy the right place |
| **Cut the primary volume up to load-bearing density** | Once, immediately after the volume is created | Take it to the **minimum** density at which the zone carries its own large-scale curvature. The segment count is not assigned in advance: the criterion is the behaviour of the form, not a figure. Check: the subdivided envelope reads as a volume and not as a rounded box, **and** the density is the least of those at which that is so — removing one cut must spoil the form | Not stocking up on density for later |
| **Continue the shell** | The form continues in a new direction. The place is found **by eye on the reference** — where the character of the form changes | The nearest measurement is the nearest in height within half the distance to the next measurement; the bounding measurement is gauged off the final surface **at the measurement's own height**, not at the ring's height. If there is no measurement in that window, beat 5 is skipped explicitly. The transition has no crease and no pinch on the subdivided surface | Not "continue to level N": the height is a result, not a brief |
| **Run a loop along a form line** | The reference has a drawn or plainly readable line where the form breaks | The loop is continuous and nowhere ends in the middle of a surface: a broken-off end gives a pinch | Not a cut for the sake of density |
| **Close an end cap** | The shell has to become closed; at a part boundary | Zero open edges in the whole part; the end cap is made of quads only; the end cap coincides with the part boundary in both views. **Failure branch:** if open edges are found somewhere other than the cap being closed, that is not a failure of the current step: record where they are, close the current step, and open a separate repair step with a rollback to the step that built that zone | Not a plug put there "so that it's covered": an end cap is a joint with the neighbouring part |
| **Cut a loop** | Only when the density test (§11.4) has fired | The "before" state is taken from the step's rollback point (see [step-cycle.md](step-cycle.md), §13). An improvement means a change of silhouette or of surface flow visible **while orbiting, without switching to the cage**; if the difference is visible only on the cage, the cut is rolled back | Not preparation "for later" |
| **Collapse density** | Density is excessive in a zone with no curvature | Targeted removal of rings or edges, preserving the quad mesh and the edge flow; automatic decimation is forbidden — it produces triangles and arbitrary poles. The transition is done with the assigned scheme (see [measure-vs-eye.md](measure-vs-eye.md), §7); the transition's poles lie outside deformation zones, off the seam and off the part boundary. The zone's silhouette in three views and its smooth shading are unchanged compared with the step's rollback point; on any visible change the collapse is rolled back | Not optimisation for the sake of a number |
| **Delete a region** | When rolling back wrong topology inside a step, and when cutting out a zone for rebuilding | Zero open edges after the rebuild, or an explicitly recorded border due to be closed within the same stage. **Failure branch:** the border was still open at the end of the stage — the stage is not accepted | Not a way to lower the polygon count: "collapse density" is for that |

### 10.2 How an operation is worded

An operation is named by **an action and a location marker on the reference**, not by a coordinate
and not by a pointer into the plan:

- "continue the shell downward to the place where the profile stops widening";
- "run a loop along the drawn joint line";
- "cut a loop where the density test has fired".

Wrong wordings, both with numbers and without: "to level 1041"; "to a bounding measurement of
283 × 179"; "put rings at every level of the block"; "to the boundary of zone 3"; "to the end of the
pelvis block"; "at a third of the part's height"; "to the level of the second-to-last guide".

### 10.3 Typical blockout order

**An example of an order, not a quota**: there is no step count here; the set and the number are
determined by the form.

The list runs across a phase boundary on purpose — it shows the whole opening of work on a part in
one sequence. Items 1–2 are not blockout steps: item 1 carries out a decision taken at M1, item 2 engages the
level assigned at M2, and neither touches geometry, so beat 3 of the cycle is not performed on
them. Blockout proper — and the step cycle with it — begins at item 3.

**M1, carrying out the setup:**

1. Set up mirroring.

**M3, opening the blockout:**

2. Engage subdivision at the level L assigned at M2, viewport level equal to render level. Done at
   the moment the first volume is created, not before: at M1 the number does not yet exist.

**M3, blockout steps:**

3. Create the primary volume in the riskiest zone of the part.
4. Cut it up to load-bearing density.
5. Shape the large-scale form of the primary volume.
6. Run loops along the break lines readable on the reference.
7. Create the surface turns where there are any (§10.4).
8. Continue the shell from volume to volume, each time as a separate step, up to the last part
   boundary.
9. Close the end caps at the part boundaries.

Setup comes first, before any geometry: otherwise beat 5 cannot be performed — the final surface a
gauge is taken off does not exist yet.

The primary volume is created **in the riskiest zone** — where the form is hardest (surface turns,
branching of the shell): that zone gets settled while the mesh is still cheapest to redo.

### 10.4 Shaping tasks

These are **not topological operations** but goals of shaping (beat 3). The step is the topological
operation that produces geometry able to carry such a form — a loop cut, a continuation of the
shell, a loop along a form line; the form itself is built up by moving vertices inside that same
step.

| Task | When | Check |
|------|------|-------|
| **Create a surface turn** | Where the surface goes back under the form | A cutting plane at that height gives **two separate closed contours**, not one; the profile has a concavity rather than a straight transition. If the two contours have merged into one, there is no turn |
| **Flatten a section** | The sections pass at M4 | The form does not read as a solid of revolution when orbited; the bounding measurement has been restored to its pre-operation value and re-gauged (M4, §1) |
| **Bow the surface inward** | The concavities pass at M4 | By the class of the concavity (M4, §2) |

---

## 11. Checks

### 11.1 After every step

Two orthographic views, **the view from above** and **an orbit**. Mandatory, without exceptions.

Four viewpoints, not three. The top view is not an extra: without it the shape of a section is
invisible from every other angle, for the reason set out in 11.2 — a square and an oval of the same
width and depth give the same silhouette from the front and from the side. The orbit is not an
extra either: a ridge standing edge-on to both orthographic cameras appears in neither.

**This section is the home of the set.** [step-cycle.md](step-cycle.md), beat 4 states it and
[blender.md](blender.md) §6, "Inspection in two passes", says how to execute it; both follow this
section. If they ever disagree, this is the set.

### 11.2 Perception channels

It is not only the angle that has to change but the channel: one channel hides what another shows.

| Channel | What it shows |
|---------|---------------|
| Silhouette fill | Whether the part reads from a single contour |
| Smooth shading with a plain material | How the surface flows: tearing and bumps are visible only here |
| **Reflective channel** (a mirror or striped material, an environment reflection) | **Continuity of curvature.** A diffuse grey material shows the position of the surface and hides its character: a curvature break with zero positional error is not visible on it at all. On a reflective one it reads immediately — the reflected stripe breaks where the curvature breaks. Without this channel "a clean arc" cannot be verified |
| Wireframe over the smoothed result | What is being edited and what comes out of it — at the same time |
| **Close-up of the operation's zone** | A defect a fraction of a millimetre in size. In a wide shot the part occupies a small share of the frame, and such a defect is visible neither to a human nor to a review |
| Mirroring the image | A skew the eye has grown used to |
| **View from above and from below** | **The shape of the section.** Front, side and three-quarter views show the bounding measurement, not the section: a square and an oval of the same width and depth give the same silhouette. Without this channel a square section lives on unnoticed |
| Orbit around the part | A wrongly placed vertex is not visible from every angle |
| Three-quarter view against the same view of the reference | Everything that is not visible in the orthographic views |
| Comparison with the step's rollback point or with the previous accepted stage | Drift: slow degradation, imperceptible step by step |

### 11.3 Rhythm

- After every step, a short check (§11.1).
- Every few minutes, a forced orbit, even in the middle of a step.
- Metric verification after a step is against the nearest affected measurement only — one or two
  numbers.
- Full verification against all measurements happens only at stage gates. No more often than that:
  a table permanently in front of your eyes turns control into construction.
- An actual polygon report against the part's share of the R2 range, at every stage gate.

### 11.4 The density test

It is run before **adding density** — before a loop cut and before any other densification of an
already-built zone. It **does not apply** to continuing the shell, closing an end cap or running a
loop along a form line: those do not add density. The one exception is "cut the primary volume up to
load-bearing density": the test applies from the step at which there is something to judge.

- **Fired (before the operation):** to move the form you have to work on an ever smaller area, and
  the neighbouring regions get spoiled in the process.
- **Did not fire (before the operation):** the form still obeys the vertices already present.
- **Cancelling sign (after the operation):** the model has come to look lumpy — the cut was
  premature; roll back per §11.5.

The temptation to add density arrives earlier than the need for it does.

### 11.5 The failure branch

**Every check must have a failure branch.** A check with no instruction on what to do when it fails
is not a check but a report.

The general rule: a failed check returns you to **the last step that touched this geometry** — it is
found from the journal (see [step-cycle.md](step-cycle.md), §14) — and not to the beginning of the
phase and not to the previous step in sequence. The steps made after that point are replayed.

---

## 12. Phase-level and budget failures

### 12.1 Phase failure

A failed check returns you to a step. A phase failure is a different event: a phase's result is not
fixed by steps inside it.

| Phase | Failed if | Return to |
|-------|-----------|-----------|
| M2 | the forecast does not fit the range under any plan | R2 / R8 |
| M3 | after a pass over the whole part the silhouette does not read from a single fill, or the proportions do not agree with the overall bounding measurement | M2 or R8 |
| M4 | placing a section or a concavity requires moving the bounding measurement — that is, refinement has run up against the large-scale form | all of M3 |
| M5 | the repair pass limit is exhausted | by the human's decision |

The builder declares a phase failure, the human takes the decision to return; it is always
presented. Fixing a phase failure with edits inside that phase is forbidden — that is hidden
degradation (A6).

### 12.2 Budget exhaustion

The actual polygon count is checked against the part's share of the R2 range at every stage gate,
not only in the plan. If the upper bound is reached before the phase closes:

1. **adding density stops immediately** — a fired §11.4 test no longer confers the right to a cut;
2. **slack is looked for inside the part**: collapsing in zones with no curvature; replacing
   supporting loops with creases wherever the delivery form allows it; removing poles that carry no
   form;
3. **there is no slack** — the human is presented with a choice of three, each with its price: raise
   the bound (re-negotiating R2); simplify a named zone according to the priorities of the R2
   questionnaire; change the method (returning to R8);
4. the choice is recorded in the task and in the journal.

**Forbidden:** exceeding the bound "temporarily" with a plan to optimise later; making up polygons
out of another part's share without agreement.
**Violated if:** a stage gate was presented without an actual report against the range.

---

## 15. Special cases

### 15.1 Parts with no plane of symmetry

The branch is chosen at M2 and recorded in the task.

1. **The part is symmetric about its own plane** — the base branch, unchanged.
2. **The part is one of a pair** (left and right): one is built, the second is obtained by mirroring
   the already-accepted one and is accepted as a separate iteration under R3. No mirroring is
   engaged inside the part itself; the requirement of even segment counts is dropped — its
   justification lies in the seam, and there is no seam; the seam check is replaced by a joint check
   of both parts against the neighbour, per the boundary contract.
3. **The part is asymmetric**: no mirroring is set up, parity is dropped, and the M1 report says
   "no mirroring" with the branch named; the markup's plane of symmetry remains the datum for
   measurements.

For (2) and (3): the reference's measured asymmetry (R6, item 7) is not carried into the model.
**Violated if:** the branch was not assigned at M2 and the absence of mirroring came to light during
the blockout.

### 15.2 Second and later parts

**Reused without repeating** (confirmed by a short report, "the scene has not changed"): the state
of the scene and the placement of the references (R5); the axis and the zero point in depth; the
transform properties; the pole policy; the end-cap closing scheme; the delivery form and the
hard-edge policy; the set of views and channels.

**Done afresh for every part:** the markup (R6/R7); the guides built from it; the "form is a function
of height" check; the build zones; the stage boundaries; the limits; the polygon forecast against
this part's share of the range; the rollback points.

**Inherited as a contract from accepted neighbours:** the position of the boundary; the section's
bounding measurement at the boundary; the number of segments at the joint; the direction of edge
flow across the joint.

The segment count changes only where the part does not join an already-accepted one. Changing the
policy for poles, end caps or edges after the first accepted part means re-accepting every accepted
part, and is declared to the human explicitly.

### 15.3 Input data changing mid-work

Any change of input is declared explicitly and classified before work continues.

| What changed | What happens |
|--------------|--------------|
| The reference, its normalisation or its placement (R5) | M1 is repeated in full; every part already built is re-verified; work does not continue until the human decides the fate of what has been accepted |
| The current part's markup | The form is not redone automatically: the guides are rebuilt, a full verification is run as at a gate, and divergences are handled per [measure-vs-eye.md](measure-vs-eye.md), §5.2/§5.4. Accepted stages are not reopened if verification is within tolerance |
| The part boundaries | This is a change of contract: return to M2 and re-accept the joints |
| The polygon range (R2) | The M2 forecast is recomputed, then proceed per §12.2 |

A note of the input change goes into the journal, with the date and the version of the input file.
**Violated if:** a step was continued on new numbers without a note.

---

## 16. What the regulation is based on

### 16.A From sources

**Order: large-scale form before refinement.** Practice is unanimous: first the main volumes and the
silhouette of the **whole** part are roughed in, and only then is the form refined. The goal of the
blockout is proportions, not surface. Hence: the blockout builds the part as a whole; a markup block
is not a unit of blockout.

**Topology is settled before any geometry.** The main loops are laid down first — around deformation
zones and along the boundaries of forms — and only then are the gaps filled with quads. Hence: the
topology plan comes **before** the blockout.

**Topology rules.**

- Quads are the basis for organics. **N-gons are forbidden everywhere (R2)**: they give
  unpredictable shading and triangulation, and in deformable zones they also tear the edge flow.
  Triangles are admissible only in closed zones where they do not break edge loops.
- Poles are unavoidable and are needed for changing the direction of flows. They go in flat places
  without deformation. The curvature rule: if a pole changes the curvature of the surface, it has to
  go.
- Loops at joints cross the axis of bending at a right angle.
- Transitions between a dense zone and a sparse one are made with the assigned schemes (see
  [measure-vs-eye.md](measure-vs-eye.md), §7), not with ones invented on the spot.

**The unit of work and the rhythm.** The end-of-step criterion is event-based. Add new geometry only
when the current level physically cannot carry the required curvature. There is no formalised metric
of "N operations between checks" in any source; the only numeric frequency that occurs anywhere is
to rotate the model every few minutes. The worst habit is bringing a form to a finish from one angle
and discovering a catastrophe on turning it.

**The limits of two orthographic views are proven, not a consequence of carelessness.** A width ×
depth pair specifies at most an ellipse: one class of shape for the whole section. Concavities
cannot be recovered from silhouettes **in principle**: a concavity does not affect the silhouette;
two views give a convex hull, no more. Surface turns are structurally inaccessible to horizontal
sections.
Hence: a third source has to enter the model — volumetric perception and the three-quarter view.

**The order of the transforms.** Mirroring is set up in the setup, before any geometry — it is an
act of M1, not a step: set up after the blockout, it requires redoing everything asymmetric.
Mirroring acts **before** subdivision, otherwise the seam is subdivided as a border. Subdivision is
engaged at M3 and, if the delivery form calls for baking at all, is not baked before **M6**: once
baked, it takes away the ability to re-shape the proportions in a single movement. A gauge taken off the cage
is invalid under an approximating scheme.

**An alternative rejected deliberately.** Ready-made base meshes of the human figure exist under a
free licence, with clean quad topology and closed volumes; in production this is the most common
starting point. The decision to build our own was taken when the method was chosen (R8); the
alternative is on record as a way out if schedule becomes more important.

### 16.B From practice

**The "form is a function of height" check pays for itself immediately.** On the very first part it
found a zone where two surfaces live at one height, and explained why earlier attempts to build from
sections had failed: they were solving a problem that has no solution in that zone. The check takes
one pass over the data and is done **before** any building.

The other side of it: the sign "the measurement is narrower than the silhouette" produces false
positives. Below the shoulders the silhouette includes the arms, and the torso is legitimately
narrower than it. The sign works only where the silhouette belongs to the same part — and the
suspicion has to be confirmed on the reference.

**The method comes back in disguise.** Building from a table of sections came back three times in a
row, each time in a new guise: as a method, as a plan, as a list of operations with numbers inside
their wording. No ban on a guise ever protected against the next one. The only things that did
protect were the ordering rule (see [measure-vs-eye.md](measure-vs-eye.md), §5) and presenting the
plan to the human before executing it.

**A consequence for auditing the regulation:** re-read the wordings from the journal and strike out
every one in which the location of the operation can be determined without a look at the reference.
As a separate check, deliberately.

**A check with no failure branch is not a check.** In a procedure assembled from a hundred and three
sources, exactly one check out of twenty-eight had a failure branch. Until you demand it explicitly,
it will not be there.

---

## 17. Sources

The review covered 103 sources: official documentation of editors and subdivision algorithms,
topology references, production breakdowns, courses and tutorials on figure modelling, and work on
recovering form from silhouettes.

- [(CG Cookie Workshop: Mastering Mesh Modeling, Jonathan Williamson — course programme)](http://cgc-workshops.s3.amazonaws.com/mastering_modeling_blender/workshop_master-modeling.pdf)
- <http://sig.biostr.washington.edu/projects/bodygen/developement/thesis.htm>
- <http://wiki.polycount.com/wiki/Character_Modeling>
- <http://wiki.polycount.com/wiki/Subdivision_Surface_Modeling>
- [Hippydrome (reference chart of facial topology; the front page is navigation only, the detailed charts are in the sections)](http://www.hippydrome.com/)
- <http://www.makehumancommunity.org/wiki/Documentation:Targets>
- [Neil Blevins, "Primary, Secondary and Tertiary Shapes" (the original source of the concept; direct access to the page failed, the content is known from the CG Cookie link and from search results)](http://www.neilblevins.com/art_lessons/composition_primary_secondary_and_tertiary_shapes/composition_primary_secondary_and_tertiary_shapes.htm)
- <https://3dtotal.com/tutorials/t/joan-arc-modeling-the-body-michel-roger-character-arc>
- [80.lv, Hard-Surface Prop Production For Games (PureRef, blockout: silhouette and proportions before moving on)](https://80.lv/articles/001agt-002mrs-004adk-hard-surface-prop-production-for-games)
- [80.lv, Emil Skriver: blocking out large forms, the side view, checking from all angles, clusters of detail](https://80.lv/articles/010md-hard-surface-modeling-game-art-tips-from-emil-skriver)
- [80.lv, Juan Hernandez, "5 Rules of 3D Modeling" (rule 2: never start with details, go from the general to the particular)](https://80.lv/articles/5-rules-of-3d-modeling)
- [80.lv, stylised portraits: three-quarter angles, coming back with a fresh eye, comparing yesterday against today](https://80.lv/articles/sculpting-two-expressive-stylized-female-portraits)
- <https://animost.com/tutorials/box-modeling-guide/>
- <https://apps.dtic.mil/sti/tr/pdf/AD0608463.pdf>
- <https://arxiv.org/abs/2409.00829>
- <https://blenderartists.org/t/guidance-on-base-mesh/1544567>
- [Blender Artists, "How to smoothly connect his head to its torso?"](https://blenderartists.org/t/how-to-smoothly-connect-his-head-to-its-torso/1492103)
- [AnimSchool Blog, "3D Head Modeling Topology & Techniques"](https://blog.animschool.edu/2024/04/27/3d-head-modeling-topology-techniques/)
- [The Level Design Book, Blockout](https://book.leveldesignbook.com/process/blockout)
- <https://cgcookie.com/community/7315-character-modeling-is-there-a-default-order-to-create-a-3d-body-mesh>
- [CG Cookie, "6 Principles of Great 3D Modeling in Blender" (form → passes → reference/scale → surface quality)](https://cgcookie.com/posts/6-principles-of-great-3d-modeling)
- [CG Cookie, "The Art of Good Topology" (403 on a direct request; quoted via the search index)](https://cgcookie.com/posts/the-art-of-good-topology-blender)
- [University of Washington CSE458, "Project 2: Head Modeling" (the page is now behind a UW NetID login; the text was obtained via the search index)](https://courses.cs.washington.edu/courses/cse458/14au/content/projects/project2/)
- <https://dl.acm.org/doi/abs/10.1145/882262.882311>
- [Autodesk Softimage, "Modeling the Head" (Face Robot requirements)](https://download.autodesk.com/global/docs/softimage2012/en_US/userguide/files/face_modeling_ModelingtheHead.htm)
- <https://download.autodesk.com/us/3dsmax/2012help/files/GUID-1456D1B2-7B31-4894-AC2C-A2F60660C92-497.htm>
- <https://en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro/Modeling_a_Human_Character_-_Modeling>
- <https://en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro/Modeling_a_Simple_Person>
- <https://en.wikipedia.org/wiki/Box_modeling>
- <https://en.wikipedia.org/wiki/Lofting>
- <https://en.wikipedia.org/wiki/Lofting_coordinates>
- <https://en.wikipedia.org/wiki/Star_domain>
- <https://figshare.com/articles/journal_contribution/The_simulation_of_aerial_movement_II_A_mathematical_inertia_model_of_the_human_body/9624596/1/files/17273201.pdf>
- <https://flylib.com/books/en/2.770.1.20/1/>
- <https://flylib.com/books/en/2.770.1.22/1/>
- <https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/AV0809/schneider.pdf>
- <https://iconscout.com/blog/how-to-model-a-3d-human-in-blender>
- <https://idoc.pub/documents/joan-of-arc-3dmax-tutorial-od4po893yrlp>
- <https://knowledge.autodesk.com/support/3ds-max/getting-started/caas/CloudHelp/cloudhelp/2023/ENU/3DSMax-Modifiers/files/GUID-1456D1B2-7B31-4894-AC2C-A2F60660C922-htm.html>
- <https://labs.cs.queensu.ca/perklab/wp-content/uploads/sites/3/2024/02/Sunderland2015-manuscript.pdf>
- [Lance A. Glasser, "50 Rules for Figurative Sculpture" (walk around the model, use a mirror and photographs, from large to small, part → return to the whole, eyes last)](https://lanceglasser.com/50-rules-for-figurative-sculpture/)
- <https://link.springer.com/chapter/10.1007/978-3-540-79246-8_39>
- <https://link.springer.com/chapter/10.1007/978-3-642-02345-3_12>
- <https://link.springer.com/chapter/10.1007/978-3-642-54212-1_5>
- [Jake Palandri, "Facial Topology Construction"](https://medium.com/@jakepalandri/facial-topology-construction-5ae720e094e1)
- <https://medium.com/universe-factory/digital-character-modelling-2-making-the-basic-body-94b23b2bbea2>
- [Nasty Rodent, art-direction playbook: the silhouette acceptance test as a hard gate between stages](https://nastyrodent.com/stylized-3d-characters-art-direction-principles/)
- [Novedge, tying subdivision levels to the scale of the form](https://novedge.com/blogs/design-news/zbrush-tip-efficient-subdivision-level-management-in-zbrush)
- [Novedge, Progressive Subdivision Sculpting Workflow (one level at a time, short up-and-down cycles, the brush as an indicator)](https://novedge.com/blogs/design-news/zbrush-tip-progressive-subdivision-sculpting-workflow)
- <https://pmc.ncbi.nlm.nih.gov/articles/PMC2390921/>
- <https://pmc.ncbi.nlm.nih.gov/articles/PMC4329601/>
- [Polycount, "Neck Topology; Option A or B?" (blocked by Cloudflare; quoted via the search index)](https://polycount.com/discussion/216166/neck-topology-option-a-or-b)
- [Polycount thread on primary/secondary/tertiary (access blocked by Cloudflare, only search snippets used)](https://polycount.com/discussion/233026/sculpting-issue-primary-secondary-and-tertiary-shapes)
- <https://polycount.com/discussion/237289/human-basemesh-topology>
- <https://polycount.com/discussion/63686/spline-modeling>
- <https://polycount.com/discussion/80005/face-topology-breakdown-guide>
- <https://pubmed.ncbi.nlm.nih.gov/14243640/>
- [Sketchfab Community Blog, a silhouette workflow for a game asset (the silhouette as the basis of the base mesh)](https://sketchfab.com/blogs/community/a-silhouette-workflow-for-game-asset-modeling/)
- <https://static.makehumancommunity.org/about/concepts/basemesh.html>
- <https://static.makehumancommunity.org/makehuman/docs/professional_mesh_topology.html>
- <https://studio.blender.org/training/blenderella/>
- <https://studio.blender.org/training/blenderella/chapter/56040ecf044a2a00a515adcd/>
- <https://studio.blender.org/training/realistic-human-research/use-of-base-meshes/>
- <https://studio.blender.org/training/stylized-character-workflow/chapter/5d384eb4a5b8f5c2c32c8505/>
- [Autodesk 3ds Max Help, "Refining the Head and Neck"](https://techshelps.github.io/3dsmax_t/WSf742dab041063133-62b9306f112a19e40dd-7fc6.htm)
- <https://thundercloud-studio.com/article/guide-to-3d-face-modeling-topology/>
- [Thunder Cloud Studio, "Modeling guide to face topology" (403 on a direct request; quoted via the search index)](https://thundercloudstudio.artstation.com/blog/AgRyn/modeling-guide-to-face-topology)
- <https://tohawork.com/en/zeromodelling>
- [UMBC ART 484, "Block Modeling a Polygonal Head"](https://userpages.umbc.edu/~bailey/Courses/Tutorials/ModelPolyHead/ModelPolyHead.html)
- [Vitez, "Clean Face Topology"](https://vitez.me/face-topology)
- <https://vsquad.art/blog/modeling-guide-to-achieving-good-face-topology>
- [VSQUAD, Face Topology Guide: How to Model a Head for Animation](https://vsquad.art/blog/modeling-guide-to-achieving-good-face-topology)
- [Scott Spencer, "ZBrush Character Creation", the chapter Form and Details (stages of increasing complexity; form matters more than details) — accessible only through search results, the page returned a connection error](https://what-when-how.com/zbrush-character-creation-advanced-digital-sculpting/form-and-details-zbrush-for-detailing-zbrush-character-creation/)
- <https://www.aircorpsaviation.com/loft-contour-layout-lines-ordinates/>
- <https://www.animares.com/_book/Modeling/Patches/Spline-Patch-Modeling.html>
- <https://www.blenderbasecamp.com/box-modelling-basics-start-in-blender/>
- <https://www.cambridge.org/core/books/abs/forensic-facial-reconstruction/facial-tissue-depth-measurement/4B6C7251ECE7FB76892ABCD8BFDE9912>
- <https://www.centricsoftware.com/press-releases/integration-between-alvanon-3d-avatars-and-centric-plm-will-streamline-more-realistic-and-accurate-3d-design/>
- <https://www.eecs.harvard.edu/~sjg/papers/ibvh.pdf>
- <https://www.emerald.com/insight/content/doi/10.1108/09556220910983795/full/html>
- <https://www.emergentmind.com/topics/smpl-mesh>
- <https://www.futurelearn.com/info/courses/forensic-facial-reconstruction/0/steps/31185>
- <https://www.highend3d.com/maya/tutorials/modeling/nurbs/c/how-to-patchmodel-a-head-in-maya>
- <https://www.highend3d.com/maya/tutorials/modeling/nurbs/c/modeling-a-nurbs-head-general-concept-tutorial>
- <https://www.onlinedesignteacher.com/2019/01/low-poly-character-modelling-part-1.html>
- [(Oliver Villar, Learning Blender: A Hands-On Guide — Modeling the Basic Shapes for the Torso and Arms)](https://www.oreilly.com/library/view/learning-blender-a/9780133886283/ch07lev2sec15.html)
- <https://www.packtpub.com/en-us/learning/how-to-tutorials/blender-25-modeling-basic-humanoid-character>
- <https://www.researchgate.net/publication/235285062_A_mannequin_modeling_method_based_on_section_templates_and_silhouette_control>
- <https://www.researchgate.net/publication/3192242_The_Visual_Hull_Concept_for_Silhouette-Based_Image_Understanding>
- [RMCAD, Environment Artist Playbook: the blockout as the first pass, mistakes are cheap at blockout](https://www.rmcad.edu/blog/environment-artist-playbook-from-blockout-to-final-pass/)
- <https://www.sciencedirect.com/science/article/abs/pii/002192909090370I>
- <https://www.sciencedirect.com/science/article/abs/pii/S0010448504000776>
- <https://www.sciencedirect.com/science/article/abs/pii/S0169814109000584>
- <https://www.sciencedirect.com/science/article/pii/S2351978915008859>
- <https://www.scitepress.org/papers/2007/20503/20503.pdf>
- [Sculpture Atelier, "5 Tips to Improve Your Figure Sculpting" (turn it every few minutes; the worst habit is a single angle)](https://www.sculptureatelier.com/blog/5-tips-improve-sculpting)
- [Sergi Caballer, "3D Facial Modeling Timelapse" (404 on a direct request; quoted via the search index)](https://www.sergicaballer.com/3d-facial-modeling-timelapse/)
- [Francesco Furneri, "3D Modeling Part 3: Big Shapes and Tiny Details" (main/secondary/tertiary/micro, gates before subdividing, checking with a shader)](https://www.shutterstock.com/blog/3d-modeling-shapes-and-details)
- <https://www.strayspark.studio/blog/how-to-make-a-3d-character-in-blender-2026>
- <https://www.theinterline.com/tech-hub/alvanon/>
- [Tripo3D, "Smart Mesh Facial Topology Loops: A Practical Guide"](https://www.tripo3d.ai/blog/explore/smart-mesh-facial-topology-loops-basics)
- [Wacom, three common mistakes in 3D modelling (keep the reference to hand)](https://www.wacom.com/en-us/discover/3d-game/common-3d-modeling-mistakes)
- [World of Level Design, methods for moving from blockout to detail](https://www.worldofleveldesign.com/categories/newsletter/2026-02-blockouts-to-detail-methods.php)

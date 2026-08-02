# Work rules: building a 3D character from 2D reference art

This file is the work-type layer of the method: the eight rules R1–R8 that govern a project from
an empty scene up to the moment building begins — empty scene, polygon budget derived from purpose
and reference, one part per iteration, the first part as the model's base, scene setup for the
reference, per-part metrics before building, markup as tool and hand-off, choosing the build
method — followed by the failure modes those rules exist to prevent, the queue of rules still under
discussion, and the change log. Read it when a project starts or when you pick up a new part:
before the scene is set up, before the polygon range is agreed, before the first part is chosen and
measured. Once building has actually begun, the step-by-step discipline lives in
[step-cycle.md](step-cycle.md), [measure-vs-eye.md](measure-vs-eye.md), [phases.md](phases.md) and
[blender.md](blender.md).

**Work type:** modelling characters and mannequins for games and 3D applications from a
two-dimensional reference (concept art, photograph, orthographic views).

**Scope:** any task of this type. The rules are stated **generally** — they are not tailored to a
particular model. Everything that belongs to one specific model (its list of parts, its
proportions, its budget in numbers) lives in the task, not here.

The process for working with the rules themselves — their lifecycle, statuses, the requirements on
how a rule is worded, the template for a new rule — is common to the whole rule set and is not
reproduced here.

---

## 1. Rules in force

### R1 — Modelling starts from an empty scene

**Status:** `approved` — verified in practice 2026-07-30, wording refined from the results of that
trial (see "What the trial found").

**Statement.**
Any modelling work starts from an empty scene. If there is no scene — create one. If a scene
exists — clear it, **but only after the user confirms**.
Exactly two utility objects always remain in the scene: **one camera and one light** — they are
needed for the renders used in visual checking. If they are missing — create them. If there is
more than one — delete the extras.

**Why.** Leftovers from earlier attempts contaminate the result silently: helper primitives get
into measurements, hidden objects distort bounding measurements, a name collision points the next
script at somebody else's mesh, orphan datablocks drag old modifiers and materials along with
them. A clean start is the only condition under which an iteration is reproducible.
Deleting without confirmation is forbidden separately: the scene may hold work the user had no
intention of losing.
The camera and the light are pinned to exactly one copy each for the same reason: two cameras or
two lights give two different images of the same geometry, and iterations can no longer be
compared with each other.

**What counts as an empty scene.** No geometry, no orphan datablocks, no leftover empty
collections. Exactly one camera (set as active) and exactly one light. Blender's default startup
cube is junk and gets deleted. The camera and the light are not an inheritance from previous work
but a working instrument: their parameters are chosen deliberately and stated out loud when they
are created.

**Procedure.**
1. **Inspect the scene first.** Never assume it is empty.
2. No geometry, one camera and one light — carry on working.
3. Something extra is there — present the user with the list of what will be deleted (objects,
   collections, orphan datablocks) and ask for confirmation. Without confirmation, delete nothing.
   **Exception:** an untouched editor startup file — no unsaved changes (`is_dirty == False`), no
   file path, and its contents match the defaults. Such a file is cleaned without asking: there is
   nothing in it to lose, and asking on every launch is a wasted step. The inventory is still
   published.
4. After confirmation — delete the objects, then the orphan datablocks (**several passes**:
   deleting a mesh frees its material), then the empty collections.
5. Bring the utility objects to norm: one camera (set active in the scene), one light. Create the
   missing ones, delete the extras. State the parameters of anything created out loud.
6. Publish a report on the state of the scene **before** the first modelling operation.

**How to check** — inspection (read-only):

```python
import bpy

GEOMETRY = {"MESH", "CURVE", "SURFACE", "META", "FONT", "GPENCIL"}

def block(coll):
    return {"total": len(coll), "orphans": [d.name for d in coll if d.users == 0]}

by_type = {}
for o in bpy.data.objects:
    by_type[o.type] = by_type.get(o.type, 0) + 1

result = {
    "file": bpy.data.filepath or "<не сохранён>",   # "<не сохранён>" = not saved
    "blender_version": bpy.app.version_string,
    "is_dirty": bpy.data.is_dirty,
    "objects": [
        {"name": o.name, "type": o.type, "hide_viewport": o.hide_viewport}
        for o in bpy.data.objects
    ],
    "counts_by_type": by_type,
    "geometry_objects": sum(n for t, n in by_type.items() if t in GEOMETRY),
    "collections": [c.name for c in bpy.data.collections],
    "active_camera": bpy.context.scene.camera.name if bpy.context.scene.camera else None,
    "meshes": block(bpy.data.meshes),
    "materials": block(bpy.data.materials),
    "armatures": block(bpy.data.armatures),
    "images": block(bpy.data.images),
}
result["is_ready"] = (
    result["geometry_objects"] == 0
    and by_type.get("CAMERA", 0) == 1
    and by_type.get("LIGHT", 0) == 1
    and result["active_camera"] is not None
    and not any(result[k]["orphans"] for k in ("meshes", "materials", "armatures"))
)
```

Clearing and normalising — **only after confirmation**:

```python
import bpy
from math import radians

if bpy.context.object and bpy.context.object.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")

scene = bpy.context.scene
report = {"removed_objects": [o.name for o in bpy.data.objects], "created": []}

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

# orphan datablocks: several passes — deleting a mesh frees its material
BLOCKS = [
    ("meshes", bpy.data.meshes), ("curves", bpy.data.curves),
    ("armatures", bpy.data.armatures), ("materials", bpy.data.materials),
    ("node_groups", bpy.data.node_groups), ("collections", bpy.data.collections),
]
report["removed_orphans"] = []
for _ in range(3):
    freed = False
    for label, coll in BLOCKS:
        for d in list(coll):
            if d.users == 0:
                report["removed_orphans"].append(f"{label}/{d.name}")
                coll.remove(d)
                freed = True
    if not freed:
        break

# empty collections: linked to the scene, users > 0, so they do not count as orphans
report["removed_empty_collections"] = []
for c in list(bpy.data.collections):
    if not c.objects and not c.children:
        report["removed_empty_collections"].append(c.name)
        bpy.data.collections.remove(c)

# exactly one camera
cams = [o for o in bpy.data.objects if o.type == "CAMERA"]
if not cams:
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 50.0
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0.0, -6.0, 1.0)
    cam.rotation_euler = (radians(90.0), 0.0, 0.0)   # front view along +Y
    cams = [cam]
    report["created"].append("Camera")
for extra in cams[1:]:
    bpy.data.objects.remove(extra, do_unlink=True)
scene.camera = cams[0]

# exactly one light
lights = [o for o in bpy.data.objects if o.type == "LIGHT"]
if not lights:
    l_data = bpy.data.lights.new("Light", type="SUN")
    l_data.energy = 3.0
    lamp = bpy.data.objects.new("Light", l_data)
    scene.collection.objects.link(lamp)
    lamp.location = (0.0, 0.0, 4.0)
    lamp.rotation_euler = (radians(55.0), 0.0, radians(-40.0))
    lights = [lamp]
    report["created"].append("Light")
for extra in lights[1:]:
    bpy.data.objects.remove(extra, do_unlink=True)

result = report
```

**Done when:** the report shows 0 geometry objects, 0 orphan datablocks, exactly one camera (set
active) and exactly one light; and the report was published before the first modelling operation.
**Violated if:** the first modelling operation was performed without a report on the state of the
scene; anything was deleted without confirmation; "emptiness" was claimed without inspection; the
camera or the light is missing, or there is more than one of either.

**What the trial found (2026-07-30).** The rule was applied to the standard startup file of
Blender 5.1.2. Three defects in the first edition were found and fixed:
- A single pass over the orphans did not remove materials freed by deleting a mesh — repeated
  passes were added.
- The empty `Collection` is linked to the scene (`users > 0`), so it does not count as an orphan
  and the script did not delete it — a separate pass over empty collections was added.
- The default camera and light were deleted together with the geometry, after which there was
  nothing to render with — the requirement of exactly one camera and one light was added.

---

### R2 — The polygon range is derived from the model's purpose and from the 2D reference

**Status:** `under verification` — the questionnaire has been asked, the range computed and
**approved** by the user on 2026-07-30 (project photopilot; the calculation is kept in the
project's task). One verification step remains: confirm the minimum on the real geometry of the
first part. Until then the rule is not moved to `approved`.

**Statement.**
Before modelling starts, a **polygon range [min, max]** is determined.
The **maximum** is derived from the model's purpose: where, for what, on which devices and in which
applications it will run. To get this, the user is asked the questionnaire below — the whole of it,
not a selection from it.
The **minimum** is derived from the 2D reference: how many polygons are needed for the form on the
reference to read at all.
We work at the **lower** bound of the range. Until the range is approved by the user, modelling
does not begin.

**Why.** "The minimum number of polygons at acceptable quality" is not an absolute quantity:
acceptability is set by the application. Without asking, you have to guess, and guessing at exactly
this point poisons all the work that follows — a mesh built for film will not fit into a mobile
runtime, and a mesh built for a mobile runtime falls apart in a close-up. Two numbers are needed
because they forbid different things: **max** is a ban from above (you may not exceed it), **min**
is a guard against shoddy work (below it the form does not read, whatever the metric says).
Closes A4.

**Procedure.**
1. Ask the user every question in the questionnaire. To the ones that do not apply he answers "does
   not matter" — that is an answer too, and it is recorded.
2. Record the answers in the task (not in this file — only the rule lives here).
3. Derive **max** from the answers (§ "How the maximum is computed").
4. Derive **min** from the 2D reference (§ "How the minimum is computed").
5. Present the user with the range, with a justification for each bound and a breakdown by part.
   Get approval.
6. From then on, on each iteration — count and compare against the range (§ "Staying inside the
   range").

#### The questionnaire

**The questionnaire's boundary.** Only what directly determines the polygon count belongs in the
questionnaire. Questions about how the mesh is obtained (subdivision or direct modelling), LOD,
normal maps, UVs and export format are **not** part of R2 — those are separate rules, and the range
does not depend on them. The range applies to the **final mesh that ships to the application**; by
what route it was obtained is a matter for another rule.

**Block A — purpose and runtime** (sets the ceiling)

| # | Question | What it changes |
|---|--------|-----------|
| A1 | What is the model for? The end use in one sentence. | Rules out orders of magnitude that are obviously wrong |
| A2 | Where will it run: game engine, AR/VR, mobile app, web, offline render, 3D printing, reference only? | The main determinant of the ceiling |
| A3 | Which engine/framework exactly, and which version. | Limits on vertices and per object |
| A4 | Real time or offline? If real time — the target FPS. | Offline lifts the ceiling almost entirely |
| A5 | The weakest device among the targets. | The ceiling is computed from it, not from the top-end one |
| A6 | Is the model rendered at the same time as another heavy load: live camera video, ARKit, ML inference? | Splits the frame budget; can cut the ceiling by half or more |

**Block B — presence on screen** (sets what detail is visible at all)

| # | Question | What it changes |
|---|--------|-----------|
| B1 | How large is the model on screen in the worst case: filling the frame, full height, waist-up, a small figure, background? | A polygon smaller than a pixel is invisible — a direct limit |
| B2 | Will there be close-ups of individual parts? Which ones? | A local rise of the minimum for those parts only |
| B3 | How many instances are in frame at once: one, a handful, dozens, hundreds? | The ceiling is divided by that number |
| B4 | The target screen/render resolution. | The visibility threshold for a polygon |
| B5 | Does the model rotate freely, or is it seen from a limited set of angles? | Limited angles allow saving on the sides that are never seen |

**Block C — deformation** (raises the minimum)

| # | Question | What it changes |
|---|--------|-----------|
| C1 | Does the model deform: skinning with animation, hinged rotation of rigid parts, or static? | Deforming joints require edge loops — a direct addition to the minimum |

**Block D — constraints and priorities**

| # | Question | What it changes |
|---|--------|-----------|
| D1 | Is there a ready limit from the project: a per-character budget, a vertex limit, an asset size constraint? | If there is — max is taken from it, no calculation needed |
| D2 | Which matters more in a conflict: silhouette accuracy or smoothness of shading? | Where the polygons go when there are not enough |
| D3 | What has to read even if it costs polygons? What can be simplified beyond recognition? | Local additions and local savings |
| D4 | Are there benchmark models whose quality level counts as the target? | Lets "acceptable" be calibrated against a fact rather than a word |

#### How the minimum is computed

It is computed from the 2D reference, separately for each part:

1. Find the **mandatory sections** along the contour — the extrema and inflection points of the
   silhouette, that is, the places where the form changes character. Their number is
   `N_сечений` (N_sections).
2. Determine the minimum number of **segments around the girth**: 8 for organic forms with free
   rotation, 6 with limited viewing angles (B5), 4 for faceted and technical forms.
3. Estimate the minimum from the number of places where the form changes character and from the
   smoothness required around the girth. How the estimate is made depends on the method and lives
   in the method's document: for box modelling, see [phases.md](phases.md), M2 item 4. The "stack
   of sections × segments" model is not fixed here: it assumes that form is a function of height
   (A14).
4. Additions: 2 edge loops per animated joint (C1); separate polygons for the elements from D3 that
   have to read.
5. `min = Σ min_quads(parts) + closing caps`.

**The minimum has to pass a visual check.** If the silhouette does not read at the minimum, the
minimum is too low and the calculation is repeated. A number not confirmed by a picture is not a
minimum.

#### How the maximum is computed

- If D1 gives a ready limit — **max is taken from it**, no calculation needed.
- Otherwise: `max = runtime ceiling (from A2–A5) / number of simultaneous instances (B3)`, then a
  correction: close-ups (B2) raise the figure locally for the parts listed, not the ceiling as a
  whole.

**Order-of-magnitude guides** — used only when no ready limit exists:

| Application | Order of magnitude per figure |
|-----------|--------------------|
| Real-time, mobile / VR | a few to tens of thousands of tris |
| Real-time, PC / console, main character | tens of thousands to a hundred thousand tris |
| Film / offline render | no limit |

#### Staying inside the range

1. After each iteration on a part, a report is published: `verts / faces / tris / n-gons` for the
   final mesh — the one that will ship to the application. If modifiers are used in the work, the
   result of applying them is counted, not the source cage.
2. We aim at the lower bound. If adding polygons produces no visible improvement in the silhouette
   or the shading, they are rolled back. "Let's leave it denser just in case" is forbidden.
3. One part exceeding its share is not offset by savings on another part without agreement.
4. **n-gons (5+ sides) = 0** — unpredictable shading and triangulation. Triangles are allowed only
   in closed zones where they do not break edge loops.

**How to check** (Blender MCP, `execute_blender_code`):

```python
import bpy

def stats(ob):
    me = ob.data
    by_sides = {}
    for p in me.polygons:
        n = len(p.vertices)
        by_sides[n] = by_sides.get(n, 0) + 1
    return {
        "verts": len(me.vertices),
        "faces": len(me.polygons),
        "tris": sum(len(p.vertices) - 2 for p in me.polygons),
        "by_sides": by_sides,            # 3 = tri, 4 = quad, 5+ = n-gon
    }

dg = bpy.context.evaluated_depsgraph_get()
result = {}
for ob in bpy.context.scene.objects:
    if ob.type != "MESH":
        continue
    result[ob.name] = {
        "base": stats(ob),                              # control cage
        "evaluated": stats(ob.evaluated_get(dg)),        # with modifiers
        "modifiers": [m.type for m in ob.modifiers],
    }
```

**Done when:** the questionnaire has been asked in full and the answers recorded in the task; min
and max have been computed with a justification for each bound; the range and the breakdown by part
have been approved by the user.
**Violated if:** modelling started without an approved range; the questionnaire was asked partially
or not at all; min was taken by eye, without analysing the reference; the bounds are not justified;
the polygon report is not published on iterations.

---

### R3 — One part per iteration

**Status:** `draft`

**Statement.**
One iteration makes **exactly one part**. Moving on to the next one happens only after the user
explicitly accepts the current one.

**Why.** A mistake spotted on one part costs one iteration. A mistake spotted in a scene of a dozen
parts costs the whole scene. This is how a live sculptor works: block by block, not "the whole body
at once, by eye".

**Procedure.**
1. **Decomposition.** The 2D reference is broken down into a list of parts with boundaries. The
   list is agreed once and does not change afterwards without an explicit decision.
2. **Choice.** One part is taken, in the agreed order.
3. **Work.** Only that part is modelled. Other parts are not created even as blanks, are not
   touched, and are not "tidied up along the way".
4. **Presentation.** Shown: orthographic renders (front / side / three-quarter), wireframe, the R2
   report.
5. **Acceptance.** The user says "accepted" or gives corrections. Corrections are the same part, a
   new iteration. Without the word "accepted" the next part does not begin.

**Where part boundaries come from.** First of all — from the reference itself, if it defines them:
the joint lines of an articulated mannequin, the seams of a costume, the divisions of armour, a
change of material. Such lines are drawn by the concept's author; there is no need to invent them.
If the reference gives no boundaries — the boundaries are placed anatomically, in the places where
the form changes character.

**Done when:** the user has written "accepted" for this part.
**Violated if:** more than one part was touched in one iteration; the next part was started without
the previous one being accepted; neighbouring geometry was "fixed along the way".

---

### R4 — The first part: the model's base

**Status:** `approved` — verified in practice 2026-07-30, wording refined from the results of that
trial (see "What the trial found").

**Statement.**
Before the first modelling operation, study the 2D reference and choose one part — the **base** —
from which the rest of the model is measured out. Present the choice to the user with a
justification and get approval. Without approval, modelling does not begin.

**Why.** The first part sets the scale and the proportions of the whole figure: every following
part is measured relative to it. A mistake in the base does not stay local — it is dragged through
the whole model and is discovered when redoing it is expensive. The base is chosen not on the
principle of "what is easiest to start with" but by how many reference dimensions it gives the
others. Closes A8.

**Criteria for the base.** A part will serve as the base if:

1. **It sets the bounding measurement.** The figure's height and width can be measured out from it.
2. **Its boundaries are unambiguous on the reference.** Every boundary is either a drawn line or a
   free end. Boundaries that would have to be invented are a defect in a candidate.
3. **It has the most adjacencies.** The largest number of other parts join onto it.
4. **It is visible in all the views provided.** Otherwise it cannot be verified.
5. **It is self-contained.** It can be built without knowing the other parts.

**Criterion 2 is eliminating, the rest are comparative.** A boundary that would have to be invented
is not compensated for by any advantage on the other criteria: an invented boundary carries a
mistake through the whole model, and that is exactly what the rule protects against. A candidate
with even one boundary that is neither drawn nor a free end is out, even if it is the best on every
other point.

**Procedure.**
1. Study the reference: which views are given, which parts are visible, where the boundaries run
   and — separately — what the reference does **not** show.
2. Assess all the candidates against the criteria, not just the presumed winner.
3. Choose one and name the concrete dimensions the other parts will measure from it.
4. Present it for approval together with the justification and an analysis of the rejected options.

**How to check.** The justification contains an analysis of the alternatives. The chosen part is
visible in at least two views of the reference. Concrete dimensions that it sets for the others are
named.

**Done when:** the user has approved the first part.
**Violated if:** modelling started without an approved base; alternatives were not analysed; a part
was chosen whose boundaries had to be invented on the reference; the choice was justified by
convenience instead of by how much it anchors.

**What the trial found (2026-07-30).** The rule was applied to a reference of an articulated
mannequin in three views. The criteria produced an unambiguous winner, but a gap in the first
edition came to light: **the criteria conflicted, and no order for resolving the conflict had been
set**. The candidate with the most adjacencies (criterion 3) lost to the candidate with
unambiguous boundaries (criterion 2) — with the criteria weighted equally the choice would have
been arbitrary. A resolution rule was added: criterion 2 is eliminating, the rest are comparative.
A second observation: the winning boundary turned out to be a boundary that **does not exist** — a
free end of the form beats any drawn line, because it cannot be placed wrongly. This is recorded in
criterion 2 itself.

---

### R5 — Setting up the scene for the reference

**Status:** `approved` — verified in practice 2026-07-30, procedure extended from the results of
that trial (see "What the trial found").

**Statement.**
Before the first modelling operation, the scene is brought into a state in which form can be
compared against the reference: metric units, real scale, orthographic views along the axes, the
reference split into separate views and placed in the corresponding planes. The contents of the
scene are presented to the user with a report and screenshots.

**Why.** The minimum calculation in R2 rests on physical radii in millimetres; the base under R4
rests on reference dimensions at real scale. In a dimensionless scene both turn into empty numbers.
Orthography is needed because perspective distorts the contour: a silhouette can only be compared
against a 2D reference in orthographic projection. Closes A9, and gives the means for A5.

**Procedure.**
1. Perform R1: empty scene, one camera, one light.
2. Units metric, `scale_length = 1.0`.
3. **Split the reference into separate views.** A composite image with several projections in one
   file is unusable as a reference — it cannot be aligned to an axis. Each view is cut out into its
   own file. The figure's bounds in each view are measured, not estimated: they will be needed for
   placement.
4. **Judge the reference's fitness with a number, not a word.** Record what it is — orthographic
   projections or a perspective render. Then **measure the divergence between the views**: the
   scaling dimension in each view and the spread between them as a percentage. The formulation
   "this is perspective, so it is approximate" is useless — it does not say whether the views can
   be aligned. A number does.
5. **Declare the scaling dimension** — one bounding measurement (usually full height) from which
   everything else is scaled. Agree it with the user.
6. **Normalise each view separately** by the scaling dimension: in different views it occupies a
   different number of pixels, and without separate normalisation the views will diverge by exactly
   the discrepancy from item 4.
7. Place each view in the plane of its own axis: front in XZ, profile in YZ. The lowest point on
   the floor (`Z = 0`), the axis of symmetry on the Z axis.
8. **Check the placement instrumentally.** Put temporary markers at the bounds of the scaling
   dimension (floor and top), take a screenshot of the view, measure it and compare with the target
   value. This step cannot be passed by eye: a 2 % error is a few pixels. Remove the markers after
   the check.
9. Set up the orthographic views. Shrink any utility objects that fall into frame down to an
   unnoticeable size: in orthography the camera projects onto the reference regardless of where it
   stands.
10. Present: the script's report and a screenshot of each configured view.

**How to check.** The report contains: `unit_system`, `scale_length`, the list of objects with
their type and transform, the sizes and positions of the references, the projection type of the
views. Plus a screenshot of each view and the **numeric result of the instrumental placement check**
from item 8.

**Done when:** the report and the screenshots are published, the instrumental check showed agreement
with the scaling dimension, and the user confirmed.
**Violated if:** modelling started in a perspective view; a composite image is used whole as the
reference; the scaling dimension was not declared; the views were not normalised; placement was
confirmed "by eye" without a gauge; the units are not metric.

**What the trial found (2026-07-30).** The rule was applied to a reference of three views in one
file. Four findings, all folded into the procedure:
- **A verbal judgement of the reference is useless.** "A perspective render, roughly usable" — that
  is what I wrote at first. The gauge said otherwise: the scaling dimension agreed between the
  views to within 0.23 %, and the floor and top levels coincided. The reference is fit for precise
  alignment, and that only came out through measurement. Hence item 4 in the new edition.
- **Views have to be normalised individually.** A 0.23 % discrepancy is small, but it is
  systematic: without normalisation the profile would have come out 4 mm shorter than the front.
  Hence item 6.
- **Checking placement by eye does not work.** The difference between the correct height and the
  wrong one was 1.7 % — about 5 pixels on a screenshot, indistinguishable from the error of reading
  the edges. The instrumental gauge gave 0.0 mm. Hence item 8.
- **R1's "exactly one camera" requirement touches R5.** In an orthographic view the camera projects
  onto the reference regardless of its own position and covers the figure. Separate ortho cameras
  per view cannot be set up — R1 forbids them. The solution: shrink the camera's viewport display
  size. Hence item 9. As a side effect: the check renders required by R3 will have to be taken with
  one camera, moving it between views.

---

### R6 — A part's metrics before it is built

**Status:** `draft` — reworked 2026-07-30 after the first application: gauging the whole figure in
advance was replaced by gauging one part, and approval is given on the markup rather than on a
table.

**Statement.**
Metrics are taken **not for the whole figure at once, but for the part being built now**. Before a
part is built, the following are measured from the reference: **height** — the position of the
upper and lower boundary along Z and the distance between them; **width** — from the front view;
**depth** — from the profile. The result is presented as **markup on the reference**, where every
bounding measurement is drawn as a segment of exactly the measured length at its own level.
Approval is given on the picture. After approval the part is built, and the next part gets its own
gauge from scratch.

**Why.** Measuring the whole figure in advance is the same mistake as building everything at once
(A3): there turn out to be a great many measurements, they refer to forms that are not yet in front
of your eyes, and they have to be approved as a list. A gauge of one part is checked in a minute,
because there are few segments and all of them lie on the form being looked at right now.
**A table of numbers is not a presentation.** There is nothing to check numbers against but trust:
the line "437.5 mm" gives no way to see what exactly was measured. A segment drawn on the reference
is checked directly — it either butts against the edges of the form or misses. That is why the rule
demands a picture, and the numbers exist as labels on the segments. Closes A10.

**What is measured on a part.**

| Quantity | Where from | How it is shown |
|----------|--------|------------------|
| Height | Z of the upper and lower boundary, the distance between them | A vertical dimension beside the figure |
| Width | Front view, levels inside the part's range | Horizontal segments on the front |
| Depth | Profile, levels inside the part's range | Horizontal segments on the profile |

Width and depth are taken **at the same level**: the band is shared by the two views. Measurements
taken at different heights do not form a section, and there is nothing to build a volume from.

**Levels are grouped into vertical segments.** A height segment is a block of the part (head, neck,
chest), and the levels that fall into it are its rings. The grouping is not there for tidiness in
the list: it defines the **zones of comparison and the measurement coverage of the part**. The
build order is not determined by the grouping — that belongs to the method's document.

**Blocks may overlap, and that is normal.** The head reaches below the top of the neck: the chin
belongs to the head, and the neck continues behind and below it. Therefore:
- a level's membership in a block is **derived from Z only when there is one block**;
- where a Z falls into two blocks, membership is **stated explicitly**, not guessed;
- coverage of the part is checked by the **union** of the blocks, not by the sum of their lengths:
  where they overlap the sum is bound to exceed the total height and says nothing.

**The status of the metrics: a guide, not a standard.**
The metrics are taken from a two-dimensional reference, so they are **advisory and approximate**.
The reference is a precise support for proportions, but not a one-to-one standard: the projection
of a flat image is not obliged to coincide with the form a volume will give, and the reference
itself may be internally inconsistent (see the measured asymmetry). Hence:

- the metrics hold the **proportions and the scale**; they do not dictate literal reproduction;
- the tolerance describes the **precision of measuring the reference**, not a requirement on the
  model: you may go outside it if the form reads better that way — but deliberately and out loud;
- a divergence between the model and a metric is **grounds for discussion**, not an automatic
  defect;
- the metrics must not be presented as a standard to be reproduced exactly: that would bring back
  acceptance-by-number, which is precisely what the rule moves away from (A2).

A quality criterion for the form is **not** set by the metrics — that is a separate rule, not yet
written.

**Procedure.**
1. R5 must be done (the scene is set up) and a part chosen: the first one under R4, each following
   one under R3.
2. **Determine the part's boundaries along Z.** A boundary drawn on the reference is measured, not
   assigned by eye. A free end is taken at the edge of the silhouette. If a drawn boundary does not
   stand out under measurement — agree its position with the user explicitly instead of choosing it
   silently.
3. **The levels inside the part's range come from the reference, not from an anatomical atlas.**
   Three sources, in order of reliability:
   - **silhouette extrema** — where width or depth passes a local maximum or minimum of the
     smoothed profile. The most reliable source: independent of lighting;
   - **free ends** — the floor, the crown of the head;
   - **drawn part boundaries** (joint lines, seams). On a photographic or rendered reference this
     source is **unreliable**: a brightness detector responds identically to a seam and to shading.
     Use it only if the lines stand out unambiguously; otherwise discard it and rely on the
     extrema.
4. **Build a mask of the figure and close the short gaps in it.** Drawn joint lines cut the mask
   across the part: without closing the gaps the silhouette falls apart into dozens of pieces and
   counting pieces loses its meaning. The closing threshold is noticeably larger than the thickness
   of the lines and noticeably smaller than the real gaps between parts.
5. **Measure from the reference's pixel data, not with a cursor over the viewport.** With a cursor
   reproducibility is lost, and the quantities are needed as a standard for comparison.
   **A label is mandatory for every dimension that gauges an internal feature of the form rather
   than a full section** (chin, cheekbone, protrusion). Without a label such a gauge is
   indistinguishable from a miss: it falls out of the smooth run of its neighbours and looks like a
   segment that fell short. The label is the only thing that separates an observation from an
   error, and it costs one word.
6. Where the silhouette at a level falls into several pieces (for example the torso and the lowered
   arms), measure the pieces **separately** and say so. The combined width of the silhouette in
   such a place is not a bounding measurement of the part.
7. **Measure the reference's own asymmetry** within the part's range. The axis is taken as the
   median of the silhouette's row centres (the median, not the mean: it is robust to rows where
   part of the mask has dropped out). Isolated outliers in the extreme rows are an artefact of the
   mask, not a skew.
8. **Declare the tolerance.** A tolerance is not assigned by taste:
   - for comparison against a **full bounding measurement** — twice the measurement error of the
     reference (1 px of the reference in mm × 2). Over the full width a shift of the axis cancels
     out;
   - for comparison against **one side** — the same plus the measured asymmetry from item 7. Such a
     comparison is inherently weaker and is used only when the full bounding measurement is
     unavailable.
9. **Assemble the markup — that is the presentation.** Both views of the reference side by side on a
   common vertical scale; at each level a segment of exactly the measured length with ticks at its
   ends; the vertical height dimension of the part at the side; the numbers as labels on the
   segments. The part's range is highlighted, the rest of the figure dimmed. A separate table for
   approval is not required — it cannot be checked.
10. Present the markup and get approval **on the picture**.
11. **Feed the measured bounding measurements back into R2.** This part's share of the budget is
    recomputed from the measured dimensions instead of the assumed ones.
    - A section is treated as an **ellipse** built from the width–depth pair at one level. The
      number of segments around the girth is taken **by integrating around the perimeter with the
      local curvature**, not from a single radius: an ellipse's curvature varies from `b²/a` to
      `a²/b`, and computing from the sharpest radius overstates the mesh by roughly a tenth.
    - **Gauges of internal features (see item 5) do not enter the section calculation.** The pair
      "chin width — neck depth" gives an ellipse the part does not have.
    - **Markup levels are places of comparison, not the model's rings.** The number and heights of
      the rings are determined while building (see the method's document). For the budget check,
      take a forecast of the ring count as one number per part, labelled "forecast, not a build
      order".
12. Build the part, comparing its bounding measurements against those same segments. A divergence
    larger than the tolerance is examined: either the model is fixed, or the divergence is accepted
    deliberately with an explanation. Leaving a divergence in silence is not allowed — but neither
    is blindly fitting to the number.
13. The next part starts again from item 2. Measurements are not taken ahead of time.

**How to check.** The markup contains: the part's height, the width and depth segments at every
level of the range, the tolerance. After building — the same script takes the model's bounding
measurements at the same levels and prints the deviation in millimetres and in tolerances.

**Done when:** the part's markup is assembled and approved by the user on the picture.
**Violated if:** the whole figure was measured instead of the current part; a table of numbers was
presented instead of markup; the levels were taken from general ideas about anatomy; the
measurements were made with a cursor or by eye; the tolerance was assigned arbitrarily; a composite
silhouette width was passed off as a bounding measurement of the part; the part's height was not
measured; width and depth were taken at different heights; a drawn boundary was assigned silently
instead of being measured or agreed; **the metrics were presented as a standard to be reproduced
exactly.**

**What the trial found (2026-07-30).** The rule was applied to the placed views of the mannequin.
The result was a table of 13 width levels, 12 depth levels and 2 levels of the torso without the
arms. Four findings, all folded into the procedure:
- **Drawn joint lines did not work as a source of levels.** The brightness detector produced 14
  levels scattered over the whole figure, corresponding neither to seams nor to extrema: the soft
  shading of a render gives pixels just as dark as a seam does. The source was demoted in
  reliability, and the work proceeded on silhouette extrema. Hence items 2 and 3.
- **Joint lines cut the mask of the figure.** Without closing the gaps, the number of silhouette
  pieces jumped from 1 to 7 on adjacent rows, and the torso could not be separated from the arms.
  With gaps up to 6 px closed, the profile became structural. Hence item 3.
- **The reference is four times more asymmetric than the tolerance:** a median of 8 mm and a 99th
  percentile of 16 mm against a tolerance of ±4 mm. The systematic maximum is at head level. So
  full bounding measurements have to be compared rather than half-widths, and the reference is not
  proof of the model's symmetry. Hence items 7 and 8. As a side effect: the 229 mm outlier in the
  very lowest row turned out to be a mask artefact — which is why the axis is taken as a median and
  outliers in the extreme rows are discarded.
- **R6 feeds data back into R2.** The polygon minimum had been computed from an assumed torso
  radius of 150 mm. Measurement gave an ellipse with semi-axes 174 × 104 at pelvis level, for which
  the governing radius of curvature is `ρ = b²/a = 62 mm`, not 150. The torso needs ~32
  segments around the girth instead of 48 — that is, **the minimum had been overstated**. Hence
  item 11.

---

### R7 — Markup: tool, hand-off, acceptance

**Status:** `draft` — assembled from the results of the first complete markup, 2026-07-31.

**Statement.**
A part's markup is made by the **user** in the markup editor, not by me by eye. My job is to
prepare the tool and the starting blank, hand over control, then **check what comes back and put
the findings as questions**. Markup is accepted not when the file arrives, but when every finding
has been examined and the chain of heights is closed.

**Why.** Gauging from a 2D reference means making decisions: where the part's boundary is, what
counts as a section and what as an internal feature of the form. Those decisions are made by the
model's author. The machine, meanwhile, is irreplaceable at something else: it counts pixels
without tiring and finds contradictions the eye does not see. Hence the division: **the human
decides what to measure, the machine counts and checks.** Closes A11.

#### What to start up

1. The reference's views are cut and placed under R5, and a part is chosen under R4 or R3.
2. **Assemble a starting markup** — automatic levels from the silhouette extrema, the part's
   boundaries, rough height segments. An empty editor pushes onto the human work the machine does
   better.
3. **Bring up a local server** rather than publishing a page. A published page cannot write a file,
   and the result would have to be carried over by hand — exactly what we are moving away from.
4. **Check the server on every loopback address** — IPv4 `127.0.0.1` and IPv6 `::1`. The system
   resolves `localhost` to IPv6 first, and a server listening only on IPv4 will give a connection
   refusal on the very link I handed over.
5. Give **one link** and explain three things: the tools, autosave, and the "finished" button.

#### What not to do while markup is in progress

- **Do not clear the browser's storage and do not reload the tab** the person is working in: the
  unwritten state lives there.
- **Do not delete markup files or history.** That is the human's result, not my temporary file.
  Cleaning up after yourself does not extend to someone else's work.
- **Do not slip in a "corrected" file** while editing is under way: it will diverge from the current
  state within a minute and roll the edits back. Give numbers, not a file.

#### What to ask

| When | Question |
|-------|--------|
| Before starting | Is an axis of symmetry needed, and in what form |
| Before starting | Which height segments must cover the part completely |
| For each finding | Is this a measurement or a miss — with the numbers attached |
| Before acceptance | Label the dimensions that gauge internal features of the form |

#### What to check in what comes back

The checks are run by script, all at once, before any conclusions:

| # | Check | Sign of trouble |
|---|----------|--------------|
| 1 | Completeness | no levels, heights, axis, scale or tolerance |
| 2 | The part's range | the declared range disagrees with the actual data |
| 3 | Distance between levels | two levels closer than the tolerance — one of them is redundant |
| 4 | Dips in a bounding measurement | a middle level noticeably narrower than both neighbours over a small height |
| 5 | Repeated bounding measurements | the same value on three levels in a row — it was not re-measured |
| 6 | Coverage of the part | the union of the blocks leaves holes; check by union, not by sum — blocks may overlap |
| 6a | Level membership | a level falls into no block; a block holds fewer than two gauged levels — the block gives no comparison |
| 7 | Axis consistency | the midpoint offset does not match the axis for the dimensions bound to it |
| 8 | Comparison against the reference | its own width against the part's width and against the full silhouette |

#### How to present findings

Every finding is a **question with numbers**, not a verdict. Two kinds are kept apart:

- **An observation** — a smooth, consistent divergence from my own gauge. That is the author's
  decision, and it takes priority over my detector.
- **A probable error** — a sharp dip over a small height, a repeated value, a pair of levels closer
  than the tolerance. That contradicts itself, not me.

What tells one from the other is comparison against **two** supports at once: against the part's
boundary and against the full silhouette. A finding must not be phrased as a fact: three of the
three "errors" in the first markup turned out to be measurements I had not anticipated.

#### How to accept

1. Every finding has been dealt with: fixed or explained by the author.
2. The blocks cover the part without holes (checked by union), each block has at least two rings,
   and every level is assigned to a block — explicitly where several blocks fit.
3. Dimensions of internal features of the form are labelled (R6, item 5).
4. The file is marked finished, and a copy has gone into the history.
5. Only after that — the measurements are fed back into R2 and building proceeds under R3.

**How to check.** The check script from the table above prints the list of findings with numbers.
Acceptance passes when the list is empty or every item is closed by an answer from the author.

**Done when:** the checks have passed, the findings are closed, the chain of heights is joined up,
and the file is marked finished.
**Violated if:** the markup was made by me instead of the author; the result was accepted without
running the checks; a finding was presented as an error without examining the alternative; files or
state holding someone else's work were deleted; a page was published instead of a local server and
the result is being carried over by hand.

---

### R8 — Building: choosing the method

**Status:** `draft`

**Statement.**
Building begins not with a polygon but with a **choice of method**. There are two methods, and both
are presented to the user:

1. **Box modelling** — the shell is built by extruding from a simple form along the orthographic
   views, edge by edge, with a mirror along the axis and subdivision on while working.
2. **Sculpting followed by retopology** — the form is sculpted with no regard for the mesh, then a
   clean quad mesh is laid over it and the detail is transferred into a normal map.

The recommendation is derived **from the answers to the R2 questionnaire**, not from taste. The
decision is made by the user. The chosen method is recorded in the task, and all further build
sub-steps branch on it.

**Why.** The method determines the topology, the order of work and the way of checking — that is,
almost everything that cannot afterwards be changed without starting over. A method chosen in
hindsight is not chosen at all: the first hundred polygons already made the choice. Closes A13.

**Lofting through sections is not on the list.** Pulling a shell through a set of rings is standard
in CAD and hard-surface work, where the form is defined by sections in essence. For organic forms
it gives a regular lattice: the edge loops run across the form instead of along it, poles land
wherever they happen to, and where the form changes character the mesh either tears or spends
polygons for nothing. Measured markup makes a loft justified in its bounding measurements, but does
not change its nature: **markup is a tool for controlling proportions, not a generator of form**
(R6, "The status of the metrics").

**The signs from which a method is recommended.**

| R2 questionnaire answer | In favour of box modelling | In favour of sculpting |
|-----------------|------------------------|----------------------|
| Model's surface | large smooth forms, no fine relief | folds, pores, fabric, musculature |
| Polygon budget | low: the result will be sparse anyway | high, or there is a normal map |
| Transferring detail into a map (C4) | not planned | planned — sculpting's main gain |
| Deformation (C1) | hinged or static | skinning with complex zones |
| Priority (D2) | accuracy of silhouette and bounding measurements | plasticity of the surface |
| Measured markup available | yes: the markup gives bounding measurements and boundaries to compare against, and the form is built by eye | not required |

The rule is simple: **sculpting is justified where the form cannot be described by bounding
measurements.** If the markup from R6 describes the part adequately, there is nothing to sculpt.

**Procedure** (following the sub-step cycle: studied → agreed → recorded → performed → checked):
1. **Studied** — pull up the R2 questionnaire answers and the R6 markup, match them against the
   table of signs.
2. **Agreed** — present both methods, the recommendation and its justification point by point; get
   the user's decision.
3. **Recorded** — the method is fixed in the task before the first modelling operation.
4. **Performed** — further build sub-steps follow the branch of the chosen method.
5. **Checked** — at the very first acceptance, confirm that the method is giving what was expected:
   the topology matches the chosen branch rather than having formed by itself.

**How to check.** The task holds a record of the chosen method with a justification against the
questionnaire's points. The topology of what was built matches the branch: with box modelling the
loops run along the form; with retopology they follow the sculpted surface.

**Done when:** the method has been chosen by the user out of the two presented, and the
justification is recorded in the task.
**Violated if:** building started without a recorded method; one option was presented instead of
two; the recommendation was given without leaning on the questionnaire; lofting through sections
was chosen.

#### The method branch

The methodology of the chosen method — the unit of work, the step cycle, the phases, the operations
and the checks — lives in a separate **method regulation**: it depends neither on the work type nor
on the editor. For box modelling that regulation is
[step-cycle.md](step-cycle.md), [measure-vs-eye.md](measure-vs-eye.md) and
[phases.md](phases.md); the mapping of its operations onto one editor's tools is
[blender.md](blender.md).

R8 ends with the choice of method and hands the work to the first phase of the chosen regulation.

---

## 2. Failure modes

This document came into being after three failed attempts to build a model from a reference. Every
time there was no modelling — what happened was distorted primitives being fitted to a silhouette
while a numeric metric was optimised. Below are the general failure modes it all comes down to.
These are **not rules**, but a list of what the rules have to prevent.

| ID | Failure mode | How it shows up |
|----|--------------|-------------------|
| A1 | **Primitive fitted to the silhouette** | A primitive is scaled and bent until the contour agrees. There is no internal form and no meaningful edges. |
| A2 | **Metric instead of form** | Acceptance on silhouette agreement (IoU, bounding measurements). The metric measures the fill of a contour, not a volume: a flat cut-out along the contour scores almost perfectly. |
| A3 | **Everything at once** | One pass generates the whole figure. A mistake anywhere poisons the scene, and there is nothing to roll back to. |
| A4 | **Polygons are not counted** | Density is set by a generator parameter, with no budget and no answer to "why this many". |
| A5 | **No visual check** | Decisions are made from numbers in the output rather than from a render. Degenerate geometry lives in the scene for iterations. |
| A6 | **Silent degradation** | A known defect is carried from iteration to iteration instead of stopping and fixing it. |
| A7 | **Dirty scene** | Work proceeds on top of the leftovers of previous attempts. |
| A8 | **No base part** | Modelling starts with whichever part came to hand. The proportions are assembled from independently made pieces and do not add up, because each was measured on its own. |
| A9 | **Dimensionless scene** | Modelling without real scale and without orthography. The polygon budget and the reference dimensions lose their meaning, and the silhouette is compared by eye in perspective. |
| A10 | **Proportions by eye** | A part is fitted to its neighbour instead of to the reference. The error runs along the chain and surfaces on the last part, when everything has to be redone. |
| A11 | **Markup instead of the author** | I decide for the author what to measure and where the boundary is, and pass my own gauge off as agreed. Or I present a divergence from my own detector as the author's error. |
| A12 | **Destroying someone else's result** | Cleaning up after myself touches files and state that hold a person's work: deleted markup, cleared browser storage, an overwritten file. |
| A13 | **Method chosen in hindsight** | Building started without an explicit choice of method. The first hundred polygons have already set the topology and the order of work, and the choice turned out to have been made silently. |
| A14 | **Form treated as a function of height** | A part is built as a stack of horizontal sections: one height, one ring. But the form has turns — under the jaw, under the chest, in the armpit — where there are two surfaces at one height. A stack of rings does not describe them **at any number of rings**. Measurements that do not fit the picture are then declared markup errors. |

---

## 3. Queue of rules for discussion

Topics for which rules have **not yet been formulated**. We take them one at a time. The order in
the queue is not a priority.

- [ ] An acceptance criterion for form: what replaces silhouette agreement (A2).
- [ ] Mandatory visual verification of every iteration: what we render, with what settings, why a
      decision is not made from numbers (A5).
      *Partly covered, method-specifically, in [step-cycle.md](step-cycle.md), §2 and
      [phases.md](phases.md), §11; a general work-type rule is still needed.*
- [ ] Topology quality: edge flow, loops around joints, the number and placement of poles.
      *Partly covered in [measure-vs-eye.md](measure-vs-eye.md), §7 and [phases.md](phases.md),
      §16.A; a general rule is still needed.*
- [ ] Phases within a single part: blockout → refinement → detailing; what completes each.
      *Partly covered in [phases.md](phases.md), §9 (M3–M6, "Done / Violated"); a general rule is
      still needed.*
- [ ] What counts as a legitimate starting form and what counts as fitting a primitive (A1).
      *Partly covered in [phases.md](phases.md), §10.1 "Create the primary volume"; a general rule
      is still needed.*
- [ ] Scene and reference setup: the position and type of the camera for orthographic views, light
      parameters, background images, units, real scale. R1 guarantees that a camera and a light
      exist, but does not define how they are placed.
- [ ] Stopping on a known defect: an iteration does not continue on top of degradation (A6).
      *Partly covered in [phases.md](phases.md), §12.1 "Phase failure"; a general rule is still
      needed.*
- [ ] Symmetry: where we work in half and mirror, and where we do not.
      *Partly covered in [phases.md](phases.md), §15.1; a general rule is still needed.*
- [ ] Joining parts and seams: when and how parts are merged into a single mesh.
      *Partly covered in [phases.md](phases.md), M5 "The joint contract"; a general rule is still
      needed.*
- [ ] Saving progress: a rollback point **for every accepted stage and every accepted part**, file
      versions.
      *Partly covered in [step-cycle.md](step-cycle.md), §13–14; a general rule is still needed.*
- [ ] How the final mesh is obtained: control cage + subdivision, or direct modelling at final
      density. Moved out of R2 — it does not affect the polygon range.
- [ ] LOD levels: are they needed, how many, how each is computed.
- [ ] Transferring detail into a normal map: when it is justified, what gets baked.
- [ ] UVs and textures: unwrapping, seams, the effect on the final vertex count.
- [ ] Export format: glTF / USDZ / FBX, triangulation, format limits.
- [ ] Shape keys and deformation: when they are needed, which edge loops they require.
- [x] ~~Mapping the regulation's operations onto the tools of a specific editor.~~
      [blender.md](blender.md) has been written for Blender.

---

## 4. Change log

| Date | Change |
|------|-----------|
| 2026-07-30 | Document created. Rules R1 (polygon budget) and R2 (one part per iteration), failure modes A1–A6. |
| 2026-07-30 | The rules were generalised: everything tied to one specific model (its list of parts, its numeric budget, its order of work) was removed — that is the task level, not the rules level. The rule "modelling starts from an empty scene" was added as R1, and the former R1/R2 became R2/R3. §0 was added — the rule lifecycle and statuses. Failure mode A7 was added. |
| 2026-07-30 | R1 applied in practice and **approved**. Fixed from the results of the trial: repeated passes over orphan datablocks, a separate pass over empty collections, the requirement of exactly one camera and one light with automatic creation. |
| 2026-07-30 | R2 reworked: instead of "the budget comes from the task", the rule now **derives the range [min, max]**. Added the questionnaire (blocks A–D), the method of computing the minimum from the 2D reference, the method of computing the maximum from purpose, and the requirement of visual confirmation of the minimum. |
| 2026-07-30 | R2 narrowed to its own job. Six questions that do not determine the polygon count were removed from the questionnaire: runtime subdivision, LOD, normal map, UV/textures, export format, shape keys — moved into the queue in §3 as separate rules. An explicit boundary for the questionnaire was added. The range now applies to the final mesh that ships to the application, regardless of how it was obtained. 15 questions remain. |
| 2026-07-30 | R2 applied, status `under verification`. From the results of that application, question A6 was added to the questionnaire — whether the model is rendered at the same time as the camera/ARKit/ML: a missed input that halves the frame budget and without which the ceiling cannot be computed. The answers and the calculation are kept in the project's task. |
| 2026-07-30 | The rules were moved into a separate `work-rules` repository. The common process (rule lifecycle, statuses, wording requirements, template) was moved to the repository's README, and the file's sections were renumbered. |
| 2026-07-30 | R4 added — the first part is chosen as the model's base, with five criteria for how much it anchors and a mandatory analysis of the alternatives. Failure mode A8 added (no base part). |
| 2026-07-30 | R6 added — reference levels and bounding measurements, and failure mode A10 (proportions by eye). |
| 2026-08-01 | Eleven unverified toolkit functions were run through a live session in four calls. The check ran both ways: on clean geometry the tools must stay silent; on broken geometry they must name addresses. A clean half of a cube with a mirror gave 48 quads, zero open edges after reflection and zero poles on the seam — this confirmed the rule that "the legal degree of a seam vertex is three". A torus with its axis along Y gave two contours through the hole and one below it, and gauging on it separated three outcomes: normal, turn, empty. Two new facts were found: the mirror doubles the polygon count on top of subdivision, so the multiplier is 2 × 4^L rather than 4^L; and rollback silently makes the rollback point itself the working file — subsequent saves would have gone into the directory of rollback points. The second was fixed: `restore` now takes the path of the working file. The scene, the collections and the working file were returned to their original state after the run. |
| 2026-08-01 | The mapping document and the toolkit went through a review of four checks: 72 findings (15 blocking, 36 substantial, 21 minor). The toolkit's genuine bugs were all of one class — they return a plausible wrong number instead of failing: a section's bounding measurement was taken along fixed axes whatever the cut axis was; an empty section counted as a passed comparison; the counter of poles on the seam was identically zero; a pole was counted by edges instead of faces; millimetres were computed by multiplying by a thousand without accounting for the scene scale; a cut with zero tolerance tore the contour at a cage ring; a tangent section looked like two contours. From the server's source it was confirmed that a screenshot takes the largest area, that `jump_to_*` changes the mode and the selection, and that `*_for_cli` starts a separate process. My own claim about element-wise assignment to `use_axis` was withdrawn: the "verified" mark stood on an observation that did not contradict the claim but did not confirm it either. |
| 2026-07-31 | The mapping document "box modelling in Blender" and its session toolkit were written. Going through the installed skills and the MCP server showed that out of the server's twenty tools I had been using one: inspection and checking, for which ready tools exist, I had been replacing with my own one-off scripts. Verified by experience: `sys.modules` survives across calls while `globals()` does not — so the tools are installed into the session once; measuring the final surface and telling one contour from two in a section both work; and the mirror reflects relative to the object's origin, not the world's, which silently gives the wrong plane of symmetry. |
| 2026-07-31 | The method regulation went through a review of five independent checks (hidden loft, coupling to the editor, executability, contradictions with R1–R8, completeness): 11 blocking corrections, 32 substantial, 12 minor, and 11 findings rejected with justification. The corrections touched the work-type rules as well: R8 no longer recommends box modelling on the grounds that "vertices are placed by numbers"; R6 no longer assigns the model's rings from the markup levels — the levels are declared places of comparison; R7 does not make the ring count a criterion for accepting markup; and the minimum formula in R2 stopped resting on the "stack of sections" model, which is incompatible with A14. |
| 2026-07-31 | The method document was rewritten as a **regulation**: a step cycle of six beats, a division of roles (the builder inspects every step himself, the human is shown stages), the rule "measurement belongs in verification, never in the operation" with two exceptions, the role of markup as an instrument of control, a catalogue of operations by kind, the density test, a failure branch on every check, rollback. The names of one editor's tools were removed from the document: the mapping of operations onto tools is written up separately. |
| 2026-07-31 | Sub-step M2 "Topology plan" was described. Its first item became the check "is the form a function of height?": on the mannequin it found a zone where two surfaces live at one height (the dome of the chin in front and the neck behind it), which explained the failure of three earlier loft attempts — a stack of rings does not describe such a zone at any number of rings. Failure mode A14 was added. It was also recorded that a gauge narrower than the silhouette does not always mean a gauge of a feature of the form: below the shoulders the silhouette includes the arms. |
| 2026-07-31 | The method's methodology was moved out of R8 into a separate document, the method regulation: the work-type rule is responsible for choosing the method, the method's document for how one works with that method. The sub-steps were renumbered 8.2–8.7 → M1–M6, since they no longer depend on a rule number. |
| 2026-07-31 | Sub-step 8.2 "Setup" was described: inspecting the scene as a whole, aligning the markup axis with the mirror plane by shifting the reference, guides taken from the markup and not made as geometry, the "mirror before subdivision" stack with its parameters recorded before any mesh appears. |
| 2026-07-31 | Seven build sub-steps along the box-modelling branch were written into R8, together with a section "What practice has confirmed" summarising the sources. As a result of the comparison, the topology plan was moved from fifth position to third — the direction of the loops is settled before the blockout, not after refinement; the blockout builds the part as a whole, and the markup blocks remain the unit of refinement; seam convergence is checked on the blockout. |
| 2026-07-31 | R8 added — choosing the build method: box modelling or sculpting with retopology, both presented, the recommendation derived from the answers to the R2 questionnaire. Lofting through sections is excluded explicitly, with justification. Failure mode A13 added. The sub-step cycle was written into the README: studied → agreed → recorded → performed → checked. |
| 2026-07-31 | Levels are grouped into vertical segments: a segment is a block of the part, and the levels that fall into it are its rings. Blocks may overlap (head and neck), so a level's membership is stated explicitly where its Z falls into two blocks, and coverage is checked by union rather than by the sum of lengths. |
| 2026-07-31 | R7 added — markup: what to start up, what to ask, what to check, how to accept. Eight checks on the returned markup, the division of findings into observations and probable errors, and the prohibitions on acting during someone else's work. Failure modes A11 (markup instead of the author) and A12 (destroying someone else's result) added. |
| 2026-07-31 | R6 applied to the first part in full. Added: a label is mandatory for gauges of internal features of the form (otherwise they are indistinguishable from a miss — a chin 36.9 mm wide against a silhouette of 100.3 looked like a defect); a section is treated as an ellipse with an integral around the perimeter rather than a single radius; gauges of internal features are excluded from the section calculation; the ring count is taken from the levels that were placed. The minimum for the central block was recomputed: 1 800 → 2 484 tris. |
| 2026-07-30 | R6 refined during application: width and depth are taken at a common level (otherwise there is no section); the section "The status of the metrics" was added — metrics from a 2D reference are advisory, the reference is a support for proportions but not a one-to-one standard, and presenting them as mandatory to reproduce exactly is forbidden. |
| 2026-07-30 | R6 applied and **approved**. The procedure grew from 8 steps to 12. Findings: drawn joint lines are unreliable as a source of levels on a rendered reference (shading gives equally dark pixels); joint lines cut the mask of the figure and require gaps to be closed; the reference's own asymmetry turned out to be four times the tolerance, hence the requirement to compare full bounding measurements rather than half-widths; measured bounding measurements are fed back into R2 — an assumed torso radius of 150 mm turned out to be an ellipse with a governing radius of curvature of 62 mm, that is, the polygon minimum had been overstated. |
| 2026-07-30 | R5 added — setting up the scene for the reference, and failure mode A9 (dimensionless scene). |
| 2026-07-30 | R5 applied and **approved**. From the results of the trial the procedure grew from 8 steps to 10: judging the reference's fitness became numeric, and separate normalisation of the views plus an instrumental check of placement by measuring a screenshot were added. An interaction with R1 was noted: "exactly one camera" forces the camera's viewport display size to be shrunk and the check renders to be taken with a single camera. |
| 2026-07-30 | An exception was added to R1: an untouched editor startup file (`is_dirty == False`, default contents) is cleaned without asking for confirmation. The inventory is published as before. |
| 2026-07-30 | R4 applied and **approved**. From the results of the trial, a resolution for conflicting criteria was added: criterion 2 (unambiguous boundaries) is eliminating and the rest are comparative — otherwise the choice between a candidate with more adjacencies and a candidate with unambiguous boundaries is arbitrary. |

# Box modelling in Blender

This file covers the Blender half of the method: which tool performs each operation and each
check, how the beats of the step cycle map onto calls to the Blender MCP server, what the session
toolkit is and why it is installed as a module, and thirty-odd traps that were each paid for with
a concrete failure. Read it when you are about to touch Blender — before the first operation of a
part, and again whenever a number, a screenshot or a mesh behaves in a way you cannot explain. The
logic, the order and the criteria are not here: they live in
[work-rules.md](work-rules.md), [step-cycle.md](step-cycle.md),
[measure-vs-eye.md](measure-vs-eye.md) and [phases.md](phases.md).

**What this is.** It ties the operations and checks of the regulation to the tools of Blender and
of the MCP server. The logic, the order and the criteria are there; here only **what does it**.

**Status:** `draft`. Statements verified by experience in a live session, or against the server's
source code, are marked ✓; anything unverified is marked `?` and is to be verified on first use.

**Target stack.** Blender 5.1+, the official Blender Lab MCP server (`blender-mcp`, package
`blmcp`), the add-on listening on `localhost:9876`.

---

## 1. Layers of tooling

The server gives twenty tools for the live session and eight `*_for_cli` twins.

| Layer | Tools | Note |
|------|-------------|-----------|
| **Inspection** | `get_objects_summary`, `get_object_detail_summary`, `get_blendfile_summary_*` (5), `get_screenshot_of_window_as_json` | the contents of the scene are taken from here, not from a script |
| **Documentation** | `search_api_docs`, `get_python_api_docs`, `search_manual_docs`, grep over the files on disk | see 6.4, 6.5 |
| **Action** | `execute_blender_code` | the only one that changes the live scene arbitrarily |
| **Showing** | `get_screenshot_of_area_as_image`, `get_screenshot_of_window_as_image` | the working check comes from here |
| **Navigation — changes state as a side effect** ⚠ | `jump_to_view3d_object_by_name`, `jump_to_view3d_object_data_by_name`, `jump_to_tab_by_name`, `jump_to_tab_by_space_type` | see 6.6 |
| **Render** | `render_viewport_to_path`, `render_thumbnail_to_path` | for presenting to a human |
| **A separate process** ⚠⚠ | the eight `*_for_cli` | see 6.12 — **not** an alternative to the live ones |

The server's own instruction, verbatim:

> The `execute_blender_code` tool is a **last resort**, if there are other tools that provide
> the functionality you need, use those instead.

The order of work, common to all eight installed Blender skills:

> inspect with a `get_*` / `search_*` tool → mutate via `execute_blender_code` → verify with a
> screenshot or summary tool. Keep code blocks **small and idempotent**.

---

## 2. Map of the step cycle's beats

The beats come from the regulation — see [step-cycle.md](step-cycle.md), §4.

**The rule of economy.** Everything that does not require my eye between calls goes into **one**
`execute_blender_code` block. A separate call is justified only where the next action depends on
what I saw. With three view angles per step that comes to **five** calls to the server, not
fourteen.

| Beat | What performs it | Calls |
|------|-----------------|-----------|
| 1 — name | a line in the journal (§8); Blender is not touched | 0 |
| 2–3 — operate and shape | one block: `pp.snapshot()` + `pp.shots()` (the point and the "before" pictures) → the operation → shaping | **1** |
| 4 — inspect | one block sets the first view angle, then one screenshot per angle; the change of angle between shots goes inside the block of the next shot | **1 + n** |
| 5–6 — verify and decide | one block: `pp.gauge()`, `pp.bbox()`, `pp.budget(share)`, `pp.topology()`, `pp.seam()`, `pp.mods()`; then a line in the journal | **1** |

**The stage gate**, additionally: `pp.gauge()` over all measurements, `pp.snapshot()` as a rollback
point, `render_viewport_to_path` for presenting to a human.

---

## 3. The session toolkit

### 3.1 Why a module and not a fresh script each time

Verified by direct experience ✓:

| What | Survives an `execute_blender_code` call |
|-----|------------------------------------------|
| `sys.modules` | **yes** |
| bare `globals()` | **no** — every call gets its own dictionary |

Hence: the tools are installed into the session **once**, and from then on each beat is a call by
name. A new script for every check is unverified, is not reused, and may differ from yesterday's
in some small detail that changes the number.

**Intermediate values between calls** (for example the pre-operation bounding measurement for the
shaping task "flatten the section") are put into an attribute of the module: `pp.KEEP = {...}`.
Bare variables of a call are no good for this — they will not survive the next block.

### 3.2 What is in it

Code: [../scripts/pp_blender.py](../scripts/pp_blender.py). Installed with a single call:

Blender's Python does not inherit `CLAUDE_PLUGIN_ROOT`, so resolve the path on the calling side and
paste the resolved value in — do not read the variable inside Blender. From an installed plugin it
is `<plugin root>/skills/model-from-reference/scripts/pp_blender.py`.

```python
import sys, types, pathlib
p = "/absolute/path/to/skills/model-from-reference/scripts/pp_blender.py"
mod = types.ModuleType("pp"); mod.__file__ = p
exec(compile(pathlib.Path(p).read_text(encoding="utf-8"), p, "exec"), mod.__dict__)
sys.modules["pp"] = mod
result = {"установлено": mod.VERSION, "функции": sorted(mod.__all__)}
```

(`"установлено"` — installed; `"функции"` — functions.)

| Function | What it gives |
|---------|----------|
| `obj(name)` | the object, or a loud error with the list of names |
| `cage(ob)` | the cage, with a check of type and mode |
| `evaluated(ob)` | a context for the final surface; checks that the viewport and render levels are equal |
| `mm_per_unit()` | millimetres per scene unit — from `unit_settings`, not as a constant |
| `section(ob, coord, axis)` | the bounding measurement **in the cutting plane**, the centre, **the number of contours**, tangent points |
| `bbox(ob)` | the final result's bounding box: width, depth, height, centre, bottom, top |
| `gauge(ob, levels, tol)` | the comparison; three outcomes per level: in tolerance, **empty** (a refusal), **a turn** |
| `budget(ob, share)` | cage polygons against the final result, and a **verdict** against the range |
| `topology(ob)` | n-gons, triangles, loose vertices, open and wire edges, edges with 3+ faces, poles — **with addresses** |
| `seam(ob, axis)` | seam vertices, deviation, those that crossed the plane, doubled ones, poles on the seam with addresses |
| `mods(ob)` | the stack: order, viewport and render levels, mirror properties |
| `guide(...)` | a guide **for a measurement**, as an empty, not as geometry |
| `view(angle)` | the view angle in **the** area the screenshot will come from |
| `channel(name, ob)` | the channels: silhouette, shading, wireframe, working |
| `shots(name, dir)` | a set of viewport screenshots — the "before" and "after" pictures |
| `snapshot` / `restore(path, work_file)` / `points` | rollback points; `work_file` is mandatory by its very meaning — see 6.19 |
| `scene_report()` | only what `get_objects_summary` does not give: units, scale, file |

**Catalogue of points:** `<task>/points/`. The name of a stage's rollback point is
`stage<N>_<stage>`, of a step's rollback point `step<N>_before` (the two kinds are defined in
[step-cycle.md](step-cycle.md), §13). Screenshots go to `<task>/shots/`.

### 3.3 The dictionary keys the toolkit returns

The toolkit grew up in Russian and its returned dictionaries kept their Russian keys. Renaming a
proven tool to make its documentation prettier is a bad trade, so the keys stay as they are. This
is the phrasebook:

| Key | Meaning |
|-----|---------|
| `ширина_мм` | width in mm — measured **in the cutting plane** for `section()`, along X for `bbox()` |
| `глубина_мм` | depth in mm — the other in-plane axis for `section()`, along Y for `bbox()` |
| `контуров` | the number of separate contours the cut produced; two means a turn |
| `вершин` | vertex count |
| `пусто` | empty — the cutting plane met no geometry at all; a refusal, not a zero |
| `координата_мм` | the coordinate the cut was taken at, in mm |
| `центр_ширина_мм` | the centre of the cut along the width axis, in mm |
| `центр_глубина_мм` | the centre of the cut along the depth axis, in mm |
| `мм_на_пиксель` | millimetres per pixel of the frame or of the reference crop |
| `кадр_мм` | the frame's size in millimetres, as `[width, height]` |
| `размах` | the span of a scanned row of the reference — the measured extent from edge to edge |
| `разрывов` | breaks — pixels inside that extent that failed to differ from the background; non-zero means the row cannot be trusted |
| `n_угольников` | the count of n-gons |
| `треугольников` | the count of triangles |

Other keys are glossed where they first appear below.

**English aliases exist** for channel names — `shading`, `silhouette`, `wireframe`, `curvature`,
`working` — and for view angles — `front`, `back`, `left`, `right`, `top`, `bottom`,
`three_quarter` (and `three_quarter_back`). The constants have aliases too: `pp.RING_CHECK` for
`pp.ПРОВЕРКА_КОЛЬЦА`, `pp.ORBIT` for `pp.ОБЛЁТ`. Either spelling works; the Russian ones are used
in this file because that is what the source of the toolkit says.

---

## 4. Correspondence of operations

### 4.0 Setup (M1)

| What | What does it | What checks it |
|-----|--------------|-----------------|
| A guide for a measurement | `pp.guide(label, z_mm, width_mm, depth_mm, collection)` — an empty of type `CUBE`, `show_in_front`, `hide_select` | `get_objects_summary`: the `EMPTY` count grew by the number of measurements; `pp.scene_report()["геометрических_объектов"]` (geometry objects) did not change |
| Scene sets | the collections `REFERENCE`, `MARKUP`, `MODEL`; switching via `layer_collection.hide_viewport`, exclusion from the render via `exclude`; locking selection via `hide_select` on the objects | `get_objects_summary` |
| Showing only the working zone | the visibility of the block's collection; the rest hidden | the markup does not work as an open table |
| Aligning the axis | shift the **reference**, then re-confirm the placement per R5 ([work-rules.md](work-rules.md)) | `pp.section()`: `центр_ширина_мм ≈ 0` |
| The zero point in depth | an empty `DEPTH_ZERO` in the scene plus the number in the M1 report: the scene survives the session, the report does not | `pp.bbox()["центр_мм"][1]` (centre, mm) |
| Units and scale | `scene.unit_settings` | `pp.scene_report()["мм_в_единице"]` (mm per unit) |

### 4.1 The operations of catalogue 10.1

The catalogue itself is in [phases.md](phases.md), §10.1.

| Operation of the regulation | What does it | What checks it |
|---------------------|--------------|-----------------|
| Set up mirroring | the `"MIRROR"` modifier, `use_axis`, `use_clip`, `use_mirror_merge`, `merge_threshold`; **mandatory** `mirror_object` (6.1). Created **first**, before subdivision | `pp.mods()["отражение_раньше_сглаживания"]` (mirror before subdivision), `pp.seam()` |
| Engage subdivision | `"SUBSURF"`, `subdivision_type="CATMULL_CLARK"`, **`levels == render_levels == L`**; inequality is forbidden: the gauge is taken at the viewport level, and if the two diverge it was not taken off the render | `pp.mods()["уровни_показа_и_выдачи_равны"]` (viewport and render levels equal); `pp.budget()["множитель"]` (multiplier) = **2 × 4^L** with a mirror in the stack and 4^L without it — verified: cage 48 → final 384 |
| Create the primary volume | `bmesh.ops.create_cube` into a new mesh; **the object's origin on the plane of symmetry** | screenshot: fits inside the zone's contour; `pp.bbox()` |
| Cut the primary volume up to load-bearing density | `bmesh.ops.subdivide_edges` | `pp.budget()`, a screenshot of the envelope |
| Continue the shell | `bmesh.ops.extrude_face_region` + `translate`; the ring's scale via `bmesh.ops.scale`. **The source faces must be deleted** — see 6.20 | `pp.section()` at the coordinate of the **nearest measurement**; `pp.topology()["итог_рёбер_с_3+_гранями"] == 0` (final: edges with 3+ faces) |
| Run a loop along a form line | `bmesh.ops.bisect_plane` without clearing, or `subdivide_edges` around a ring | `pp.topology()`: no n-gons and no poles were added |
| Close an end cap | **not** `holes_fill`: it closes a contour with a single face, and on a ring of six or more edges that is an n-gon, which is forbidden everywhere. The options: `bmesh.ops.grid_fill` — but it needs a contour with an even number of edges and two opposing chains; otherwise draw the contour in with rings via `extrude_edge_only` + `scale` and close it with a quad grid by hand | `pp.topology()`: `итог_открытых_рёбер == 0` (final: open edges) **and** `n_угольников == 0` |
| Cut a loop | `bmesh.ops.subdivide_edges` along a ring of edges | comparison of `pp.shots()` before and after |
| Collapse density | `bmesh.ops.dissolve_edges`, addressed | `pp.topology()` with the addresses of poles, `pp.section()`: the bounding measurement did not drift |
| Delete a region | `bmesh.ops.delete` with the right `context` | `pp.topology()`: the boundary is either recorded or closed |

### 4.2 Shaping tasks (10.4)

See [phases.md](phases.md), §10.4.

| Task | With what | What checks it |
|--------|-----|-----------------|
| Create a surface turn | the load-bearing operation plus movement of vertices inside the same step | `pp.section()["контуров"] == 2` at the height of the turn |
| Flatten a section | movement of vertices; the pre-operation bounding measurement is put into `pp.KEEP` **before** the edit | `pp.section()` against what was kept in `pp.KEEP`, and then, as a separate beat, against the measurement |
| Bow the surface inward | movement of vertices | the silhouette did not change (for hollows outside the silhouette) — comparison of `pp.shots("силуэт")` (silhouette) |

### 4.3 The junction (M5)

| What | With what |
|-----|-----|
| The bounding measurement of an end | `pp.section(ob, coord, axis)` in the plane of the boundary; for a slanted boundary, `bmesh.ops.bisect_plane` with an arbitrary normal |
| The number of segments on an end | the length of the boundary chain: `[e for e in bm.edges if e.is_boundary]` before the end is closed |
| Gap and interpenetration | `mathutils.bvhtree.BVHTree.FromObject` for both parts and `overlap()`; distance via `find_nearest` over the boundary vertices — `?` until the first pair of parts |
| The direction of edge flow across the boundary | the addresses of boundary vertices from `pp.topology()` on both parts |

**The general rule for working with the mesh.** Do not enter edit mode; work through
`bmesh.new()` → `from_mesh()` → `bmesh.ops.*` → `to_mesh()` → `free()`. This is **our** choice, for
the sake of reproducibility, and not an instruction from the server: the server in fact recommends
operators for standard actions (see 6.6). The reason for the choice: a `bmesh` result depends
neither on the mode, nor on the selection, nor on the active object, whereas operators depend on
all three and change them as a side effect.

---

## 5. The regulation's checks

| Check | Tool | Verified |
|----------|-----------|-----------|
| The gauge taken off the final surface | `pp.section()` through `evaluated_get(...).to_mesh()` | ✓ cage 6 polygons → final 44 |
| Two separate contours in a surface-turn zone | `pp.section()["контуров"]` | ✓ a torus about Y: 2 through the hole, 1 below |
| The mirror seam is welded | `pp.section()` gives a single contour | ✓ half a cube plus a mirror |
| The seam: deviation, doubles, poles | `pp.seam()` | ✓ a clean seam: 16 vertices, deviation 0, 0 doubled, 0 poles |
| The part's overall bounding measurement | `pp.bbox()` against the three numbers from R6 | ✓ agrees with `section` at the same height |
| Quads only | `pp.topology()["n_угольников"] == 0` with addresses | ✓ a clean cage: 48 quads, 0 others; a broken one: 2 heptagons with addresses |
| Zero open edges | `pp.topology()["итог_открытых_рёбер"]` | ✓ the half's cage has 16 open, the final after mirroring 0 |
| Stack order and equality of levels | `pp.mods()` | ✓ order and levels are read; when the levels diverge, `evaluated` fails |
| Transforms not baked in | `pp.mods()["стек"]` (stack) — MIRROR and SUBSURF still there | ✓ |
| Polygon count against the range | `pp.budget(ob, share=(min, max))["вердикт"]` (verdict) | ✓ 768 out of (200, 800) → "near the upper bound", 32 to spare |
| Full comparison against the markup | `pp.gauge()` — empty and turn are counted separately | ✓ three levels gave three different outcomes: in tolerance, turn, empty |
| The contents of the scene, R1 | `get_objects_summary` | ✓ |

### 5.1 Perception channels

| Channel | With what |
|-------|-----|
| Silhouette fill | `pp.channel("силуэт")` — flat lighting, one colour, overlays off |
| Smooth shading | `pp.channel("затенение")` (shading) — `use_smooth` via `foreach_set`, an even grey |
| Wireframe over the smoothed result | `pp.channel("каркас")` (wireframe) — `show_wire`, `show_all_edges`, `show_on_cage` |
| The three-quarter view against the reference | `pp.view("три_четверти")` (three_quarter) + a screenshot; the reference's own ¾ view file is placed beside it if there is one. An orthographic view of the model and a perspective render of the reference are compared by proportions, not by overlay |
| Comparison against a point | `pp.shots()` before and after, reading the two PNGs |
| Mirroring the picture | flip the PNG **outside** Blender. A mirrored view angle is not a substitute: `pp.view` with a reflected azimuth shows the model's other side, not a mirrored picture of the same side |

The way back to the working state is `pp.channel("рабочий")` (working).

---

## 6. Traps

### 6.1 A mirror reflects about the object's origin, not the world's ✓

A cube whose origin is at `X = 250 mm`, mirrored in X **without** a mirror object:

| Setting | Result along X | Centre |
|-----------|-----------|-------|
| no `mirror_object` | −250 … 750 mm | **250 mm** |
| `mirror_object` = an empty at zero | −750 … 750 mm | **0 mm** |

The model looks right. The only thing that is wrong is the plane of symmetry — and that is
discovered at the junction with the neighbouring part, when everything has to be redone.

### 6.2 ~~`use_axis` is assigned element by element~~ — claim retracted

The first edition said here that `use_axis` may not be assigned as a tuple, marked "verified".
**That was wrong.** Assigning a sequence to a property array is the normal way to do it; the
failure that was observed had a different cause, found later: the mirror was reflecting about the
object's origin (6.1) rather than the world's, and the halves coincided with themselves. The claim
is retracted in full.

The lesson: the mark "verified" is earned by verifying **that very** claim, not by an observation
that fails to contradict it.

### 6.3 A gauge taken off the cage reads low ✓

The cage sits **outside** the result: Catmull-Clark shrinks the volume. A gauge taken from
`ob.data` is invalid.

### 6.4 Documentation search is strict ✓

`search_api_docs` requires **every** word of the query to occur. `"bmesh ops extrude face
region"` → zero; `"extrude_face_region"` → the exact signature. Search by name, not by
description.

### 6.5 The documentation is on disk ✓

The blender-mcp package ships the documentation as files: `blmcp/data/` holds `api/` with 2062 RST
files and `manual/` with 2217, about 25 MB. Where that lands depends on how the server was
installed — under a `uv tool install` on Python 3.12 it is
`~/.local/share/uv/tools/blender-mcp/lib/python3.12/site-packages/blmcp/data/`; find yours once and
note it. Grep gives you a regular expression and context. For reconnaissance, grep; for an exact
signature, `search_api_docs`.

### 6.6 `jump_to_*` changes mode, selection and visibility ✓ (from the server's source)

`jump_to_view3d_object_by_name` performs: `bpy.ops.object.mode_set(mode="OBJECT")`,
`bpy.ops.object.select_all(action="DESELECT")`, `obj.select_set(True)`, assigns the active object,
takes the view out of the camera into perspective, calls `view3d.view_selected()`; with
`allow_edits` it also clears `hide_viewport`, `hide_set` and `exclude` from collections.

Do not call it between `pp.view()` and a screenshot, nor before a block that depends on the
selection.

**Separately, about the server's advice.** The server recommends: operators (`bpy.ops`) for
standard actions, since they take care of defaults and context; the data API (`bpy.data`) for
precise control and to avoid side effects. Our choice in favour of `bmesh`/`bpy.data` follows from
the second half of that advice; it does not deny the first.

### 6.7 Edits made in edit mode are not visible in `ob.data`

In Edit Mode the cage in `ob.data` is stale: a report will return plausible and wrong numbers.
`pp.cage()` and `pp.evaluated()` check the mode and fail loudly.

### 6.8 The order of the stack is visible only on the seam

`modifiers.new()` always appends **to the end**. A SUBSURF created before a MIRROR smooths the
half as a body with an open edge: the seam falls inward. The model still looks right. Check
`pp.mods()`.

### 6.9 `v.is_boundary` eats the whole seam ✓ (from the code)

On the half being mirrored, the seam is an open boundary of the cage, so a "not boundary" filter
in the pole count makes the count of poles on the seam **identically zero**. Poles inside and the
seam are counted separately: `pp.topology()` and `pp.seam()`.
The legitimate degree of a seam vertex on the half's cage is **three**: after the mirror welds it,
it becomes four.

### 6.10 The view angle and the screenshot can come from different areas ✓ (from the server's source)

The screenshot tool takes `context.area` if its `ui_type` matches, otherwise **the largest**
suitable one. Code that takes the first one it finds will, in a layout with two 3D views, set the
angle in one area while the screenshot arrives from another. `pp.view()` repeats the server's rule
and returns `областей_3d` (the number of 3D areas).

### 6.11 The scene's units and scale

One Blender unit equals one metre only when `scale_length == 1.0`. A hard-coded thousand in the
conversion would give plausible numbers, off by exactly that factor. The whole toolkit computes
through `pp.mm_per_unit()`.

### 6.12 `*_for_cli` is a different Blender ✓ (from the server's source)

The eight twins take a path to a file and launch a **separate** `blender --background` on it. If
the live session is holding the same file with unsaved edits, a temporary numbered copy is made
and the work goes through that. The live session will **not see** the result of such a call.

They are good only for reading files that are not currently in work. They must not be used to
mutate.

### 6.19 A rollback silently changes the working file ✓

Opening a point makes the point **itself** the working file. Subsequent saves go into the
directory of points while the working file stays at its pre-rollback state — and the divergence
surfaces several steps later, when it is unclear which of the two files is the real one.

Verified: after a rollback, `bpy.data.filepath` pointed at the snapshot in the directory of
points. `pp.restore()` takes `work_file` and immediately saves the session there; without it, it
returns a field `ВНИМАНИЕ` (attention) with the actual path.

The `pp` module survives the reload of the file ✓ — Blender is not restarted. But every reference
to an object taken before the rollback is invalid: take them again through `pp.obj()`.

### 6.20 Continuing the shell leaves a wall inside ✓

`bmesh.ops.extrude_face_region` **does not delete** the source faces: after the shell is
continued, they stay inside the volume as a partition. From outside it is invisible at every
angle — the form looks sound.

Verified on a rehearsal of the cycle: continuing eight faces gave **52 edges with three or more
faces**, eight poles on the seam and a polygon count outside its share, while the three-quarter
view was flawless.

**The sign:** `pp.topology()["итог_рёбер_с_3+_гранями"] > 0`.
**What to do:** delete the source faces in the same block — `bmesh.ops.delete(bm, geom=<source>,
context="FACES_ONLY")`.
**The decision on discovery:** roll back, do not shape your way out of it: the cause is in the
operation, not in the form.

### 6.21 Projection onto a form tears the seam ✓

Shaping by projecting vertices onto a target form (an ellipsoid, a sphere, an envelope) also
displaces the seam vertices across the plane of symmetry. Giving them back `x = 0` **after** the
projection does not save it: the other coordinates have already moved, and a slit with notches at
the ends runs down the centre.

Verified on the very first step of the real build.

**What to do:** shape by **scaling from the axis of symmetry**, not by projection. Multiplying `x`
by any factor leaves `x = 0` at zero by construction, and the seam cannot come apart. The check is
`pp.seam()` immediately after shaping, not at the end of the step.

### 6.22 `pp.seam()` does not see a ridge on the seam ✓

The seam check looks at the **positions** of vertices: whether they lie on the plane, whether they
have crossed it, whether there are doubles and poles. It does not look at **what angle** the
surface meets the plane at, and a ridge on the seam comes from exactly that: if the surface
crosses the plane other than perpendicularly, the mirror welds the two halves into a wedge. The
numbers are clean all the while.

The only instrument against this is the **smooth shading channel** and a front view: a real seam
ridge will lie exactly on the centre line. Check with the channel, not by guesswork: on the very
first step a kink I took for the seam turned out to be a vertical edge of the original box, and
the front view under smooth shading showed it at once.

### Inspection in two passes — how it is executed

The rule — what the two passes judge, how the question is put, and why the reference is attached —
is [step-cycle.md](step-cycle.md), §4, beat 4. Here only how it is executed against the server.

Beat 4 requires two passes: the surface and the mesh. In Blender these are two sets of screenshots
of the same view angles, taken **through different channels**:

| Pass | Channel | Angles |
|-------|-------|---------|
| Surface | `pp.channel("затенение")` | `pp.ПРОВЕРКА_КОЛЬЦА` + `pp.orbit()` |
| Mesh | `pp.channel("каркас")` | the same |

The screenshots are reviewed by **separate agents with precise questions**, not by one general
look:

1. **Surface** — the form: how it flows, bulges, hollows, kinks, how it sits on the reference.
2. **Mesh, edge flow** — n-gons and triangles, poles and where they are, broken loops, skewed
   flow, uneven density.
3. **Mesh, vertex placement** — even distribution around a ring, clumped and stretched stretches,
   seam vertices, symmetry of left and right, rings not where they belong.

Questions 2 and 3 are asked **separately**: the mesh is harder to look at than the surface, and a
general question "how is the mesh" misses both defects at once.

**The reviewer is given the reference.** Without it they judge by their own idea of the object
rather than by what we are building, and produce findings about somebody else's form. Verified on
the very first review: the agent wrote that the maximum width of the head should sit a third of
the way down from the top — true for a typical skull and false for our mannequin, where it is at
the middle, exactly where the model has it. A whole item of the review turned out to be about a
different object.

The reviewer's assignment must include:

1. **crops of the reference** for the zone under review — front and profile, the very files the
   work is going by;
2. **screenshots of the model over the reference** — the working channel shows the reference
   behind the model, and on those the divergence of contours is visible;
3. **an explicit ban on judging by general knowledge of the object**: the target is this
   reference, not a typical head, arm or torso;
4. **the tolerance and what is being measured** — otherwise "far too wide" will turn out to be two
   millimetres.

**Reviewers do not go into Blender.** The screenshots are prepared by whoever is running the step,
in one call to the server; reviewers read only the finished files. The reason is simple: there is
one server, the state of the scene is shared, and two calls at once mean a view angle set by one
and a screenshot taken by another. For the same reason reviewers are run **one at a time**, not
all at once.

### 6.23 A grid cannot be reconstructed from coordinates ✓

A grid patch (a cap, a patch) is tempting to take apart into rows and columns by sorting the
vertices by coordinate: collect the unique X, the unique Y, and find every vertex its cell. This
works exactly once — while the patch is flat. After the first shaping the vertices scatter, there
become more unique coordinates than cells, and the mapping confuses places.

Verified: an attempt to reposition the crown dome that way sent vertices to the wrong places — the
seam produced ten poles instead of zero, four open edges appeared and twenty-eight edges with
three faces. The mesh did not visibly fall apart; the numbers caught it.

**What to do:** take the patch apart **by connectivity**, not by coordinates. A vertex's ring is
its distance in edges to the boundary of the patch, measured inside the patch itself; that does
not depend on where the vertex has already been moved. The order of vertices within a ring is a
walk along edges, not a sort by angle.

**The decision on discovery:** roll back. A scrambled mapping is repaired by going back, not by
touching up.

### 6.23a Selecting a ring by coordinate holds until the first slanted loop ✓

A continuation of 6.23, and more dangerous than the original trap because it fires later. While
all the rings are horizontal, height works as the marker of a row, and the selection
`abs(v.co.z - z) < tol` gives exactly the ring. An undercut requires a **slanted** loop — and at
that same moment the marker breaks: one vertex of the slanted ring sits at the height of its
neighbour, the selection grabs too much, and the walk yields three ends instead of two.

Verified: the jaw ring, rising from 1522 at the front to 1566 at the back, put one vertex exactly
at 1555. A row of thirteen vertices arrived as fourteen. The error was loud — the walk failed by
itself — but it might not have been: had the extra vertex landed in the middle of the path, the
walk would have gone through silently and put someone else's vertex onto the ellipse.

**What to do:** the marker of a ring is the **distance in edges from a known boundary**, not a
coordinate. The seed is the cage's open boundary, minus the seam; from there the rings grow by a
breadth-first walk. The marker does not depend on where the vertices have moved and survives any
shaping. In the toolkit: `pp.rings`, `pp.ring_order`, `pp.place_ring`.

**When writing the seed:** the connectivity of boundary vertices is computed **over the boundary
edges themselves**. A walk over all the edges of a vertex goes off into the mesh and merges all
the boundaries into one. And `_components` returns a pair — groups, discarded — not a list of
groups: `len()` of it is always 2.

### 6.23b Guides cover the cage in a screenshot ✓

Guide empties are drawn over the cage and read on a render as dense black bars. A ring's line that
falls under such a bar disappears.

Verified: the mesh review reported that ring 1593 is not in the model, and backed it up with a
threshold scan of the rows. The ring was there; it was hidden by the rectangle of the guide
standing at that same height — which is natural, that is where the guide was put.

**What to do:** shoot the wireframe channel with the guides removed. **A negative finding on a
screenshot** ("there is nothing here") requires the same check against the mesh as a positive one:
absence from a picture is not absence from the model.

### 6.24 A screenshot's view angle is verified by measuring the silhouette, not by eye ✓

"Looks like a skewed angle" is an unreliable judgement: the studio light is bound to the camera
and shines from the side, so even a strict top view reads as three-dimensional, and a shaded edge
looks like the edge of another body part. That is exactly what happened: the screenshot was
declared skewed and turned out to be exact.

**A recipe for checking, objective and cheap.** The aspect ratio of the silhouette in the
screenshot must match the ratio of the corresponding sides of the bounding box:

| Angle | What to compare |
|--------|----------------|
| top | silhouette width/height against `ширина_мм / глубина_мм` from `pp.bbox()` |
| front | silhouette width/height against `ширина_мм / высота_мм` |
| right | silhouette width/height against `глубина_мм / высота_мм` |

Agreement within a per cent — the projection is right. A discrepancy of several times over — wrong
angle. Verified: the view from above gave 0.8036 against an expected 0.7996.

**When to apply it:** once after setting up the shooting, and every time a review produces findings
that look like projection distortion — "a flat cap", "a chamfer on the slope", "a spike on the
side".

### 6.26 Lighting eats the contour, and the review measures the wrong thing ✓

The studio light shines from one side, and the opposite side of the object converges in brightness
with the background. The silhouette disappears there — and the reviewer is measuring the
divergence from the reference precisely by the silhouette. As a result they describe not the form
but the boundary of illumination: "a flat cap", "a chamfer on the slope", "a spike on the side"
appear where the light simply ran out.

The "silhouette" channel did not save this, because it painted the object nearly black,
`(0.02, 0.02, 0.02)`, against the viewport's dark grey background — almost zero contrast. Fixed:
**a white object on a black background**, `background_type = "VIEWPORT"`,
`background_color = (0, 0, 0)`.

**The rule for reviewing a contour:** measure the contour **only through the silhouette channel**,
and use the shading channel for the flow of the surface and for kinks. They must not be mixed: in
shading the contour is unreliable, in silhouette the form is invisible.

### 6.25 The light is bound to the camera, not to the scene ✓

During an orbit the light source turns with the camera. Two consequences follow. First: mirrored
pairs of angles differ in their shading, and that is normal — what you compare in them is the
contour, not the brightness. Second: a shaded edge reads as the edge of another part, and that is
an easy mistake to make. The reviewer has to be told this explicitly, or they will describe a
shadow as geometry.

### 6.27 A grid cap has no concentric rings ✓

A grid patch invites being laid out "by rings": ring 0 is the boundary, ring 1 the next one, and
so on up to the crown, each ring at its own height on the dome. **This is wrong.** A ring of a
grid is a square ring, not a circle: its corners lie three times further from the centre than the
midpoints of its sides. Lay such a ring onto a section of the dome and you get either a crease
with spikes at the corners, or corners flying far outside the form.

Verified twice, both attempts rolled back: the first rolled the vault into a crease with an
overhang, the second threw the corners of the patch out to a radius of 66–73 mm on a base of
56 mm.

**What this means in substance.** A grid cap imposes square symmetry on the dome, and the dome is
round. Any layout "by radius" runs into that mismatch. The right move is not to lay out the
existing patch, but to change it for a scheme whose lines follow the form: either a cap with a
different division, chosen to fit the dome's proportions, or a different way of closing.

**Until the scheme is changed**, the patch's unevenness is a known defect, not grounds to run the
cycle: it lies outside the zone of the current operation and is closed by the density pass in M4.

### 6.28 An argument between the markup and the reference is decided by the reference, and decided by a number ✓

The rule is [measure-vs-eye.md](measure-vs-eye.md), §5.4 — a finding about size made by inspection
is verified by measurement before any fix. Here it is the same review, seen from the instrument's
side.

A review by eye can pose a question and cannot answer it. Verified on a full review of the form:
of nine claimed divergences four were large, and all four were false.

| Claimed by the review | In fact |
|---|---|
| the neck is 17 mm smaller than the reference | 1.5 mm, and with the opposite sign |
| the back of the head is 25–35 mm too high | 3.7 mm |
| the width at 1600 is 10 mm too great | 1.0 mm |
| the front of the neck leans 9 mm backwards | 1.7 mm |

The only real divergence — the tip of the chin 4 mm too high — was absent from the report. The
cause is not carelessness in the review: it measured on a crop of the reference in pixels,
choosing the row and the edge by eye, and accumulated row error.

**What to do:** verify any dimensional finding of a review by a pixel measurement of the reference
itself (`pp.ref_measure`) before editing. An edit made on an unverified finding costs twice: it
spoils correct form and hides the real defect.

### 6.29 Pixel measurement of the reference: the background per row, the threshold low ✓

Two failures, both silent.

*One background pixel per frame.* The background on art is not perfectly even. A threshold of 0.06
off the corner pixel produced a row where the light edge of the head did not differ from the
background: the silhouette fell apart, `min`/`max` returned a clipped bounding measurement, and the
row looked ordinary. The cure is a background taken **at the start of that same row**, and the
counter `разрывов` — the number of pixels inside the extent that did not differ from the
background. A non-zero counter means the row cannot be trusted.

*The threshold.* The working value is around 0.02. The price is that the antialiased edge is
caught — the measurement comes out wider than the true one by roughly a pixel per side, the bias is
one-sided, and it has to be remembered.

*Rounding of the row.* One pixel vertically is two millimetres. On a smooth stretch the cost of the
error is nil; on a **cliff** in the contour (the tip of the chin, where the silhouette jumps by
40 mm) a shift of one row changes the answer entirely. At cliffs, measure with a bracket of two
neighbouring rows.

### 6.30 A measurement of one of two families cannot be checked against the silhouette ✓

In a surface-turn zone the cutting plane gives two contours, and the markup describes them
separately.
A measurement of the rear family ("the neck behind the chin") says where the neck is and says
**nothing** about the front edge of the silhouette at that same height.

Verified: checking the model's front contour against the rear measurement, I declared a correct
placement of the jaw ring an overshoot and raised the tip of the chin by four millimetres. The
error was found only by measuring the reference's silhouette.

**The rule:** a silhouette is checked against a silhouette, a section gauge against a section. The
list of measurements taken out of ordinary verification is kept in the topology plan and is read
at the moment of verification, not recalled from memory.

### 6.34 The scale of a screenshot must come from the tool, not from your head ✓

An inspection measures in pixels. Only whoever took the screenshot can convert pixels to
millimetres — and if they get it wrong, **all** the reviews get it wrong at once, including the
adversarial check: the lenses get the same wrong number and therefore refute nothing.

Proven ruinously. I took `distance` for the width of the frame in millimetres. The true relation is
different: Blender sets the field with a 36 mm "sensor" over half of the **larger** side of the
frame, so

    frame width = 2 · (36 / lens) · distance

With a 50 lens and a distance of 200 that is 288 mm, not 200 — the scale was low by a factor of
1.44. The review issued nine "confirmed" findings, and the chief of them — "the neck is a third
thinner than the reference" — was entirely generated by that error: the screenshot gave 675 pixels,
which at the correct scale is 101 mm against the reference's 102.

**What to do:** hand out the scale together with the screenshots, taking it from `pp.frame_scale()`;
no inspection assignment goes out without it. The function computes from the **lens and the
distance**, not from `window_matrix`: the window matrix is not recomputed until a redraw and,
immediately after a change of view, describes the previous frame.

**A one-action check:** take a silhouette, measure its width in pixels at a known height and compare
against `pp.section()`. A discrepancy of more than a couple of per cent means the scale is wrong.

It is worth noting separately that it was the **inspection** that found the error, not I: five
checkers independently fitted the visible lines of the cage to the declared ring heights and got
0.145…0.150 instead of 0.1042. A negative finding about the assignment itself is a legitimate
finding.

### 6.31 The frame does not reset itself ✓

A call that sets the view **with no focus and no distance changes nothing**: the camera stays where
the previous call left it. A wide shot taken after a close-up silently comes out as the same
close-up.

The failure is silent and especially harmful: the screenshot looks perfectly sound, while the scale
stated in the inspection assignment turns out to be false — and all the review's estimates of
heights drift. Verified: two files, presented to the inspection as a wide shot and a close-up,
were byte-identical; the review found this, not I.

**What to do:** when the focus is omitted, the frame is set up afresh from the part (`pp._frame`).
This is the same class of failure as the poisoned "working" channel (6.x): the tool hands back a
plausible picture of something other than what was asked for. The general rule — **state of the
view is set explicitly, not inherited**.

### 6.32 A supporting loop made by oversight ✓

A hard edge under subdivision is made **deliberately**, by putting a second ring right up against
the first. The same result arrives by oversight, when two rings come close somewhere you did not
intend.

Verified: the slanted jaw ring settled at Z 1548 on the sides, and the ring at the top of the neck
stood at 1550 — two millimetres. Around the whole circuit except the front, the rings stuck together
and produced a crease running as a ring around the entire head: a collar, out of which the neck
emerged like a pipe out of a socket. No numeric check showed it, because the position of the
surface agreed with the reference to within two millimetres.

**The sign:** a slanted loop crosses a neighbouring horizontal one in height. In the neighbourhood
of the crossing the distance between them drops to single millimetres over a long stretch of the
circuit.

**What to do:** move the rise of the slanted loop into the sector it was slanted for, and check
along its whole length that at least half a ring's spacing is left to the neighbouring rings. Hold
the tip not by overshooting the cage but with a **crease on the edges** — a crease is local,
whereas rings closing on each other acts along the whole circuit.

### 6.33 Equal arc computed for each ring separately skews the meridians ✓

A ring is laid onto an ellipse by its front, back and width, distributing the vertices by equal
arc. While neighbouring rings are close in proportion, this is all correct. As soon as the front
moves far between them — the chin against the neck, fifty millimetres — the ellipse's **centre**
shifts, and the side vertices, which had no business moving, move with it.

A vertex sits at a quarter of the arc of its own ellipse, but on its neighbour that quarter falls
at a different place in space: the meridian runs diagonally, and the strip of faces acquires a
shift around the whole circuit. On the surface this reads as a shelf and as swirls.

**What to do:** compute the distribution **once** per zone and hand it to all of that zone's rings
(`pp.ring_phis` → `pp.ring_positions(..., phis=...)`). The meridians then run straight.

### 6.13 A redraw is scheduled by `tag_redraw`, not by `view_layer.update`

`view_layer.update()` updates the dependency graph and has nothing to do with redrawing the view.

### 6.14 A cut exactly through vertices

With a zero tolerance on the cut, vertices lying exactly on the plane are distributed between the
sides unpredictably, and the contour tears. And a cut along a ring of the cage is exactly that
case. `pp.section()` cuts with a non-zero tolerance.

### 6.15 A tangent section looks like two contours

A cut tangent to the surface leaves single vertices with no edges. Counting them as components
gives "two contours" where there is no turn. `pp.section()` discards them and reports them in a
separate field, `касательных_точек` (tangent points).

### 6.16 `is_manifold` is false for a boundary too

An edge's `is_manifold` property is false both for a boundary edge with one face and for a wire
edge with none. A direct count off it is always inflated by the size of the open boundary. What
must be counted separately is edges with **three or more** faces.

### 6.17 Undo does not work for direct data edits

Edits made through `bpy.data` and `bmesh` from `execute_blender_code` do not put a step on the undo
stack: `Ctrl+Z` in the interface will roll back to the wrong place or not at all. The only reliable
rollback is a file point (`pp.snapshot` / `pp.restore`), which is why a step's rollback point is
mandatory, not desirable.

### 6.18 What `execute_blender_code` returns

- **Only** the variable `result` is handed outwards. `print()` does not make it out: a block that
  "did everything and printed it" looks like a block that did nothing.
- The response is limited in size. Lists of addresses and lines of a comparison are truncated on
  the toolkit's side (`адреса_полюсов[:30]` — pole addresses), not handed over whole.
- An exception inside a block interrupts it halfway: part of the edits have already been applied.
  Hence the requirement of idempotency — a block must survive being run again, and the step's
  rollback point is created **before** the operation, not after.

---

## 7. What not to do

| Wrong or redundant | Why | Instead of this |
|-----------------------|--------|--------------|
| Writing a script to find out the contents of the scene | There is `get_objects_summary` | An inspection tool |
| Writing a new gauge script for every step | Unverified code, incomparable numbers | `pp.*`, installed once |
| Keeping intermediate values in a call's variables | Bare `globals()` does not survive a call ✓ | `pp.KEEP` |
| Taking the gauge off `ob.data` | The cage sits outside the result | `pp.section()`, `pp.bbox()` |
| Computing millimetres by multiplying by a thousand | True only when `scale_length == 1` | `pp.mm_per_unit()` |
| Taking a report without leaving edit mode | `ob.data` is stale | `pp.cage()` fails loudly |
| Working with the viewport and render levels diverged | The gauge goes by the viewport one | `pp.mods()`, `evaluated` fails loudly |
| Judging the form by orthographic views | The form falls apart at three quarters | `pp.view("три_четверти")` |
| Guessing the name of an operator or a parameter | A wrong string of a type breaks the script silently | `search_api_docs`, grep over `data/api` |
| Setting up a mirror without `mirror_object` | It reflects about the object's origin ✓ | `pp.seam()`, `pp.mods()` |
| Creating SUBSURF before MIRROR | `modifiers.new()` appends to the end; the seam falls inward | `pp.mods()` |
| Closing an end with `holes_fill` | One face per contour is an n-gon, forbidden everywhere | `grid_fill` or a hand-made quad grid |
| Calling `jump_to_*` next to a screenshot | It changes mode, selection, visibility ✓ | `pp.view()` |
| Mutating through `*_for_cli` | That is a different process; the live session will not see it ✓ | Only `execute_blender_code` |
| Splitting one check into four calls to the server | Every call is a round of waiting with no new knowledge | One block for everything that does not require my eye |
| One enormous block for the whole step | A failure cannot be localised, and part of the edits are already applied | Short idempotent blocks, the point **before** the operation |
| Relying on `print()` for a report | Only `result` goes outwards | Assign to `result` |
| Counting on `Ctrl+Z` after edits made from code | Direct data edits are not put on the undo stack | A file point |
| A render instead of a screenshot for the working check | A render is a camera and its settings | A `VIEW_3D` screenshot, `pp.shots()` |
| Leaving `to_mesh()` without `to_mesh_clear()` | The temporary mesh leaks | `with pp.evaluated(ob)` |
| Continuing the shell without deleting the source faces | A wall stays inside, invisible from outside ✓ | `pp.topology()`, the sign is edges with 3+ faces |
| Taking the verdict of a summary of checks for the decision | On the rehearsal the automatic rule said "shape further" where the right answer was "roll back" | Beat 6: the decision is made by the builder, the summary is its input |
| Counting a skipped or two-contour measurement as a passed check | A model that did not reach the level, and a surface-turn zone, are different things, and neither is "in tolerance" | `pp.gauge()` separates the three outcomes |
| Building guides "one per ring" | That is a table of sections brought into the scene | `pp.guide()` — one per measurement |
| Trying something out "just to look at it in the live scene" | Rubbish stays behind, R1 breaks (A7, A12) | A self-cleaning probe in a temporary collection, with a check that the scene was restored |

---

## 8. The step journal

What an entry must contain, and when it is written, is [step-cycle.md](step-cycle.md), §14. Here
only where the file lives and what shape it takes.

The journal is **not** in Blender. One file per part: `<task>/journal-<part>.md`, a table with the
columns:

| step | stage | beat 1's wording verbatim | operation 10.1 | zone | beat 5's result | beat 6's decision | returns to beat 3 | rollback point | change of input |

It is written by appending a line during beat 6, **before the next step starts**. Answering "which
step touched this zone" is a grep over the "zone" column. The list of a stage's steps for the gate
is assembled by reading the file, not from memory.

---

## 9. What has been verified

| Claim | How it was verified |
|-------------|---------------|
| `sys.modules` survives calls, `globals()` does not | two consecutive calls with a counter |
| Gauging the final surface works | cage 6 polygons → final 44 |
| The number of contours distinguishes a turn | a torus about Y: 2 through the hole, 1 below; half a cube with a mirror: 1 |
| A mirror reflects about the object's origin | two cubes, with `mirror_object` and without: centre 0 against 250 mm |
| Documentation search is strict | two queries about the same subject |
| The documentation is on disk | 2062 + 2217 RST files |
| A screenshot takes the largest area | the source of `get_screenshot_of_area_as_image_toolcode.py` |
| `jump_to_*` changes mode, selection, visibility | the source of `jump_to_view3d_object_by_name_toolcode.py` |
| `*_for_cli` launches a separate `blender --background` | the source of `tools_helpers/blender_cli.py` |
| The probe leaves no traces | `сцена_восстановлена: true` (scene restored), `мешей_осталось: 0` (meshes left) in every experiment |
| `mods`, `bbox`, `seam`, `topology`, `budget`, `gauge`, `guide`, `view`, `channel`, `shots`, `snapshot`, `points`, `restore` | a run on the probe: a clean half-cube with a mirror, and a torus about Y |
| The tools stay silent on clean geometry | a clean cage: 0 n-gons, 0 triangles, 0 open edges after mirroring, 0 poles on the seam |
| The tools shout on a broken one | a probe with degenerate caps: 2 heptagons, 4 edges with 3+ faces, 4 doubled seam vertices — all with addresses |
| The legitimate degree of a seam vertex is three | a clean seam of 16 vertices gave 0 poles under the rule "a pole is degree ≠ 3" |
| A mirror doubles the polygon count on top of subdivision | cage 48 → final 384, multiplier 8 = 2 × 4¹ |
| `evaluated` fails when the levels have diverged | `RuntimeError` at `levels=2`, `render_levels=1` |
| `cage` fails on the wrong type | `TypeError` on an empty |
| A viewport screenshot is a real picture | the PNG was opened and looked at |
| A rollback changes the working file | after `open_mainfile`, `bpy.data.filepath` pointed at the point |

**What is left unverified.** One thing: the check of the junction of two parts
(`BVHTree.overlap`) — it cannot be verified while there is only one part. It gets verified on the
second part.

The run took four calls and left no traces: the scene, the collections and the working file
returned to their original state, geometry objects 0, guides 33, the reference's axis at −8.8 mm.

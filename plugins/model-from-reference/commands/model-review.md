---
description: Close a modelling step properly — render the mandatory frame set and run the three inspections against the reference
argument-hint: Optional zone to inspect, e.g. "shoulder girdle 1268-1468"
allowed-tools: ["Read", "Bash", "Glob", "Task", "mcp__blender__execute_blender_code"]
---

# Close the step: three looks

Run beat 4 of the step cycle in full. This is the beat most often executed wrongly — usually by
skipping the top view, skipping the orbit, or skipping the reference — so this command exists to
make the full set the default.

Zone to inspect: `$ARGUMENTS` (if empty, inspect the zone changed by the last operation).

## 1. Find the reference

Locate the reference art the work must match — the actual image files, not silhouette objects in
the scene and not the markup. Both of those are derivatives: they show neither the character of the
surface nor what is drawn on the reference. If you cannot find the reference files, ask the user
where they are before going further; an inspection without them judges against generic anatomy
rather than against this task.

## 2. Render the mandatory set

Two orthographic views are not enough. Render, at minimum:

| Frames | Why |
|--------|-----|
| Two orthographic views | Proportions, overall silhouette |
| **View from above** | Section shape. Without it a box lives on where an oval was intended — a bounding box is identical for both |
| **Orbit, six angles** | Ridges standing edge-on to the orthographic cameras are invisible in them |
| Smooth shading | Volume, hollows, folds, flat facets |
| Reflective / striped matcap | Continuity of curvature — shows breaks at zero positional error |
| Silhouette fill | Outline without shading noise; from above, this is the fastest oval-or-box test |
| Wireframe over the smoothed result | For the flow and placement looks |
| Close-ups of the zone | A defect a fraction of a millimetre deep is invisible in a wide shot |

In Blender with the session toolkit — `${CLAUDE_PLUGIN_ROOT}/skills/model-from-reference/scripts/pp_blender.py`
— this is roughly:

```python
pp.shots("ortho", D, angles=("front","right","back","top"), chan="shading", ob=ob)
pp.shots("curv",  D, angles=("front","right","back","top"), chan="curvature", ob=ob)
pp.shots("sil",   D, angles=("front","right","top"),        chan="silhouette", ob=ob)
pp.orbit("orb",   D, chan="shading", ob=ob)
pp.shots("wire",  D, angles=("front","right","three_quarter","top"), chan="wireframe", ob=ob)
pp.shots("zone",  D, angles=("front","three_quarter","right","top"), chan="shading",
         ob=ob, focus=(x, y, z), distance=d)
```

Record the **frame scale** — millimetres per pixel and the height of the frame's top edge — and
pass it to every inspector, so they can convert a pixel row into a height.

## 3. Look yourself first

Before dispatching anyone, open the top view and one orbit angle yourself. You are about to ask
three people a question; knowing the answer to part of it makes the rest of their findings easier
to weigh — and if the top view already shows a box, that is the finding, and you can say so
plainly rather than discovering it third-hand.

## 4. Dispatch the three looks, in parallel

Launch `surface-inspector`, `edge-flow-inspector` and `vertex-inspector` in the same message so
they run concurrently. Each gets:

- the reference image paths — **the reference itself, not a paraphrase**;
- the frame paths for its channels;
- the frame scale and how to convert a pixel row to millimetres;
- what the object is, factually — including which parts are boundaries where a neighbouring mesh
  attaches.

And each is asked according to the rules for putting the question:

- **Do not say what was just built** or how it should read. Name the zone by coordinates, not by
  meaning. Saying it up front turns inspection into confirmation.
- **Do not grant indulgences in advance.** Known defects outside the zone are filtered *after* the
  inspection, when findings are reviewed — not before.
- **Ask about the arc directly.** "Are there bumps and creases" is a question about position, and a
  curvature break answers "no".

## 5. Weigh the findings

The looks are voices, not verdicts. Two things to do before acting:

- **Verify findings about size by measurement** before acting on them. A finding about *form* is
  authoritative — measurement is blind to form. A finding about a *dimension* is a hypothesis until
  a number confirms it.
- **Check findings against the reference.** An inspector may demand detail the reference does not
  have. Anatomy that is not on the reference is not a defect, and sculpting it is inventing against
  the art.

## 6. Decide

Report to the user: what each look said, which findings survived checking, which were dismissed and
why, and the decision.

The step closes only when **none of the three looks** names a defect in the affected zone. A fix
after a bad inspection leads to a new inspection, not to the next operation — even when the fix
looks obvious and small. "The numbers are clean" is not grounds to close anything.

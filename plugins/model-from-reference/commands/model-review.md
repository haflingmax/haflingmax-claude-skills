---
description: Close a modelling step — render the mandatory frame set and run the three looks against the reference
argument-hint: "[zone, e.g. shoulder girdle 1268-1468]"
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

Also collect, because the inspectors need them and cannot derive them:

- **the form tolerance** for this part, and **what is being measured** against it — without these,
  "far too wide" turns out to be two millimetres;
- **crops of the reference for the zone**, front and profile, at a scale where the zone fills the
  frame.

## 2. Render the mandatory set — in one call

You prepare every frame; the inspectors read finished files and never touch Blender. There is one
server and the scene state is shared, so a view angle set by one caller and a screenshot taken by
another is a real failure mode. Render everything in a single call.

Two orthographic views are not enough. The set is:

| Frames | Why |
|--------|-----|
| Two orthographic views | Proportions, overall silhouette |
| **View from above** | Section shape. Without it a box lives on where an oval was intended — a bounding box is identical for both |
| **Orbit, six angles** | Ridges standing edge-on to the orthographic cameras are invisible in them |
| Smooth shading | Volume, hollows, folds, flat facets |
| Reflective / striped matcap | Continuity of curvature — shows breaks at zero positional error |
| Silhouette fill | The outline alone. **Contour judgements are made on this channel only** — shape and divergence from the art alike — shading darkens the far side and the contour is lost exactly where it is being measured |
| Cage over the smoothed result | For the flow and placement looks — **same angles as the surface pass, orbit included** |
| **Model over the reference** | The working channel draws the reference behind the model, putting the art in the same frame. It shows *that* something is off fastest; the contour itself is still read on the silhouette, which decides if the two disagree |
| Close-ups of the zone | A defect a fraction of a millimetre deep is invisible in a wide shot |

**Hide the guides before shooting the cage.** A guide plane crossing the frame covers the ring line
underneath it, and the reviewer reports a break in flow that does not exist. Switch them off rather
than asking the reviewer to ignore them.

With the session toolkit — `${CLAUDE_PLUGIN_ROOT}/skills/model-from-reference/scripts/pp_blender.py`
— this is roughly:

```python
pp.shots("ortho", D, angles=pp.RING_CHECK, chan="shading",   ob=ob)   # top, front, right
pp.shots("curv",  D, angles=pp.RING_CHECK, chan="curvature", ob=ob)
pp.shots("sil",   D, angles=pp.RING_CHECK, chan="silhouette", ob=ob)
pp.orbit("orb",   D, chan="shading",   ob=ob)
# guides off first, then the mesh pass — same angles as the surface pass
pp.shots("wire",  D, angles=pp.RING_CHECK, chan="wireframe", ob=ob)
pp.orbit("wire_orb", D, chan="wireframe", ob=ob)
pp.shots("over",  D, angles=("front","right"), chan="working", ob=ob)  # model over the reference
pp.shots("zone",  D, angles=pp.RING_CHECK, chan="shading", ob=ob, focus=(x, y, z), distance=d)
# the seam is the one check that adds the back view — the vertex inspector asks for it
pp.shots("seam",  D, angles=pp.SEAM_CHECK, chan="curvature", ob=ob)   # front, back, top
```

Record the **frame scale** — millimetres per pixel and the height of the frame's top edge — and
pass it to every inspector, so they can convert a pixel row into a height. Never guess it: the
camera distance is not the frame width, and a scale reported 1.44× low once produced nine
"confirmed" findings that were all artefacts of that one number.

## 3. Look yourself first

Before dispatching anyone, open the top view and one orbit angle yourself. You are about to ask
three people a question; knowing the answer to part of it makes the rest of their findings easier
to weigh — and if the top view already shows a box, that is the finding, and you can say so plainly
rather than discovering it third-hand.

## 4. Dispatch the three looks — one at a time

Run `surface-inspector`, then `edge-flow-inspector`, then `vertex-inspector`, each in its own
message. The rule is sequential dispatch, not concurrent.

Each gets:

1. **The reference itself** — the image files, and the zone crops. Not a paraphrase of them.
2. **The frames for its channels**, and the frame scale with how to convert a pixel row to
   millimetres.
3. **The form tolerance and what is measured against it** — the one assigned at M2, never the
   measurement tolerance (see references §7).
4. **An explicit instruction to judge against this reference, not against general knowledge of the
   object.** Verified on the very first review ever run: an agent reported that the widest part of
   a head should sit a third of the way down — true of a typical skull, false of the mannequin
   being built, where it is at the middle and the model already had it there. A whole item of the
   review was about a different object.
5. **What the object is, factually** — including which edges are boundaries where a neighbouring
   mesh attaches. State this as fact, not as permission.

And each is asked according to the rules for putting the question:

- **Do not say what was just built** or how it should read. Name the zone by coordinates, not by
  meaning. Saying it up front turns inspection into confirmation.
- **Do not grant indulgences in advance.** "Don't count this as a defect" closes exactly the zone
  the inspection was for. Known defects outside the zone are filtered *after* the inspection, when
  findings are reviewed — not before.
- **Ask about the arc directly.** "Are there bumps and creases" is a question about position, and a
  curvature break answers "no".

One thing the inspectors should be told, because it is a property of the renderer rather than of
the model: the light is attached to the camera, so mirrored orbit angles differ in shading. That is
normal and is not evidence of asymmetry — asymmetry is judged on contours, not on brightness.

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

The step closes when **all** of these hold — the fix loop has closed, meaning none of the three
looks names a defect in the affected zone; the form has been taken as far as this density allows;
the operation's own check has passed; and any remaining divergence from the measurement is either
inside the form tolerance assigned at M2 (measure-vs-eye §7) — not the measurement tolerance — or explained by density and
written into the journal with its number.

A fix after a bad inspection leads to a new inspection, not to the next operation — even when the
fix looks obvious and small. "The numbers are clean" is not grounds to close anything.

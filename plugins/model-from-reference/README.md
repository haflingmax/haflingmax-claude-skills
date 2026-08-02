# model-from-reference

Discipline for building a 3D model that has to match 2D reference art.

Every rule here was paid for with a concrete failure on a real model, and each carries the story of
what it cost. That is deliberate: a rule without its failure is a platitude, and platitudes do not
survive the moment when following them is inconvenient.

## The law it exists to protect

**Measurement belongs in verification. Never in the operation.**

A cross-section's bounding box is identical for an ellipse and for a rounded rectangle. Width and
depth agree to the millimetre while one is a smooth oval and the other is a box with corners.
Measurement cannot tell them apart — it is blind to form by construction.

This is not theoretical. It produced a torso whose front and side silhouettes both matched the
reference within 5 mm of an 8 mm tolerance, and which, seen from above, was a flat slab with two
hard corners and a ridge running its whole height. Nobody looked from above for weeks, because
"the numbers agreed".

So the eye judges form; measurement only guards proportion, and "the numbers are clean" is neither
an argument in an inspection nor an objection to its finding.

## What is in the plugin

| Component | What it does |
|---|---|
| **skill** `model-from-reference` | The step cycle, the inspection discipline, the traps. Loads on any modelling-from-reference task. |
| **agent** `surface-inspector` | Judges form: does the contour run as one arc, where does curvature break, oval or box |
| **agent** `edge-flow-inspector` | Judges how the form is made: loop routing, poles, density gradient |
| **agent** `vertex-inspector` | Judges vertex placement and the mirror seam |
| **command** `/model-review` | Renders the mandatory frame set and runs all three looks against the reference |
| **script** `pp_blender.py` | Session toolkit for Blender: rings by connectivity, pixel measurement of the reference, frame scale, perception channels, orbit, topology counters |

## The three looks

Inspection is three separate questions asked separately, every time. A smooth surface can sit on a
bad mesh and the reverse; a vertex-placement defect is invisible on the surface entirely and
surfaces later, at densification or deformation.

The frame set is not negotiable: two orthographic views, **the view from above**, and **an orbit**.
Without the top view a section's shape is invisible from every angle. Without the orbit, a ridge
standing edge-on to both orthographic cameras is invisible in both.

And the reference itself goes to every inspector — not a paraphrase of it. Without it the looker
judges against generic anatomy, which is a different task. That mistake once produced three
consecutive rejections demanding a triceps and shoulder blades from a shop-window mannequin that
has neither and must not.

## Installation

```bash
/plugin marketplace add haflingmax/haflingmax-claude-skills
/plugin install model-from-reference@haflingmax-claude-skills
```

## Using the toolkit

`pp_blender.py` is written for Blender's Python console via the MCP add-on. Import it once per
session; it survives across calls because `sys.modules` persists while bare globals do not.

```python
import os, sys, importlib.util
path = os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"],
                    "skills", "model-from-reference", "scripts", "pp_blender.py")
spec = importlib.util.spec_from_file_location("pp_blender", path)
pp = importlib.util.module_from_spec(spec); spec.loader.exec_module(pp)
sys.modules["pp_blender"] = pp
```

Blender's Python does not inherit `CLAUDE_PLUGIN_ROOT`, so when driving Blender over MCP, pass the
resolved path in from the calling side rather than reading the variable inside Blender.

Its function names are English; its string arguments and returned dictionary keys grew up in
Russian and stayed that way, because renaming a proven tool to make its documentation prettier is a
bad trade. English aliases are accepted for every channel name and view angle, and
[blender.md](skills/model-from-reference/references/blender.md) glosses the returned keys.

## Provenance

These rules were extracted from a real build — a mannequin modelled from photographic reference —
where each was discovered by failing without it. The build journal that records which rule came
from which failure lives with that project, not here: this plugin holds only what outlives the
task.

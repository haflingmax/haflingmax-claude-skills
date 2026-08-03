# Measurement versus the eye

This file is the law that measurement belongs in verification and never in the operation, together
with everything learned about the ways measurement lies. It holds rule 5 and all of its sub-rules —
how to check your own wording, how a divergence is repaired, the only two things a number may fix
before an operation, when to suspect the measurement rather than the form, and the specific traps
around part boundaries, hidden surfaces, quantised readings, shallow boundaries, creases, limb
openings, convergence loops, stencils, partial rings (§5.13) and shape-preserving interpolation
between levels (§5.14) — followed by the role of markup (§6), what is settled
before the first polygon (§7), and what may not be settled in advance (§8). Read it before any
operation that involves a number, and read it again whenever a mesh matches every measurement and
still looks wrong.

---

## 5. The main rule: measurement belongs in verification, never in the operation

This rule exists because building from a table of sections comes back again and again, changing its
disguise each time: first as a method, then as a plan, then as a list of operations with numbers
inside their wording. Banning one disguise gives no protection against the next one. Only the
ordering protects.

> **Where an operation goes is found by eye, on the reference. Measurement passes judgment
> afterwards.**

### 5.1 How to check yourself

Re-read the wording of the operation (beat 1; see [step-cycle.md](step-cycle.md), §4). If the
location of the operation can be determined **without looking at the reference** — from the table of
measurements, from the plan, from the guides, from a zone or block number, from a fraction of the
part's height — the operation is worded wrongly and gets rewritten before it is performed.

The location marker has to be something visible on the reference: a change in the character of the
form, a drawn line, the point where width stops growing, the start of a surface turn.

### 5.2 How a divergence is fixed

A divergence larger than the **form tolerance** (§7 — the one assigned at M2, not the measurement
tolerance the reference was read with) is fixed by **moving already existing vertices across the
form, without carrying them along it**.

Carrying geometry along the form in order to land inside the form tolerance is forbidden on exactly the same
footing as adding new geometry at the measured height: if the bounding measurement only agrees after
such a move, what is wrong is not the geometry but the form between the things already built, and
that means rolling back to the step that built the zone.

If moving vertices does not remove the divergence, then either the form is wrong (roll back) or the
measurement is wrong (§5.4).

### 5.3 Two exceptions, and only two

These, and only these, are fixed by number before an operation:

1. **The part's boundaries** — where the part ends and the neighbouring one begins. This is not
   form, it is a contract with the neighbouring part: if the boundaries diverge, the joint will not
   meet. What the contract contains is set at M5 (see [phases.md](phases.md), M5).
2. **The part's overall bounding measurement** — the three numbers of the bounding box: height,
   greatest width, greatest depth. **The height at which the maximum occurs is not part of the
   exception:** where exactly the part is widest is found by eye on the reference, and measurement
   only confirms it. Using the height of the widest section in the wording of an operation is
   forbidden.

Intermediate sections are not exceptions **under any circumstances** — not as a zone's bounding
measurement, not as a hint, not as a reference figure.

### 5.4 When it is the measurement under suspicion, not the form

The **measurement** tolerance describes the precision of measuring the reference, and it is not an
obligation on the form to coincide with a number (see [work-rules.md](work-rules.md), R6, "The
status of the metrics"). How far the form may diverge is the *form* tolerance (§7), and that one is
an obligation — a wide one. A divergence is grounds to investigate, not an automatic defect.

**Signs that the measurement is at fault:**

- rolling the step back and moving the ring's vertices does not remove the divergence, and the form
  reads better without hitting the number;
- the measurement falls out of the smooth series of neighbouring levels;
- the level landed in a zone where the silhouette is composite, or where the form is not a function
  of height;
- the divergence is one-sided and does not exceed the measured asymmetry of the reference (see
  [work-rules.md](work-rules.md), R6, item 7).

**First re-measure the source, and only then argue.** The markup is a derivative of the reference:
it was taken once, with one interpretation of the contour, and it may simply be inaccurate. Arguing
with its author costs an exchange of messages; re-measuring the reference costs one call. So the
order is:

1. measure **the reference itself** at the disputed height — the contour of the silhouette, not the
   markup;
2. if the reference confirms the markup, the form is fixed per §5.2;
3. if the reference disagrees with the markup, the measurement is disputed, and the question to its
   author already carries a number taken off the reference rather than bare disagreement.

Re-measuring is mandatory in the other direction too: **a finding about size made by inspection is
verified by measurement before any fix.** Inspection by eye reliably raises the question and cannot
answer it with a number. Proven by a full review: of four large claimed divergences (17, 25–35, 10
and 9 mm) not one was confirmed — the actual figures were 1.5, 3.7, 1.0 and 1.7 mm — while the one
real defect never made it into the report. A fix made on an unverified finding costs twice over: it
spoils correct form and hides the real defect.

**The dispute procedure.** The step is closed with the note "accepted with divergence"; the number
and the sign are written into the journal. The measurement is marked "disputed" and put to the
author of the markup as a question carrying numbers (see [work-rules.md](work-rules.md), R7, "How to
present findings"). Until the author answers, the form is not fitted to that measurement and no new
rings are placed for its sake. The author's answer is either a corrected measurement or a
confirmation, and then the repair follows §5.2.

The limit on how many measurements may be disputed in one zone is set at M2, item 7 (see
[phases.md](phases.md)). Exhausting it returns the zone to M2.

**Violated if:** a divergence is left in silence; it is cured by shifting neighbouring rings; a
measurement is declared wrong without being put to its author.

### 5.5 A measurement that describes a part boundary is not a section measurement

Markup is taken off the reference as a whole, and some of its numbers describe not a section of the
surface but the place where the part **ends**: a seam, an opening, a dividing line. Such a
measurement demands of a section something a section does not have.

Proven in practice: a measurement at the height of the leg opening demanded a drop of 54 mm in width
over 7 mm of height. The closed shell executed this literally and acquired a break in curvature
closed all the way around — a hard edge encircling the hips, visible from the front, the side and
the back. On the reference there is a smooth surface there and a thin stitching line.

**Sign:** measurements adjacent in height give rates of change of the bounding measurement differing
by several times over, and the suspect height coincides with a seam or an edge drawn on the
reference.

**What to do:** take such a measurement out of ordinary verification on the same footing as the
measurements of a surface-turn zone (see [phases.md](phases.md), M2, item 7), and seat the ring at
that height on a **smooth curve** between its neighbours. The boundary itself is built by a separate
operation working from the part's boundaries, not squeezed out of a section.

### 5.6 A crease goes where the reference has an edge, and only there

An edge crease is a legitimate way to hold a hard edge (the policies set at M2). But a ring goes
right around the part, whereas an edge, as a rule, lives on only part of that girth.

Proven twice on one part. Top of the shoulder: a crease over the whole ring made the numbers agree
and produced a ridge across the chest and back that the reference does not have. The underwear line:
a crease over the whole ring produced an edge encircling the hips. In both cases the numbers were in
tolerance and the surface was ruined — and it was inspection that saw it, not measurement.

**What to do:** before setting a crease, look at the reference to see **how far the edge runs**, and
set the crease only on those edges. Choose the weight by sweeping it against two criteria at once:
agreement with the reference at intermediate levels **and** the second difference of the contour.
Either criterion without the other chooses wrongly — proven in practice: on measurement alone, the
winning weight was the one that produced a visible ridge.

### 5.6a A measurement of a hidden surface is an approximation, not a contract

Part of the markup describes surface that is **not visible** on the reference: it is covered by
another part of the part itself. The author took it by guesswork, and it cannot be checked by
verification — there is nothing to compare against.

Proven in practice: the measurement `"шея, мин"` (neck, min) describes the throat at a height where
an overhanging chin covers it. The ring seated on it stood fifteen millimetres behind its neighbour
below, dragging the surface backwards — and the turn bled downwards into the **visible** part of the
neck, where it produced a bulge with a hollow behind it. The human saw it immediately; verification
was silent, because every measurement was in tolerance.

**What to do:** take such a measurement as a first approximation and refine it by sweeping against
two criteria simultaneously — agreement of the **visible** contour with the reference, and the
second difference along it. The fitness criterion: the visible contour has no turn that the
reference does not have.

**Sign that a measurement is of hidden surface:** the height falls in a zone where one part of the
part occludes another (a surface-turn zone, an undercut, a joint between parts). Such heights are
written out at M2 together with the list of excluded measurements (see [phases.md](phases.md), M2,
item 7).

### 5.7 The intermediate level is a mandatory part of verification

Measurements sit where they were taken, and the surface lives between them as well. A ring converged
onto its own measurement by overshooting with the cage bows the neighbouring stretch, and at the
measurements themselves this is invisible.

Proven twice: a shoulder went out by +10.6 mm at a level between two converged rings; a hip went out
by +24 mm, rising above the shoulders. Both times every measurement was in tolerance.

**What to do:** include in the step's verification at least one level **between** measurements, with
an expected value computed as a smooth interpolation of the neighbours. Going outside the **form**
tolerance there is as much a rejection as going outside it at a measurement — the interpolated level
is compared model-against-reference like any other, so it runs on the same tolerance.

**Stronger than that: what must be checked is not levels but the SLOPE of the contour along its
whole run.** Rings each converged onto their own measurement give zero at every measurement — and
give a polyline with corners at the rings, because between rings the contour runs almost straight.
Measurement cannot see this by construction, and the eye reads it as the curvature of the part.

Proven in practice: the slope of the neck's half-width went in steps of 0.8 → 0.3 → 0 mm/mm with
transitions shorter than two millimetres, with every measurement in tolerance. The human called it
"the neck is crooked".

**Sign of a polyline:** the slope holds constant within a ring span and changes in a jump at the
ring — one step per span. On a smooth form it changes gradually, inside the spans too.

**The cure:** where the reference's contour bends most, the ring span is too long — a ring goes
there. The density test (see [phases.md](phases.md), §11.4) fires on such a cut by definition: the
form cannot be moved without spoiling its neighbours.

### 5.8 The target is taken from the smoothed reference, not from a raw sample

Measurement off the reference is quantised: the image has a pixel pitch, and readings are rounded
onto it. One pixel easily amounts to two millimetres — comparable with the precision for whose sake
the convergence is being run.

If each ring is converged onto the raw sample at its own height, neighbouring rings receive values
rounded in **different directions**, and the difference between them swings up and down. The noise
of the source is carried into the model as **a wave with a period of one ring span** — exactly the
"crookedness" the eye reads at once.

Proven in practice: the slope of the neck's rear contour wandered 0.37 ↔ 0.65 around 0.47, while on
the reference the samples ran 0.402 / 0.805 / 0.402 / 0.403 — pure quantisation around 0.4. After
converging onto a reference smoothed with a ±7 mm window, the slope became a single-humped curve
0.49 → 0.56 → 0.52 → 0.36 → 0.27, and the divergence from the **raw** reference fell to 0.65 mm on
average.

**What to do:** before converging, smooth the measurements off the reference with a window on the
order of a ring span, and take the smoothed values as targets. Verify against the raw reference
nonetheless: smoothing is a way to set a target, not a way to report.

**First caveat:** the window must not span a discontinuity in the form. At the edge of an overhang,
smoothing will drag alien surface into the average; there the target is taken raw, or the window is
made one-sided.

**Second caveat, and it cost a step of its own: smooth with the MEDIAN, not with the mean.**
Measurements off the reference contain occasional single outliers of a whole quantum — an edge
caught half a pixel higher. The mean is pulled towards the outlier and drags the target with it; the
median does not notice it.

Proven in practice: a single outlier of 52.18 among steady values of 50.17 around it raised the
target at the neighbouring height, and the neck acquired a 0.7 mm deep waist where the reference has
a straight column. The sign of a genuinely flat stretch is reliable: on the reference the half-width
held **for seventeen rows running** at one value — quantisation does not behave like that, it would
flicker between adjacent steps.

### 5.8a A shallow boundary is measured across its run, not along it

Verification by default runs as "bounding measurement at a height": take a horizontal cut and
measure the width. While the surface runs steeply, this is correct. But where a boundary is
**shallow** — the shoulder line, the edge of an overhang, the top of the underwear line — one pixel
of height displaces it by ten millimetres of width, and measuring along its run turns a tiny error
into a monstrous one.

Proven in practice: the shoulder line, by the "width at a height" measurement, diverged from the
reference by **10.9 mm** and counted as the single out-of-tolerance point in the whole part. The
same stretch, measured across its run — "height at a given half-width" — gave a divergence of
**0.0…1.6 mm**. There was no defect at all; there was a badly conditioned measurement.

**Sign of a shallow boundary:** the derivative of the bounding measurement with respect to height is
large — more than two or three millimetres of width per millimetre of height. There the "bounding
measurement at a height" verification is switched off.

**What to do:** swap the roles of the axes. For each width, find the height at which it is reached,
and compare heights. The same goes for images: a shallow edge is scanned by columns, not by rows.

### 5.9 A crease has a limit, and beyond it it only does harm

An edge crease holds a hard edge, but its action saturates: from some weight onwards the limit
surface stops responding, while further increases in weight keep raising the curvature on the edge
itself — that is, they add a visible ridge and win nothing in form.

Proven in practice: a sweep of 0.45 / 0.60 / 0.75 / 0.90 on the rim of the shoulder cap gave an
identical result from 0.60 onwards, while the second difference of the contour grew from 1.86 to
2.31. The gain in form was 1.2 mm; the price was a noticeable ridge.

**What this means:** if the crease has saturated and the form still does not agree, the weight is
not the issue. The radius the reference demands simply does not fit into a ring span of that length
— a cut is needed, and the density test (see [phases.md](phases.md), §11.4) fires on it.

**How to check:** the weight is chosen by sweeping **up to saturation**, and the smallest of those
that give the same result in form is taken. A larger weight is pure loss.

---

### 5.10 A limb opening is seated on the mesh's lines, not on the seam's contour

A seam on the reference is decoration. Its place is in the texture, or in a shallow sunken groove,
but **not in the topology**. Cut the opening along the contour of the seam and the boundary runs
diagonally across the mesh and turns into a staircase, with every step of it giving birth to a pole.

Proven in practice: cutting the arm root along the seam's ellipse (deleting the faces whose centres
fell inside the ellipse) produced **sixteen** poles of valence 3 and 5 in the zone 1250…1520. In
(ring, column) coordinates the opening turned out to be an ellipse — 6–8, 5–9, 4–9, 4–9, 4–9, 4–8,
5–7 across seven rings. Both inspections — of the surface and of the edge flow — returned REJECTED
independently of each other, naming the same thing: a ring of singular points around the whole
perimeter of the join.

The same opening, brought to a **rectangle** in (ring, column) coordinates, gave one boundary,
valences of only 3 and 4, and exactly **four** poles — one per corner. And the corners then land
where they belong: two in the armpit, two at the trapezius.

**Rule:** a limb opening is a block of faces, whole in rings and whole in columns. The size of the
block is chosen so that it covers the required area; the shape of the opening is refined afterwards
by the position of vertices, but not by the set of faces deleted.

**Sign of violation:** more than four poles around the opening.

---

### 5.11 A convergence loop is checked against the reference, not against a target it moves itself

If a fix loop recomputes its target from its own result on every pass, it converges to itself rather
than to the reference, and its report looks healthy while it does so.

Proven in practice: a loop in which the table of targets was corrected by the measured deviation
reported a worst divergence of 116 mm where the true figure was 12 mm — because it was comparing the
model against a target that had already drifted. Nine "converged" levels had nothing to do with
anything.

**Rule:** the target is taken from the reference once, before the loop, and does not change inside
the loop.

**Sign of the forgery:** the "worst" figure across passes does not fall monotonically but wanders or
grows.

---

### 5.11a A stencil is inverted, not groped for

For a ring of a smooth tube the limit surface equals `(prev + 4·current + next) / 6`. This is not
only a rule for checking — it is **an equation**, and it is to be solved, not approached by
nudging the cage towards it pass after pass.

A chain of rings with known targets gives a tridiagonal system; it is solved by a sweep in one pass
and lands on the target the first time. Boundary conditions: at a free rim the limit equals the cage
itself (a boundary vertex is determined by the boundary curve alone); at a fixed neighbour, take its
current position.

Proven expensively: fitting the arm's cage to a limit-surface measurement failed three times running
and, over two rounds, blew a ring apart — from a half-width of 40 mm to 245. The same task solved by
a sweep converged **on the first pass** to 0.9 mm in width and 0.4 mm in centre, across seven rings
at once.

**This is not the multi-ring convergence that beat 3 forbids.** The ban in
[step-cycle.md](step-cycle.md), §4, beat 3 is on a **loop of successive passes** run over several
rings —
rings corrected through each other, pass after pass, with nobody looking in between. A sweep is a
direct solve: the system is written once from targets already taken off the reference, solved in one
pass, and the result is inspected before anything else happens. What still bounds it is the
**step's own scope** (see [step-cycle.md](step-cycle.md), §4, beat 3): the chain solved is the
geometry this operation changed plus its immediate neighbours. Seven rings were legitimate because
the operation had created all seven — not because a solve may reach anywhere. It is also on the
legitimate side
of §6: the targets come from the reference, and the sweep only inverts the subdivision stencil — a
transform whose effect is known exactly. It originates no form. The sign the ban turns on — "more
than four rings in one convergence loop" — is a sign of groping, not of arithmetic. Solving seven
rings at once and looking at the result is allowed; nudging seven rings at once and looking at the
numbers is not.

**When groping is nevertheless needed:** if the form is not a tube and the stencil is inexact
(unequal ring spacing, a pole nearby, a crease). Then the sweep gives the first approximation and
the search gives the correction — and it starts **not from zero but from the solution**.

**Sign of violation:** a convergence loop running more than three or four passes where the relation
between target and cage is linear.

---

### 5.12 A push that does not move the surface means that this height is held by something else

When moving a vertex by 25 mm moves the silhouette by 2 mm, the conclusion "I did not push hard
enough" is wrong. The right conclusion is that **the outermost vertex at this height is a different
one**, and the one being pushed lies inside.

Proven in practice: at height 1445 the edge of the opening already stands on the front and back of
the arm (y 7.6 and 83.8), not on its outer side; there was no outer meridian at all in the range
1400…1461. Four passes of pushing grew a spike on the rim at x 183 with neighbours at 137 —
subdivision ate it, and the eye saw it.

**Rule:** before repeating a push, find which vertex is the outermost at that height. If there is
more than one step of emptiness between two supports, what is needed is a **row**, not a
displacement.

---

### 5.13 A partial ring's bounding box is not the section's semi-axis

Around an opening — an armhole, a leg opening — a ring no longer spans a whole section. It holds
only the arc that survived the cut. Its `max(x)` is therefore the edge of the hole, not the
half-width of the section the ring belongs to.

Any quantity derived from that `max(x)` inherits the error. Two derivations do it silently:

- an **angular parameter** recovered as `cos θ = (x / a)^(n/2)` with `a` taken from the ring —
  every vertex gets the wrong angle, and re-placing them flings the arc out to the full width;
- a **semi-axis** for re-seating the ring — the ring is rebuilt at the size of its own remnant.

Proven expensively, twice in one session. First: an angular parameter taken from a partial belt at
the shoulder threw the armhole edge from x 76.9 to x 102.9 and lumped the whole girdle. Second,
worse: a convergence loop seeded from the current mesh with the same defect blew a ring from a
40 mm radius to 245 mm — the topology stayed clean the whole time, so no counter registered
anything, and the damage was found by eye on a render.

**Rule:** when a section's semi-axis is needed **as a number to compare against**, it comes from the
**markup**, never from the ring in front of you. If a ring is partial, its own extent describes the
hole, not the section, and the only honest source for the section is the level measurement. This is
a rule about where a *verification* number is read from — it does not licence placing the ring from
that number; where the ring goes is still found by eye on the reference (§6).

**Violated if:** `max()` over a ring's own vertices appears in a formula that re-places those
vertices; if a re-seating operation changes a hole's boundary that no operation asked to move.

**Which side of the law.** This rule does not licence building the section from the markup. It
governs the *verification* arithmetic of §6: when a number is taken for comparison, take it from the
level measurement rather than from a ring that holds only part of the section. Where a ring goes is
still found by eye on the reference.

---

### 5.14 A target profile is interpolated shape-preservingly, never by a natural spline

Markup levels are sparse. Between them a target for width, front or back has to be interpolated —
and the choice of interpolation is not cosmetic, because an overshoot invents form that neither the
reference nor the markup contains.

A natural cubic spline overshoots by construction: it minimises curvature globally, so it is free
to swing outside the interval between two neighbouring data points to buy smoothness elsewhere. On
sparse, unevenly spaced levels this happens constantly.

Proven in practice: a natural cubic through the shoulder levels produced a half-width of 158.5 mm
between neighbours of 139.5 and 143.3 — a value present in no measurement — and the shoulder came
out lumpy. The same data through a Fritsch–Carlson monotone cubic (PCHIP), which cannot overshoot
because it clamps the derivative at each knot to preserve monotonicity, gave a profile that passed
inspection.

**Rule:** use a shape-preserving interpolant for every profile derived from markup. If a value
appears between two levels that is outside the range of those two levels, the interpolation
invented it.

**How to check.** For every interpolated profile, compare each sampled value against the two
bracketing markup levels. Any excursion beyond both is an overshoot.

**Which side of the law.** Interpolation here builds a **target for comparison**, not a form. The
profile is what beat 5 gauges against between the levels the markup actually carries; it never
becomes the wording of an operation, and it never assigns a ring its height. Used the other way —
sampled to place rings — it is exactly the table of sections §6 forbids, and the smoothness of the
interpolant does not redeem it.

---

## 6. The role of markup

Markup is an **instrument of control**, applied in two places:

1. **During shaping** — as a visible ruler in the scene. You continue the shell, see that a guide is
   sticking out or has sunk inside, and move the form. A guide shows which way to pull; it does not
   dictate where to place a ring.
2. **During verification** — beat 5 of the step and the full verification at stage gates.

**Where the line runs.** The prohibition below is on a computation that **originates a form** —
that decides, from numbers, where the form goes. It is not a prohibition on arithmetic as such. A
computation is legitimate when it only **inverts a transform whose effect is known exactly**: the
target was placed by eye on the reference, and the arithmetic merely works out where the cage must
sit for the *limit surface* to land on that target (§5.11a). The test is what supplies the target.
Eye and reference: legitimate. A table of measurements: forbidden, however the arithmetic is
dressed. §5.13 and §5.14 both live on the legitimate side by this test, and say so.

**Forbidden:**

- generating geometry from the markup by computation — that is, letting a formula decide where the
  form goes;
- assigning ring heights from measurement heights;
- building guides at one per ring — that is the same table of sections, brought into the scene;
- keeping the guides of the whole part switched on at once: the markup then works as a permanently
  open table, and verification turns into construction.

**Mandatory:**

- a measurement is taken off the final surface, not off the cage. With an **approximating**
  subdivision scheme (Catmull-Clark, assigned at M1) the surface passes inside the cage, the cage
  sits outside the result, and a measurement taken on the cage is invalid. An interpolating scheme
  is not provided for by this standard;
- measurements flagged by the author of the markup (see [work-rules.md](work-rules.md), R7) as
  internal details of the form — that is, ones that do not span the full section at their height
  (see [work-rules.md](work-rules.md), R6, item 5) — are not part of section verification. Unflagged
  measurements count as full sections by default;
- full verification against all measurements is carried out only at stage gates (see
  [phases.md](phases.md), §11.3).

---

## 7. What is settled before the first polygon

Legitimate planning: the rules of the game, not a drawing of the part. All of these decisions are
taken at M2 and written into the task.

| Decision | Why up front and not as you go |
|----------|--------------------------------|
| Assembly order and its justification | There is no single canonical order; the choice is justified by which zone of the part is the riskiest — that zone is built while the mesh is still cheapest to redo |
| **Delivery form** | What goes out — the cage, or baked subdivision, and at which level. The hard-edge policy and the density at which form is judged depend on it. What does **not** depend on it is which mesh the polygon count comes off: that is always the result of the transforms, never the cage, in both branches ([phases.md](phases.md), M6) |
| **Subdivision level L** | Follows from the delivery form. It is also the factor that converts cage segments into faces on the final surface when N is checked **after** the build — not a licence to convert in advance and assign the cage a count — and the ring forecast depends on it |
| **The girth requirement on the final surface** | Not a cage number but an acceptance criterion: at the most demanding section the final surface must carry no fewer than N faces around its girth, where N comes from the calculation in [work-rules.md](work-rules.md), R6, item 11. How many segments the cage ends up with, and when they appear, is a result of the work (§8) |
| **The parity rule at the seam** | Any closed ring crossing the plane of symmetry must have an even number of segments: with an odd number it has no vertices on the plane itself — the seam runs through the middle of a face, the halves do not meet vertex to vertex, and the edge flow is skewed. This is a constraint **on operations**, not a number assigned in advance: a cut that produces an odd ring at the seam is forbidden |
| Construction zones | Where the form is a stack of rings, where the part's boundaries run, and **whether a surface-turn zone exists at all**. The fact is established on the reference; a sign derived from the data only raises suspicion and requires confirmation on the reference (see [phases.md](phases.md), §16.B) |
| **Polygon range** | From R2; it comes from outside and is not edited by the builder. We work at the lower bound: the minimum is not a wish but a guard against shoddy work |
| **Two tolerances, not one** | **Measurement tolerance** is the precision with which the reference was read (see [work-rules.md](work-rules.md), R6, item 8); section numbers are checked against each other by it. **Form tolerance** is how far the model is entitled to diverge from the reference; it is **wider**, and it is set here, before building. A two-dimensional reference does not transfer into three dimensions one to one: it has its own asymmetry, its own capture distortions, its own contour thickness. Holding the form to the measurement tolerance means driving it to the error of the source |
| Part boundaries | They follow the joints with neighbours, not personal discretion |
| End-cap closure scheme | Closing with segments converging into a single vertex gives a pole of high degree and tearing in the shading; closing with a grid gives four poles of degree three and stays quadrangular |
| Pole policy | Only in places without deformation and without noticeable curvature. The curvature rule: if a pole changes the curvature of the surface, it has to go |
| **Density transition scheme** | A transition invented on the spot puts poles wherever they happen to fall, not where they are allowed to stand. Permitted schemes: halving through three quadrangles with two poles of degree five; shifting the flow sideways without changing the number of edges. Reduction through a pair of triangles is not permitted in deformable zones |
| Hard-edge policy | Supporting loops always work, but they cost polygons. Edge creases are a mesh attribute interpreted by the subdivision scheme: they are fit for use if the subdivision is baked before delivery or the interchange format carries creases; they are unfit if what goes out is an unsubdivided cage in a format without crease support |
| Symmetry branch | See [phases.md](phases.md), §15.1 |
| The set of viewpoints and check channels | See [phases.md](phases.md), §11.2 |
| Stage boundaries | See [step-cycle.md](step-cycle.md), §2.2 |
| Pass limits | See [step-cycle.md](step-cycle.md), §4.1 |
| The acceptance criterion of each phase | See [phases.md](phases.md), §9 |

---

## 8. What may not be settled in advance

These are results of the work. Settled in advance, they turn building into computation.

| Not in advance | Why |
|----------------|-----|
| Vertex coordinates | Vertex positions are the result of shaping, not its input |
| Ring heights | A ring goes where the form has stopped responding to the current density — and that is discovered at the moment of work |
| **The number of rings in a zone** | Rings are placed according to the behaviour of the form; a number of rings per zone assigned in advance is the same quota as their heights |
| **The heights of zone boundaries** | A zone boundary is discovered at the moment of building. Recorded as a number, it brings back building-from-a-table through the wording "continue to the zone boundary" |
| **The place and the extent of a surface-turn zone** | These are refined at the moment of building; they are not fixed by number in advance |
| The shape of a section inside its bounding measurement | A width × depth pair specifies an ellipse at most — one class of shape for the whole section. Flattenings inside the same bounding measurement do not follow from measurements however hard one tries |
| The number and the places of loop cuts | The sign that one is needed is that the form has stopped responding; the sign that it is premature is that the model becomes lumpy |
| **The number of cage segments around the girth** | Segments appear from cuts, and cuts are not assigned in advance (the row above). What is known in advance is only **the requirement on the result** (§7); how many segments and when is a result |
| The placement of poles | A pole is a consequence of how the edge flows actually met; one designed in advance will have to be moved |
| Concavities | Concavities cannot be recovered from two orthographic silhouettes **in principle**: a concavity does not affect the silhouette. Two views give the convex hull at best |
| Places where the surface turns under itself | At such a height the cutting plane is either tangent or gives two separate contours. That class of shape is structurally inaccessible to horizontal sections |
| The final polygon count as a quota | The range is known in advance; the actual figure is counted after the fact, and checking that it falls inside the R2 range after building is mandatory. Assigning vertices to hit a figure is forbidden |
| The order of fixes inside a step | Which vertices to move is determined by the inspection after the operation |

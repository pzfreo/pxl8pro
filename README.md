# Pixel 8 Pro case — parametric rebuild

`case.py` is a [build123d](https://build123d.readthedocs.io) parametric rebuild
of JamesSF69's Pixel 8 Pro TPU case (see Attribution). Every dimension was
measured off the source meshes rather than eyeballed; `verify.py` checks the
result back against them.

## Attribution

This is a derivative work of **[Pixel 8 Pro Case
(TPU)](https://www.printables.com/model/765202-pixel-8-pro-case-tpu)** by
**[JamesSF69](https://www.printables.com/@JamesSF69_537205)** on Printables.

The original design is theirs: the overall form, the cavity and its clearances,
the lip and rim profile, the camera bar recess and lens cutouts, the port
layout, and the button bumps. `case.py` re-derives that geometry
parametrically by measuring their STLs — it does not introduce a new design,
and the source files (`pixel8proCase.stl`,
`pixel8CaseChargeHoleBigger.stl`) are their work.

### The two source STLs are not the same model

`pixel8CaseChargeHoleBigger.stl` is **not** simply the Printables model with a
bigger charging port — it is a thickened derivative:

| | `pixel8proCase.stl` | `pixel8CaseChargeHoleBigger.stl` |
|---|---|---|
| Outer | 82.14 × 167.21 × 14.00 | 83.68 × 169.76 × 14.70 |
| Volume | 62.1 cm³ | 75.2 cm³ |
| Side wall | 1.729 mm | 3.000 mm |
| Back | 4.5 mm | 5.2 mm |
| Button bumps | **yes, 1.00 mm proud** | **none** |
| Corner geometry | clean | 1 mm step at all four corners |
| Cavity | identical | identical |

Both share the same centre (1.3416, −1.7777) and the same corner-arc rails
(±28.842, ±71.878), and their cavities are identical — so the phone fit is the
same. The difference is entirely the outer shell, thickened by ~1.27 mm per
side. **That is what removed the button bumps**: the wall grew 1.271 mm while
the bumps stood only 1.000 mm proud, so the offset swallowed them, and it also
introduced the corner step.

`case.py` reproduces *both* files by changing only two parameters. Against
`pixel8proCase.stl`, `wall=1.729, back_thk=4.5` gives an identical bounding box
and 0.046 mm mean deviation.

> **TODO — check the licence before publishing or sharing.**
> Printables blocks automated fetches (HTTP 403), so the licence could not be
> read from the model page. **It governs whether these derivatives can be
> redistributed at all** — any `-ND` variant forbids publishing modified
> versions, and `-NC` forbids commercial use. Check
> [the model page](https://www.printables.com/model/765202-pixel-8-pro-case-tpu)
> before uploading anything here, and keep JamesSF69's credit and a link to
> the original on any upload.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python build123d trimesh numpy rtree matplotlib

.venv/bin/python case.py vented      # -> pixel8pro_case_vented.{stl,step}
.venv/bin/python case.py             # default preset
```

**The STLs are not in this repo** — neither JamesSF69's source files nor the
derived exports. `case.py` regenerates every variant exactly, and the source
models belong to their author (see Attribution). To run `verify.py`, download
`pixel8CaseChargeHoleBigger.stl` from
[the Printables page](https://www.printables.com/model/765202-pixel-8-pro-case-tpu)
into the repo root first:

```bash
.venv/bin/python verify.py           # deviation report + compare.png
```

Optional, for the printability report:

```bash
uv pip install --python .venv/bin/python augura
.venv/bin/augura analyze pixel8pro_case_vented.step --nozzle 0.4
```

## Presets

`case.py <name>` builds one of these and prints the thicknesses that decide
whether it is printable. `case.py <style>` or `<style>-open` builds a bare
back style; anything else is reachable by constructing `Params` directly.

| Preset | Volume | ≈ TPU | Outer W × L × H | Notes |
|---|---|---|---|---|
| `original` | 77.6 cm³ | 94 g | 83.68 × 169.78 × 14.70 | faithful rebuild of the thickened file |
| `light` | 45.2 cm³ | 55 g | 84.68 × 169.78 × 13.00 | closed back, hollowed inside |
| `open` | 33.3 cm³ | 40 g | 84.68 × 169.78 × 13.00 | 12.0 mm cells, phone shows through |
| `mesh` | 36.9 cm³ | 45 g | 84.68 × 169.78 × 13.00 | 6.5 mm cells |
| `slim` | 31.6 cm³ | 38 g | 82.68 × 167.78 × 13.00 | `mesh` + 2.0 mm side walls |
| **`vented`** | **25.3 cm³** | **31 g** | **81.68 × 166.78 × 13.00** | + 1.5 mm walls, trimmed borders, side vents |

All are watertight single solids. Against `pixel8CaseChargeHoleBigger.stl`
(75.2 cm³, 14.70 mm), `vented` is **66 % lighter and 1.70 mm thinner**, and
smaller in plan than even the stock case (82.14 × 167.21 × 14.00).

## Where the mass actually is

Before adding geometry, it is worth knowing what is left. Decomposing `slim`
(31.6 cm³) by region:

| Region | Volume | Share |
|---|---|---|
| honeycomb lattice | 11.50 cm³ | 36.4 % |
| side walls + rim (z > 0) | 9.06 cm³ | 28.7 % |
| back frame (the `rib_border` ring) | 5.56 cm³ | 17.6 % |
| back perimeter skirt (wall below z = 0) | 3.15 cm³ | 10.0 % |
| camera surround + skin | 2.64 cm³ | 8.4 %

The surprise is the **back frame: 8.25 cm³, nearly as much as the entire side
walls and rim combined**, for what is only a 4 mm ring. Together with the
skirt below it, the solid rail around the perimeter is 13 cm³ — 31 % of the
case. Trimming `rib_border` 4.0 → 2.5 and `rib_cam_border` 3.0 → 2.0 costs
nothing but a parameter change:

| | Volume | ≈ TPU |
|---|---|---|
| `slim` | 42.5 cm³ | 51 g |
| + `rib_border` 3.0 | 40.5 cm³ | 49 g |
| + `rib_border` 2.5 | 39.8 cm³ | 48 g |
| + `rib_border` 2.5, `rib_cam_border` 2.0 | 38.7 cm³ | 47 g |
| + `rib_border` 2.0, `rib_cam_border` 1.5 | 38.0 cm³ | 46 g |

## Side wall vents

`side_vents=True` cuts hexagons through the side walls. They are **vertex-up**,
so the top of each hole closes to a point and needs no support printed
back-down — overhang area rises only from 2.97 % to 3.69 %.

Placement is automatic and skips what it must:

| Wall | Vents | Skipped |
|---|---|---|
| −X (long) | 21 | — |
| +X (long) | 13 | button relief pockets, y −13.7…34.2 |
| +Y (top) | 8 | — |
| −Y (bottom) | 0 | USB-C and both speaker slots fill it entirely |

42 vents total, confirmed by genus: `slim` is 167, `slim` + vents is 209.
Corners are always left solid — they take the drops.

**Vents are the smallest of the three levers**, worth 1.5 cm³ against 3.8 cm³
for the border trim, because the perforable band is only the 6.07 cm³ of side
wall below the lip (`z` 0–7.0); the 2.46 cm³ of rim and lip above it has to
stay. They are additive though, and they suit the mesh back:

| | Volume | ≈ TPU |
|---|---|---|
| `slim` | 31.6 cm³ | 38 g |
| `slim` + vents | 30.1 cm³ | 36 g |
| `slim` + borders | 29.0 cm³ | 35 g |
| `slim` + both, 1.5 mm wall (= `vented`) | 25.3 cm³ | 31 g |

Below that, the remaining mass is structural: the lattice itself (40 %) and
the rim/lip. `back_thk` 5.2 mm is the other big lever, but it exists to keep
the back flat over the camera bar — dropping it means a camera bump, which
cannot be printed support-free in any orientation (see `bump`).

## Side walls

`wall` (3.0 mm in the original) sets the outer size directly, since
`out_w = cav_w + 2·wall`. Thinning it is the only change that makes the case
*smaller* as well as lighter. Three thicknesses are derived from it, and they
bind before the wall itself does:

| `wall` | Outer W × L | Volume | ≈ TPU | Rim top | Behind buttons | Port bore |
|---|---|---|---|---|---|---|
| 3.0 | 83.68 × 169.78 | 48.7 cm³ | 59 g | 2.70 | 2.50 | 2.00 |
| 2.5 | 82.68 × 168.78 | 45.6 cm³ | 55 g | 2.70 | 2.00 | 1.50 |
| **2.0** | **81.68 × 167.78** | **42.5 cm³** | **51 g** | 2.70 | 1.50 | 1.00 |
| 1.8 | 81.28 × 167.38 | 41.2 cm³ | 50 g | 2.70 | 1.30 | 0.90 |
| 1.5 | 80.68 × 166.78 | 39.4 cm³ | 48 g | 2.70 | 1.00 | 0.75 |
| 1.2 | 80.08 × 166.18 | 37.6 cm³ | 45 g | 2.70 | 0.70 | 0.60 |

*(volumes on the `mesh` back — `hex_pitch` 8, `rib_w` 1.5)*

**The button relief pocket binds first.** It is *clearance for the button*,
which stands proud of the phone's frame — without it the wall rests on the
button and holds it part-pressed. So it cannot be dropped to buy wall
thickness. What the button actually sees is `clr_xy + btn_depth`:

| | Wall | Relief | Behind buttons | Gap at the button |
|---|---|---|---|---|
| `pixel8proCase.stl` (stock) | 1.729 | 0.229 | 1.500 | **0.821 mm** |
| `pixel8CaseChargeHoleBigger.stl` | 3.000 | 0.500 | 2.500 | **1.092 mm** |

The stock case's 0.821 mm is known to work in practice, so `wall = 1.5` with
`btn_depth = 0.229` reproduces that gap exactly while leaving 1.271 mm of
material behind the button — comfortably printable. `vented` uses this.

1.5 mm is where this stops: the wall is then thinner than the stock case's,
and the relief still has to come out of it.

Two couplings had to be fixed before thin walls behaved:

- **The rim scaled wrong.** `rim_ledge` and `rim_taper` were absolute (1.0 and
  2.0 mm), and their sum is exactly the original's 3.0 mm wall — which is why
  the original's rim top lands precisely on the cavity wall. Held absolute,
  they ate past the lip as the wall thinned. They are now fractions of `wall`
  (1/3 and 2/3), so the rim top stays exactly `lip_inset` wide — 2.70 mm at
  every row above, instead of collapsing to 0.90 mm at `wall` 1.2.
- **The port chamfer could eat the whole wall.** `port_chamfer` is 1.0 mm, so
  at `wall` 1.0 there was no straight bore left at all and the port became a
  pure funnel. It is now clamped to `wall/2`.

Reducing `wall` costs edge drop protection, and thin TPU walls stretch more —
easier to fit, but also easier for the phone to leave the case on impact.
`lip_inset` is measured from the cavity, so the lip's grip on the phone is
unaffected.

## Coordinate system

Origin at the centre of the case in X/Y, **Z = 0 at the cavity floor** (where
the phone's back rests). `+Z` points out of the opening, `+Y` towards the
camera bar, `+X` towards the buttons. `export()` drops the part onto Z = 0 so
the STL is ready to slice back-down. The original mesh was translated off
origin by (1.34, −1.78); this one is centred.

## What the original actually is

| Feature | Measured |
|---|---|
| Outer | 83.68 × 169.76 × 14.70 mm, corner R13.0 |
| Phone cavity | 77.68 × 163.76 × 9.50 mm, corner R10.0 |
| Clearance vs 76.5 × 162.6 × 8.8 | 0.59/side XY, 0.70 Z |
| Side walls | 3.0 mm |
| Back | **5.2 mm solid** — a flat-back design, filled to camera-bar height |
| Camera skin | 1.5 mm, over a 76.28 × 22.30 × 3.7 mm recess |
| Lip | 2.70 mm past the cavity wall (≈2.11 mm over the phone face) |
| Ports | USB-C 15.05 × 7.08, two speaker slots 14.34 × 4.68 |
| Buttons | inner relief pockets only, no through-holes |
| Volume | 75.2 cm³ ≈ 91 g TPU |

## Defects found in the original, fixed here

1. **End walls were 2.0 mm, not 3.0 mm.** The straight top and bottom outer
   edges sat 1.0 mm inboard of where the corner arcs are tangent, leaving an
   abrupt 1 mm step at all four corners — a stress riser exactly where drop
   impacts land, on the thinnest walls in the part. Now a proper tangent
   rounded rectangle, 3.0 mm all round.
2. **Back-edge chamfer was on two sides only** — 3.2 mm at 45° on −X and −Y,
   square on +X and +Y. Replaced with a symmetric 0.8 mm chamfer, which also
   keeps the first layer off the very edge when printing back-down.
3. **Sharp-cornered camera recess** — now R1.0.
4. **Exact-stadium port slots** meshed with a seam that reads as a hole in
   some slicers. `_rrect()` now holds the radius clear of w/2 and h/2.

## Back styles

Set via `Params.back_style`. All four are watertight, single-solid, genus 6
(same topology as the original).

| Style | Volume | ≈ TPU | Overhang area printed back-down | Notes |
|---|---|---|---|---|
| original | 75.2 cm³ | 91 g | 3.1 % | — |
| `flat` | 77.6 cm³ | 94 g | 3.5 % | faithful rebuild, solid back |
| `honeycomb` | 55.1 cm³ | 67 g | **2.9 %** | **default** |
| `ribbed` | 56.1 cm³ | 68 g | 3.0 % | square grid |
| `bump` | 37.8 cm³ | 46 g | 33.9 % | lightest, but needs support |

`honeycomb` and `ribbed` void the back slab **from the cavity side**, leaving a
1.8 mm skin against the outer face. The outer back stays perfectly flat and
smooth; the phone rests on the rib tops at Z = 0. Because every pocket opens
upwards, both print back-down with no support and no bridging — measurably
*less* overhang than the solid version. They also vent the cavity, so the
phone no longer suctions in and out.

### Why honeycomb over the square grid

Both come out at roughly the same mass, but the hex pattern is better on two
counts:

- **Less wall for the same cell area.** Hexagonal cells meet three-way at
  120°, which is the minimum-length way to partition a plane into equal cells.
  For cell area *A* a honeycomb needs 1.861·√A of wall per cell against 2·√A
  for squares — 7 % less. Measured on the actual field: 60 hex cells open
  6614 mm² where 36 square cells open 6330 mm².
- **No hinge lines.** The square grid runs continuous straight ribs the whole
  length of the case, and a TPU case will preferentially fold along them. No
  straight line crosses a honeycomb field, so it stiffens isotropically.

`hex_pitch` is the cell centre spacing, and the wall left between neighbours
is exactly `rib_w` (verified: 14.0 pitch − 2×6.0 inradius = 2.000 mm). Cells
are pointy-top. Boundary cells below `pocket_min_frac` of a full cell are
dropped rather than left as slivers.

### Going lighter

The ribs are *not* where the mass is — the skin thickness and the borders are
the real levers, and cell size barely moves the number:

| Settings | Volume | ≈ TPU | vs original |
|---|---|---|---|
| default (`rib_skin` 1.8, `hex_pitch` 14, `rib_w` 2.0) | 55.1 cm³ | 67 g | −27 % |
| `hex_pitch` 22, `rib_w` 1.6 | 52.1 cm³ | 63 g | −31 % |
| `rib_skin` 1.4 | 52.5 cm³ | 64 g | −30 % |
| `rib_skin` 1.4, `rib_border` 3.0 | 51.8 cm³ | 63 g | −31 % |
| `rib_skin` 1.4, `rib_border` 3.0, `rib_cam_border` 2.5, `hex_pitch` 18, `rib_w` 1.6 | 49.1 cm³ | 59 g | −35 % |

`rib_skin` is the drop-protection layer over the back; 1.4 mm is about as thin
as is sensible (the camera skin is 1.5 mm).

### Open cells — `pocket_through`

Set `pocket_through=True` (or run `case.py honeycomb-open`) and the cells cut
clean through the back instead of stopping at the skin. The phone shows
through, and the back becomes a pure lattice.

| | volume | ≈ TPU | overhang | bed contact |
|---|---|---|---|---|
| `honeycomb` | 55.1 cm³ | 67 g | 2.9 % | 12 382 mm² |
| `honeycomb-open` | **43.2 cm³** | **52 g** | 3.6 % | 5 768 mm² |
| `ribbed-open` | 44.7 cm³ | 54 g | 3.8 % | 6 052 mm² |

−43 % against the original, and it very nearly matches `bump` (37.8 cm³) while
still printing support-free — the holes are vertical prisms, so they add no
overhang, and 58 cm² of bed contact is plenty for TPU. It also lets the phone
sit closer to a Qi coil.

The cost is real, though: **there is no longer any material behind the phone's
back glass.** Dropped on gravel, something can reach the glass through a 12 mm
hole. The 1.8 mm skin was also doing plate work — without it the back is a 2D
lattice and noticeably floppier. Grit gets in, too.

If that matters, spend the grams on *smaller cells* rather than thicker walls
— the same mass buys a much smaller opening:

| Settings | Hole across flats | Cells | Volume | ≈ TPU | Hole perimeter |
|---|---|---|---|---|---|
| `hex_pitch` 14, `rib_w` 2.0 | 12.0 mm | 60 | 43.2 cm³ | 52 g | 2352 mm |
| `hex_pitch` 18, `rib_w` 2.5 | 15.5 mm | 40 | 44.1 cm³ | 53 g | — |
| `hex_pitch` 14, `rib_w` 3.0 | 11.0 mm | 60 | 48.5 cm³ | 59 g | — |
| `hex_pitch` 10, `rib_w` 2.0 | 8.0 mm | 116 | 48.8 cm³ | 59 g | 2982 mm |
| **`hex_pitch` 8, `rib_w` 1.5** | **6.5 mm** | 161 | 48.7 cm³ | 59 g | 3466 mm |

Rows 3–5 all weigh the same to within 0.3 cm³ but leave an 11.0, 8.0 or 6.5 mm
opening. Spending the grams on smaller cells rather than thicker walls is
clearly the better trade: `hex_pitch` 8 / `rib_w` 1.5 has the smallest holes
*and* the highest cell count for the same mass.

Walls stay exactly at `rib_w` everywhere — eroding the lattice section by
0.75 mm/side breaks it into 227 pieces at `rib_w` 1.5, i.e. precisely half the
nominal, so the boundary trim leaves no thin ligaments. The 1 mm corner fillet
costs only 1 % of cell area, so the cells are still true hexagons.

The catch at fine pitch is **print time, not material**: the last column is
total hole perimeter, and it rises faster than volume falls. `hex_pitch` 8
traces 47 % more wall than `hex_pitch` 14 through the full 5.2 mm depth, so it
prints appreciably longer despite the two being within 6 cm³ of each other.
1.5 mm walls are still comfortable for a 0.4 mm nozzle (about four lines).

`bump` is the conventional thin-back-plus-camera-plateau design. It is by far
the lightest but the back skin overhangs the plateau, so it needs support in
any orientation — best kept for resin or for when you don't mind supports.

## Camera

`back_thk` is **derived, not free**: the back is exactly as thick as the recess
the camera bar drops into plus the skin over it.

```
back_thk = cam_recess + cam_skin
```

The Pixel 8 Pro's camera bar measures **2.5 mm on the phone**, which is also
exactly what the stock case uses — so `cam_recess = 2.5` is confirmed from both
ends. The thickened file instead used a 3.7 mm recess and took the difference
out of the skin, so it was 0.7 mm *thicker* overall while giving 0.5 mm *less*
protection over the lenses:

| | Recess | Skin over bar | `back_thk` | Case height |
|---|---|---|---|---|
| `pixel8proCase.stl` (stock) | 2.500 | 2.000 | 4.5 | 14.00 |
| `pixel8CaseChargeHoleBigger.stl` | 3.700 | 1.500 | 5.2 | 14.70 |
| presets here | 2.500 | **1.000** | 3.5 | **13.00** |

At `cam_skin = 1.0` the lens openings become a 0.5 mm straight bore plus a
0.5 mm chamfer (`cam_straight` is clamped to half the skin so it can never
exceed it). 1.0 mm is five layers at 0.2 mm and it is unsupported TPU directly
over the lens glass — this is the floor, not a value with headroom in it.

Because the honeycomb cells are `back_thk` tall, shortening the back takes mass
out of the whole lattice, not just at the camera: it is worth more than any
other single change here.

### Flash opening

The source models put the flash and the temperature sensor in two circles whose
centres are 9.503 mm apart with radii summing to 9.294 — leaving a **0.209 mm
ligament** between them, 0.5 mm tall, which the chamfer below merges away
0.104 mm down. It is a floating flake no nozzle can produce.

`flash_stadium=True` (default) replaces the pair with one stadium of
9.294 × 18.797 mm, r = 4.647 — the exact same outer envelope, one clean
opening. `original` keeps the two circles, since it reproduces the source file.

## Charging port

The stock case's USB-C opening does not clear a real cable. Measured at its
narrowest point (it is chamfered from both faces, so the waist is mid-wall):

| | Narrowest aperture | Wall |
|---|---|---|
| `pixel8proCase.stl` (stock) | **12.65 × 4.68 mm** | 1.729 mm |
| `pixel8CaseChargeHoleBigger.stl` | **15.05 × 7.08 mm** | 3.000 mm |
| every preset here | **15.05 × 7.08 mm** | 2.0–3.0 mm |

**Height is the blocker, not width.** A USB-C tongue is only 2.4 mm tall, but
the moulded housing around it is typically 5–7 mm — so 12.65 mm of width was
never the problem, and 4.68 mm of height was. The enlarged file adds 2.4 mm in
both directions, and `case.py` uses those dimensions throughout (`usb_w`,
`usb_h`), so all presets clear a cable.

If a particularly fat cable still fouls, **widen rather than heighten**:

- **Height is essentially maxed out.** The hole spans z 0.30…7.38 of the
  0…7.50 available between the cavity floor and the wall top. Going taller
  breaks into the lip above or the back below.
- **Width has room.** The USB opening ends at x = 7.60 and the speaker slot
  starts at x = 10.58, so there is 2.98 mm of material each side. `usb_w`
  could go to roughly 19 mm before the ribs get too thin to print.

`slim` and `vented` also help here for a second reason: their 2.0 mm wall is
1 mm thinner than the enlarged file's, so the plug traverses less material
before reaching the phone.

## Button bumps

`button_bumps=True` (default) puts raised press pads back on the outside of
the +X wall. They were measured off `pixel8proCase.stl` and reproduce it to
**0.011 mm** through the whole profile:

| | Value |
|---|---|
| Proud of wall | 1.00 mm |
| Plateau (y × z) | 8.75 × 1.47 mm |
| Plateau centre height | z = 4.27 |
| Edges | 45° chamfer all round |
| Spans (y) | −9.25…−0.50, 2.75…11.50, 20.75…29.50 |

Three pads — volume down, volume up, power. The 45° lower chamfer is what
makes them printable back-down; a square pad would leave a horizontal
overhang. `side_vents` knows about them and keeps clear.

The `original` preset sets `button_bumps=False`, since the STL it reproduces
does not have them.

## Fit

Defaults reproduce the original's clearance (0.592 mm/side XY, 0.70 Z) so the
first print is a known-good baseline. For TPU that is on the loose side:

```python
Params(back_style="honeycomb", clr_xy=0.40)
```

`lip_inset` (2.70 mm) reaches ≈2.11 mm over the phone face once cavity
clearance is accounted for — normal for a case lip. Reduce it if you use a
screen protector with a raised edge.

## Verification

`verify.py` samples the rebuilt surface and measures distance to the original:

```
surface deviation: mean 0.073  p95 0.700  max 2.519 mm
within 0.10 mm: 90.0%
```

The 10 % that differs is accounted for by the four fixes above plus the button
pocket depth (the original varies between 0.5 and 1.0 mm; this uses a uniform
0.5 mm). `compare.png` overlays slices of both models.

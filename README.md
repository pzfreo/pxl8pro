# Pixel 8 Pro case

A printable TPU case for the Pixel 8 Pro, built as a parametric
[build123d](https://build123d.readthedocs.io) program rather than a fixed mesh —
so you can change the fit, the wall thickness or the back pattern and rebuild.

Based on [JamesSF69's Pixel 8 Pro Case (TPU)](https://www.printables.com/model/765202-pixel-8-pro-case-tpu).

![Pixel 8 Pro case](docs/hero.png)

## How this came about

The Printables model ships as two STLs, and they turn out to be different
designs, not one plus a bigger charging port. The stock file has proper button
bumps and thin 1.7 mm walls; the other has a usable USB-C opening but is a
thickened copy whose extra 1.27 mm of wall had swallowed the bumps entirely.

So neither file was the good one. Rebuilding both parametrically meant we could
take the button bumps from the first and the working charge hole from the
second, fix a few things that turned up on the way — end walls that were 2 mm
instead of 3, a chamfer applied to only two sides, a flash cutout with an
unprintable 0.2 mm sliver in it — and then make it a lot lighter.

The result is **31 g against the original's 91 g**, and 1.7 mm thinner.

Full measurements, defects and design reasoning are in **[DESIGN.md](DESIGN.md)**.

## Which one to print

| Preset | Weight | Size (W × L × H) | What you get |
|---|---|---|---|
| `vented` | **31 g** | 81.7 × 166.8 × 13.0 | Lightest. Open honeycomb back, vented sides |
| `slim` | 38 g | 82.7 × 167.8 × 13.0 | Same open back, plain 2 mm sides |
| `mesh` | 45 g | 84.7 × 169.8 × 13.0 | Open back, original 3 mm walls |
| `open` | 40 g | 84.7 × 169.8 × 13.0 | Open back with larger 12 mm cells |
| `light` | 55 g | 84.7 × 169.8 × 13.0 | **Closed** back — nothing shows through |
| `original` | 94 g | 83.7 × 169.8 × 14.7 | Faithful copy of the source file |

```bash
python case.py vented
```

**Pick `light` if you want a solid back.** The others cut the honeycomb clean
through, so the phone is visible and there is no material behind the back
glass — lighter and better for wireless charging, but a drop onto gravel can
reach the glass through a cell. `light` keeps a 1.8 mm skin.

**Pick `vented` if you want the lightest.** 1.5 mm walls: slimmer in the hand,
but less edge protection, and thin TPU stretches more.

## Printing

Print **back down, opening upwards**, exactly as exported. No supports.

| | |
|---|---|
| Material | TPU (95A or similar) |
| Layer height | 0.2 mm |
| Nozzle | 0.4 mm |
| Supports | none |
| Infill | irrelevant — the part is all perimeters |

Everything is designed around that one orientation: the honeycomb cells open
upwards, the button bumps have a 45° lower chamfer, and the case sits on a flat
back with no elephant-foot on the very edge.

### Snip out the USB bar

`vented` includes a **sacrificial 0.8 mm bar across the middle of the USB-C
opening**. It halves the bridge the printer has to span, and it must be cut out
before use — it sits where the plug goes. Flush cutters or a sharp blade
through the opening; TPU will not snap cleanly.

The bars in the two speaker slots are **permanent** — leave those in. Nothing
passes through a speaker slot, so they are just a grille.

To print without the sacrificial bar, use `usb_bar=False` and accept a slightly
rougher bridge over the port.

## Fit

The defaults reproduce the original's clearance, which is a known-good starting
point but slightly loose in TPU. For a snugger fit:

```python
from case import PRESETS, export
from dataclasses import replace
export(replace(PRESETS["vented"], clr_xy=0.40), "snug")
```

Charging: the USB-C opening is **15.05 × 7.08 mm**, the enlarged one. The stock
case's is 12.65 × 4.68 and will not clear most cables — the height is what
blocks them, not the width.

## Customising

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python build123d trimesh numpy rtree matplotlib

python case.py vented        # -> pixel8pro_case_vented.{stl,step}
python case.py               # default preset
```

`case.py <preset>` also prints the thicknesses that decide whether a build is
printable, so you can see what a change actually did:

```
  outer          80.68 x 166.78 x 13.00 mm
  side wall      1.50 mm
  rim top        2.70 mm
  behind buttons 1.27 mm
  port bore      0.75 mm straight + 0.75 chamfer
  back skin      none (open cells)
```

The knobs you are most likely to want:

| Parameter | Default | Effect |
|---|---|---|
| `clr_xy` | 0.592 | Fit. Lower is snugger; 0.40 is good for TPU |
| `wall` | 3.0 (1.5 in `vented`) | Side wall — also sets the outer size |
| `cam_skin` | 1.0 | Material over the lenses. Do not go below 1.0 |
| `hex_pitch` | 14 (8 in `mesh`+) | Honeycomb cell size |
| `pocket_through` | False | True = open cells, False = closed back |
| `side_vents` | False | Hexagonal vents through the side walls |
| `usb_bar` | False | Sacrificial bar across the USB opening |

Every dimension is a named parameter in `Params` — see
[DESIGN.md](DESIGN.md) for what each one is and why it has that value.

**The STLs are not in this repo**, neither the sources nor the exports.
`case.py` regenerates them exactly. To run `verify.py`, first download
`pixel8CaseChargeHoleBigger.stl` from
[the Printables page](https://www.printables.com/model/765202-pixel-8-pro-case-tpu)
into the repo root.

## Credits and licence

Original design: **[JamesSF69](https://www.printables.com/@JamesSF69_537205)** —
[Pixel 8 Pro Case (TPU)](https://www.printables.com/model/765202-pixel-8-pro-case-tpu).
The form, cavity, lip, camera cutouts, port layout and button bumps are theirs.

Licensed **[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)**,
same as the original — ShareAlike means this cannot be relicensed. If you
redistribute or remix it, keep the credit and the licence. See
[LICENSE](LICENSE) for the full attribution and the list of changes made.

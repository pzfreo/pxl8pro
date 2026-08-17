"""Compare the rebuilt case against the original STL.

SPDX-License-Identifier: CC-BY-SA-4.0

The reference mesh is not centred on the origin; REF_SHIFT moves it into the
coordinate system `case.py` builds in (see the module docstring there).
"""

from __future__ import annotations

import numpy as np
import trimesh

REF = "pixel8CaseChargeHoleBigger.stl"
REF_SHIFT = np.array([-1.3415, 1.7775, -5.2 + 2.7])  # -> centred, floor at z=0


def load_ref() -> trimesh.Trimesh:
    m = trimesh.load(REF)
    m.apply_translation(REF_SHIFT)
    return m


def to_trimesh(part, tol: float = 0.02) -> trimesh.Trimesh:
    import tempfile
    import os
    from build123d import export_stl

    fd, path = tempfile.mkstemp(suffix=".stl")
    os.close(fd)
    export_stl(part, path, tolerance=tol, angular_tolerance=0.1)
    m = trimesh.load(path)
    os.unlink(path)
    return m


def deviation(new: trimesh.Trimesh, ref: trimesh.Trimesh, n: int = 60000):
    """Distance from sampled points on `new` to the surface of `ref`."""
    pts, _ = trimesh.sample.sample_surface(new, n)
    d = trimesh.proximity.closest_point(ref, pts)[1]
    return pts, d


def report(part, label: str = "rebuild"):
    ref = load_ref()
    new = to_trimesh(part)
    print(f"=== {label} vs {REF} ===")
    for nm, m in (("ref", ref), ("new", new)):
        b = m.bounds
        print(
            f"  {nm}: {b[1][0]-b[0][0]:8.3f} x {b[1][1]-b[0][1]:8.3f} x "
            f"{b[1][2]-b[0][2]:7.3f} mm   vol {m.volume/1000:6.2f} cm^3   "
            f"watertight={m.is_watertight}"
        )
    _, d = deviation(new, ref)
    print(
        f"  surface deviation: mean {d.mean():.3f}  p95 {np.percentile(d,95):.3f}  "
        f"p99 {np.percentile(d,99):.3f}  max {d.max():.3f} mm"
    )
    print(f"  within 0.10 mm: {100*(d<0.10).mean():.1f}%   "
          f"within 0.25 mm: {100*(d<0.25).mean():.1f}%")
    return d


def overlay(part, path: str = "compare.png"):
    """Slice both models at the same planes and draw them on top of each other."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ref, new = load_ref(), to_trimesh(part)
    zs = [-4.5, -3.0, -1.0, 1.0, 4.0, 6.0, 8.0, 9.0]
    fig, axs = plt.subplots(2, 4, figsize=(24, 13))
    for ax, z in zip(axs.ravel(), zs):
        for m, c, lw in ((ref, "tab:red", 2.2), (new, "tab:blue", 1.0)):
            s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
            if s is None:
                continue
            for e in s.entities:
                v = np.asarray(s.vertices[e.points])
                ax.plot(v[:, 0], v[:, 1], color=c, lw=lw)
        ax.set_title(f"z={z}  (red=original, blue=rebuild)")
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=58)
    print("wrote", path)


if __name__ == "__main__":
    from case import PRESETS, build_case

    # `original` is the preset that reproduces REF; the bare defaults have
    # since moved on (thinner back, stadium flash, button bumps).
    part = build_case(PRESETS["original"])
    report(part, "original preset")
    overlay(part)

"""Parametric Pixel 8 Pro case (build123d).

Derived from "Pixel 8 Pro Case (TPU)" by JamesSF69:
    https://www.printables.com/model/765202-pixel-8-pro-case-tpu
    https://www.printables.com/@JamesSF69_537205
Rebuilt from `pixel8CaseChargeHoleBigger.stl` by measuring the mesh; every
dimension below was taken off that model unless marked otherwise.

The original is CC BY-SA 4.0, so this derivative is too. See LICENSE for
attribution and the list of changes.

SPDX-License-Identifier: CC-BY-SA-4.0

Coordinate system
-----------------
    origin  : centre of the case in X/Y, cavity floor (where the phone's back
              rests) at Z = 0
    +Z      : out of the case opening, i.e. towards the phone's screen
    +Y      : towards the camera bar / top of the phone
    +X      : towards the button side (power + volume are on +X)

`build_case()` returns the part in these coordinates. `export()` drops it onto
Z = 0 first so the STL is ready to slice back-down.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from build123d import (
    Axis,
    Box,
    Circle,
    Plane,
    Pos,
    Rectangle,
    RectangleRounded,
    RegularPolygon,
    export_step,
    export_stl,
    extrude,
    fillet,
    loft,
)


# --------------------------------------------------------------------------
# parameters
# --------------------------------------------------------------------------


@dataclass
class Params:
    # ---- phone -----------------------------------------------------------
    phone_w: float = 76.5  # Pixel 8 Pro body width
    phone_l: float = 162.6  # ... length
    phone_t: float = 8.8  # ... thickness, excluding the camera bar
    phone_corner_r: float = 9.41  # implied by the cavity radius less clearance

    # ---- fit -------------------------------------------------------------
    # 0.59/side is what the original STL used. It works in TPU but is on the
    # loose side; 0.35-0.45 gives a noticeably snugger TPU fit.
    clr_xy: float = 0.592
    clr_z: float = 0.70

    # ---- shell -----------------------------------------------------------
    wall: float = 1.5  # side/end wall thickness
    # The back is exactly as thick as the camera bar plus the skin over it,
    # so `back_thk` is derived rather than free. The Pixel 8 Pro's bar
    # measures 2.5 mm on the phone, which is also what the stock case uses.
    cam_recess: float = 2.5  # depth the phone's camera bar drops into
    cam_skin: float = 1.0  # material left over the camera bar

    # ---- rim / lip -------------------------------------------------------
    # The break around the outer back edge -- the edge the hand runs along.
    # The original chamfers it 3.2 mm at 45 deg on the -X and -Y sides only
    # and leaves +X/+Y square; applied symmetrically here.
    #
    # `back_edge` is how far it climbs the wall. Its ceiling is `back_thk`
    # (3.5 mm): above the cavity floor the wall is only `wall` thick with the
    # phone behind it, and the USB-C slot starts 0.3 mm above that floor.
    # 2.5 leaves the back face a 1.5 mm frame to stand on, since the
    # honeycomb starts wall + rib_border = 4.0 mm in from the outer face.
    #
    # The break is also the case's corner drop protection, and it spends it:
    # the clearance between the phone's back corner and the 45 deg face is
    # (5.59 - back_edge) / sqrt(2), so every millimetre of break costs
    # 0.71 mm of crush distance. 2.5 keeps 2.19 mm there.
    #
    # Three profiles, all printable back-down except where noted:
    #   "soft"    45 deg chamfer, its top edge blended into the wall with
    #             `back_edge_blend`. Rounded where the fingers wrap over it,
    #             still a 45 deg surface off the bed, so it prints clean.
    #   "chamfer" the original's flat 45 deg cut, two hard lines.
    #   "fillet"  a true round, tangent to the bed. Softest in the hand and
    #             the worst to print: the second layer steps out
    #             sqrt(2*r*layer) with nothing under it -- 1.1 mm at r = 3.0
    #             and 0.2 mm layers, so the first few perimeters hang and
    #             droop. Fine at r <= ~0.8; use "soft" for anything bigger.
    back_edge: float = 2.5
    back_edge_style: str = "soft"  # "soft" | "chamfer" | "fillet"
    back_edge_blend: float = 1.5  # "soft": radius rounding chamfer into wall

    rim_h: float = 2.0  # height of the tapered rim above the wall
    # The rim's total inward run equals the wall thickness, so the rim top
    # stays exactly `lip_inset` wide at any wall thickness instead of the rim
    # eating the lip as the wall thins. How that run is split between a flat
    # ledge and the taper is free, and only the ledge is visible: the original
    # spends 1/3 of it on a ledge (1.0 + 2.0 on a 3.0 wall), which leaves an
    # upward-facing shelf around the case that catches the fingers and the
    # pocket lint. Here the whole run is taper, so the wall rises straight
    # into it, and `rim_blend` rounds the crease where they meet.
    rim_ledge_frac: float = 0.0
    rim_taper_frac: float = 1.0
    rim_blend: float = 1.5  # rounds the wall-to-taper crease
    rim_top_r: float = 0.8  # rounds the outer edge of the rim top
    lip_inset: float = 2.70  # how far the lip reaches in past the cavity wall
    lip_ramp_h: float = 1.0  # rise over which the lip ramps inward
    lip_ramp_fillet: float = 0.8  # softens the ramp so the phone slides in

    # ---- camera ----------------------------------------------------------
    cam_pocket_w: float = 76.283  # recess the phone's camera bar drops into
    cam_pocket_h: float = 22.299
    cam_pocket_y: float = 54.547  # centre, from the case centre
    cam_pocket_r: float = 1.0  # original is sharp-cornered; rounded here

    # Openings through the skin: a straight bore, then a 45 deg chamfer that
    # breaks out on the outer face.
    lens_w: float = 50.619
    lens_h: float = 20.564
    lens_r: float = 8.948
    lens_x: float = 6.456
    lens_y: float = 55.007

    flash_r: float = 4.647  # flash + temperature sensor
    # One stadium spanning both, instead of two circles that leave a 0.209 mm
    # unprintable ligament between them. Same outer envelope.
    flash_stadium: bool = True
    flash_x: float = -26.49
    flash_y_hi: float = 59.740
    flash_y_lo: float = 50.237

    cam_straight: float = 0.5  # straight bore before the chamfer starts
    cam_flare: float = 45.0

    # ---- bottom edge ports ----------------------------------------------
    port_z: float = 3.839  # shared centre height of all three openings
    usb_w: float = 15.05  # "ChargeHoleBigger" sizing, as measured
    usb_h: float = 7.08
    usb_x: float = 0.077
    spk_w: float = 14.34
    spk_h: float = 4.68
    spk_x: float = 17.75  # mirrored to -X
    port_chamfer: float = 1.0  # 45 deg relief on the outer face
    port_flare: float = 45.0
    # Bars put back across the openings so the ceiling is not one wide bridge.
    # Speaker bars are permanent (nothing passes through a speaker slot) and
    # turn the slot into a grille. The USB bar is sacrificial -- it blocks the
    # plug and must be snipped out -- so it is off by default.
    spk_bars: int = 2
    spk_bar_w: float = 1.0
    usb_bar: bool = True
    usb_bar_w: float = 0.8

    # ---- button relief ---------------------------------------------------
    # Clearance for the buttons, which stand proud of the phone's frame. The
    # gap the button sees is clr_xy + btn_depth. 0.5 is the thickened file's
    # value; the stock case uses 0.229, giving a 0.821 mm gap that is known
    # to work. There are no button through-holes -- TPU flexes over them.
    btn_depth: float = 0.229
    btn_z0: float = 2.7
    btn_z1: float = 5.9
    btn_r: float = 1.0
    # (y_start, y_end) per pocket: volume down, volume up, power
    btn_pockets: tuple[tuple[float, float], ...] = (
        (-10.72, 0.68),
        (1.78, 13.18),
        (19.28, 31.18),
    )

    # Raised press pads on the outside of the +X wall. Absent from
    # pixel8CaseChargeHoleBigger.stl but present in pixel8proCase.stl, where
    # they measure 1.00 mm proud with 45 deg chamfers; plateau spans below.
    button_bumps: bool = True
    btn_bumps: tuple[tuple[float, float], ...] = (
        (-9.25, -0.50),
        (2.75, 11.50),
        (20.75, 29.50),
    )
    bump_proud: float = 1.00  # how far the pad stands off the wall
    bump_h: float = 1.47  # plateau height in Z
    bump_z: float = 4.27  # plateau centre height
    bump_r: float = 0.60  # plateau corner radius
    bump_chamfer: float = 1.00  # 45 deg skirt around the plateau

    # ---- back style ------------------------------------------------------
    # "flat"   - original: the back is solid all the way out to camera-bar
    #            height. Heaviest by far (~94 g PLA / ~110 g TPU).
    # "bump"   - conventional case: thin back skin plus a raised plateau
    #            around the camera. Lightest.
    # "ribbed"    - keeps the flat back and its flat resting face, but voids
    #               the slab from the cavity side on a square rib grid.
    # "honeycomb" - as "ribbed" but hexagonal cells: stiffer per gram and no
    #               long straight rib runs. Default.
    # Both print back-down with no support and no bridging; the phone rests
    # on the rib tops.
    back_style: str = "honeycomb"

    bump_skin: float = 1.8  # back thickness away from the camera ("bump")

    rib_skin: float = 1.8  # solid skin left against the outer back face
    rib_w: float = 1.5  # wall left between neighbouring pockets
    rib_pitch: float = 16.0  # "ribbed": square grid spacing
    hex_pitch: float = 8.0  # "honeycomb": cell centre spacing
    rib_border: float = 2.5  # solid frame kept around the perimeter
    rib_cam_border: float = 2.0  # solid kept around the camera pocket
    pocket_through: bool = True  # cut cells clean through: open, no skin
    # Break on the bed-side edge of every cell, where the lattice is the face
    # you see and touch on the back of the case. 45 deg, not a round: printed
    # back-down these are first-layer edges, and a fillet there is tangent to
    # the bed, so each layer would step into the cell unsupported. The 45 deg
    # flare advances one layer height per layer and prints clean.
    #
    # It is spent out of the first layer: each cell wall loses 2 x this at the
    # bed, and so does the frame where cells meet it. Measured:
    #
    #   break   rib at bed   first layer   frame
    #   0.30      0.90 mm      3512 mm2    1.24 mm
    #   0.40      0.70 mm      3071 mm2    1.14 mm
    #   0.50      0.50 mm      2617 mm2    1.04 mm
    #
    # 0.40 is the shipped value: 0.70 mm is still under two 0.4 mm extrusion
    # widths but prints as a pair of thin perimeters, and the first layer is
    # one connected island at every value above. 0.50 leaves 0.50 mm walls --
    # a single extrusion -- which is where this stops being safe.
    cell_chamfer: float = 0.4
    pocket_fillet: float = 1.0  # rounds pocket corners; helps flow and stress
    pocket_min_frac: float = 0.30  # drop boundary pockets below this of full

    # ---- side wall vents -------------------------------------------------
    side_vents: bool = True
    side_vent_af: float = 4.5  # hex size across flats
    side_vent_rib: float = 2.0  # material left between vents
    side_vent_z: float = 3.75  # centre height of the row
    side_vent_margin: float = 3.0  # keep-out at corners, ports, buttons

    # ---- derived ---------------------------------------------------------
    @property
    def back_thk(self) -> float:
        """Cavity floor to the outer back face."""
        return self.cam_recess + self.cam_skin

    @property
    def rim_ledge(self) -> float:
        return self.wall * self.rim_ledge_frac

    @property
    def rim_taper(self) -> float:
        return self.wall * self.rim_taper_frac

    @property
    def rim_top_width(self) -> float:
        """Material across the top of the rim."""
        return self.wall - self.rim_ledge - self.rim_taper + self.lip_inset

    @property
    def cav_w(self) -> float:
        return self.phone_w + 2 * self.clr_xy

    @property
    def cav_l(self) -> float:
        return self.phone_l + 2 * self.clr_xy

    @property
    def cav_r(self) -> float:
        return self.phone_corner_r + self.clr_xy

    @property
    def cav_depth(self) -> float:
        """Cavity floor to the top of the rim. The rim taper lives inside
        this height, it is not stacked on top of it."""
        return self.phone_t + self.clr_z

    @property
    def out_w(self) -> float:
        return self.cav_w + 2 * self.wall

    @property
    def out_l(self) -> float:
        return self.cav_l + 2 * self.wall

    @property
    def out_r(self) -> float:
        return self.cav_r + self.wall

    @property
    def wall_top(self) -> float:
        """Z at which the rim taper starts."""
        return self.cav_depth - self.rim_h

    @property
    def rim_top(self) -> float:
        return self.cav_depth

    @property
    def back_z(self) -> float:
        """Z of the outer back face (negative)."""
        return -self.back_thk

    @property
    def cam_pocket_z(self) -> float:
        """Z of the floor of the camera recess (negative)."""
        return self.back_z + self.cam_skin


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _rrect(w: float, h: float, r: float):
    """Rounded rectangle, degrading to a plain rectangle when r ~ 0.

    The radius is held just clear of w/2 and h/2: an exact stadium leaves
    zero-length straight segments, which OCCT then meshes with a seam that
    STL viewers and slicers report as a hole.
    """
    r = min(r, w / 2 - 0.02, h / 2 - 0.02)
    return RectangleRounded(w, h, r) if r > 1e-6 else Rectangle(w, h)


def _bore(section, plane, d_in, d_straight, d_chamfer, angle, sign=1, over=0.5):
    """A cutting solid: a straight bore that then chamfers out to the surface.

    `section` is a callable taking a growth offset and returning a sketch, so
    the same code serves rounded rectangles and circles. The bore starts
    `d_in` along the plane normal and runs in the `sign` direction.
    """
    from math import radians, tan

    grow = d_chamfer * tan(radians(angle))
    z0 = d_in - sign * over
    z1 = d_in + sign * d_straight
    solid = loft([plane.offset(z0) * section(0.0), plane.offset(z1) * section(0.0)])
    if d_chamfer > 0:
        solid += loft(
            [
                plane.offset(z1) * section(0.0),
                plane.offset(z1 + sign * (d_chamfer + over)) * section(grow + over),
            ]
        )
    return solid


def _rr(w, h, r, at=(0.0, 0.0)):
    return lambda g: Pos(at[0], at[1]) * _rrect(w + 2 * g, h + 2 * g, r + g)


def _ci(r, at=(0.0, 0.0)):
    return lambda g: Pos(at[0], at[1]) * Circle(r + g)


# --------------------------------------------------------------------------
# construction
# --------------------------------------------------------------------------


def _outer_shell(p: Params):
    """Outer solid: prismatic walls, then the tapered rim on a small ledge."""
    c = p.back_edge
    if c > p.back_thk:
        raise ValueError(
            f"back_edge {c} exceeds back_thk {p.back_thk}: the break would "
            "climb past the cavity floor into the side wall"
        )
    if p.back_edge_style == "fillet":
        body = Pos(0, 0, p.back_z) * extrude(
            _rrect(p.out_w, p.out_l, p.out_r), amount=p.wall_top - p.back_z
        )
        if c > 0:
            body = fillet(body.faces().sort_by(Axis.Z)[0].edges(), c)
    else:
        z0 = p.back_z + c
        body = Pos(0, 0, z0) * extrude(
            _rrect(p.out_w, p.out_l, p.out_r), amount=p.wall_top - z0
        )
        if c > 0:
            body += loft(
                [
                    Plane.XY.offset(p.back_z)
                    * _rrect(p.out_w - 2 * c, p.out_l - 2 * c, p.out_r - c),
                    Plane.XY.offset(z0) * _rrect(p.out_w, p.out_l, p.out_r),
                ]
            )
            if p.back_edge_style == "soft" and p.back_edge_blend > 0:
                # Round the chamfer-to-wall line. The blend runs 0.414 * r
                # further up the wall than the chamfer does and is tangent
                # there; with the defaults that lands 0.38 mm below the
                # cavity floor, so the side wall keeps its full thickness.
                top = [e for e in body.edges() if abs(e.center().Z - z0) < 1e-6]
                body = fillet(top, p.back_edge_blend)

    ledge_w = p.out_w - 2 * p.rim_ledge
    ledge_l = p.out_l - 2 * p.rim_ledge
    ledge_r = p.out_r - p.rim_ledge
    rim = loft(
        [
            Plane.XY.offset(p.wall_top) * _rrect(ledge_w, ledge_l, ledge_r),
            Plane.XY.offset(p.rim_top)
            * _rrect(
                ledge_w - 2 * p.rim_taper,
                ledge_l - 2 * p.rim_taper,
                ledge_r - p.rim_taper,
            ),
        ]
    )
    shell = body + rim

    # Soften the top. Both edges face upwards and inwards, so neither costs
    # anything to print: every layer above them is smaller than the one below.
    if p.rim_blend > 0:
        crease = [e for e in shell.edges() if abs(e.center().Z - p.wall_top) < 1e-6]
        if crease:
            shell = fillet(crease, p.rim_blend)
    if p.rim_top_r > 0:
        # The cavity is not cut yet, so the top face is the whole rim and its
        # edges are the outer lip of the case.
        shell = fillet(shell.faces().sort_by(Axis.Z)[-1].edges(), p.rim_top_r)
    return shell


def _cavity(p: Params):
    """The phone pocket, including the lip that curls over the screen bezel."""
    pocket = extrude(_rrect(p.cav_w, p.cav_l, p.cav_r), amount=p.wall_top)

    lip_w = p.cav_w - 2 * p.lip_inset
    lip_l = p.cav_l - 2 * p.lip_inset
    lip_r = p.cav_r - p.lip_inset
    ramp_top = p.wall_top + p.lip_ramp_h

    ramp = loft(
        [
            Plane.XY.offset(p.wall_top) * _rrect(p.cav_w, p.cav_l, p.cav_r),
            Plane.XY.offset(ramp_top) * _rrect(lip_w, lip_l, lip_r),
        ]
    )
    land = Pos(0, 0, ramp_top) * extrude(
        _rrect(lip_w, lip_l, lip_r), amount=p.rim_top - ramp_top + 0.5
    )
    return pocket + ramp + land


def _camera_cuts(p: Params):
    """Camera bar recess plus the lens slot and flash/sensor openings."""
    pocket = Pos(0, p.cam_pocket_y, p.cam_pocket_z) * extrude(
        _rrect(p.cam_pocket_w, p.cam_pocket_h, p.cam_pocket_r),
        amount=-p.cam_pocket_z + 0.5,
    )

    # Cut downwards from the floor of the recess out through the back face.
    straight = min(p.cam_straight, p.cam_skin * 0.5)
    d_ch = p.cam_skin - straight

    def cut(section):
        return _bore(
            section, Plane.XY, p.cam_pocket_z, straight, d_ch,
            p.cam_flare, sign=-1,
        )

    cuts = pocket + cut(_rr(p.lens_w, p.lens_h, p.lens_r, at=(p.lens_x, p.lens_y)))

    if p.flash_stadium:
        # The source models put the flash and the temperature sensor in two
        # circles whose centres are 9.503 mm apart with radii summing to
        # 9.294 -- leaving a 0.209 mm ligament between them that no nozzle
        # can print, and which the chamfer below merges away anyway. One
        # stadium spans both and occupies exactly the same envelope.
        span = abs(p.flash_y_hi - p.flash_y_lo)
        cuts += cut(
            _rr(
                2 * p.flash_r,
                span + 2 * p.flash_r,
                p.flash_r,
                at=(p.flash_x, (p.flash_y_hi + p.flash_y_lo) / 2),
            )
        )
    else:
        cuts += cut(_ci(p.flash_r, at=(p.flash_x, p.flash_y_hi)))
        cuts += cut(_ci(p.flash_r, at=(p.flash_x, p.flash_y_lo)))
    return cuts


def _port_cuts(p: Params):
    """USB-C and the two speaker/mic slots in the -Y wall."""
    y_in = -p.cav_l / 2
    y_out = y_in - p.wall

    # Built in the XZ plane looking along -Y: local x is global X, local y is
    # global Z, and offsets run towards -Y.
    plane = Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    d_in = -y_in
    # Never let the chamfer eat the whole wall: on a thin wall it would leave
    # no straight bore at all, and the port would just be a funnel.
    chamfer = min(p.port_chamfer, p.wall / 2)
    d_straight = (y_in - y_out) - chamfer

    def slot(w, h, x):
        return _bore(
            _rr(w, h, min(w, h) / 2, at=(x, p.port_z)),
            plane, d_in, d_straight, chamfer, p.port_flare,
        )

    return {
        "usb": slot(p.usb_w, p.usb_h, p.usb_x),
        "spk+": slot(p.spk_w, p.spk_h, p.spk_x),
        "spk-": slot(p.spk_w, p.spk_h, -p.spk_x),
    }


def _port_bars(p: Params, slots):
    """Vertical bars put back across the port openings, to break up the flat
    ceiling each one would otherwise have to bridge.

    The speaker bars are permanent -- nothing has to pass through a speaker
    slot, so splitting it into a grille removes the bridge for free. The USB
    bar is sacrificial: it stands in the plug's way and is snipped out after
    printing, so it is off by default.
    """
    bars = None

    def add(solid):
        nonlocal bars
        bars = solid if bars is None else bars + solid

    # A box tall and deep enough to cross the whole opening; intersecting it
    # with the slot trims it to that slot's exact profile.
    def bar_at(x, width, slot):
        # Depth is exactly the wall: the slot solid overshoots both faces to
        # cut cleanly, and a bar must not inherit that overshoot.
        box = Pos(x, -p.cav_l / 2 - p.wall / 2, p.port_z) * Box(
            width, p.wall, p.usb_h + p.spk_h + 8
        )
        return box & slot

    if p.spk_bars > 0:
        step = p.spk_w / (p.spk_bars + 1)
        for sx in (p.spk_x, -p.spk_x):
            for i in range(1, p.spk_bars + 1):
                add(bar_at(sx - p.spk_w / 2 + i * step, p.spk_bar_w, slots["spk+" if sx > 0 else "spk-"]))

    if p.usb_bar:
        add(bar_at(p.usb_x, p.usb_bar_w, slots["usb"]))

    return bars


def _button_cuts(p: Params):
    """Clearance pockets for the power and volume buttons.

    The Pixel's buttons stand proud of its frame, so without these the inner
    wall would rest on them and hold them part-pressed. The gap the button
    actually sees is `clr_xy + btn_depth`, not `btn_depth` alone -- 0.821 mm
    in the stock case, 1.092 mm in the thickened one. Keep this whatever the
    wall does; it is clearance, not wall thinning.
    """
    if p.btn_depth <= 0:
        return None
    x0 = p.cav_w / 2
    h = p.btn_z1 - p.btn_z0
    plane = Plane(origin=(0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    cuts = None
    for y0, y1 in p.btn_pockets:
        sk = plane * Pos((y0 + y1) / 2, (p.btn_z0 + p.btn_z1) / 2) * _rrect(
            y1 - y0, h, p.btn_r
        )
        solid = extrude(sk, amount=-p.btn_depth, dir=(1, 0, 0))
        solid = Pos(x0 + p.btn_depth, 0, 0) * solid
        cuts = solid if cuts is None else cuts + solid
    return cuts


def _button_bumps(p: Params):
    """Raised press pads over the buttons, on the outside of the +X wall.

    Measured off `pixel8proCase.stl`: 1.00 mm proud, 45 deg chamfered on all
    four edges. The lower chamfer is what makes them printable back-down --
    a square pad would leave a horizontal overhang.
    """
    if not p.button_bumps:
        return None
    ch = p.bump_chamfer
    plane = Plane(origin=(0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    pads = None
    for y0, y1 in p.btn_bumps:
        base = plane.offset(p.out_w / 2 - 0.01) * Pos(
            (y0 + y1) / 2, p.bump_z
        ) * _rrect(y1 - y0 + 2 * ch, p.bump_h + 2 * ch, p.bump_r + ch)
        pad = extrude(base, amount=p.bump_proud + 0.01, taper=45)
        pads = pad if pads is None else pads + pad
    return pads


def _side_vents(p: Params):
    """Hexagonal vents through the side walls.

    Vertex-up. Note the top edges of a vertex-up hexagon sit at exactly
    30 deg from horizontal, so a strict 45 deg support rule flags them; over
    the ~1.3 mm rise here, converging to a point, TPU handles it. Set
    `rotation=0` below for a flat-top cell if you want it strictly compliant.

    Corners are left solid — they take the drops — and runs with ports or
    button pockets behind them are skipped.
    """
    if not p.side_vents:
        return None
    from math import sqrt

    r = p.side_vent_af / 2  # inradius, half across-flats
    radius = r * 2 / sqrt(3)  # circumradius, half vertex-to-vertex
    pitch = p.side_vent_af + p.side_vent_rib
    m = p.side_vent_margin
    cell = RegularPolygon(radius, 6, rotation=30)
    if p.pocket_fillet > 0:
        cell = fillet(cell.vertices(), min(p.pocket_fillet, r * 0.5))

    btn_lo = min(a for a, _ in p.btn_pockets) - m
    btn_hi = max(b for _, b in p.btn_pockets) + m

    # (half-length of the straight run, inner face distance, exclusions, plane)
    runs = [
        (p.cav_l / 2 - p.cav_r, p.cav_w / 2, [(btn_lo, btn_hi)],
         Plane(origin=(0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))),
        (p.cav_l / 2 - p.cav_r, p.cav_w / 2, [],
         Plane(origin=(0, 0, 0), x_dir=(0, -1, 0), z_dir=(-1, 0, 0))),
        (p.cav_w / 2 - p.cav_r, p.cav_l / 2, [],
         Plane(origin=(0, 0, 0), x_dir=(-1, 0, 0), z_dir=(0, 1, 0))),
        # -Y is skipped entirely: the USB-C and both speaker slots fill it.
    ]

    cuts = None
    for half, inner, excl, plane in runs:
        span = 2 * (half - m - r)
        if span < p.side_vent_af:
            continue
        n = int(span // pitch) + 1
        start = -(n - 1) * pitch / 2
        for i in range(n):
            u = start + i * pitch
            if any(a < u + r and u - r < b for a, b in excl):
                continue
            sk = plane.offset(inner - 0.5) * Pos(u, p.side_vent_z) * cell
            solid = extrude(sk, amount=p.wall + 1.0)
            cuts = solid if cuts is None else cuts + solid
    return cuts


def _field(p: Params):
    """2D region of the back that may be hollowed: the cavity footprint less
    a perimeter frame, less a solid surround for the camera recess."""
    sk = _rrect(
        p.cav_w - 2 * p.rib_border,
        p.cav_l - 2 * p.rib_border,
        max(p.cav_r - p.rib_border, 0.5),
    )
    return sk - Pos(0, p.cam_pocket_y) * _rrect(
        p.cam_pocket_w + 2 * p.rib_cam_border,
        p.cam_pocket_h + 2 * p.rib_cam_border,
        p.cam_pocket_r + p.rib_cam_border,
    )


def _trim(pockets, field, min_area):
    """Clip pockets to the field, dropping slivers left at the boundary."""
    clipped = pockets & field
    keep = [f for f in clipped.faces() if f.area >= min_area]
    if not keep:
        raise ValueError("no pockets survived trimming; check the rib settings")
    out = keep[0]
    for f in keep[1:]:
        out += f
    return out


def _grid_pockets(p: Params):
    """Square pockets on an orthogonal rib grid."""
    field = _field(p)
    w, l = p.cav_w, p.cav_l
    cell = p.rib_pitch - p.rib_w
    n_x = int(w // p.rib_pitch) + 1
    n_y = int(l // p.rib_pitch) + 1
    lim_x, lim_y = w / 2 + cell, l / 2 + cell
    pockets = None
    for i in range(-n_x, n_x + 1):
        for j in range(-n_y, n_y + 1):
            x, y = (i + 0.5) * p.rib_pitch, (j + 0.5) * p.rib_pitch
            if abs(x) > lim_x or abs(y) > lim_y:
                continue  # never reaches the field; skip the fuse
            sq = Pos(x, y) * _rrect(cell, cell, p.pocket_fillet)
            pockets = sq if pockets is None else pockets + sq
    return _trim(pockets, field, p.pocket_min_frac * cell * cell)


def _hex_pockets(p: Params):
    """Hexagonal pockets on a honeycomb lattice.

    `hex_pitch` is the cell centre spacing, so the wall left between two
    neighbouring cells is exactly `rib_w`. Cells are pointy-top, which puts a
    pair of walls across the case's short axis where it needs the stiffness.
    """
    from math import ceil, sqrt

    field = _field(p)
    s = p.hex_pitch
    r_cell = (s - p.rib_w) / 2  # inradius, centre to wall
    radius = r_cell * 2 / sqrt(3)  # circumradius, centre to vertex
    if r_cell <= p.pocket_fillet:
        raise ValueError("hex_pitch too small for rib_w / pocket_fillet")

    cell = RegularPolygon(radius, 6, rotation=30)
    if p.pocket_fillet > 0:
        cell = fillet(cell.vertices(), p.pocket_fillet)
    area = 3 * sqrt(3) / 2 * radius**2

    dx, dy = s, s * sqrt(3) / 2
    n_x = ceil(p.cav_w / dx) + 1
    n_y = ceil(p.cav_l / dy) + 1
    lim_x, lim_y = p.cav_w / 2 + radius, p.cav_l / 2 + radius
    pockets = None
    for j in range(-n_y, n_y + 1):
        for i in range(-n_x, n_x + 1):
            x, y = i * dx + (j & 1) * dx / 2, j * dy
            if abs(x) > lim_x or abs(y) > lim_y:
                continue  # never reaches the field; skip the fuse
            c = Pos(x, y) * cell
            pockets = c if pockets is None else pockets + c
    return _trim(pockets, field, p.pocket_min_frac * area)


def _back_lightening(p: Params):
    """Voids that take mass out of the solid back, per `back_style`."""
    if p.back_style == "flat":
        return None

    if p.back_style == "bump":
        # Everything below the skin goes, except a plateau around the camera.
        skin_z = -p.bump_skin
        slab = Pos(0, 0, p.back_z - 1) * extrude(
            _rrect(p.out_w + 2, p.out_l + 2, p.out_r), amount=(skin_z - p.back_z) + 1
        )
        keep = Pos(0, p.cam_pocket_y, p.back_z - 1) * extrude(
            _rrect(
                p.cam_pocket_w + 2 * p.rib_cam_border,
                p.cam_pocket_h + 2 * p.rib_cam_border,
                p.cam_pocket_r + p.rib_cam_border,
            ),
            amount=(skin_z - p.back_z) + 1,
        )
        return slab - keep

    if p.back_style in ("ribbed", "honeycomb"):
        # Pockets opening *into the cavity* rather than out of the back. That
        # keeps the outer face flat and, printed back-down, every pocket opens
        # upwards: no overhangs, no bridges, no support. The phone rests on
        # the rib tops at Z = 0.
        sk = _grid_pockets(p) if p.back_style == "ribbed" else _hex_pockets(p)
        if p.pocket_through:
            # Cells go clean through the back: the phone shows through, and
            # the back becomes a pure lattice with no skin behind it.
            cut = Pos(0, 0, p.back_z - 0.5) * extrude(sk, amount=p.back_thk + 1.0)
            if p.cell_chamfer > 0:
                # Flare each cell out towards the bed. Extruding downwards
                # with a negative taper grows the section as it descends, so
                # the cell is `cell_chamfer` wider where it breaks out of the
                # back face and nominal `cell_chamfer` above it.
                over = 0.5
                cut += Pos(0, 0, p.back_z + p.cell_chamfer) * extrude(
                    sk, amount=-(p.cell_chamfer + over), taper=-45
                )
            return cut
        depth = p.back_thk - p.rib_skin
        return Pos(0, 0, -depth) * extrude(sk, amount=depth + 0.5)

    raise ValueError(f"unknown back_style {p.back_style!r}")


def build_case(p: Params | None = None):
    p = p or Params()

    part = _outer_shell(p)
    part -= _cavity(p)
    part -= _camera_cuts(p)
    slots = _port_cuts(p)
    for _slot in slots.values():
        part -= _slot
    _bars = _port_bars(p, slots)
    if _bars is not None:
        part += _bars
    btn = _button_cuts(p)
    if btn is not None:
        part -= btn

    bumps = _button_bumps(p)
    if bumps is not None:
        part += bumps

    vents = _side_vents(p)
    if vents is not None:
        part -= vents

    light = _back_lightening(p)
    if light is not None:
        part -= light

    # Soften the ramp-to-lip junction so the phone slides past it.
    if p.lip_ramp_fillet > 0:
        ramp_top = p.wall_top + p.lip_ramp_h
        edges = [e for e in part.edges() if abs(e.center().Z - ramp_top) < 1e-4]
        if edges:
            part = fillet(edges, p.lip_ramp_fillet)

    return part


# --------------------------------------------------------------------------
# export
# --------------------------------------------------------------------------


def export(p: Params | None = None, stem: str = "pixel8pro_case"):
    p = p or Params()
    part = build_case(p)
    part = Pos(0, 0, -part.bounding_box().min.Z) * part  # sit on the bed
    export_stl(part, f"{stem}.stl", tolerance=0.01, angular_tolerance=0.1)
    export_step(part, f"{stem}.step")
    bb = part.bounding_box()
    print(
        f"{stem}: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm, "
        f"{part.volume / 1000:.1f} cm^3"
    )
    return part


# --------------------------------------------------------------------------
# presets
# --------------------------------------------------------------------------

# Named combinations worth building. Everything else is reachable by
# constructing Params directly.
PRESETS = {
    # The design. Bare `Params()` is this, so anything built without an
    # explicit preset is the tested configuration.
    "vented": Params(),
    # Reproduces pixel8CaseChargeHoleBigger.stl for `verify.py`. NOT for
    # printing -- it is the source file's geometry, defects and all. Every
    # deviation from the current defaults is stated explicitly so that
    # changing a default can never silently move the verification baseline.
    "original": Params(
        back_style="flat",
        back_edge=0.8,  # what the baseline was measured against
        back_edge_style="chamfer",
        rim_ledge_frac=1 / 3,  # the source's ledge-and-taper rim, ...
        rim_taper_frac=2 / 3,
        rim_blend=0.0,  # ... unsoftened
        rim_top_r=0.0,
        wall=3.0,
        cam_recess=3.7,
        cam_skin=1.5,
        btn_depth=0.5,
        button_bumps=False,
        flash_stadium=False,
        pocket_through=False,
        cell_chamfer=0.0,
        side_vents=False,
        usb_bar=False,
        spk_bars=0,
    ),
}


def _edge_note(p: Params) -> str:
    if p.back_edge_style == "soft":
        return f"45 deg + R{p.back_edge_blend:.2f} blend"
    return "45 deg chamfer" if p.back_edge_style == "chamfer" else "fillet"


def describe(p: Params) -> str:
    """The thicknesses that actually decide whether a variant is printable."""
    chamfer = min(p.port_chamfer, p.wall / 2)
    return "\n".join(
        [
            f"  outer          {p.out_w:.2f} x {p.out_l:.2f} x {p.rim_top + p.back_thk:.2f} mm",
            f"  side wall      {p.wall:.2f} mm",
            f"  rim top        {p.rim_top_width:.2f} mm",
            f"  behind buttons {p.wall - p.btn_depth:.2f} mm",
            f"  port bore      {p.wall - chamfer:.2f} mm straight + {chamfer:.2f} chamfer",
            f"  back skin      {'none (open cells)' if p.pocket_through else f'{p.rib_skin:.2f} mm'}",
            f"  cell edge      {p.cell_chamfer:.2f} mm 45 deg (ribs {p.rib_w - 2 * p.cell_chamfer:.2f} mm at the bed)",
            f"  back edge      {p.back_edge:.2f} mm {_edge_note(p)}",
            f"  stands on      {p.wall + p.rib_border - p.back_edge:.2f} mm frame",
        ]
    )


if __name__ == "__main__":
    import sys

    name = sys.argv[1] if len(sys.argv) > 1 else "vented"
    if name in PRESETS:
        p = PRESETS[name]
    else:
        # "<style>" or "<style>-open" for a bare back style
        style, _, suffix = name.partition("-")
        p = replace(Params(), back_style=style, pocket_through=(suffix == "open"))
    export(p, f"pixel8pro_case_{name}")
    print(describe(p))

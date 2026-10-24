#!/usr/bin/env python3
"""gen_hall_layout.py - draw `hall_test` straight to GDS with klayout's Python
API, check it, and emit everything a donor die needs beside it.

    python3 gen_hall_layout.py            # -> hall_test.gds, hall_test.lef,
                                          #    hall_test.v, hall_test_pins.json,
                                          #    hall_test_pins.md

Needs `klayout` (pip install klayout, or the one inside any LibreLane image).
No PDK is needed to DRAW; the PDK is needed to CHECK (run_drc.sh).

Every number comes from hall_cfg.py.  This file is the geometry: where each
rectangle goes, and why a wire runs where it runs.

THE DRAWING, BOTTOM UP (cfg.MATRIX = True)

    y = 3..5     GUARD bus (Metal1) joining every ring and p+ strip
    plates       n-well bodies on one baseline (Y_NW0), each in its own p+
                 guard ring; terminal bands at the arm ends with their contact
                 arrays; via1 pads; Metal2 stubs out past the ring to the
                 riser lanes; risers go NORTH
    crossbar     east of the plates, six rows of horizontal-gate NMOS: rows
                 PH0..PH3 (4 x 4, A_((b+d) mod 4) <-> bus b), KV, VBI; bus
                 columns (Metal2) run north to the pins; A-stubs (Metal2) run
                 north to the A-lines; PH/KV/VBI lines (Metal1) run east to
                 their risers
    stage 1      one row of vertical-gate NMOS per plate, one switch on each
                 terminal riser; SEL[p] (Metal1) along the gate pads; the far
                 side of each switch stubs north to A_k
    p+ strip     a substrate tap the full width of the cell, 2 um above the
                 switches (DF.14: every NCOMP within 20 um of a tap)
    A0..A3       four Metal3 lines the full width of the cell
    y = H        north edge: one Metal2 pin per external net, 2 x 4 um

Per cross plate the four Metal2 routes never cross each other:
    T1 (north)  riser straight up at x = cx
    T2 (east)   stub east along y = cy to lane 1, riser up
    T4 (west)   stub west along y = cy to lane 1, riser up
    T3 (south)  stub west along y = south terminal (below T4's riser start)
                to lane 2, riser up
so the risers stand west -> east as T3 T4 T1 T2, 4 um apart on the west side
- one switch each.  A plate in cfg.DIRECT also sends each terminal straight
to a pin of its own, 2.7 um east of its riser.

With cfg.MATRIX = False the risers go to pins and nothing else is drawn (the
5-pin and 22-pin cells).

FOUR CHECKS THE GENERATOR MAKES BEFORE IT WRITES ANYTHING

 1. SYMMETRY.  For every plate, the union of (n-well, NCOMP, PCOMP) inside its
    ring is compared with its own 90-degree rotation about the plate centre;
    they must be identical.  Spinning-current offset cancellation assumes it.
 2. CONNECTIVITY.  A LayoutToNetlist pass over COMP/poly/contact/Metal1-3
    (n-well deliberately NOT connected) must find every net carrying exactly
    one label - no net with two (a short), none with zero (an open).
 3. DEVICES.  The same pass extracts the NMOS switches; the set of
    (gate, source, drain) net triples must equal the switch list hall_cfg
    implies.  That is an LVS of the matrix, against the intent, with no PDK.
 4. NO METAL OVER A PLATE BODY.  Metal1 and Metal2 inside any n-well must lie
    on a terminal band, or be the p+ cover's tie on x12p.
"""
import json
import os
import sys

import klayout.db as db

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hall_cfg as cfg  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

ly = db.Layout()
ly.dbu = cfg.DBU
top = ly.create_cell(cfg.CELL)
_LI = {}


def LI(name):
    if name not in _LI:
        _LI[name] = ly.layer(*cfg.LAYERS[name])
    return _LI[name]


def snap(v):
    return round(v / cfg.GRID) * cfg.GRID


def box(layer, x1, y1, x2, y2):
    r = db.DBox(snap(min(x1, x2)), snap(min(y1, y2)), snap(max(x1, x2)), snap(max(y1, y2)))
    top.shapes(LI(layer)).insert(r)
    return r


def poly(layer, pts):
    p = db.DPolygon([db.DPoint(snap(x), snap(y)) for x, y in pts])
    top.shapes(LI(layer)).insert(p)
    return p


def label(layer, name, x, y):
    top.shapes(LI(layer)).insert(db.DText(name, db.DTrans(db.DVector(snap(x), snap(y)))))


def cross_pts(cx, cy, w, half):
    """12-vertex Greek cross: arm width w, overall half-extent half."""
    h = w / 2
    return [(cx - h, cy - half), (cx + h, cy - half), (cx + h, cy - h), (cx + half, cy - h),
            (cx + half, cy + h), (cx + h, cy + h), (cx + h, cy + half), (cx - h, cy + half),
            (cx - h, cy + h), (cx - half, cy + h), (cx - half, cy - h), (cx - h, cy - h)]


def fill_array(layer, x1, y1, x2, y2, size, pitch, enc):
    """Centred array of `size` squares on `pitch` inside the rect inset by enc."""
    ix1, iy1, ix2, iy2 = x1 + enc, y1 + enc, x2 - enc, y2 - enc
    nx = int((ix2 - ix1 - size) // pitch + 1e-9) + 1
    ny = int((iy2 - iy1 - size) // pitch + 1e-9) + 1
    assert nx >= 1 and ny >= 1, (layer, x1, y1, x2, y2)
    ox = (ix1 + ix2) / 2 - ((nx - 1) * pitch + size) / 2
    oy = (iy1 + iy2) / 2 - ((ny - 1) * pitch + size) / 2
    for i in range(nx):
        for j in range(ny):
            box(layer, ox + i * pitch, oy + j * pitch, ox + i * pitch + size, oy + j * pitch + size)
    return nx * ny


def contact_rect(x1, y1, x2, y2):
    """One terminal / tap contact band: contacts on CT_PITCH + the Metal1 plate."""
    n = fill_array("contact", x1, y1, x2, y2, cfg.CT, cfg.CT_PITCH, cfg.CT_ENC_COMP)
    m1 = box("metal1", x1 - cfg.CT_ENC_M1 + cfg.CT_ENC_COMP, y1 - cfg.CT_ENC_M1 + cfg.CT_ENC_COMP,
             x2 + cfg.CT_ENC_M1 - cfg.CT_ENC_COMP, y2 + cfg.CT_ENC_M1 - cfg.CT_ENC_COMP)
    return n, m1


def via1(x, y):
    return box("via1", x - cfg.VIA / 2, y - cfg.VIA / 2, x + cfg.VIA / 2, y + cfg.VIA / 2)


def via2(x, y):
    box("via2", x - cfg.VIA / 2, y - cfg.VIA / 2, x + cfg.VIA / 2, y + cfg.VIA / 2)


def via_pad(cx, cy, cols, rows):
    """A cols x rows via1 array centred at (cx, cy) with its Metal2 pad (the
    Metal1 under it is the terminal plate, already drawn)."""
    wx = (cols - 1) * cfg.VIA_PITCH + cfg.VIA
    wy = (rows - 1) * cfg.VIA_PITCH + cfg.VIA
    x1, y1 = cx - wx / 2, cy - wy / 2
    for i in range(cols):
        for j in range(rows):
            box("via1", x1 + i * cfg.VIA_PITCH, y1 + j * cfg.VIA_PITCH,
                x1 + i * cfg.VIA_PITCH + cfg.VIA, y1 + j * cfg.VIA_PITCH + cfg.VIA)
    e = cfg.VIA_ENC
    return box("metal2", x1 - e, y1 - e, x1 + wx + e, y1 + wy + e)


def hrun(layer, y, xa, xb, w):
    return box(layer, xa, y - w / 2, xb, y + w / 2)


def vrun(layer, x, ya, yb, w):
    return box(layer, x - w / 2, ya, x + w / 2, yb)


def m1pad(x, y, s=0.6):
    return box("metal1", x - s / 2, y - s / 2, x + s / 2, y + s / 2)


# ---------------------------------------------------------------- bookkeeping
PINS = []            # (name, x) -> sorted by x at the end
RISER_X = []         # x of EVERY plate terminal riser (oc12's Q plate included)
PLATE_SHAPES = []    # per plate: dict(id, cx, cy, half, shapes=[(layer, DPolygon)])
TERMINALS = []       # (plate id, Tn, DBox of the terminal COMP)
COVER_TIES = []      # metal allowed inside an n-well (x12p's tie)
EXPECT_DEV = []      # (gate net, frozenset{net a, net b}) the matrix must contain
PIN_Y = cfg.H - cfg.PIN_D
PIN_TOP = cfg.H - cfg.PIN_D / 2
TIDX = {"T1": 0, "T2": 1, "T3": 2, "T4": 3}


def pin(name, x):
    box("metal2", x - cfg.PIN_W / 2, PIN_Y, x + cfg.PIN_W / 2, cfg.H)
    label("metal2_label", name, x, PIN_TOP)
    PINS.append((name, x))


def riser(x, y_from, y_to, name=None):
    """Metal2 riser; with a name it ends in a pin (y_to must be the pin row)."""
    vrun("metal2", x, y_from, y_to, cfg.M2_W)
    if name is not None:
        assert abs(y_to - PIN_TOP) < 1e-6
        pin(name, x)


def guard_ring(x1, y1, x2, y2, cx):
    """p+ ring around an n-well bbox, with its contacts, Metal1, and a Metal1
    stub down to the GUARD bus."""
    g, w = cfg.RING_GAP, cfg.RING_W
    ox1, oy1, ox2, oy2 = x1 - g - w, y1 - g - w, x2 + g + w, y2 + g + w
    sides = [(ox1, oy1, ox2, oy1 + w), (ox1, oy2 - w, ox2, oy2),
             (ox1, oy1, ox1 + w, oy2), (ox2 - w, oy1, ox2, oy2)]
    for (a, b, c, d) in sides:
        box("comp", a, b, c, d)
        box("pplus", a - cfg.IMP_EXT, b - cfg.IMP_EXT, c + cfg.IMP_EXT, d + cfg.IMP_EXT)
        contact_rect(a, b, c, d)
    vrun("metal1", cx, cfg.BUS_Y[1] - 0.5, oy1 + w / 2, cfg.M1_W)
    return (ox1, oy1, ox2, oy2)


def ptap_strip(x1, x2, y1):
    """A horizontal p+ substrate-tap strip (COMP 1.0 tall) with its Metal1."""
    y2 = y1 + 1.0
    box("comp", x1, y1, x2, y2)
    box("pplus", x1 - cfg.IMP_EXT, y1 - cfg.IMP_EXT, x2 + cfg.IMP_EXT, y2 + cfg.IMP_EXT)
    contact_rect(x1, y1, x2, y2)
    return (y1 + y2) / 2


def terminal_band(x1, y1, x2, y2):
    """NCOMP band with contacts and Metal1; returns the Metal1 plate box."""
    box("comp", x1, y1, x2, y2)
    e = cfg.IMP_EXT
    box("nplus", x1 - e, y1 - e, x2 + e, y2 + e)
    n, m1 = contact_rect(x1, y1, x2, y2)
    return m1, n


# ---------------------------------------------------------------- PLATES
def draw_cross(p, cx, cy, y_to, shield_name=None):
    """A Greek cross plate at (cx, cy).  `y_to` = {Tn: y} where each riser
    ends.  Returns the riser x per terminal."""
    w, a = p["w"], p["a"]
    half = cfg.cross_half(w, a)
    shapes = []
    nw = poly("nwell", cross_pts(cx, cy, w, half))
    shapes.append(("nwell", nw))
    E, D, hw = cfg.NW_ENC_NCOMP, cfg.TERM_D, w / 2
    bands = {
        "T1": (cx - hw + E, cy + half - E - D, cx + hw - E, cy + half - E),
        "T2": (cx + half - E - D, cy - hw + E, cx + half - E, cy + hw - E),
        "T3": (cx - hw + E, cy - half + E, cx + hw - E, cy - half + E + D),
        "T4": (cx - half + E, cy - hw + E, cx - half + E + D, cy + hw - E),
    }
    for t, (x1, y1, x2, y2) in bands.items():
        terminal_band(x1, y1, x2, y2)
        shapes.append(("ncomp", db.DPolygon(db.DBox(x1, y1, x2, y2))))
        TERMINALS.append((p["id"], t, db.DBox(x1, y1, x2, y2)))
    if p.get("cover"):
        ec = cfg.NW_ENC_PCOMP
        half_c = half - E - D - cfg.COVER_GAP
        cov = poly("comp", cross_pts(cx, cy, w - 2 * ec, half_c))
        poly("pplus", cross_pts(cx, cy, w - 2 * ec + 2 * cfg.IMP_EXT, half_c + cfg.IMP_EXT))
        shapes.append(("pcomp", cov))
        tx, ty = cx + 4.0, cy + 4.0
        tb = 0.36 + cfg.CT_ENC_COMP
        contact_rect(tx - tb, ty - tb, tx + tb, ty + tb)
        COVER_TIES.append(box("metal1", tx - 0.6, ty - 0.6, tx + 0.6, ty + 0.6))
        via1(tx, ty)
        COVER_TIES.append(box("metal2", tx - 0.5, ty - 0.5, tx + 0.5, ty + 0.5))
        riser(tx, ty - 0.5, PIN_TOP, shield_name)
    rx = {}
    t1 = via_pad(cx, cy + half - E - D / 2, cfg.VIA_COLS, cfg.VIA_ROWS)
    riser(cx, t1.bottom, y_to["T1"])
    rx["T1"] = cx
    x_e = cx + half + cfg.LANE1
    via_pad(cx + half - E - D / 2, cy, cfg.VIA_ROWS, cfg.VIA_COLS)
    hrun("metal2", cy, cx + half - E - D / 2 - 0.5, x_e + cfg.M2_W / 2, cfg.M2_W)
    riser(x_e, cy - cfg.M2_W / 2, y_to["T2"])
    rx["T2"] = x_e
    x_w = cx - half - cfg.LANE1
    via_pad(cx - half + E + D / 2, cy, cfg.VIA_ROWS, cfg.VIA_COLS)
    hrun("metal2", cy, x_w - cfg.M2_W / 2, cx - half + E + D / 2 + 0.5, cfg.M2_W)
    riser(x_w, cy - cfg.M2_W / 2, y_to["T4"])
    rx["T4"] = x_w
    x_s = cx - half - cfg.LANE2
    ys = cy - half + E + D / 2
    via_pad(cx, ys, cfg.VIA_COLS, cfg.VIA_ROWS)
    hrun("metal2", ys, x_s - cfg.M2_W / 2, cx + 0.5, cfg.M2_W)
    riser(x_s, ys - cfg.M2_W / 2, y_to["T3"])
    rx["T3"] = x_s
    ring = guard_ring(cx - half, cy - half, cx + half, cy + half, cx)
    PLATE_SHAPES.append(dict(id=p["id"], cx=cx, cy=cy, half=half, shapes=shapes, ring=ring))
    RISER_X.extend(rx.values())
    return rx


def draw_square(p, cx, cy, y_to):
    s, c = p["s"], p["c"]
    half = s / 2
    shapes = []
    nw = box("nwell", cx - half, cy - half, cx + half, cy + half)
    shapes.append(("nwell", db.DPolygon(nw)))
    E = cfg.NW_ENC_NCOMP
    i1, i2 = half - E - c, half - E
    corners = {"T1": (-1, +1), "T2": (+1, +1), "T3": (+1, -1), "T4": (-1, -1)}  # NW NE SE SW
    centres = {}
    for t, (sx, sy) in corners.items():
        x1, x2 = sorted([cx + sx * i1, cx + sx * i2])
        y1, y2 = sorted([cy + sy * i1, cy + sy * i2])
        terminal_band(x1, y1, x2, y2)
        shapes.append(("ncomp", db.DPolygon(db.DBox(x1, y1, x2, y2))))
        TERMINALS.append((p["id"], t, db.DBox(x1, y1, x2, y2)))
        centres[t] = ((x1 + x2) / 2, (y1 + y2) / 2)
        via_pad(centres[t][0], centres[t][1], 2, 2)
    x1n, y1n = centres["T1"]
    riser(x1n, y1n, y_to["T1"])
    x2n, y2n = centres["T2"]
    riser(x2n, y2n, y_to["T2"])
    x4, y4 = centres["T4"]
    xw = cx - half - cfg.LANE1
    hrun("metal2", y4, xw - cfg.M2_W / 2, x4, cfg.M2_W)
    riser(xw, y4 - cfg.M2_W / 2, y_to["T4"])
    x3, y3 = centres["T3"]
    xe = cx + half + cfg.LANE1
    hrun("metal2", y3, x3, xe + cfg.M2_W / 2, cfg.M2_W)
    riser(xe, y3 - cfg.M2_W / 2, y_to["T3"])
    ring = guard_ring(cx - half, cy - half, cx + half, cy + half, cx)
    PLATE_SHAPES.append(dict(id=p["id"], cx=cx, cy=cy, half=half, shapes=shapes, ring=ring))
    rx = {"T1": x1n, "T2": x2n, "T3": xe, "T4": xw}
    RISER_X.extend(rx.values())
    return rx


def draw_ocpair(p, cxP, cxQ, cy, y_to):
    """Two crosses P and Q; Q's four risers stop at Metal1 merge bars that tie
    them onto P's risers, so P's four risers ARE the pair's four nets."""
    pid = p["id"]
    rxP = draw_cross(dict(p, id=pid + "_P"), cxP, cy, y_to)
    bar_y = {k: cfg.OC_BAR_Y0 + i * cfg.OC_BAR_PITCH for i, k in enumerate(("T2", "T4", "T3", "T1"))}
    rxQ = draw_cross(dict(p, id=pid + "_Q"), cxQ, cy, {k: bar_y[k] + cfg.VIA_ENC + 0.1 for k in bar_y})
    # B1 = P.T1 + Q.T2, B2 = P.T3 + Q.T4, H1 = P.T2 + Q.T3, H2 = P.T4 + Q.T1
    pairs = [("T1", "T2"), ("T3", "T4"), ("T2", "T3"), ("T4", "T1")]
    for (tp, tq) in pairs:
        xa, xb, y = rxP[tp], rxQ[tq], bar_y[tq]
        hrun("metal1", y, min(xa, xb) - cfg.M1_W / 2, max(xa, xb) + cfg.M1_W / 2, cfg.M1_W)
        via1(xa, y)
        via1(xb, y)
    assert max(bar_y.values()) + cfg.M1_W < min(y_to.values()) - 1.0, "oc12's bars reach the switch row"
    return rxP


# ---------------------------------------------------------------- SWITCHES
def nmos_v(x_r, y0):
    """Vertical-gate nfet_06v0 whose LEFT contact column is centred on x_r
    (the terminal riser) and whose RIGHT column is at x_r + 1.6 (the A side).
    Gate pad below.  Returns the key points."""
    L, W, SD, co = cfg.MOS_L, cfg.MOS_W, cfg.MOS_SD, cfg.MOS_CT_OFF
    xl = x_r - (SD - co)                      # COMP left edge
    xg1, xg2 = x_r + co, x_r + co + L         # gate
    xr = xg2 + co                             # right contact column
    xr2 = xr + (SD - co)                      # COMP right edge
    box("comp", xl, y0, xr2, y0 + W)
    box("nplus", xl - cfg.NP_EXT, y0 - cfg.NP_EXT, xr2 + cfg.NP_EXT, y0 + W + cfg.NP_EXT)
    box("poly2", xg1, y0 - cfg.MOS_EC, xg2, y0 + W + cfg.MOS_EC)
    gx = (xg1 + xg2) / 2
    gpy = y0 - cfg.MOS_EC - cfg.MOS_GP / 2
    box("poly2", gx - cfg.MOS_GP / 2, y0 - cfg.MOS_EC - cfg.MOS_GP, gx + cfg.MOS_GP / 2, y0 - cfg.MOS_EC)
    box("contact", gx - cfg.CT / 2, gpy - cfg.CT / 2, gx + cfg.CT / 2, gpy + cfg.CT / 2)
    m1pad(gx, gpy)
    for xc in (x_r, xr):
        fill_array("contact", xc - cfg.CT / 2 - cfg.CT_ENC_COMP, y0, xc + cfg.CT / 2 + cfg.CT_ENC_COMP, y0 + W,
                   cfg.CT, cfg.CT_PITCH, cfg.CT_ENC_COMP)
        box("metal1", xc - cfg.BAR_W / 2, y0 + 0.05, xc + cfg.BAR_W / 2, y0 + W - 0.05)
    box("dualgate", xl - cfg.DG_ENC_COMP, y0 - cfg.MOS_EC - cfg.MOS_GP - cfg.DG_ENC_POLY,
        xr2 + cfg.DG_ENC_COMP, y0 + W + cfg.MOS_EC + cfg.DG_ENC_POLY)
    return dict(xl_bar=x_r, xr_bar=xr, gx=gx, gpy=gpy, y_lo=y0 + 0.8, y_hi=y0 + W - 0.8)


def nmos_h(x0, y0):
    """Horizontal-gate nfet_06v0: COMP from x0 to x0 + W, BOTTOM contact row
    centred on y0 (the bus side), TOP row at y0 + 1.6 (the A side), gate pad
    beyond the right end."""
    L, W, SD, co = cfg.MOS_L, cfg.MOS_W, cfg.MOS_SD, cfg.MOS_CT_OFF
    yb = y0 - (SD - co)
    yg1, yg2 = y0 + co, y0 + co + L
    yt = yg2 + co
    yt2 = yt + (SD - co)
    box("comp", x0, yb, x0 + W, yt2)
    box("nplus", x0 - cfg.NP_EXT, yb - cfg.NP_EXT, x0 + W + cfg.NP_EXT, yt2 + cfg.NP_EXT)
    box("poly2", x0 - cfg.MOS_EC, yg1, x0 + W + cfg.MOS_EC, yg2)
    gy = (yg1 + yg2) / 2
    gpx = x0 + W + cfg.MOS_EC + cfg.MOS_GP / 2
    box("poly2", x0 + W + cfg.MOS_EC, gy - cfg.MOS_GP / 2, x0 + W + cfg.MOS_EC + cfg.MOS_GP, gy + cfg.MOS_GP / 2)
    box("contact", gpx - cfg.CT / 2, gy - cfg.CT / 2, gpx + cfg.CT / 2, gy + cfg.CT / 2)
    m1pad(gpx, gy)
    for yc in (y0, yt):
        fill_array("contact", x0, yc - cfg.CT / 2 - cfg.CT_ENC_COMP, x0 + W, yc + cfg.CT / 2 + cfg.CT_ENC_COMP,
                   cfg.CT, cfg.CT_PITCH, cfg.CT_ENC_COMP)
        box("metal1", x0 + 0.05, yc - cfg.BAR_W / 2, x0 + W - 0.05, yc + cfg.BAR_W / 2)
    box("dualgate", x0 - cfg.MOS_EC - cfg.DG_ENC_POLY, yb - cfg.DG_ENC_COMP,
        x0 + W + cfg.MOS_EC + cfg.MOS_GP + cfg.DG_ENC_POLY, yt2 + cfg.DG_ENC_COMP)
    return dict(y_bot=y0, y_top=yt, gy=gy, gpx=gpx)


def a_line_y(k):
    return cfg.Y_A0 + k * cfg.A_PITCH


def a_net(k):
    """What the k-th A-line is called: an internal net with the crossbar,
    the output pin itself without it."""
    return f"A{k}" if cfg.CROSSBAR else cfg.OUT_NAMES[k]


def stub_to_a(x, y_from, k):
    """Metal2 stub (STUB_W) from y_from up to A_k, with its via2."""
    ya = a_line_y(k)
    vrun("metal2", x, y_from, ya + 0.5, cfg.STUB_W)
    via2(x, ya)


def stage1_row(pid, rx, tnames, sel_name):
    """Four switches on a plate's four risers.  `tnames` = {Tn: net name}."""
    y0 = cfg.Y_ROW
    gxs = []
    for t in ("T1", "T2", "T3", "T4"):
        x_r = rx[t]
        d = nmos_v(x_r, y0)
        via1(x_r, d["y_lo"])                                   # riser -> left bar
        via1(d["xr_bar"], d["y_hi"])                           # right bar -> A stub
        stub_to_a(d["xr_bar"], d["y_hi"] - 0.25, TIDX[t])
        gxs.append(d["gx"])
        EXPECT_DEV.append((sel_name, frozenset({tnames[t], a_net(TIDX[t])})))
        gpy = d["gpy"]
    x_sel = min(rx.values()) - cfg.SEL_OFF
    hrun("metal1", gpy, x_sel, max(gxs) + 0.3, 0.4)
    m1pad(x_sel, gpy)
    via1(x_sel, gpy)
    box("metal2", x_sel - 0.5, gpy - 0.5, x_sel + 0.5, gpy + 0.5)
    riser(x_sel, gpy - 0.5, PIN_TOP, sel_name)


def crossbar(x_cb0):
    """Six rows x four columns east of the plates.  Returns (x_end, bus x's)."""
    W = cfg.MOS_W
    cols = [x_cb0 + b * cfg.XB_COL_PITCH for b in range(4)]
    bus_x = [x0 + cfg.XB_BUS_OFF for x0 in cols]
    x_end = cols[-1] + W + cfg.MOS_EC + cfg.MOS_GP        # east edge of the last gate pad
    # which (row, col) exist, and what the top bar reaches
    plan = {}
    for d in range(4):
        for b in range(4):
            plan[(d, b)] = ("A", (b + d) % 4)
    plan[(4, 0)] = ("A", 0)
    plan[(4, 1)] = ("A", 0)
    plan[(4, 2)] = ("A", 2)
    plan[(4, 3)] = ("A", 2)
    plan[(5, 0)] = ("PIN", cfg.VBIAS_INT)
    plan[(5, 2)] = ("GUARD", None)
    y_rows = [cfg.Y_XB0 + (cfg.MOS_SD - cfg.MOS_CT_OFF) + d * cfg.XB_ROW_PITCH for d in range(6)]
    strip_lo = ptap_strip(x_cb0 - 4.0, x_end + 4.0, cfg.Y_XB0 - 3.5)
    strip_hi = ptap_strip(x_cb0 - 4.0, x_end + 4.0, cfg.Y_XB0 + 5 * cfg.XB_ROW_PITCH + (cfg.MOS_SD - cfg.MOS_CT_OFF) + 1.95 + 2.2)
    for (d, b), (kind, arg) in sorted(plan.items()):
        x0, y0 = cols[b], y_rows[d]
        dev = nmos_h(x0, y0)
        via1(bus_x[b], dev["y_bot"])                            # bottom bar -> bus column
        xs = x0 + cfg.XB_STUB_OFF + d
        via1(xs, dev["y_top"])
        row = cfg.ROW_NAMES[d]
        if kind == "A":
            stub_to_a(xs, dev["y_top"] - 0.25, arg)
            EXPECT_DEV.append((row, frozenset({cfg.BUS_NAMES[b], f"A{arg}"})))
        elif kind == "PIN":
            vrun("metal2", xs, dev["y_top"] - 0.25, PIN_TOP, cfg.STUB_W)
            pin(arg, xs)
            EXPECT_DEV.append((row, frozenset({cfg.BUS_NAMES[b], arg})))
        else:  # GUARD: down to the lower strip
            vrun("metal2", xs, strip_lo - 0.5, dev["y_top"] + 0.25, cfg.STUB_W)
            via1(xs, strip_lo)
            EXPECT_DEV.append((row, frozenset({cfg.BUS_NAMES[b], cfg.GUARD_NAME})))
    # row lines (Metal1) through the gate pads, east to their risers
    for d in range(6):
        gy = y_rows[d] + cfg.MOS_CT_OFF + cfg.MOS_L / 2
        present = [b for b in range(4) if (d, b) in plan]
        x_pe = x_end + 2.0 + 3.0 * d
        hrun("metal1", gy, cols[min(present)] + W + cfg.MOS_EC, x_pe, 0.3)
        m1pad(x_pe, gy)
        via1(x_pe, gy)
        box("metal2", x_pe - 0.5, gy - 0.5, x_pe + 0.5, gy + 0.5)
        riser(x_pe, gy - 0.5, PIN_TOP, cfg.ROW_NAMES[d])
    # bus columns north to their pins
    for b in range(4):
        riser(bus_x[b], y_rows[0] - 0.5, PIN_TOP, cfg.BUS_NAMES[b])
    # GUARD: one Metal2 vertical at the crossbar's west edge ties the bus,
    # both crossbar strips and the full-width stage-1 strip together
    xg = x_cb0 - 3.0
    gy_bus = (cfg.BUS_Y[0] + cfg.BUS_Y[1]) / 2
    vrun("metal2", xg, gy_bus - 0.5, cfg.Y_STRIP + 0.5 + 0.5, cfg.M2_W)
    for y in (gy_bus, strip_lo, strip_hi, cfg.Y_STRIP + 0.5):
        via1(xg, y)
    return x_end + 2.0 + 3.0 * 5 + 4.0


# ---------------------------------------------------------------- PLACE
def tnames_for(p, nm):
    if p["kind"] == "ocpair":
        return {"T1": nm(p["id"], "B1"), "T2": nm(p["id"], "H1"), "T3": nm(p["id"], "B2"), "T4": nm(p["id"], "H2")}
    return {t: nm(p["id"], t) for t in ("T1", "T2", "T3", "T4")}


def place():
    x = cfg.X0
    # the riser must cover the via at Y_ROW + 0.8 by VIA_ENC + a margin (V1.4a)
    y_riser = cfg.Y_ROW + 0.8 + 0.3 if cfg.MATRIX else PIN_TOP
    rows = []   # (plate, rx, tnames)
    for p in cfg.PLATES:
        half = cfg.plate_half(p)
        pid = p["id"]
        nm = cfg.PIN_NAME[p["kind"]]
        tn = tnames_for(p, nm)
        y_to = {t: y_riser for t in ("T1", "T2", "T3", "T4")}
        if p["kind"] == "cross":
            cx, cy = x + half, cfg.Y_NW0 + half
            rx = draw_cross(p, cx, cy, y_to, shield_name=nm(pid, cfg.SHIELD_SUFFIX) if p.get("cover") else None)
            x = cx + half + cfg.GAP
        elif p["kind"] == "square":
            cx, cy = x + half, cfg.Y_NW0 + half
            rx = draw_square(p, cx, cy, y_to)
            x = cx + half + cfg.GAP
        else:
            cxP, cy = x + half, cfg.Y_NW0 + half
            cxQ = cxP + 2 * half + cfg.GAP
            rx = draw_ocpair(p, cxP, cxQ, cy, y_to)
            x = cxQ + half + cfg.GAP
        rows.append((p, rx, tn))
        if not cfg.MATRIX:
            for t, xr in rx.items():
                pin(tn[t], xr)
    last_riser = max(RISER_X)      # NOT the rows' rx: oc12 reports only P's
    if cfg.MATRIX:
        for p, rx, tn in rows:
            sel = f"SEL_{p['id'].upper()}"
            stage1_row(p["id"], rx, tn, sel)
            direct = p["id"] in cfg.DIRECT
            for t, xr in rx.items():
                if direct:
                    xd = xr + cfg.DIRECT_OFF
                    yj = cfg.Y_ROW - 3.0
                    hrun("metal2", yj, xr - cfg.M2_W / 2, xd + cfg.STUB_W / 2, cfg.STUB_W)
                    vrun("metal2", xd, yj, PIN_TOP, cfg.STUB_W)
                    pin(tn[t], xd)
                else:
                    label("metal2_label", tn[t], xr, cfg.Y_ROW - 2.0)
        if cfg.CROSSBAR:
            W = crossbar(last_riser + cfg.XB_GAP)
            x_a_end = W - 3.0
        else:
            # the A-lines ARE the outputs: each turns up into a pin at the
            # east end, 3 um apart, via2 down onto its own line
            x_out0 = last_riser + cfg.XB_GAP
            for k in range(4):
                x = x_out0 + 3.0 * k
                via2(x, a_line_y(k))
                box("metal2", x - 0.5, a_line_y(k) - 0.5, x + 0.5, a_line_y(k) + 0.5)
                riser(x, a_line_y(k) - 0.5, PIN_TOP, cfg.OUT_NAMES[k])
            x_a_end = x_out0 + 3.0 * 3 + 0.5
            W = x_a_end + 8.0
            # GUARD: tie the bus and the p+ strip at the east edge
            xg = W - 4.0
            gy_bus = (cfg.BUS_Y[0] + cfg.BUS_Y[1]) / 2
            vrun("metal2", xg, gy_bus - 0.5, cfg.Y_STRIP + 1.0, cfg.M2_W)
            via1(xg, gy_bus)
            via1(xg, cfg.Y_STRIP + 0.5)
        # the full-width p+ strip and the A-lines (from the west margin: the
        # first plate's T3 switch stubs up at X0 - 6.4)
        ptap_strip(3.0, W - 3.0, cfg.Y_STRIP)
        for k in range(4):
            hrun("metal3", a_line_y(k), 6.0, x_a_end, 1.0)
            if cfg.CROSSBAR:
                label("metal3_label", f"A{k}", 7.0, a_line_y(k))
    else:
        W = x - cfg.GAP + cfg.X0
    # GUARD bus and its riser/pin
    gy = (cfg.BUS_Y[0] + cfg.BUS_Y[1]) / 2
    hrun("metal1", gy, 3.0, W - 3.0, cfg.BUS_Y[1] - cfg.BUS_Y[0])
    via1(cfg.GUARD_X, gy)
    box("metal2", cfg.GUARD_X - 0.5, gy - 0.5, cfg.GUARD_X + 0.5, gy + 0.5)
    riser(cfg.GUARD_X, gy - 0.5, PIN_TOP, cfg.GUARD_NAME)
    box("pr_bndry", 0, 0, W, cfg.H)
    return W


# ---------------------------------------------------------------- CHECKS
def check_symmetry():
    for ps in PLATE_SHAPES:
        cx, cy = ps["cx"], ps["cy"]
        for lname in ("nwell", "ncomp", "pcomp"):
            reg = db.Region()
            for ln, pg in ps["shapes"]:
                if ln == lname:
                    # NOT db.DPolygon(pg).to_itype(): the copy-constructor
                    # route lands 0.5 um off in y (klayout 0.30.9, measured)
                    reg.insert(pg.to_itype(ly.dbu))
            if reg.is_empty():
                continue
            reg.merge()
            icx, icy = int(round(cx / ly.dbu)), int(round(cy / ly.dbu))
            t = db.Trans(db.Vector(icx, icy)) * db.Trans(db.Trans.R90) * db.Trans(db.Vector(-icx, -icy))
            diff = reg ^ reg.transformed(t)
            assert diff.is_empty(), f"{ps['id']}: {lname} not 4-fold symmetric about ({cx},{cy}): {diff.area()*ly.dbu**2:.4f} um2 differs"
    return len(PLATE_SHAPES)


def extract():
    """LayoutToNetlist over everything but the n-well, with NMOS extraction."""
    l2n = db.LayoutToNetlist(db.RecursiveShapeIterator(ly, top, []))
    comp = l2n.make_layer(LI("comp"), "comp")
    nplus = l2n.make_layer(LI("nplus"), "nplus")
    pplus = l2n.make_layer(LI("pplus"), "pplus")
    poly2 = l2n.make_layer(LI("poly2"), "poly2")
    ct = l2n.make_layer(LI("contact"), "contact")
    m1 = l2n.make_layer(LI("metal1"), "metal1")
    v1 = l2n.make_layer(LI("via1"), "via1")
    m2 = l2n.make_layer(LI("metal2"), "metal2")
    v2 = l2n.make_layer(LI("via2"), "via2")
    m3 = l2n.make_layer(LI("metal3"), "metal3")
    m2l = l2n.make_text_layer(LI("metal2_label"), "metal2_label")
    m3l = l2n.make_text_layer(LI("metal3_label"), "metal3_label")
    ncomp = comp & nplus
    pcomp = comp & pplus
    gate = ncomp & poly2
    nsd = ncomp - poly2
    for name, r in (("ncomp", ncomp), ("pcomp", pcomp), ("gate", gate), ("nsd", nsd)):
        l2n.register(r, name)
    ex = db.DeviceExtractorMOS3Transistor("nmos")
    l2n.extract_devices(ex, {"SD": nsd, "G": gate, "P": poly2})
    for a in (nsd, pcomp, poly2, ct, m1, v1, m2, v2, m3):
        l2n.connect(a)
    l2n.connect(nsd, ct)
    l2n.connect(pcomp, ct)
    l2n.connect(poly2, ct)
    l2n.connect(ct, m1)
    l2n.connect(m1, v1)
    l2n.connect(v1, m2)
    l2n.connect(m2, v2)
    l2n.connect(v2, m3)
    l2n.connect(m2, m2l)
    l2n.connect(m3, m3l)
    l2n.extract_netlist()
    return l2n


def check_connectivity(l2n):
    circ = l2n.netlist().circuit_by_name(cfg.CELL)
    named, unnamed = {}, []
    for net in circ.each_net():
        n = net.name or ""
        (named.__setitem__(n, net) if n else unnamed.append(net))
    shorts = [n for n in named if "," in n]
    assert not shorts, f"SHORT: nets carrying two labels: {shorts}"
    expected = {n for n, _ in PINS}
    if cfg.MATRIX:
        if cfg.CROSSBAR:
            expected |= {f"A{k}" for k in range(4)}
        for p in cfg.PLATES:
            if p["id"] not in cfg.DIRECT:
                expected |= set(tnames_for(p, cfg.PIN_NAME[p["kind"]]).values())
    assert set(named) == expected, f"nets vs expected differ: missing {expected - set(named)}, extra {set(named) - expected}"
    assert not unnamed, f"OPEN: {len(unnamed)} unlabelled net(s) (pins/terminals/A-lines reach nothing labelled)"
    return len(named)


def check_devices(l2n):
    circ = l2n.netlist().circuit_by_name(cfg.CELL)
    got = []
    for dev in circ.each_device():
        tdefs = {td.name: td.id() for td in dev.device_class().terminal_definitions()}
        nets = {k: (dev.net_for_terminal(i).name if dev.net_for_terminal(i) else None) for k, i in tdefs.items()}
        got.append((nets["G"], frozenset({nets["S"], nets["D"]})))
    want = list(EXPECT_DEV)
    missing = [w for w in want if w not in got]
    extra = [g for g in got if g not in want]
    for w in want:
        if w in got:
            got.remove(w)
    assert not missing and not extra, f"DEVICES: missing {missing}; unexpected {extra}"
    return len(want)


def check_no_metal_over_plates():
    nw = db.Region(top.begin_shapes_rec(LI("nwell")))
    allowed = db.Region()
    for _, _, b in TERMINALS:
        allowed.insert(db.DBox(b.left - 1.0, b.bottom - 1.0, b.right + 1.0, b.top + 1.0).to_itype(ly.dbu))
    for b in COVER_TIES:
        allowed.insert(b.to_itype(ly.dbu))
    allowed += db.Region(top.begin_shapes_rec(LI("comp"))) & db.Region(top.begin_shapes_rec(LI("pplus"))) & nw
    bad = 0
    for lname in ("metal1", "metal2"):
        m = db.Region(top.begin_shapes_rec(LI(lname)))
        inside = (m & nw) - allowed
        if not inside.is_empty():
            bad += inside.count()
            print(f"  !! {lname} over a plate body: {inside.count()} polygon(s), {inside.area()*ly.dbu**2:.3f} um2")
    assert bad == 0, "metal over a plate body"


# ---------------------------------------------------------------- EMIT
def write_lef(W):
    pins = sorted(PINS, key=lambda t: t[1])
    L = ["VERSION 5.8 ;", 'BUSBITCHARS "[]" ;', 'DIVIDERCHAR "/" ;', "",
         f"MACRO {cfg.CELL}", "  CLASS BLOCK ;", "  ORIGIN 0 0 ;", f"  FOREIGN {cfg.CELL} 0 0 ;",
         f"  SIZE {W:.3f} BY {cfg.H:.3f} ;", "  SYMMETRY X Y ;"]
    for name, x in pins:
        direction = "INPUT" if is_control(name) else "INOUT"
        L += [f"  PIN {name}", f"    DIRECTION {direction} ;", "    USE SIGNAL ;", "    PORT", "      LAYER Metal2 ;",
              f"        RECT {x - cfg.PIN_W/2:.3f} {PIN_Y:.3f} {x + cfg.PIN_W/2:.3f} {cfg.H:.3f} ;",
              "    END", f"  END {name}"]
    L += ["  OBS", "    LAYER Metal1 ;", f"      RECT 0 0 {W:.3f} {cfg.H:.3f} ;",
          "    LAYER Metal2 ;", f"      RECT 0 0 {W:.3f} {PIN_Y:.3f} ;",
          "    LAYER Metal3 ;", f"      RECT 0 0 {W:.3f} {cfg.H:.3f} ;",
          "  END", f"END {cfg.CELL}", "", "END LIBRARY", ""]
    with open(os.path.join(HERE, f"{cfg.CELL}.lef"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return pins


def is_control(name):
    return name.startswith("SEL_") or name in cfg.ROW_NAMES


def write_verilog(pins):
    L = ["// hall_test - Hall-plate test structure, GF180MCU.  Blackbox: the switch",
         "// matrix is bare NMOS pass gates; the digital inputs are their gates, at",
         "// the host's logic level, and every other pin is analog.",
         "// Generated by gen_hall_layout.py from hall_cfg.py - do not edit.",
         "(* blackbox *)", f"module {cfg.CELL} ("]
    L += [f"    {'input' if is_control(n) else 'inout'} {n}{',' if i < len(pins)-1 else ''}" for i, (n, _) in enumerate(pins)]
    L += [");", "endmodule", ""]
    with open(os.path.join(HERE, f"{cfg.CELL}.v"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def describe(name):
    if name == cfg.GUARD_NAME:
        n_rings = sum(2 if p["kind"] == "ocpair" else 1 for p in cfg.PLATES)
        ring = "the p+ guard ring (substrate tap)" if n_rings == 1 else f"all {n_rings} p+ guard rings and the p+ strips (substrate taps)"
        return f"{ring}; tie to the die's VSS", "guard", "analog"
    if name.startswith("SEL_"):
        return f"plate select for {name[4:].lower()} (one-hot, active high); 0 = that plate disconnected", name[4:].lower(), "control"
    if name in cfg.ROW_NAMES[:4]:
        d = int(name[2])
        return f"spinning phase {d}: bias T{d+1}->T{(d+2)%4+1}, Hall T{(d+1)%4+1}-T{(d+3)%4+1} (one-hot, active high)", "crossbar", "control"
    if name == "KV":
        return "Kelvin: with all PH low, puts A0 on BIAS_P+H_P and A2 on BIAS_N+H_N - the sense buses read the bias terminals", "crossbar", "control"
    if name == "VBI":
        return "internal bias: VBIAS_INT -> BIAS_P and GUARD -> BIAS_N (no bias pad needed)", "crossbar", "control"
    if name in cfg.BUS_NAMES:
        role = {"BIAS_P": "bias + bus (force)", "H_P": "Hall + bus (sense)", "BIAS_N": "bias - bus (return)", "H_N": "Hall - bus (sense)"}[name]
        return role + "; to an analog pad", "bus", "analog"
    if name == cfg.VBIAS_INT:
        return "optional on-die bias source for VBI mode; tie to the host's analog/IO rail or leave open", "bus", "analog"
    if name in cfg.OUT_NAMES:
        role = {"T1": "north terminal of the selected plate (bias +)", "T2": "east terminal of the selected plate (Hall +)",
                "T3": "south terminal of the selected plate (bias -)", "T4": "west terminal of the selected plate (Hall -)"}[name]
        return role + "; to an analog pad", "selected plate", "analog"
    base, _, t = name.rpartition("_")
    plate = {p["id"].upper(): p for p in cfg.PLATES}.get(base)
    if t == cfg.SHIELD_SUFFIX:
        return "x12p's p+ cover; tie to GUARD/VSS (or bias it, see bench.md)", "shield", "analog"
    role = {"T1": "north terminal (bias +, phase 0)", "T2": "east terminal (Hall +, phase 0)",
            "T3": "south terminal (bias -, phase 0)", "T4": "west terminal (Hall -, phase 0)",
            "B1": "bias + (P.T1 + Q.T2)", "B2": "bias - (P.T3 + Q.T4)",
            "H1": "Hall + (P.T2 + Q.T3)", "H2": "Hall - (P.T4 + Q.T1)"}[t]
    if plate["kind"] == "square":
        role = role.replace("north", "NW corner").replace("east", "NE corner").replace("south", "SE corner").replace("west", "SW corner")
    if cfg.MATRIX:
        role += " - DIRECT, switch-free copy of the terminal"
    return role, plate["id"], "analog"


def write_pins(pins, W):
    rows = []
    for i, (n, x) in enumerate(pins):
        role, plate, kind = describe(n)
        rows.append(dict(index=i, name=n, plate=plate, kind=kind, role=role, layer="Metal2",
                         rect=[round(x - cfg.PIN_W / 2, 3), round(PIN_Y, 3), round(x + cfg.PIN_W / 2, 3), round(cfg.H, 3)]))
    doc = dict(cell=cfg.CELL, size_um=[round(W, 3), round(cfg.H, 3)], matrix=cfg.MATRIX, pins=rows,
               plates=[{k: v for k, v in p.items()} for p in cfg.PLATES], switches=len(EXPECT_DEV))
    with open(os.path.join(HERE, f"{cfg.CELL}_pins.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    md = [f"# {cfg.CELL} pins - {W:.1f} x {cfg.H:.1f} um, {len(pins)} pins on the north edge, west to east",
          "", "Generated by `gen_hall_layout.py` from `hall_cfg.py`; the LEF and the Verilog carry the same order.",
          "`control` pins are NMOS gates driven at the host's logic level; everything else is analog.", "",
          "| # | pin | kind | plate | role | Metal2 rect (um) |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['index']} | `{r['name']}` | {r['kind']} | {r['plate']} | {r['role']} | {r['rect'][0]}..{r['rect'][2]} x {r['rect'][1]}..{r['rect'][3]} |")
    with open(os.path.join(HERE, f"{cfg.CELL}_pins.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def main():
    W = place()
    n_plates = check_symmetry()
    l2n = extract()
    n_nets = check_connectivity(l2n)
    n_dev = check_devices(l2n)
    check_no_metal_over_plates()
    pins = write_lef(W)
    write_verilog(pins)
    write_pins(pins, W)
    ly.write(os.path.join(HERE, f"{cfg.CELL}.gds"))
    nwell_um2 = db.Region(top.begin_shapes_rec(LI("nwell"))).area() * ly.dbu ** 2
    n_ctrl = sum(1 for n, _ in pins if is_control(n))
    print(f"{cfg.CELL}: {W:.1f} x {cfg.H:.1f} um ({W*cfg.H/1e6:.4f} mm2), {len(pins)} pins ({n_ctrl} control), "
          f"{n_plates} plate drawings 4-fold symmetric, {n_nets} labelled nets, {n_dev} NMOS switches as intended, "
          f"n-well {nwell_um2:.0f} um2")
    for n, x in pins:
        print(f"  {n:10s} x={x:7.2f}")


if __name__ == "__main__":
    main()

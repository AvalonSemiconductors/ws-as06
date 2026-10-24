#!/usr/bin/env python3
"""hall_cfg.py - the ONE description of the Hall test structure that the
drawing (gen_hall_layout.py), the LEF, the Verilog blackbox, the pin table and
the bench protocol all read.  Change a number here, re-run the generator,
re-run DRC.  Nothing downstream keeps a copy.

WHAT THIS CELL IS

`hall_test` is a set of lateral Hall plates drawn in GF180MCU n-well, with
their terminals brought to Metal2 pins on the cell's north edge, meant to be
dropped onto a donor die and bonded to pads.  It is a TRANSDUCER TEST
STRUCTURE, not a sensor: there is no bias source, no spinning-current switch
matrix, no amplifier and no ADC on it.  All of that is done on the bench, with
instruments, which is the point - the PDK has no Hall device and no Hall
model, so the first silicon exists to measure the four numbers every later
design decision rests on:

    S_V    voltage-related sensitivity           V / (V*T)     (expected 0.03-0.06)
    R_in   plate resistance and its tempco       ohm, %/degC   (n-well: 1000 ohm/sq +0.23 %/degC)
    V_off  raw offset, and the residual after 4-phase spinning  (mT-equivalent -> uT)
    e_n    noise: thermal floor and 1/f corner   nV/rtHz

The only PDK-stated number this file leans on: the n-well sheet resistance
under STI, from the resistor model `nwell` in
libs.tech/ngspice/sm141064.ngspice -

    .param rsh_nwell=1000        (typical; 800 fast / 1200 slow corners)
    r_tc1=2.285e-3  r_tc2=9.78e-6 /degC about 25 degC

Everything about the Hall effect itself (mobility in the well, the geometry
factor, piezo-Hall) is NOT in the PDK and is what the structure measures.

THE PLATE SET, AND WHY EACH ONE IS THERE

**WHAT IS BUILT (2026-10-22, Andrew's final call): ALL FIVE PLATES behind a
PLAIN PLATE-SELECT MUX.  Five select wires from the donor's own CPU, four
analog pads that carry the selected plate's T1 T2 T3 T4, GUARD to VSS.
Twenty NMOS switches, nothing else inside.**  Spinning, Kelvin sensing and
the bias source are the bench's job, where they are ordinary.

    CROSSBAR = False below.  Setting it True adds the phase crossbar
    described next (42 switches, 11 control lines, 2-4 pads); MATRIX = False
    drops the switches altogether (every terminal on its own pin).  All
    three were DRC-clean.

THE SWITCH MATRIX (the full version; only stage 1 is built when CROSSBAR is False)

    plate terminals ---[stage 1: plate select]---> A0..A3 ---[stage 2: phase
    crossbar]---> BIAS_P  H_P  BIAS_N  H_N  (four analog buses, to pads)

  stage 1  per plate, four 6 V NMOS pass switches gated by SEL[p]: terminal
           T_k <-> line A_k.  One-hot; all-zero disconnects every plate.
  stage 2  a 4 x 4 crossbar of NMOS between A_k and bus B_b, the switch at
           (b, d) gated by PH[d] and joining A_((b+d) mod 4) to B_b.  So
           PH[0] gives bias T1->T3 / Hall T2-T4, PH[1] rotates it a quarter
           turn, and so on - the four spinning phases, by one-hot control.
  KV       a fifth crossbar row: with every PH off and KV on, A0 reaches BOTH
           BIAS_P and H_P and A2 reaches BOTH BIAS_N and H_N - the sense
           buses then read the bias terminals themselves, i.e. the voltage
           ACROSS the plate with no switch resistance in it (Kelvin).  That
           is what makes S_V measurable through switches.
  VBI      a sixth row: VBIAS_INT -> BIAS_P and GUARD -> BIAS_N, so the plate
           can be biased from the donor's own rail with no bias pad at all.

  Switches: nfet_06v0 - thick-oxide, Dualgate, no V5_XTOR - because the gate
  is driven by HER logic and we do not know whether that is 3.3 V or 5 V.
  W/L = 16/0.7: ~250 ohm on at 3.3 V drive and 1 V source, two in series in
  the bias path against a ~2.5 kohm plate (which KV takes out of the
  measurement), pA-class leakage off.  x12's four terminals ALSO go straight
  to their own pins (DIRECT), so one plate can be bonded switch-free as the
  reference if pads allow.

  Her side: 11 digital lines (SEL[4:0], PH[3:0], KV, VBI) from any register
  or GPIO, at her logic level; 0 V on all of them is "everything off".
  Pads: H_P + H_N (2) at minimum with VBI biasing; + BIAS_P (3) for the
  proper characterisation; + BIAS_N (4) to float the bias return; + x12's
  four direct terminals (8) for a switch-free reference.

    x12    Greek cross, arm width 12 um, arm length 12 um (36 um overall).  STI
           over the plate body.  The reference plate: the shape every CMOS
           spinning-current Hall sensor uses, at a size whose resistance
           (~2-3 kohm) a bench DMM and a lock-in both like.
    x12p   The same cross with a p+ COVER over the body (COMP+Pplus inside the
           n-well, tied to its own pin).  Pushes the current away from the
           Si/oxide interface - the standard remedy for 1/f noise and offset
           drift, at the cost of a thinner, junction-modulated plate.  Its own
           pin so the bench can bias the shield as well as ground it.
    x30    The cross at 2.5x the size.  Offset and matching scale with area;
           resistance should not change (same W/L).  Same shape, so the ONLY
           variable is size.
    sq30   A 30 um square with 3 um corner terminals.  The other canonical
           shape (bias across one diagonal, Hall voltage across the other):
           higher geometry factor, higher resistance.  Shape is the variable.
    oc12   Two x12 plates wired ORTHOGONALLY COUPLED in metal: the second is
           biased 90 degrees from the first and their Hall outputs are
           paralleled, so first-order offsets (stress, lithographic gradient)
           cancel in the wiring and the Hall voltages add.  Four pins for a
           plate whose static offset is already reduced - the one structure
           here a bench amplifier can read as a sensor with no switching.

TERMINAL CONVENTION (every plate, every variant)

    T1 north, T2 east, T3 south, T4 west, clockwise - on the square the
    corners NW, NE, SE, SW.  Bias across T1-T3, Hall voltage across T2-T4.
    A spinning-current phase rotates that assignment by 90 degrees:
        phase 0: I  T1->T3   V_H = V(T2)-V(T4)
        phase 1: I  T2->T4   V_H = V(T3)-V(T1)
        phase 2: I  T3->T1   V_H = V(T4)-V(T2)
        phase 3: I  T4->T2   V_H = V(T1)-V(T3)
    The Hall term keeps its sign through the four; the offset does not.
    Each plate's drawing is asserted 4-fold rotationally symmetric by the
    generator, because that symmetry is what the cancellation assumes.

    oc12: B1 = P.T1 + Q.T2, B2 = P.T3 + Q.T4, H1 = P.T2 + Q.T3, H2 = P.T4 + Q.T1
    (Q is the copy biased a quarter turn on).

NO METAL OVER ANY PLATE BODY, except the p+ cover's own tie.  Metal over the
plate is a field plate; a toggling digital net over it is a noise source.
The LEF obstructs Metal1-3 over the whole cell for the same reason, and the
README says what a PDN strap on Metal4/5 above it costs.
"""

DBU = 0.001          # um; the foundry deck's rule `DBU` insists on 0.001 (geom.rb)
GRID = 0.005         # um; the manufacturing grid every coordinate is snapped to

# ---------------------------------------------------------------- GDS LAYERS
# gf180mcuD, read off libs.tech/klayout/tech/drc/generic_layers.rb
LAYERS = {
    "nwell":        (21, 0),
    "comp":         (22, 0),
    "nplus":        (32, 0),
    "pplus":        (31, 0),
    "contact":      (33, 0),
    "metal1":       (34, 0),
    "metal1_label": (34, 10),
    "via1":         (35, 0),
    "metal2":       (36, 0),
    "metal2_label": (36, 10),
    "poly2":        (30, 0),
    "dualgate":     (55, 0),
    "via2":         (38, 0),
    "metal3":       (42, 0),
    "metal3_label": (42, 10),
    "pr_bndry":     (0, 0),
}

# ---------------------------------------------------------------- RULES USED
# (deck minimum, what this cell draws, where it bites).  From the foundry
# deck's own rule text, rule_decks/*.rb of the same PDK revision.
RULES = {
    "NW.1a":  (0.86, 12.0,  "n-well width (narrowest arm here is 12 um)"),
    "NW.2b":  (1.40, 16.0,  "n-well space, different potential: plates are 16 um apart"),
    "DF.1a":  (0.22, 1.50,  "COMP width: terminal band is 1.5 um deep"),
    "DF.3a":  (0.28, 1.00,  "COMP space: p+ cover to terminal band"),
    "DF.2b":  (100., 10.4,  "max COMP width: widest terminal band (28.6 with x30 active)"),
    "DF.4c":  (0.43, 0.60,  "n-well overlap of PCOMP (the p+ cover)"),
    "DF.4d":  (0.12, 0.80,  "n-well overlap of NCOMP (every terminal)"),
    "DF.12":  (None, None,  "every COMP implanted: terminals Nplus, cover and rings Pplus"),
    "DF.13":  (20.0, 15.7,  "PCOMP in n-well to nearest n-well tap: cover centre to terminal band"),
    "DF.17":  (0.12, 1.50,  "n-well to PCOMP outside it: the guard ring"),
    "NP.1":   (0.40, 1.50,  "Nplus width"),
    "NP.5d":  (0.16, 0.30,  "Nplus extension beyond COMP"),
    "NP.3c":  (0.16, 0.70,  "Nplus to PCOMP (terminal implant to p+ cover)"),
    "PP.3c":  (0.16, 0.70,  "Pplus to NCOMP (cover implant to terminal band)"),
    "CO.1":   (0.22, 0.22,  "contact size"),
    "CO.2b":  (0.28, 0.28,  "contact space in arrays (pitch 0.50)"),
    "CO.4":   (0.07, 0.15,  "COMP overlap of contact"),
    "CO.6":   (0.06, 0.10,  "Metal1 overlap of contact (end-of-line value)"),
    "M1.1":   (0.23, 1.00,  "Metal1 width: narrowest route"),
    "M1.2a":  (0.23, 1.50,  "Metal1 space: OC bars are on a 2.5 pitch at 1.0 wide"),
    "V1.1":   (0.26, 0.26,  "via1 size"),
    "V1.2":   (0.26, 0.34,  "via1 space (pitch 0.60)"),
    "V1.3/4": (0.06, 0.10,  "Metal1 / Metal2 overlap of via1"),
    "M2.1":   (0.28, 1.00,  "Metal2 width: risers"),
    "M2.2a":  (0.28, 2.00,  "Metal2 space: adjacent risers 3.0 apart at 1.0 wide"),
    "MSLOT":  (30.0, 28.6,  "no metal is >30 um in both dimensions"),
    # the switch transistors (nfet_06v0: MV rules apply inside Dualgate)
    "DF.1a_MV": (0.30, 2.30, "COMP width of a switch"),
    "DF.3a_MV": (0.36, 1.70, "COMP space between switches in a row"),
    "DF.6_MV":  (0.40, 0.80, "S/D overhang beyond the gate"),
    "DF.16_MV": (0.60, 4.00, "n-well to a switch's NCOMP (the plates are >=4 um below the rows)"),
    "PL.2_MV":  (None, 0.70, "gate length: the model's own default l=7e-7"),
    "PL.4_MV":  (0.22, 0.50, "poly end-cap beyond COMP"),
    "PL.5b_MV": (0.30, 0.50, "field poly (the gate pad) to related COMP"),
    "PL.5a_MV": (0.30, 1.50, "field poly to the p+ strips"),
    "PL.3a":    (0.24, 1.50, "poly space: adjacent switches"),
    "NP.5a":    (0.23, 0.40, "Nplus overlap of the gate"),
    "CO.3":     (0.07, 0.29, "poly overlap of the gate contact"),
    "CO.7":     (0.15, 0.34, "COMP contact to gate"),
    "CO.8":     (0.17, 0.79, "poly contact to COMP"),
    "DV.6":     (0.24, 0.50, "Dualgate enclosure of COMP"),
    "DV.8":     (0.40, 0.60, "Dualgate enclosure of poly"),
    "DV.3":     (0.24, 0.90, "Dualgate to an unrelated COMP (the p+ strips, rings)"),
    "M3.1/2a":  (0.28, 1.00, "Metal3 A-lines, 1.0 wide on a 2.0 pitch"),
    "V2":       (0.26, 0.26, "via2 (0.12 Metal2/Metal3 enclosure)"),
}

# ---------------------------------------------------------------- DRAW NUMBERS
NW_ENC_NCOMP = 0.80   # terminal band inset from the n-well edge     (DF.4d 0.12)
NW_ENC_PCOMP = 0.60   # p+ cover inset from the n-well edge          (DF.4c 0.43)
IMP_EXT      = 0.30   # Nplus / Pplus beyond their COMP               (NP/PP.5 <=0.16)
COVER_GAP    = 1.00   # p+ cover COMP to terminal COMP               (DF.3a 0.28; implants stay 0.4 apart)
TERM_D       = 1.50   # terminal band depth along the arm            (2 contact rows)
CT           = 0.22   # contact                                       (CO.1)
CT_PITCH     = 0.50   # contact pitch -> 0.28 space                   (CO.2b)
CT_ENC_COMP  = 0.15   # COMP overlap of contact                       (CO.4 0.07)
CT_ENC_M1    = 0.10   # Metal1 overlap of contact                     (CO.6)
VIA          = 0.26   # via1                                          (V1.1)
VIA_PITCH    = 0.60   # -> 0.34 space                                 (V1.2)
VIA_ENC      = 0.10   # metal overlap of via1                         (V1.3/V1.4)
M2_W         = 1.00   # riser / stub width
M1_W         = 1.00   # OC merge bars, ring stubs
PIN_W        = 2.00   # Metal2 pin width at the north edge
PIN_D        = 4.00   # Metal2 pin depth into the cell
RING_GAP     = 1.50   # n-well edge to guard-ring COMP               (DF.17 0.12)
RING_W       = 1.00   # guard-ring COMP width (one contact column)
LANE1        = 4.00   # first riser lane beyond the n-well half-extent
LANE2        = 8.00   # second riser lane (4.0 from the first: one switch per lane)
GAP          = 20.0   # between adjacent n-well extents              (NW.2b 1.4)
X0           = 18.0   # first n-well's west edge
Y_NW0        = 12.5   # every n-well's south edge
BUS_Y        = (3.0, 5.0)   # GUARD bus (Metal1) y-extent
GUARD_X      = 4.0    # GUARD riser / pin x
CHANNEL      = 7.0    # clear Metal2 run between the tallest ring and the pin row
OC_BAR_PITCH = 2.5    # oc12's four Metal1 merge bars
VIA_ROWS     = 2      # via1 array on a terminal: VIA_COLS x VIA_ROWS, compact so
VIA_COLS     = 3      #   the Metal2 pad never reaches a neighbouring riser

# ---------------------------------------------------------------- THE PLATES
# left -> right on the die; `half` is the n-well half-extent the lanes key off
PLATES_FULL = [
    dict(id="x12",  kind="cross",  w=12.0, a=12.0, cover=False),   # 4 pins
    dict(id="x12p", kind="cross",  w=12.0, a=12.0, cover=True),    # 5 pins (+SH)
    dict(id="x30",  kind="cross",  w=30.0, a=30.0, cover=False),   # 4 pins
    dict(id="sq30", kind="square", s=30.0, c=3.0),                 # 4 pins
    dict(id="oc12", kind="ocpair", w=12.0, a=12.0),                # 4 pins
]
ACTIVE = ("x12", "x12p", "x30", "sq30", "oc12")
PLATES = [p for p in PLATES_FULL if p["id"] in ACTIVE]
assert len(PLATES) == len(ACTIVE), f"unknown id in ACTIVE: {set(ACTIVE) - {p['id'] for p in PLATES_FULL}}"

# ---------------------------------------------------------------- THE MATRIX
MATRIX = True            # False: every terminal straight to a pin (the 5/22-pin cells)
CROSSBAR = False         # True: add the phase crossbar + KV + VBI rows (see docstring)
DIRECT = ()              # plates whose terminals ALSO reach their own pins, switch-free
OUT_NAMES = ("T1", "T2", "T3", "T4")                 # the A-lines' pins when CROSSBAR is False
BUS_NAMES = ("BIAS_P", "H_P", "BIAS_N", "H_N")      # B0..B3; phase 0 = T1 T2 T3 T4
ROW_NAMES = ("PH0", "PH1", "PH2", "PH3", "KV", "VBI")   # crossbar rows, bottom-up
VBIAS_INT = "VBIAS_INT"

# 6 V NMOS pass switch (nfet_06v0), drawn as: COMP [SD | gate L | SD] x W,
# one contact column per S/D region, a poly end-cap and a gate pad with its
# contact beyond one end, Nplus and Dualgate around.  Two orientations:
# stage 1 has the gate VERTICAL (device 2.3 wide x W tall, S/D left/right),
# the crossbar has it HORIZONTAL (W wide x 2.3 tall, S/D bottom/top).
MOS_L        = 0.70   # gate length                                  (PL.2_MV)
MOS_W        = 16.0   # channel width
MOS_SD       = 0.80   # S/D region, gate edge to COMP edge           (DF.6_MV 0.4)
MOS_CT_OFF   = 0.45   # S/D contact centre from the gate edge        (CO.7 0.15)
MOS_EC       = 0.50   # poly end-cap beyond COMP                     (PL.4_MV 0.22)
MOS_GP       = 0.80   # gate pad (poly) beyond the end-cap           (PL.5b_MV 0.3)
BAR_W        = 0.50   # Metal1 over a contact column
NP_EXT       = 0.40   # Nplus beyond COMP                            (NP.5a 0.23)
DG_ENC_COMP  = 0.50   # Dualgate beyond COMP                         (DV.6 0.24)
DG_ENC_POLY  = 0.60   # Dualgate beyond poly                         (DV.8 0.4)
STUB_W       = 0.50   # narrow Metal2 (A-stubs, crossbar stubs)
ROW_GAP      = 4.00   # tallest ring top -> stage-1 COMP bottom
STRIP_GAP    = 2.00   # stage-1 COMP top -> the p+ strip's COMP
A_GAP        = 5.00   # stage-1 COMP top -> A0
A_PITCH      = 2.00   # A-line pitch (Metal3, 1.0 wide)
XB_GAP       = 6.00   # last riser -> crossbar
XB_COL_PITCH = 22.0   # crossbar column pitch (device is 16 + pad)
XB_ROW_PITCH = 4.00   # crossbar row pitch (device is 2.3 tall)
XB_BUS_OFF   = 8.00   # bus column x inside a crossbar column
XB_STUB_OFF  = 10.0   # first A-stub x inside a crossbar column (+1 per row; row 5
                      #   lands at +15, inside the 16-wide bar - V1.3a at 11)
XB_DROP      = 32.0   # crossbar row 0 sits this far below the stage-1 row
DIRECT_OFF   = 2.70   # a direct riser runs this far east of its terminal riser
SEL_OFF      = 2.50   # a plate's SEL riser this far west of its T3 riser

# pin names, in the order they appear west -> east along the north edge, are
# derived by the generator from PLATES; this is the per-structure naming
PIN_NAME = {
    "cross":  lambda pid, t: f"{pid.upper()}_{t}",            # X12_T1 ...
    "square": lambda pid, t: f"{pid.upper()}_{t}",            # SQ30_T1 ...
    "ocpair": lambda pid, t: f"{pid.upper()}_{t}",            # OC12_B1 ...
}
SHIELD_SUFFIX = "SH"
GUARD_NAME = "GUARD"

CELL = "hall_test"


def cross_half(w, a):
    return w / 2 + a


def plate_half(p):
    if p["kind"] in ("cross", "ocpair"):
        return cross_half(p["w"], p["a"])
    return p["s"] / 2


# vertical stack, DERIVED from the tallest active plate.  Without the matrix:
# ring top + channel + pins (full set 116, x12 alone 62).  With it: the
# stage-1 switch row, the p+ strip, the four A-lines, then the pins.
RING_TOP = Y_NW0 + 2 * max(plate_half(p) for p in PLATES) + RING_GAP + RING_W
if MATRIX:
    Y_ROW = RING_TOP + ROW_GAP                 # stage-1 COMP bottom
    Y_STRIP = Y_ROW + MOS_W + STRIP_GAP        # p+ strip COMP bottom (1.0 tall)
    Y_A0 = Y_ROW + MOS_W + A_GAP               # A0 centre; A_k = Y_A0 + k*A_PITCH
    H = Y_A0 + 3 * A_PITCH + 2.0 + PIN_D
    Y_XB0 = Y_ROW - XB_DROP                    # crossbar row 0 COMP bottom
else:
    H = RING_TOP + CHANNEL + PIN_D
# oc12's merge bars start just above ITS ring top (independent of H)
OC_BAR_Y0 = Y_NW0 + 2 * cross_half(12.0, 12.0) + RING_GAP + RING_W + 5.0

# bench.md — measuring `hall_test`

The cell gives the bench one plate at a time on four pads. This is how to
drive it, what to measure, and roughly what to expect. Expected values are
**estimates** — the only PDK-stated number is the n-well sheet resistance
(`nwell` model, `sm141064.ngspice`: 1000 Ω/sq typ, 800–1200 over corners,
+0.23 %/°C).

## 1. Hook-up

| pin | bench |
|---|---|
| `T1` `T2` `T3` `T4` | the selected plate: T1 north, T2 east, T3 south, T4 west (NW NE SE SW on the square; B1 H1 B2 H2 on the coupled pair) |
| `SEL_*` | one high at a time, set through the host CPU; all low = nothing connected |
| `GUARD` | the chip's VSS — reference everything to it |
| `X12P_SH` | VSS, or a pad if you want to bias the cover |

Limits: every T pad between VSS and VSS + 3.3 V (abs. max 5 V). The switches
are NMOS pass gates: with a 3.3 V CPU rail keep the plate bias ≤ 1.5 V, with
5 V ≤ 3.3 V. Each switch is ~250 Ω and sits in series with its terminal.

## 2. Spinning current — by lead swap

Bias across one diagonal, read across the other, then rotate:

| phase | bias current | read |
|---|---|---|
| 0 | T1 → T3 | V(T2) − V(T4) |
| 1 | T2 → T4 | V(T3) − V(T1) |
| 2 | T3 → T1 | V(T4) − V(T2) |
| 3 | T4 → T2 | V(T1) − V(T3) |

The Hall voltage keeps its sign through the four; the offset does not. Four
relays or a DAQ switch matrix do this; by hand, a 4PDT switch does.

## 3. Instruments

- Source-meter (Keithley 2400-class) for the bias; read its current.
- 6½-digit DMM for mV-level Hall voltages; a nanovoltmeter or low-noise
  preamp (SR560-class, gain 100–1000, battery) for residuals and noise.
- A reference gaussmeter at the die plane — the magnet is not the standard.
- Field: a magnet on a micrometer stage or, better, a Helmholtz pair on a
  current source (linear, reversible, zero by switching off).
- The Earth's field is ~50 µT, vertical ~45 µT across most of the US — the
  size of the residual you are after. Shield, or take every zero-field
  reading twice with the die flipped 180° and average.

## 4. Procedure

### 4.1 Sanity
1. All `SEL` low: each T pad to VSS is a reverse junction, < 1 nA at +3 V.
2. One `SEL` high: a few kΩ between any two T pads (plate + two switches).
   Repeat per plate; `oc12` reads about half.

### 4.2 Resistance and tempco
Two kinds, and the difference matters:

- **2-wire:** R(T1–T3) with the SMU = plate + two switches (~2.5 kΩ + ~0.5 kΩ).
- **Transfer resistance (switch-free):** force I from T1 to T2, read
  V(T3) − V(T4). No current flows in the sense switches, so this is the plate
  alone. For a 4-fold symmetric plate the sheet resistance follows directly:
  **R_sheet = (π / ln 2) · V(T3−T4) / I** (van der Pauw). Expect ~1000 Ω/sq.

Report both per plate at 25 °C, and R_sheet at −20 / 85 °C (expect +0.23 %/°C).
Plate input resistance for the S_V calculation: R_plate ≈ R_2wire − 2·R_sw,
with R_sw ≈ 250 Ω at 3.3 V control (less at 5 V); or N_sq · R_sheet with
N_sq ≈ 2.5 for the crosses.

| plate | expect | why |
|---|---|---|
| x12, x30 | **~2.5 kΩ** plate (2.0–3.6 over corners) | ≈ 2.5 squares; same W/L at both sizes |
| x12p | a little above x12, more bias-dependent | the cover's depletion thins the plate |
| sq30 | **~3–5 kΩ** | corner contacts: more squares + a spreading term |
| oc12 | half of x12 | two in parallel |

### 4.3 Offset (B = 0)
400 µA, phase 0: read T2 − T4. Then phases 1–3. Report raw offset per phase
(µV, and µT-equivalent = V_off / (S_I · I)) and the **spinning residual**,
the signed average of the four. Expect raw **0.1–1 mV (3–30 mT-equivalent)**
and a residual one to two orders smaller — tens of µT; at 50 mT of signal,
50 µT is 0.06° of angle. Switch leakage adds a term that does not rotate
with phase; it shows up as a residual that scales with temperature.

`oc12` at B = 0 (H1 − H2 with 400 µA B1 → B2) against x12's raw offset is the
coupling's cancellation ratio, with no switching at all.

### 4.4 Sensitivity
B_z = 0, ±10, ±20, ±40, ±60 mT at 400 µA; four phases at each; V_H =
spinning average.

- **S_I = dV_H / (I · dB)** — exact: I is the SMU's, V_H is on the sense
  terminals, no switch resistance in either. Expect **60–130 V/(A·T)**.
- **S_V = S_I / R_plate** — expect **0.02–0.05 V/(V·T)** (µ_H·G/N_sq with
  µ_H ≈ 0.08–0.1 m²/Vs for a ~10¹⁷ cm⁻³ well). The mobility is the unknown.
- Non-linearity in B < 0.5 % over ±60 mT; S_I flat with I up to ~0.5 mA.
- x30 ≈ x12 (same W/L); sq30 similar S_V, higher R; x12p 10–30 % lower S_V.
- **Sign:** with current T1 → T3 and B_z out of the die toward the magnet,
  record which of T2/T4 goes positive. A mirrored instance flips it.

### 4.5 Noise
Phase 0, 400 µA, B = 0, preamp across T2 − T4 (AC, gain 1000), 1 Hz – 100 kHz.
White floor √(4kT·R) ≈ **6.4 nV/√Hz for 2.5 kΩ** (+ ~10 % from the two
sense switches); 1/f corner expected **100 Hz – 10 kHz** — x12p tells whether
the cover lowers it. In field: B_n = e_n / (S_I · I); 6.4 nV/√Hz at
100 V/(A·T) and 0.4 mA is **160 nT/√Hz → 16 µT rms in 10 kHz**.

### 4.6 Temperature
S_I(T), R_sheet(T), offset(T) at −20, 25, 85 °C, every plate. S_I should
fall ~0.1–0.3 %/°C; for an angle sensor only differences between plates
matter. Repeat §4.1 step 1 at 85 °C (switch leakage ~2×/10 °C).

### 4.7 Shield bias (x12p, if `X12P_SH` has a pad)
`SEL_X12P`, 400 µA, sweep `X12P_SH` 0 → −1 V: R_sheet and S_I rise together as
the cover depletion thins the plate; S_V stays roughly flat; noise at each step.

## 5. Report

One table per plate, one row per temperature:

```
plate  T(°C)  R_2wire  R_sheet  S_I  S_V  V_off(4 phases)  residual(µT)  e_n floor  1/f corner  notes
```

plus the sign convention (§4.4) and `oc12`'s cancellation ratio. The numbers
go back to the bldc_driver repo's Hall topic (graph node `n34`), where the
angle-sensor design is waiting for them.

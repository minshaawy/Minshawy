# Bambu Lab A1 design guide (0.4 mm nozzle, PLA unless noted)

## Machine facts
- Build volume 256 × 256 × 256 mm, bed-slinger (Y moves the bed): tall, thin parts
  wobble — keep height/base ratio ≤ 4:1 or add a brim / widen the base.
- Heated bed to 100 °C, no enclosure → PLA, PETG, TPU are easy; ABS/ASA warp, avoid
  large ABS/ASA parts.
- AMS lite: up to 4 colours/materials. Each colour = separate part in the 3MF.
- Stock nozzle 0.4 mm → line width ~0.42 mm, smallest reliable feature ~0.8 mm.

## Dimensions that print well
| Feature | Value |
|---|---|
| Wall, cosmetic | 1.2 mm (3 lines) |
| Wall, structural | 1.6–2.4 mm |
| Floor / roof | ≥ 1.0 mm (5 layers @ 0.2) |
| Minimum pin / post | Ø 3 mm (Ø 5 mm if it takes load) |
| Embossed text | ≥ 0.6 mm tall, stroke ≥ 0.8 mm, ≥ 5 mm cap height |
| Engraved text | ≥ 0.4 mm deep, stroke ≥ 0.6 mm |
| Bridge | ≤ 20 mm clean, ≤ 40 mm acceptable |
| Overhang | ≤ 45° from vertical without support |
| Layer height | 0.2 default; make vertical dimensions multiples of 0.2 |

## Clearances (per side)
| Fit | Gap |
|---|---|
| Press / interference (pin into hole) | 0.10–0.15 mm |
| Snug, removable (lid, drawer, cap) | 0.20–0.30 mm |
| Loose / sliding | 0.40 mm |
| Print-in-place hinges & moving parts | 0.40–0.50 mm (with ≥ 0.4 mm Z gap) |
| Screw clearance hole | nominal + 0.4 (M3 → 3.4, M4 → 4.5) |
| Screw self-tap into plastic | M3 → 2.6–2.8 hole, M4 → 3.5 |
| Heat-set insert (M3 std) | 4.0–4.2 hole, depth = insert + 1 mm |
| Magnet pocket | magnet Ø + 0.2, depth + 0.2 (press fit, or glue) |

If a fit is critical, make the gap a parameter and suggest a small test print
(a 10 mm ring/peg) first.

## Common hardware
| Item | Size |
|---|---|
| M3 nut | 5.5 mm across flats, 2.4 mm thick |
| M4 nut | 7.0 AF, 3.2 thick |
| M5 nut | 8.0 AF, 4.0 thick |
| M3 cap head | Ø 5.5, 3 mm tall |
| Countersunk wood screw 3.5 mm | head Ø 7 |
| Neodymium magnet common | 6×2, 8×3, 10×3 mm |
| Wall plug screw (Ø 4) keyhole | head slot Ø 8.5, neck 4.5 |

## Orientation & strength
- Layers are weakest in Z (layer adhesion). Orient so loads run *along* layers:
  hooks and brackets lie flat on their side, not standing up.
- Put the best-looking surface facing up or on the plate (textured PEI pattern).
- Round/chamfer the bottom edge 0.4–0.6 mm or rely on Bambu Studio's
  *Elephant foot compensation* (default 0.15 mm) for tight bottom fits.
- Screw holes that run horizontally: make them teardrop shaped (45° point up) or
  accept a slightly oval hole.

## Designing around supports
1. Re-orient (fastest).
2. Replace overhangs with 45° chamfers; replace flat ceilings with arches/teardrops.
3. Split the model into parts that each print flat, join with pins
   (Ø 5 pin, Ø 5.3 hole), dovetails, or screws.
4. Only then: tree supports (auto) in Bambu Studio.

## Threads
- Prefer metal hardware (heat-set inserts, nuts in traps) over printed threads.
- Printed threads: pitch ≥ 1.5 mm, 0.3–0.4 mm radial clearance, built by
  `CrossSection` profile + `extrude(h, n_divisions=..., twist_degrees=...)`.
  For large jar-style threads a simple trapezoid profile twisted along Z works well.

## Hollowing & weight
- Bambu Studio fills solids with infill automatically — do NOT hollow models
  yourself unless you need an internal space (container, vase, enclosure).
- For true vases, export a solid body and enable *Spiral vase* mode in Bambu Studio.

## Materials cheat-sheet
| Material | Use | Notes on A1 |
|---|---|---|
| PLA | Most things, indoor | Easy, rigid, softens at ~55 °C (not in a hot car) |
| PETG | Outdoor, functional, slight flex | Stringy; use glue stick on smooth plates |
| TPU 95A | Grips, bumpers, phone cases | Slow, external spool, no AMS lite |
| PLA-CF / PETG-CF | Stiff parts | Needs hardened nozzle |

## Before exporting — checklist
- [ ] All tunable sizes are parameters at the top of the script
- [ ] Largest flat face on Z=0; parts spaced ≥ 5 mm
- [ ] Walls, clearances and holes follow the tables above
- [ ] `check_printable.py` → PRINTABLE, overhang warnings understood
- [ ] Hand-off states orientation, material, layer height, walls/infill, supports

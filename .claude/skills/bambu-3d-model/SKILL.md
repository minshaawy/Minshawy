---
name: bambu-3d-model
description: Design and generate print-ready 3D models (3MF + STL) for a Bambu Lab A1 printer, to open in Bambu Studio. Use whenever the user wants to create, design, model, or make something to 3D print — a box, holder, stand, bracket, organizer, hook, enclosure, replacement part, vase, gift, toy, cable clip, wall mount, etc. — or asks to tweak dimensions of a printable part, check if a model is printable, or prepare a file for Bambu Studio / the A1.
---

# Bambu Lab A1 — 3D model creator

You design parametric models in Python with `scripts/printlib.py` (CSG on
**manifold3d**, which always produces watertight meshes), export a **3MF** that
Bambu Studio opens directly, and verify it with `scripts/check_printable.py`.

Skill directory (below): `.claude/skills/bambu-3d-model/`.

## Workflow

1. **Understand the object.** Get the few numbers that matter: what it holds/fits
   (measure the real object: phone, screw, pipe diameter…), overall size, material
   (default PLA), and anything it must mate with. If a critical dimension is missing,
   ask once; otherwise pick sensible defaults and state them.
2. **Setup (first time per environment):**
   `pip install manifold3d trimesh numpy`
3. **Write a model script** in the user's project, e.g. `models/<name>/<name>.py`.
   Copy the structure of `examples/storage_box.py`:
   - a `# ---- parameters (mm)` block at the top with every tunable dimension,
   - import helpers: `sys.path.insert(0, "<skill>/scripts"); from printlib import *`,
   - build with primitives + booleans (`a + b` union, `a - b` cut, `a ^ b` intersect),
   - `place_on_plate()` each part, space multiple parts ≥ 5 mm apart,
   - `export({"part_name": part, ...}, "models/<name>/<name>.3mf")`.
4. **Run it**, then **check it**:
   `python .claude/skills/bambu-3d-model/scripts/check_printable.py models/<name>/<name>.3mf`
   Fix every FAIL. For overhang WARNs, prefer re-orienting, chamfering 45°, or
   splitting the part over relying on supports.
5. **Hand off** with: file path(s), size, estimated grams, orientation, and the
   Bambu Studio settings to use (see "Slicer recommendations" below). Mention which
   parameters to edit to adjust the fit.

Read `references/a1-design-guide.md` before designing anything with moving parts,
snap/press fits, threads, screws, text, or tall/thin geometry.

## printlib quick reference (mm, Z-up, plate at Z=0)

| Function | Notes |
|---|---|
| `box(x, y, z)` / `rounded_box(x, y, z, r)` | on Z=0, centred in XY |
| `cylinder(d, h, d2=None)` / `sphere(d)` / `tube(od, id, h)` | `d2` makes a cone |
| `polygon_extrude(points, h)` | 2D outline (CCW points) → prism |
| `revolve(profile)` | profile of `(radius, z)` points → vase/knob/bowl |
| `hole(d, depth, at)` | subtract; adds 0.2 mm clearance |
| `countersunk_hole(screw_d, head_d, depth, at)` | subtract; e.g. M3: 3, 6 |
| `hex_nut_trap(af, h, at)` | subtract; M3 5.5, M4 7.0, M5 8.0 |
| `shell(solid, wall)` | hollow, open top (simple shapes) |
| `union(*parts)` | fast many-part union |
| `place_on_plate(m)` | drop to Z=0 and centre |
| `export(parts, path)` | 3MF (+ STL per part) |
| Manifold methods | `.translate((x,y,z))`, `.rotate((rx,ry,rz))` degrees, `.scale()`, `.mirror()` |
| Constants | `MIN_WALL 0.8`, `GOOD_WALL 1.6`, `CLEARANCE_SLIDE 0.3`, `CLEARANCE_PRESS 0.15`, `CLEARANCE_PRINT_IN_PLACE 0.4`, `A1_BUILD_VOLUME` |

For anything not covered, use manifold3d directly: `Manifold`, `CrossSection`
(2D shapes, `.offset()`, `.extrude(h, twist_degrees=, scale_top=)`), `Manifold.hull()`,
`.warp(fn)`, `.refine(n)`.

## Non-negotiable printability rules (A1, 0.4 mm nozzle)

- Fits **256 × 256 × 256 mm**. Bigger → split into parts with alignment pins/dovetails.
- Largest **flat face on the plate**; design so it prints that way without supports.
- Walls ≥ **1.2 mm** (≥ 1.6 mm for load-bearing); floors/roofs ≥ **1.0 mm**.
- Overhangs ≤ **45°** from vertical; bridges ≤ ~**20 mm**; ceilings of horizontal
  holes → teardrop or 45° chamfer when > 8 mm diameter.
- Holes print ~0.2 mm small → `hole()` already compensates.
- Fillet/round the vertical corners (r ≥ 2 mm) for looks and less warping.
- Every part must be one closed solid: build with booleans, never loose overlapping
  shells. `check_printable.py` must say `PRINTABLE`.

## Slicer recommendations (Bambu Studio)

- Printer: **Bambu Lab A1 0.4 nozzle**; plate: **Textured PEI**.
- Process: **0.20 mm Standard** (0.12 mm Fine for figures/text, 0.28 Draft for big
  simple parts).
- Filament: **Bambu PLA Basic** (or matching generic). PETG for outdoor/heat/flex
  parts; TPU for grips/bumpers (feed from the external
  spool, not the AMS lite).
- Strength parts: 4 walls, 25–40 % gyroid infill. Decorative: 2 walls, 10–15 %.
- Supports: off unless the checker flagged overhangs you chose to keep → "tree(auto)".
- Multi-colour with **AMS lite**: export each colour as a separate named part in the
  same 3MF; in Bambu Studio select both → right-click → *Assemble*, then assign a
  filament per part.

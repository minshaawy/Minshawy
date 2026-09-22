"""
Example: parametric storage box with a slip-on lid (two parts, one 3MF).

    python storage_box.py            -> out/storage_box.3mf (+ box.stl, lid.stl)
Then:  python ../scripts/check_printable.py out/storage_box.3mf
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from printlib import (CLEARANCE_SLIDE, GOOD_WALL, export, place_on_plate,  # noqa: E402
                      rounded_box)

# ---- parameters (mm) -------------------------------------------------------
INNER_X, INNER_Y, INNER_Z = 80, 60, 40   # usable space inside the box
WALL = GOOD_WALL                         # 1.6 mm = 4 perimeters
FLOOR = 1.2                              # 6 layers at 0.2
CORNER_R = 6
LID_TOP = 1.6
LID_SKIRT = 8                            # how far the lid slides down over the box
GAP = CLEARANCE_SLIDE                    # per-side clearance lid <-> box
OUT = os.path.join(os.path.dirname(__file__), "out", "storage_box.3mf")

# ---- box -------------------------------------------------------------------
ox, oy = INNER_X + 2 * WALL, INNER_Y + 2 * WALL
outer = rounded_box(ox, oy, INNER_Z + FLOOR, CORNER_R)
cavity = rounded_box(INNER_X, INNER_Y, INNER_Z + 1, CORNER_R - WALL).translate((0, 0, FLOOR))
box = outer - cavity

# ---- lid (printed upside down: flat top on the plate, no supports) ----------
lx, ly = ox + 2 * (GAP + WALL), oy + 2 * (GAP + WALL)
lid_outer = rounded_box(lx, ly, LID_TOP + LID_SKIRT, CORNER_R + GAP + WALL)
lid_cavity = rounded_box(ox + 2 * GAP, oy + 2 * GAP, LID_SKIRT + 1,
                         CORNER_R + GAP).translate((0, 0, LID_TOP))
lid = lid_outer - lid_cavity

# ---- lay out side by side on the plate --------------------------------------
box = place_on_plate(box).translate((-(ox / 2 + 5), 0, 0))
lid = place_on_plate(lid).translate((lx / 2 + 5, 0, 0))

for path in export({"box": box, "lid": lid}, OUT):
    print("wrote", path)

#!/usr/bin/env python3
"""
check_printable.py — pre-flight checks for a model going to a Bambu Lab A1.

Usage:
    python check_printable.py model.3mf [more.stl ...] [--material pla] [--max-overhang 45]

Checks each mesh for:
  * watertight / manifold (slicers repair these badly)
  * fits the A1 build volume (256 x 256 x 256 mm)
  * sits on the plate (min Z == 0) with a usable first-layer contact area
  * share of downward faces steeper than the overhang limit (needs supports)
  * volume, and filament weight / length estimate (PLA by default)
Exit code 1 if a blocking problem is found.
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

BUILD = np.array([256.0, 256.0, 256.0])
FILAMENT_D = 1.75
DENSITIES = {"pla": 1.24, "petg": 1.27, "abs": 1.04, "asa": 1.07, "tpu": 1.21}


def read_3mf(path: str) -> list[tuple[str, trimesh.Trimesh]]:
    """Read every mesh object from a 3MF (ours or Bambu Studio's) without extra deps.
    Build-item transforms are applied where present."""
    out = []
    with zipfile.ZipFile(path) as z:
        models = [n for n in z.namelist() if n.lower().endswith(".model")]
        meshes = {}
        for n in models:
            root = ET.fromstring(z.read(n))
            ns = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
            for obj in root.iter(f"{ns}object"):
                mesh = obj.find(f"{ns}mesh")
                if mesh is None:
                    continue
                v = np.array([[float(e.get("x")), float(e.get("y")), float(e.get("z"))]
                              for e in mesh.iter(f"{ns}vertex")])
                f = np.array([[int(e.get("v1")), int(e.get("v2")), int(e.get("v3"))]
                              for e in mesh.iter(f"{ns}triangle")])
                meshes[(n, obj.get("id"))] = (obj.get("name") or f"object{obj.get('id')}",
                                              trimesh.Trimesh(v, f, process=True))
            for item in root.iter(f"{ns}item"):
                key = (n, item.get("objectid"))
                if key in meshes and item.get("transform"):
                    t = [float(x) for x in item.get("transform").split()]
                    m4 = np.eye(4)
                    m4[:3, :3] = np.array(t[:9]).reshape(3, 3).T
                    m4[:3, 3] = t[9:12]
                    meshes[key][1].apply_transform(m4)
    for name, m in meshes.values():
        out.append((f"{path}:{name}", m))
    return out


def load_meshes(path: str) -> list[tuple[str, trimesh.Trimesh]]:
    if path.lower().endswith(".3mf"):
        return read_3mf(path)
    return [(path, trimesh.load(path, force="mesh"))]


def check(name: str, m: trimesh.Trimesh, density: float, max_overhang: float,
          infill: float) -> bool:
    ok = True
    print(f"\n== {name}")
    lo, hi = m.bounds
    size = hi - lo
    print(f"   size        : {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")
    print(f"   triangles   : {len(m.faces):,}")

    if m.is_watertight and m.is_winding_consistent:
        print("   manifold    : OK (watertight)")
    else:
        ok = False
        print("   manifold    : FAIL — not watertight; fix the model (don't rely on slicer repair)")

    if np.any(size > BUILD):
        ok = False
        print("   build volume: FAIL — larger than 256 mm cube; split the part or scale down")
    else:
        print("   build volume: OK")

    if abs(lo[2]) > 0.01:
        print(f"   on plate    : WARN — lowest point is Z={lo[2]:.2f}; Bambu Studio will drop it, "
              "but check the orientation is intentional")

    normals = m.face_normals
    areas = m.area_faces
    z = normals[:, 2]
    # faces touching the plate
    face_min_z = m.vertices[m.faces][:, :, 2].min(axis=1)
    face_max_z = m.vertices[m.faces][:, :, 2].max(axis=1)
    bottom = (z < -0.999) & (face_max_z - lo[2] < 0.01)
    contact = areas[bottom].sum()
    print(f"   plate contact: {contact:.0f} mm²", end="")
    if contact < 50 and size[2] > 20:
        print("  WARN — tiny footprint for a tall part; add a brim or re-orient")
    else:
        print()

    # overhangs: downward-facing faces not on the plate, steeper than limit from vertical
    limit = -np.sin(np.radians(90 - max_overhang))  # e.g. 45° -> -0.707
    down = (z < limit) & ~bottom & (face_min_z - lo[2] > 0.3)
    over_area = areas[down].sum()
    total = areas.sum()
    pct = 100 * over_area / total if total else 0
    flag = "OK" if pct < 1 else ("WARN — probably needs supports (or re-orient / add chamfers)"
                                 if pct < 10 else "WARN — lots of overhang; re-orient or split")
    print(f"   overhang >{max_overhang:.0f}°: {over_area:.0f} mm² ({pct:.1f}% of surface) {flag}")

    if m.is_watertight:
        vol_cm3 = m.volume / 1000
        # rough print mass: shell (≈ 2 walls over the surface) + infill of the rest
        shell_cm3 = min(vol_cm3, total * 0.8 / 1000)
        eff = shell_cm3 + (vol_cm3 - shell_cm3) * infill
        grams = eff * density
        metres = eff / (np.pi * (FILAMENT_D / 20) ** 2) / 100
        print(f"   volume      : {vol_cm3:.1f} cm³ solid")
        print(f"   filament est: ~{grams:.0f} g  (~{metres:.1f} m) at {infill*100:.0f}% infill")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--material", default="pla", choices=sorted(DENSITIES))
    ap.add_argument("--max-overhang", type=float, default=45.0,
                    help="degrees from vertical the printer handles without support")
    ap.add_argument("--infill", type=float, default=0.15)
    a = ap.parse_args()
    all_ok = True
    for f in a.files:
        for name, m in load_meshes(f):
            all_ok &= check(name, m, DENSITIES[a.material], a.max_overhang, a.infill)
    print("\nRESULT:", "PRINTABLE" if all_ok else "PROBLEMS FOUND")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

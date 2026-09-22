"""
printlib — small CSG helpers for making printable models for a Bambu Lab A1.

Built on manifold3d >= 3 (guaranteed watertight/manifold booleans) and trimesh
(export to 3MF / STL). All units are millimetres. Z is up; the build plate is Z=0.

Install once:  pip install manifold3d trimesh numpy
"""
from __future__ import annotations

import math
import os
import zipfile
from xml.sax.saxutils import escape

import numpy as np
from manifold3d import CrossSection, JoinType, Manifold, OpType
import trimesh

# ---------------------------------------------------------------------------
# Bambu Lab A1 constants
# ---------------------------------------------------------------------------
A1_BUILD_VOLUME = (256.0, 256.0, 256.0)  # X, Y, Z in mm
NOZZLE = 0.4                             # stock nozzle diameter
LAYER = 0.2                              # default layer height ("0.20mm Standard")
MIN_WALL = 0.8                           # 2 perimeters at 0.4 mm
GOOD_WALL = 1.6                          # 4 perimeters: sturdy parts
CLEARANCE_SLIDE = 0.3                    # per-side gap for sliding / removable fits
CLEARANCE_PRESS = 0.15                   # per-side gap for snug press fits
CLEARANCE_PRINT_IN_PLACE = 0.4           # gap between parts printed already assembled

DEFAULT_SEGMENTS = 96                    # circle resolution (smooth but light)


# ---------------------------------------------------------------------------
# Primitives (all return manifold3d.Manifold)
# ---------------------------------------------------------------------------
def box(x: float, y: float, z: float, center_xy: bool = True) -> Manifold:
    """Box sitting on Z=0. Centred in XY by default."""
    m = Manifold.cube((x, y, z))
    return m.translate((-x / 2, -y / 2, 0)) if center_xy else m


def rounded_box(x: float, y: float, z: float, r: float,
                center_xy: bool = True, segments: int = DEFAULT_SEGMENTS) -> Manifold:
    """Box with vertically rounded corners (radius r), flat top and bottom."""
    r = max(0.0, min(r, x / 2 - 0.01, y / 2 - 0.01))
    if r == 0:
        return box(x, y, z, center_xy)
    cs = CrossSection.square((x - 2 * r, y - 2 * r)).translate((r, r)).offset(
        r, JoinType.Round, circular_segments=segments)
    m = cs.extrude(z)
    return m.translate((-x / 2, -y / 2, 0)) if center_xy else m


def cylinder(d: float, h: float, d2: float | None = None,
             segments: int = DEFAULT_SEGMENTS) -> Manifold:
    """Cylinder (or cone if d2 given) standing on Z=0, centred on the Z axis."""
    return Manifold.cylinder(h, d / 2, (d2 if d2 is not None else d) / 2, segments)


def sphere(d: float, segments: int = DEFAULT_SEGMENTS) -> Manifold:
    return Manifold.sphere(d / 2, segments)


def tube(outer_d: float, inner_d: float, h: float,
         segments: int = DEFAULT_SEGMENTS) -> Manifold:
    return cylinder(outer_d, h, segments=segments) - cylinder(
        inner_d, h + 2, segments=segments).translate((0, 0, -1))


def polygon_extrude(points: list[tuple[float, float]], h: float) -> Manifold:
    """Extrude a 2D outline (list of XY points, CCW) up to height h."""
    return CrossSection([points]).extrude(h)


def revolve(profile: list[tuple[float, float]], segments: int = DEFAULT_SEGMENTS,
            degrees: float = 360.0) -> Manifold:
    """Revolve a 2D profile around Z. Profile points are (radius, z), radius >= 0."""
    return CrossSection([profile]).revolve(segments, degrees)


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------
def hole(d: float, depth: float, at=(0, 0, 0), clearance: float = 0.2,
         segments: int = DEFAULT_SEGMENTS) -> Manifold:
    """A cylinder to SUBTRACT. Adds clearance (FDM holes print undersized).
    Extends 0.01 mm below `at` so it cleanly breaks through surfaces."""
    return cylinder(d + clearance, depth + 0.02, segments=segments).translate(
        (at[0], at[1], at[2] - 0.01))


def countersunk_hole(screw_d: float, head_d: float, depth: float, at=(0, 0, 0),
                     from_top: bool = True, clearance: float = 0.2) -> Manifold:
    """Through-hole with a 90° countersink. Subtract it. `at` is the bottom of the part
    and `depth` its thickness; the countersink is on the top when from_top=True."""
    shaft = cylinder(screw_d + clearance, depth + 0.02).translate((0, 0, -0.01))
    sink_h = (head_d - screw_d) / 2
    cone = cylinder(screw_d + clearance, sink_h + 0.01, d2=head_d + clearance)
    cone = cone.translate((0, 0, depth - sink_h + 0.01)) if from_top else \
        cone.mirror((0, 0, 1)).translate((0, 0, sink_h - 0.01))
    return (shaft + cone).translate(at)


def hex_nut_trap(across_flats: float, h: float, at=(0, 0, 0),
                 clearance: float = 0.2) -> Manifold:
    """Hexagonal pocket for a nut (M3: 5.5 AF, M4: 7.0, M5: 8.0). Subtract it."""
    r = (across_flats + clearance) / math.sqrt(3)
    return Manifold.cylinder(h, r, r, 6).translate(at)


def shell(solid: Manifold, wall: float) -> Manifold:
    """Hollow out a solid, keeping `wall` thickness, open at the top.
    Works for convex-ish extrusions built from CrossSections; for complex shapes build
    the inner cavity explicitly instead."""
    bb = solid.bounding_box()
    lo, hi = np.array(bb[:3]), np.array(bb[3:])
    size = hi - lo
    sx = (size[0] - 2 * wall) / size[0]
    sy = (size[1] - 2 * wall) / size[1]
    centre = (lo + hi) / 2
    inner = solid.translate((-centre[0], -centre[1], 0)).scale((sx, sy, 1.0)).translate(
        (centre[0], centre[1], wall))
    return solid - inner


def union(*parts: Manifold) -> Manifold:
    return Manifold.batch_boolean(list(parts), OpType.Add)


def place_on_plate(m: Manifold, center: bool = True) -> Manifold:
    """Move the part so its lowest point is at Z=0 and (optionally) centred in XY."""
    x0, y0, z0, x1, y1, _ = m.bounding_box()
    dx = -(x0 + x1) / 2 if center else 0
    dy = -(y0 + y1) / 2 if center else 0
    return m.translate((dx, dy, -z0))


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
def to_trimesh(m: Manifold) -> trimesh.Trimesh:
    mesh = m.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3]
    faces = np.asarray(mesh.tri_verts)
    return trimesh.Trimesh(vertices=verts, faces=faces, process=True)


def write_3mf(parts: dict[str, Manifold], path: str) -> None:
    """Minimal 3MF core-spec writer (no extra deps). Each part becomes its own object,
    so Bambu Studio lists them separately and can assign a filament to each."""
    objects, items = [], []
    for i, (name, m) in enumerate(parts.items(), start=1):
        mesh = m.to_mesh()
        verts = np.asarray(mesh.vert_properties)[:, :3]
        tris = np.asarray(mesh.tri_verts)
        v = "".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in verts)
        t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tris)
        safe = escape(name, {'"': "&quot;"})
        objects.append(f'<object id="{i}" name="{safe}" type="model"><mesh>'
                       f"<vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>")
        items.append(f'<item objectid="{i}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources>{"".join(objects)}</resources><build>{"".join(items)}</build></model>')
    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                     "</Types>")
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
            "</Relationships>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def export(parts: dict[str, Manifold] | Manifold, out_path: str,
           also_stl: bool = True) -> list[str]:
    """Export to a 3MF (opens directly in Bambu Studio) and optionally per-part STLs.

    `parts` may be a single Manifold or {"name": Manifold}. Multiple parts go into one
    3MF as separate objects so Bambu Studio can assign different filaments (AMS lite).
    Returns the list of written file paths.
    """
    if isinstance(parts, Manifold):
        parts = {os.path.splitext(os.path.basename(out_path))[0]: parts}
    if not out_path.lower().endswith(".3mf"):
        out_path += ".3mf"
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    for name, m in parts.items():
        if m.is_empty():
            raise ValueError(f"part '{name}' is empty — check your booleans")
    write_3mf(parts, out_path)
    written = [out_path]
    if also_stl:
        for name, m in parts.items():
            stl = os.path.join(out_dir, f"{name}.stl")
            to_trimesh(m).export(stl)
            written.append(stl)
    return written

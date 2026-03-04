"""
add_door_v2.py — Proper 3D door for the barrel sauna front wall.

Replaces the old door_wooden objects with correctly named geometry:
  door_frame_left/right/top/bottom  → matches /^door_frame/ in main.js
  door_panel                         → matches /^door_panel/  in main.js
  door_glass                         → matches /^door_glass/  in main.js

Geometry is sized to be realistic for a barrel sauna:
  - Narrower and shorter than the v3 default
  - Bottom sill sits near the ground (low on the curved wall)
  - Frame protrudes from the front wall face
  - Door panel inset inside the frame
  - Tall vertical window in upper half, cut with Boolean
  - Dark tinted glass pane with high reflectivity
"""
import bpy
import bmesh
import math

# ─────────────────────────────────────────────────────────────
# CONSTANTS — must match generate_sauna_v3.py coordinate system
# ─────────────────────────────────────────────────────────────
BARREL_R   = 1.025
WALL_THICK = 0.040
HALF_LEN   = 1.650
FRONT_X    = HALF_LEN - 0.200          # 1.450  — centre of the front wall disc
WALL_FACE  = FRONT_X + WALL_THICK / 2  # 1.470  — outer face of the wall

# ── Door opening dimensions (new, smaller than v3 default) ──
DOOR_W     = 0.560   # 56 cm wide  (was 65 cm)
DOOR_H     = 1.260   # 1.26 m tall (was 1.50 m)
DOOR_BOT   = 0.065   # bottom sill 6.5 cm above ground

# Derived
DOOR_MID_Z = DOOR_BOT + DOOR_H / 2    # centre Z of the door opening

# ── Frame ────────────────────────────────────────────────────
FRAME_BDR  = 0.055   # border/rail width around opening (5.5 cm)
FRAME_DEP  = 0.062   # how far the frame protrudes from wall face (6.2 cm)
FRAME_X    = WALL_FACE + FRAME_DEP / 2  # centre X of frame planks

# ── Door panel ───────────────────────────────────────────────
PANEL_T    = 0.038   # panel thickness (3.8 cm)
PANEL_X    = WALL_FACE + FRAME_DEP - PANEL_T / 2  # near front of frame

# ── Window in door (tall vertical pane, upper portion) ───────
WIN_W      = DOOR_W * 0.52   # 52 % of door width
WIN_H      = DOOR_H * 0.40   # 40 % of door height
WIN_TOP    = DOOR_BOT + DOOR_H - 0.075  # 7.5 cm below door top
WIN_BOT    = WIN_TOP - WIN_H
WIN_MID_Z  = (WIN_TOP + WIN_BOT) / 2


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def remove_objects_by_prefix(*prefixes):
    """Delete all objects whose name starts with any of the given prefixes."""
    for obj in list(bpy.data.objects):
        for pfx in prefixes:
            if obj.name.startswith(pfx):
                bpy.data.objects.remove(obj, do_unlink=True)
                break


def uv_and_normals(obj):
    """Smart-project UV + make normals consistent outward."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')


def apply_bool(target, cutter, op='DIFFERENCE'):
    mod = target.modifiers.new('Bool', 'BOOLEAN')
    mod.operation = op
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier='Bool')
    bpy.data.objects.remove(cutter, do_unlink=True)


def box(name, loc, sz):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, scale=sz)
    o = bpy.context.active_object
    o.name = name
    return o


def get_wood_mat():
    """Return an existing wood material or create a fallback."""
    for candidate in ('Door_Wood', 'Spruce_Exterior', 'Spruce_Wall'):
        m = bpy.data.materials.get(candidate)
        if m:
            return m
    m = bpy.data.materials.new('Door_Wood')
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.55, 0.38, 0.22, 1)
    bsdf.inputs['Roughness'].default_value = 0.60
    return m


# ─────────────────────────────────────────────────────────────
# 1. REMOVE OLD DOOR OBJECTS AND FRONT WALL
# ─────────────────────────────────────────────────────────────
print("Removing old door/front_wall objects...")
remove_objects_by_prefix(
    'door_wooden', 'door_panel', 'door_frame',
    'door_glass',  'front_wall',
)


# ─────────────────────────────────────────────────────────────
# 2. REBUILD FRONT WALL with new (smaller) door cutout
# ─────────────────────────────────────────────────────────────
print("Rebuilding front wall...")

wall_r = BARREL_R - WALL_THICK - 0.005  # 0.980

bpy.ops.mesh.primitive_cylinder_add(
    radius=wall_r, depth=WALL_THICK,
    vertices=64,
    location=(FRONT_X, 0, BARREL_R),
    rotation=(0, math.pi / 2, 0),
)
fw = bpy.context.active_object
fw.name = 'front_wall'

# Boolean: door opening
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(FRONT_X, 0, DOOR_MID_Z),
    scale=(WALL_THICK + 0.02, DOOR_W, DOOR_H),
)
apply_bool(fw, bpy.context.active_object)

# Boolean: small round vent hole (matches original v3 vent)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.04, depth=WALL_THICK + 0.02,
    vertices=16,
    location=(FRONT_X, 0.25, WALL_THICK + 0.15),
    rotation=(0, math.pi / 2, 0),
)
apply_bool(fw, bpy.context.active_object)

uv_and_normals(fw)

wall_mat = (bpy.data.materials.get('Spruce_Wall')
            or bpy.data.materials.get('Spruce_Exterior'))
if wall_mat:
    fw.data.materials.append(wall_mat)


# ─────────────────────────────────────────────────────────────
# 3. DOOR FRAME  (4 planks surrounding the opening)
# ─────────────────────────────────────────────────────────────
print("Creating door frame...")

wood_mat = get_wood_mat()
cx  = FRAME_X
bdr = FRAME_BDR
dep = FRAME_DEP
ow  = DOOR_W
oh  = DOOR_H
bot = DOOR_BOT
mz  = DOOR_MID_Z
tw  = ow + 2 * bdr   # total outer width  (0.670 m)
th  = oh + 2 * bdr   # total outer height (1.370 m)

frame_parts = [
    box('door_frame_left',
        (cx, -(ow / 2 + bdr / 2), mz),
        (dep, bdr, th)),
    box('door_frame_right',
        (cx, +(ow / 2 + bdr / 2), mz),
        (dep, bdr, th)),
    box('door_frame_top',
        (cx, 0, bot + oh + bdr / 2),
        (dep, tw, bdr)),
    box('door_frame_bottom',
        (cx, 0, bot - bdr / 2),
        (dep, tw, bdr)),
]

for fp in frame_parts:
    uv_and_normals(fp)
    fp.data.materials.append(wood_mat)


# ─────────────────────────────────────────────────────────────
# 4. DOOR PANEL with Boolean window cutout
# ─────────────────────────────────────────────────────────────
print("Creating door panel with window...")

panel = box('door_panel',
            (PANEL_X, 0, mz),
            (PANEL_T, ow - 0.012, oh - 0.012))

# Cut tall vertical window into upper portion of panel
win_cutter = box('_win_cutter',
                 (PANEL_X, 0, WIN_MID_Z),
                 (PANEL_T + 0.01, WIN_W, WIN_H))
apply_bool(panel, win_cutter)

uv_and_normals(panel)
panel.data.materials.append(wood_mat)


# ─────────────────────────────────────────────────────────────
# 5. GLASS PANE (thin slab inside the window hole)
#    Using a very thin cube so normals work correctly in Three.js
# ─────────────────────────────────────────────────────────────
print("Creating glass pane...")

glass = box('door_glass',
            (PANEL_X, 0, WIN_MID_Z),
            (0.003, WIN_W - 0.022, WIN_H - 0.022))

uv_and_normals(glass)

# Tinted glass PBR material
gm = bpy.data.materials.new('Glass_Tinted_Door')
gm.use_nodes = True
# Blender 4+ dropped shadow_method; blend_method may also vary by version
try:
    gm.blend_method = 'BLEND'
except AttributeError:
    pass
gm.use_backface_culling = False

nt = gm.node_tree
nt.nodes.clear()
out  = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (-300, 0)
out.location  = (0, 0)
# Very dark, highly reflective, smooth — tinted sauna glass
bsdf.inputs['Base Color'].default_value = (0.030, 0.055, 0.065, 1)
bsdf.inputs['Roughness'].default_value  = 0.035   # very smooth / mirror-like
bsdf.inputs['Metallic'].default_value   = 0.30    # moderate metalness for sheen
bsdf.inputs['Alpha'].default_value      = 0.15    # 15 % opaque = very dark tint
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

glass.data.materials.append(gm)


# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
new_objs = ['front_wall'] + [fp.name for fp in frame_parts] + ['door_panel', 'door_glass']
print("=== Door v2 complete ===")
print(f"  Door opening : {ow*100:.0f} cm wide × {oh*100:.0f} cm tall")
print(f"  Bottom sill  : Z = {bot:.3f} m  (centre Z = {mz:.3f} m)")
print(f"  Frame outer  : {tw*100:.0f} cm × {th*100:.0f} cm, protrudes {dep*100:.0f} cm")
print(f"  Window       : {WIN_W*100:.1f} cm × {WIN_H*100:.1f} cm, centre Z = {WIN_MID_Z:.3f} m")
print(f"  Objects      : {new_objs}")

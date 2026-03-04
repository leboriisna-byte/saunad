"""
Barrel Sauna v3 — Built from exact Tesler 3.3m blueprint dimensions.
Key features matching reference images:
  - Horizontal staves with visible seams on barrel body
  - Vertical planking on end walls
  - Front overhang ("nokk")
  - Two rooms: eesruum (950mm) + leiliruum (1780mm)
  - V-shaped support legs
  - Alder benches on both sides (500mm × 450mm)
  - Chimney pipe
  - Icopal Plano hexagonal roof shingles
  - Stainless steel bands
"""
import bpy
import math
import bmesh

# ═══════════════════════════════════════════════════════════
# BLUEPRINT DIMENSIONS (mm → meters)
# ═══════════════════════════════════════════════════════════
BARREL_LEN      = 3.300
BARREL_R        = 1.025      # 2050mm diameter / 2
WALL_THICK      = 0.040      # 40mm spruce

# Room layout
OVERHANG_FRONT  = 0.200      # Front overhang
EESRUUM_LEN     = 0.950      # Changing room
DIVIDER_THICK   = 0.040      # Dividing wall
LEILIRUUM_LEN   = 1.780      # Sauna room
OVERHANG_BACK   = 0.200      # Back overhang

# Benches
BENCH_W         = 0.500      # Width each side
BENCH_H         = 0.450      # Height from floor
BENCH_THICK     = 0.035      # Plank thickness

# Staves
STAVE_COUNT     = 32         # Number of staves
# Each stave is ~200mm wide at the widest point

# Support legs
LEG_BASE_W      = 1.500      # Base width
LEG_THICK       = 0.060      # Thickness
LEG_DEPTH       = 0.120      # Front-to-back depth

# Door
DOOR_W          = 0.650
DOOR_H          = 1.500
DOOR_THICK      = 0.045

# Back window
BACK_WIN_W      = 0.350
BACK_WIN_H      = 0.350

# Chimney
CHIMNEY_R       = 0.060
CHIMNEY_H       = 0.400

# Roof arc
ROOF_ARC_DEG    = 130        # degrees covered by shingles

# X positions (barrel centered at origin, lengthwise along X)
HALF_LEN        = BARREL_LEN / 2
FRONT_WALL_X    = HALF_LEN - OVERHANG_FRONT
DIVIDER_X       = FRONT_WALL_X - EESRUUM_LEN
BACK_WALL_X     = DIVIDER_X - LEILIRUUM_LEN
# Barrel center Z = BARREL_R (sitting on ground)

# ═══════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for b in bpy.data.meshes:
        if b.users == 0: bpy.data.meshes.remove(b)
    for b in bpy.data.materials:
        if b.users == 0: bpy.data.materials.remove(b)

def to_col(obj, name):
    if name not in bpy.data.collections:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    col = bpy.data.collections[name]
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)

def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True

def apply_bool(target, cutter, op='DIFFERENCE'):
    mod = target.modifiers.new('B', 'BOOLEAN')
    mod.operation = op
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier='B')
    bpy.data.objects.remove(cutter, do_unlink=True)

def simple_mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    return m


# ═══════════════════════════════════════════════════════════
# MATERIALS
# ═══════════════════════════════════════════════════════════
def create_mats():
    return {
        'spruce_ext':  simple_mat('Spruce_Exterior', (0.78, 0.62, 0.40, 1), 0.65),
        'spruce_wall': simple_mat('Spruce_Wall', (0.72, 0.55, 0.33, 1), 0.60),
        'alder':       simple_mat('Alder_Bench', (0.82, 0.65, 0.42, 1), 0.55),
        'glass':       simple_mat('Glass', (0.80, 0.85, 0.88, 0.3), 0.05),
        'glass_bronze':simple_mat('Glass_Bronze', (0.70, 0.55, 0.35, 0.3), 0.05),
        'metal_band':  simple_mat('Metal_Band', (0.55, 0.55, 0.58, 1), 0.30, 0.9),
        'chimney':     simple_mat('Chimney', (0.70, 0.72, 0.75, 1), 0.25, 0.95),
        'shingles':    simple_mat('Shingles', (0.15, 0.17, 0.20, 1), 0.85),
        'metal_roof':  simple_mat('MetalRoof', (0.35, 0.38, 0.42, 1), 0.35, 0.8),
        'heater':      simple_mat('Heater', (0.10, 0.10, 0.10, 1), 0.50, 0.7),
        'stone':       simple_mat('Stone', (0.42, 0.40, 0.38, 1), 0.90),
        'door_wood':   simple_mat('Door_Wood', (0.55, 0.38, 0.20, 1), 0.60),
        'floor':       simple_mat('Floor_Grate', (0.70, 0.55, 0.35, 1), 0.70),
        'leg_wood':    simple_mat('Leg_Wood', (0.45, 0.30, 0.15, 1), 0.65),
    }


# ═══════════════════════════════════════════════════════════
# BARREL BODY — individual staves for visible seams
# ═══════════════════════════════════════════════════════════
def build_barrel_staves(M):
    """Build barrel from individual stave segments with gaps."""
    inner_r = BARREL_R - WALL_THICK
    stave_angle = 2 * math.pi / STAVE_COUNT
    gap = 0.002  # 2mm gap between staves for visual seam

    parent = bpy.data.objects.new('barrel_body', None)
    bpy.context.scene.collection.objects.link(parent)
    to_col(parent, 'Barrel')

    for i in range(STAVE_COUNT):
        angle_start = i * stave_angle + gap / 2
        angle_end = (i + 1) * stave_angle - gap / 2
        arc_verts = 4  # vertices per stave arc edge

        mesh = bpy.data.meshes.new(f'stave_{i}')
        bm = bmesh.new()

        # Create stave as a curved plank
        for j in range(arc_verts + 1):
            a = angle_start + (j / arc_verts) * (angle_end - angle_start)
            cos_a = math.cos(a)
            sin_a = math.sin(a)

            # 4 vertices per column: outer-front, inner-front, inner-back, outer-back
            ox = HALF_LEN
            ix = HALF_LEN
            bm.verts.new((ox, inner_r * cos_a, inner_r * sin_a + BARREL_R))
            bm.verts.new((ox, BARREL_R * cos_a, BARREL_R * sin_a + BARREL_R))
            bm.verts.new((-HALF_LEN, BARREL_R * cos_a, BARREL_R * sin_a + BARREL_R))
            bm.verts.new((-HALF_LEN, inner_r * cos_a, inner_r * sin_a + BARREL_R))

        bm.verts.ensure_lookup_table()

        # Create faces
        for j in range(arc_verts):
            base = j * 4
            next_base = (j + 1) * 4
            # Outer face
            bm.faces.new([bm.verts[base+1], bm.verts[next_base+1],
                          bm.verts[next_base+2], bm.verts[base+2]])
            # Inner face
            bm.faces.new([bm.verts[base], bm.verts[base+3],
                          bm.verts[next_base+3], bm.verts[next_base]])
            # Front cap
            bm.faces.new([bm.verts[base], bm.verts[next_base],
                          bm.verts[next_base+1], bm.verts[base+1]])
            # Back cap
            bm.faces.new([bm.verts[base+2], bm.verts[next_base+2],
                          bm.verts[next_base+3], bm.verts[base+3]])

        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(f'stave_{i}', mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.parent = parent
        obj.data.materials.append(M['spruce_ext'])
        smooth(obj)
        to_col(obj, 'Barrel')

    return parent


# ═══════════════════════════════════════════════════════════
# END WALLS — vertical planking
# ═══════════════════════════════════════════════════════════
def build_end_wall(M, x_pos, name, door_cutout=False, window_cutout=False, vent_hole=False):
    """Circular end wall with vertical plank appearance."""
    r = BARREL_R - WALL_THICK - 0.005

    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=WALL_THICK,
        vertices=48,
        location=(x_pos, 0, BARREL_R),
        rotation=(0, math.pi/2, 0)
    )
    wall = bpy.context.active_object
    wall.name = name

    if door_cutout:
        door_z = WALL_THICK + DOOR_H / 2
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x_pos, 0, door_z),
            scale=(WALL_THICK + 0.02, DOOR_W, DOOR_H)
        )
        apply_bool(wall, bpy.context.active_object)

    if window_cutout:
        win_z = BARREL_R * 0.9
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x_pos, 0, win_z),
            scale=(WALL_THICK + 0.02, BACK_WIN_W, BACK_WIN_H)
        )
        apply_bool(wall, bpy.context.active_object)

    if vent_hole:
        vent_z = WALL_THICK + 0.15
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.04, depth=WALL_THICK + 0.02,
            vertices=16,
            location=(x_pos, 0.25, vent_z),
            rotation=(0, math.pi/2, 0)
        )
        apply_bool(wall, bpy.context.active_object)

    smooth(wall)
    wall.data.materials.append(M['spruce_wall'])
    to_col(wall, 'Walls')
    return wall


def build_divider_wall(M):
    """Internal dividing wall between changing room and sauna."""
    r = BARREL_R - WALL_THICK - 0.005

    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=DIVIDER_THICK,
        vertices=48,
        location=(DIVIDER_X, 0, BARREL_R),
        rotation=(0, math.pi/2, 0)
    )
    wall = bpy.context.active_object
    wall.name = 'divider_wall'

    # Door opening in divider (glass door to sauna)
    door_z = WALL_THICK + DOOR_H / 2
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(DIVIDER_X, 0, door_z),
        scale=(DIVIDER_THICK + 0.02, DOOR_W - 0.05, DOOR_H - 0.05)
    )
    apply_bool(wall, bpy.context.active_object)

    smooth(wall)
    wall.data.materials.append(M['spruce_wall'])
    to_col(wall, 'Walls')
    return wall


# ═══════════════════════════════════════════════════════════
# DOORS
# ═══════════════════════════════════════════════════════════
def build_front_door(M, name='door_wooden'):
    """Wooden front door with glass panes."""
    x = FRONT_WALL_X
    door_z = WALL_THICK + DOOR_H / 2

    # Door panel
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(x + 0.001, 0, door_z),
        scale=(DOOR_THICK, DOOR_W - 0.02, DOOR_H - 0.02)
    )
    door = bpy.context.active_object
    door.name = name
    door.data.materials.append(M['door_wood'])

    # Glass window area (multi-pane style)
    win_h = DOOR_H * 0.35
    win_w = DOOR_W * 0.40
    win_z = door_z + DOOR_H * 0.15
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(x + 0.003, 0, win_z),
        scale=(DOOR_THICK + 0.005, win_w, win_h)
    )
    win = bpy.context.active_object
    win.name = name + '_glass'
    win.data.materials.append(M['glass'])
    to_col(win, 'Doors')

    to_col(door, 'Doors')
    return door


def build_sauna_door(M, name='door_sauna_glass'):
    """Bronze-tinted glass door for sauna room."""
    x = DIVIDER_X
    door_z = WALL_THICK + DOOR_H / 2

    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(x + 0.001, 0, door_z),
        scale=(DOOR_THICK, DOOR_W - 0.07, DOOR_H - 0.07)
    )
    door = bpy.context.active_object
    door.name = name
    door.data.materials.append(M['glass_bronze'])
    to_col(door, 'Doors')
    return door


def build_fullglass_front(M, name='door_fullglass'):
    """Full glass front door variant."""
    x = FRONT_WALL_X
    door_z = WALL_THICK + DOOR_H / 2

    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(x + 0.001, 0, door_z),
        scale=(DOOR_THICK, DOOR_W - 0.02, DOOR_H - 0.02)
    )
    door = bpy.context.active_object
    door.name = name
    door.data.materials.append(M['glass'])
    to_col(door, 'Doors')
    return door


def build_panoramic_front(M, name='door_panoramic'):
    """Panoramic glass front door variant."""
    x = FRONT_WALL_X
    door_z = WALL_THICK + DOOR_H / 2

    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(x + 0.001, 0, door_z),
        scale=(DOOR_THICK, DOOR_W * 1.3, DOOR_H - 0.02)
    )
    door = bpy.context.active_object
    door.name = name
    door.data.materials.append(M['glass'])
    to_col(door, 'Doors')
    return door


# ═══════════════════════════════════════════════════════════
# BACK WINDOW
# ═══════════════════════════════════════════════════════════
def build_back_window(M):
    x = BACK_WALL_X
    win_z = BARREL_R * 0.9

    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(x - 0.001, 0, win_z),
        scale=(WALL_THICK + 0.005, BACK_WIN_W - 0.02, BACK_WIN_H - 0.02)
    )
    win = bpy.context.active_object
    win.name = 'back_window'
    win.data.materials.append(M['glass_bronze'])
    to_col(win, 'Walls')
    return win


# ═══════════════════════════════════════════════════════════
# BENCHES — alder, both sides of sauna room
# ═══════════════════════════════════════════════════════════
def build_benches(M):
    """Alder benches in sauna room, both sides."""
    sauna_center_x = DIVIDER_X - LEILIRUUM_LEN / 2
    bench_len = LEILIRUUM_LEN * 0.85

    for side, sign in [('left', -1), ('right', 1)]:
        y = sign * (BENCH_W / 2 + 0.05)

        # Main bench surface
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(sauna_center_x, y, BENCH_H),
            scale=(bench_len, BENCH_W, BENCH_THICK)
        )
        b = bpy.context.active_object
        b.name = f'bench_{side}'
        b.data.materials.append(M['alder'])
        to_col(b, 'Interior')

        # Bench support legs (3 per bench)
        for xoff in [-bench_len * 0.35, 0, bench_len * 0.35]:
            bpy.ops.mesh.primitive_cube_add(size=1,
                location=(sauna_center_x + xoff, y, BENCH_H / 2),
                scale=(0.04, 0.04, BENCH_H - BENCH_THICK)
            )
            leg = bpy.context.active_object
            leg.name = f'bench_{side}_leg'
            leg.data.materials.append(M['alder'])
            to_col(leg, 'Interior')


# ═══════════════════════════════════════════════════════════
# FLOOR GRATES
# ═══════════════════════════════════════════════════════════
def build_floors(M):
    """Floor grates in both rooms."""
    inner_r = BARREL_R - WALL_THICK
    floor_w = inner_r * 1.2

    # Changing room floor
    ee_cx = FRONT_WALL_X - EESRUUM_LEN / 2
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(ee_cx, 0, WALL_THICK),
        scale=(EESRUUM_LEN * 0.90, floor_w, 0.020)
    )
    f1 = bpy.context.active_object
    f1.name = 'floor_eesruum'
    f1.data.materials.append(M['floor'])
    to_col(f1, 'Interior')

    # Sauna room floor
    sa_cx = DIVIDER_X - LEILIRUUM_LEN / 2
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(sa_cx, 0, WALL_THICK),
        scale=(LEILIRUUM_LEN * 0.90, floor_w, 0.020)
    )
    f2 = bpy.context.active_object
    f2.name = 'floor_leiliruum'
    f2.data.materials.append(M['floor'])
    to_col(f2, 'Interior')


# ═══════════════════════════════════════════════════════════
# HEATERS
# ═══════════════════════════════════════════════════════════
def build_heater_wood(M):
    """Wood-burning stove with chimney, against divider wall."""
    hx = DIVIDER_X - 0.25
    hz = WALL_THICK + 0.001

    # Stove body
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(hx, 0, hz + 0.25),
        scale=(0.35, 0.30, 0.50)
    )
    stove = bpy.context.active_object
    stove.name = 'heater_harvia'
    stove.data.materials.append(M['heater'])
    to_col(stove, 'Heaters')

    # Stones on top
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=0.12, subdivisions=2,
        location=(hx, 0, hz + 0.55)
    )
    stones = bpy.context.active_object
    stones.name = 'heater_harvia_stones'
    stones.scale.z = 0.5
    stones.data.materials.append(M['stone'])
    to_col(stones, 'Heaters')

    return stove


def build_heater_electric(M):
    """Electric heater variant."""
    hx = DIVIDER_X - 0.25
    hz = WALL_THICK + 0.001

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.14, depth=0.42, vertices=16,
        location=(hx, 0, hz + 0.21)
    )
    h = bpy.context.active_object
    h.name = 'heater_huum'
    h.data.materials.append(M['heater'])
    smooth(h)
    to_col(h, 'Heaters')

    # Stones on top
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=0.12, subdivisions=2,
        location=(hx, 0, hz + 0.48)
    )
    s = bpy.context.active_object
    s.name = 'heater_huum_stones'
    s.scale.z = 0.4
    s.data.materials.append(M['stone'])
    to_col(s, 'Heaters')

    return h


# ═══════════════════════════════════════════════════════════
# CHIMNEY
# ═══════════════════════════════════════════════════════════
def build_chimney(M):
    """Stainless steel chimney pipe through roof."""
    cx = DIVIDER_X - 0.25
    cz = BARREL_R + BARREL_R * 0.5  # Through roof

    bpy.ops.mesh.primitive_cylinder_add(
        radius=CHIMNEY_R, depth=CHIMNEY_H + 0.3,
        vertices=16,
        location=(cx, 0, cz)
    )
    ch = bpy.context.active_object
    ch.name = 'chimney'
    ch.data.materials.append(M['chimney'])
    smooth(ch)
    to_col(ch, 'Heaters')

    # Cap on top
    bpy.ops.mesh.primitive_cylinder_add(
        radius=CHIMNEY_R * 1.5, depth=0.03,
        vertices=16,
        location=(cx, 0, cz + CHIMNEY_H / 2 + 0.18)
    )
    cap = bpy.context.active_object
    cap.name = 'chimney_cap'
    cap.data.materials.append(M['chimney'])
    to_col(cap, 'Heaters')


# ═══════════════════════════════════════════════════════════
# ROOF — Icopal Plano shingles
# ═══════════════════════════════════════════════════════════
def build_roof(M, name, style):
    """Curved roof shell on top portion of barrel."""
    arc = math.radians(ROOF_ARC_DEG)
    r = BARREL_R + 0.010
    su, sv = 32, 12

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    cols = su + 1
    for j in range(sv + 1):
        x = -HALF_LEN + (j / sv) * BARREL_LEN
        for i in range(cols):
            a = math.pi/2 - arc/2 + (i / su) * arc
            y = r * math.cos(a)
            z = r * math.sin(a) + BARREL_R
            bm.verts.new((x, y, z))

    bm.verts.ensure_lookup_table()
    for j in range(sv):
        for i in range(su):
            idx = j * cols + i
            bm.faces.new([
                bm.verts[idx], bm.verts[idx+1],
                bm.verts[idx+1+cols], bm.verts[idx+cols]
            ])

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    sol = obj.modifiers.new('S', 'SOLIDIFY')
    sol.thickness = 0.010
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier='S')
    obj.select_set(False)

    mat = M['shingles'] if style == 'shingles' else M['metal_roof']
    obj.data.materials.append(mat)
    smooth(obj)
    to_col(obj, 'Roof')
    return obj


# ═══════════════════════════════════════════════════════════
# V-SHAPED SUPPORT LEGS
# ═══════════════════════════════════════════════════════════
def build_v_legs(M):
    """V-shaped support legs (angled like the reference)."""
    # Two sets of legs — positions from blueprint: ~200mm from each end
    for x in [-BARREL_LEN * 0.30, BARREL_LEN * 0.30]:
        # Base plank (horizontal)
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x, 0, LEG_THICK/2),
            scale=(LEG_DEPTH, LEG_BASE_W, LEG_THICK)
        )
        base = bpy.context.active_object
        base.name = 'support_leg_base'
        base.data.materials.append(M['leg_wood'])
        to_col(base, 'Supports')

        # Left angled leg
        leg_h = BARREL_R * 0.55
        angle = math.radians(25)
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x,  -LEG_BASE_W * 0.35,  LEG_THICK + leg_h/2),
            scale=(LEG_DEPTH, LEG_THICK, leg_h)
        )
        ll = bpy.context.active_object
        ll.name = 'support_leg_left'
        ll.rotation_euler.x = -angle
        ll.data.materials.append(M['leg_wood'])
        to_col(ll, 'Supports')

        # Right angled leg
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x,  LEG_BASE_W * 0.35,  LEG_THICK + leg_h/2),
            scale=(LEG_DEPTH, LEG_THICK, leg_h)
        )
        rl = bpy.context.active_object
        rl.name = 'support_leg_right'
        rl.rotation_euler.x = angle
        rl.data.materials.append(M['leg_wood'])
        to_col(rl, 'Supports')


# ═══════════════════════════════════════════════════════════
# METAL BANDS
# ═══════════════════════════════════════════════════════════
def build_bands(M):
    positions = [-1.3, -0.4, 0.4, 1.3]
    for i, x in enumerate(positions):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=BARREL_R + 0.003,
            minor_radius=0.005,
            major_segments=48, minor_segments=8,
            location=(x, 0, BARREL_R),
            rotation=(0, math.pi/2, 0)
        )
        b = bpy.context.active_object
        b.name = f'metal_band_{i}'
        b.data.materials.append(M['metal_band'])
        to_col(b, 'Barrel')


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
print("=== BARREL SAUNA v3 — From Blueprint ===")
clear_scene()

M = create_mats()

print("Building barrel staves...")
build_barrel_staves(M)

print("Building walls...")
build_end_wall(M, FRONT_WALL_X, 'front_wall', door_cutout=True, vent_hole=True)
build_end_wall(M, BACK_WALL_X, 'back_wall', window_cutout=True)
build_divider_wall(M)

print("Building doors...")
build_front_door(M, 'door_wooden')
build_sauna_door(M)
d_fg = build_fullglass_front(M, 'door_fullglass')
d_pn = build_panoramic_front(M, 'door_panoramic')
d_fg.hide_set(True); d_fg.hide_render = True
d_pn.hide_set(True); d_pn.hide_render = True

print("Building back window...")
build_back_window(M)

print("Building interior...")
build_benches(M)
build_floors(M)

print("Building heaters...")
build_heater_wood(M)
he = build_heater_electric(M)
he.hide_set(True); he.hide_render = True
hs = bpy.data.objects.get('heater_huum_stones')
if hs: hs.hide_set(True); hs.hide_render = True

print("Building chimney...")
build_chimney(M)

print("Building roof...")
build_roof(M, 'roof_shingles', 'shingles')
rm = build_roof(M, 'roof_metal', 'metal')
rm.hide_set(True); rm.hide_render = True

print("Building support legs...")
build_v_legs(M)

print("Building metal bands...")
build_bands(M)

bpy.ops.object.select_all(action='DESELECT')

total = len(bpy.context.scene.objects)
cols = [c.name for c in bpy.data.collections]
print(f"\nDone! {total} objects, Collections: {cols}")

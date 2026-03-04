"""
Barrel Sauna v2 — Improved model with better geometry and textures.
Fixes: door positioning, proportions, adds procedural wood texture,
cleaner boolean operations, proper glass material.
"""
import bpy
import math
import bmesh

# ═══════════════════════════════════════════════════════════
# DIMENSIONS (meters)
# ═══════════════════════════════════════════════════════════
BARREL_LENGTH   = 3.300
BARREL_RADIUS   = 1.025
STAVE_THICKNESS = 0.042
STAVE_COUNT     = 36

DOOR_WIDTH      = 0.700
DOOR_HEIGHT     = 1.500
DOOR_THICKNESS  = 0.042

BENCH_DEPTH     = 0.450
BENCH_THICKNESS = 0.040
BENCH_HEIGHT_LOW  = 0.400
BENCH_HEIGHT_HIGH = 0.750

FLOOR_LEVEL     = STAVE_THICKNESS  # Inside floor relative to barrel bottom

# ═══════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0: bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0: bpy.data.materials.remove(block)

def to_collection(obj, col_name):
    if col_name not in bpy.data.collections:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    else:
        col = bpy.data.collections[col_name]
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)

def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True

def apply_bool(target, cutter, op='DIFFERENCE'):
    mod = target.modifiers.new('Bool', 'BOOLEAN')
    mod.operation = op
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier='Bool')
    bpy.data.objects.remove(cutter, do_unlink=True)


# ═══════════════════════════════════════════════════════════
# PROCEDURAL WOOD MATERIAL (node-based, no external textures)
# ═══════════════════════════════════════════════════════════
def make_wood_mat(name, base_color=(0.72, 0.52, 0.28, 1), 
                  ring_color=(0.45, 0.28, 0.12, 1),
                  scale=8.0, roughness=0.65):
    """Create a procedural wood material using noise + wave textures."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Output
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (600, 0)

    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Roughness'].default_value = roughness
    links.new(bsdf.outputs[0], out.inputs[0])

    # Color Ramp for wood grain
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (50, 0)
    ramp.color_ramp.elements[0].color = base_color
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[1].color = ring_color
    ramp.color_ramp.elements[1].position = 0.6
    links.new(ramp.outputs[0], bsdf.inputs['Base Color'])

    # Wave texture for grain lines
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-200, 0)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = scale
    wave.inputs['Distortion'].default_value = 4.0
    wave.inputs['Detail'].default_value = 3.0
    wave.inputs['Detail Scale'].default_value = 1.5
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])

    # Noise for variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-450, -100)
    noise.inputs['Scale'].default_value = 3.0
    noise.inputs['Detail'].default_value = 6.0

    # Mix coordinates with noise for natural look
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (-350, 50)
    mix.inputs['Fac'].default_value = 0.15

    coord = nodes.new('ShaderNodeTexCoord')
    coord.location = (-650, 0)
    links.new(coord.outputs['Object'], mix.inputs['Color1'])
    links.new(noise.outputs['Color'], mix.inputs['Color2'])
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(mix.outputs[0], wave.inputs['Vector'])

    # Bump for surface detail
    bump = nodes.new('ShaderNodeBump')
    bump.location = (100, -200)
    bump.inputs['Strength'].default_value = 0.15
    links.new(wave.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs[0], bsdf.inputs['Normal'])

    return mat

def make_glass_mat(name, tint=(0.85, 0.92, 0.96, 1)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (400, 0)
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.location = (150, 0)
    glass.inputs['Color'].default_value = tint
    glass.inputs['Roughness'].default_value = 0.02
    glass.inputs['IOR'].default_value = 1.45
    links.new(glass.outputs[0], out.inputs[0])
    # Set blend mode for Eevee transparency
    mat.use_backface_culling = True
    try:
        mat.blend_method = 'BLEND'
        mat.shadow_method = 'NONE'
    except:
        pass
    return mat

def make_simple_mat(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat


# ═══════════════════════════════════════════════════════════
# GEOMETRY
# ═══════════════════════════════════════════════════════════
def build_barrel(mats):
    """Hollow barrel with stave-count vertices."""
    outer_r = BARREL_RADIUS
    inner_r = BARREL_RADIUS - STAVE_THICKNESS
    half_len = BARREL_LENGTH / 2

    # Outer shell
    bpy.ops.mesh.primitive_cylinder_add(
        radius=outer_r, depth=BARREL_LENGTH,
        vertices=STAVE_COUNT,
        location=(0, 0, outer_r),
        rotation=(0, math.pi/2, 0)
    )
    barrel = bpy.context.active_object
    barrel.name = 'barrel_body'

    # Inner void
    bpy.ops.mesh.primitive_cylinder_add(
        radius=inner_r, depth=BARREL_LENGTH + 0.02,
        vertices=STAVE_COUNT,
        location=(0, 0, outer_r),
        rotation=(0, math.pi/2, 0)
    )
    void = bpy.context.active_object
    apply_bool(barrel, void)

    smooth(barrel)
    barrel.data.materials.append(mats['wood_ext'])
    to_collection(barrel, 'Barrel')
    return barrel


def build_end_wall(mats, x, name, door_hole=False):
    """Circular end wall disc."""
    r = BARREL_RADIUS - STAVE_THICKNESS - 0.005
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=STAVE_THICKNESS,
        vertices=48,
        location=(x, 0, BARREL_RADIUS),
        rotation=(0, math.pi/2, 0)
    )
    wall = bpy.context.active_object
    wall.name = name

    if door_hole:
        # Door opening centered at bottom-center of circle
        door_center_z = STAVE_THICKNESS + DOOR_HEIGHT / 2
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x, 0, door_center_z),
            scale=(STAVE_THICKNESS + 0.02, DOOR_WIDTH, DOOR_HEIGHT)
        )
        cut = bpy.context.active_object
        apply_bool(wall, cut)

    smooth(wall)
    wall.data.materials.append(mats['wood_int'])
    to_collection(wall, 'Barrel')
    return wall


def build_door(mats, name, style):
    """Build a swappable door at the front wall."""
    x = BARREL_LENGTH / 2
    door_center_z = STAVE_THICKNESS + DOOR_HEIGHT / 2

    if style == 'wooden':
        # Solid wooden door
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x + 0.001, 0, door_center_z),
            scale=(DOOR_THICKNESS, DOOR_WIDTH - 0.02, DOOR_HEIGHT - 0.02)
        )
        door = bpy.context.active_object
        door.name = name
        door.data.materials.append(mats['wood_int'])

        # Small glass window
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x + 0.005, 0, door_center_z + DOOR_HEIGHT * 0.25),
            scale=(DOOR_THICKNESS + 0.01, 0.30, 0.30)
        )
        win = bpy.context.active_object
        win.name = name + '_window'
        win.data.materials.append(mats['glass'])
        to_collection(win, 'Doors')

    elif style == 'fullglass':
        # Full glass panel with thin wood frame
        # Frame
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x + 0.001, 0, door_center_z),
            scale=(DOOR_THICKNESS, DOOR_WIDTH - 0.02, DOOR_HEIGHT - 0.02)
        )
        frame = bpy.context.active_object
        frame.name = name + '_frame'
        frame.data.materials.append(mats['wood_int'])
        to_collection(frame, 'Doors')

        # Glass center
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x + 0.005, 0, door_center_z),
            scale=(DOOR_THICKNESS + 0.01, DOOR_WIDTH - 0.10, DOOR_HEIGHT - 0.10)
        )
        door = bpy.context.active_object
        door.name = name
        door.data.materials.append(mats['glass'])

    elif style == 'panoramic':
        # Wide panoramic glass
        pw = DOOR_WIDTH * 1.3
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x + 0.001, 0, door_center_z),
            scale=(DOOR_THICKNESS, pw, DOOR_HEIGHT - 0.02)
        )
        door = bpy.context.active_object
        door.name = name
        door.data.materials.append(mats['glass'])

    to_collection(door, 'Doors')
    return door


def build_benches(mats):
    """Interior L and R benches at two heights."""
    bench_len = BARREL_LENGTH * 0.80
    inner_r = BARREL_RADIUS - STAVE_THICKNESS

    for side, sign in [('left', -1), ('right', 1)]:
        # Lower bench
        y = sign * 0.30
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(0, y, BENCH_HEIGHT_LOW),
            scale=(bench_len, BENCH_DEPTH, BENCH_THICKNESS)
        )
        b = bpy.context.active_object
        b.name = f'bench_{side}_low'
        b.data.materials.append(mats['wood_bench'])
        to_collection(b, 'Interior')

        # Upper bench (narrower, higher)
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(0, y, BENCH_HEIGHT_HIGH),
            scale=(bench_len, BENCH_DEPTH * 0.8, BENCH_THICKNESS)
        )
        bu = bpy.context.active_object
        bu.name = f'bench_{side}_high'
        bu.data.materials.append(mats['wood_bench'])
        to_collection(bu, 'Interior')

    # Floor planking
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(0, 0, STAVE_THICKNESS),
        scale=(BARREL_LENGTH * 0.90, inner_r * 1.2, 0.025)
    )
    floor = bpy.context.active_object
    floor.name = 'floor_planks'
    floor.data.materials.append(mats['wood_bench'])
    to_collection(floor, 'Interior')


def build_heater(mats, name, style):
    x = -BARREL_LENGTH / 2 + 0.35
    base_z = STAVE_THICKNESS + 0.01

    if style == 'harvia':
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.16, depth=0.45, vertices=16,
            location=(x, 0, base_z + 0.225)
        )
        h = bpy.context.active_object
        h.name = name
        h.data.materials.append(mats['heater'])
        smooth(h)
        to_collection(h, 'Heaters')

        # Stones
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=0.14, subdivisions=2,
            location=(x, 0, base_z + 0.50)
        )
        s = bpy.context.active_object
        s.name = name + '_stones'
        s.scale.z = 0.5
        s.data.materials.append(mats['stone'])
        to_collection(s, 'Heaters')

    elif style == 'huum':
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.20,
            location=(x, 0, base_z + 0.30)
        )
        h = bpy.context.active_object
        h.name = name
        h.data.materials.append(mats['heater'])
        smooth(h)
        to_collection(h, 'Heaters')

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.06, depth=0.18, vertices=12,
            location=(x, 0, base_z + 0.09)
        )
        p = bpy.context.active_object
        p.name = name + '_base'
        p.data.materials.append(mats['metal'])
        to_collection(p, 'Heaters')

    return h


def build_roof(mats, name, style):
    """Curved roof shell on top of barrel."""
    arc = math.radians(130)
    r = BARREL_RADIUS + 0.012
    segs_u, segs_v = 32, 10

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    cols = segs_u + 1
    for j in range(segs_v + 1):
        x = -BARREL_LENGTH / 2 + (j / segs_v) * BARREL_LENGTH
        for i in range(cols):
            a = math.pi/2 - arc/2 + (i / segs_u) * arc
            y = r * math.cos(a)
            z = r * math.sin(a) + BARREL_RADIUS
            bm.verts.new((x, y, z))

    bm.verts.ensure_lookup_table()
    for j in range(segs_v):
        for i in range(segs_u):
            idx = j * cols + i
            bm.faces.new([
                bm.verts[idx], bm.verts[idx+1],
                bm.verts[idx+1+cols], bm.verts[idx+cols]
            ])

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Solidify
    sol = obj.modifiers.new('Solid', 'SOLIDIFY')
    sol.thickness = 0.012
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier='Solid')
    obj.select_set(False)

    mat = mats['shingles'] if style == 'shingles' else mats['metal_roof']
    obj.data.materials.append(mat)
    smooth(obj)
    to_collection(obj, 'Roof')
    return obj


def build_supports(mats):
    """Two cradle supports under the barrel."""
    for x in [-BARREL_LENGTH * 0.30, BARREL_LENGTH * 0.30]:
        # Create arc support
        w = 0.12
        bpy.ops.mesh.primitive_cylinder_add(
            radius=BARREL_RADIUS + 0.04, depth=w,
            vertices=32, location=(x, 0, BARREL_RADIUS),
            rotation=(0, math.pi/2, 0)
        )
        sup = bpy.context.active_object

        # Cut top half
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x, 0, BARREL_RADIUS * 1.5 + 0.1),
            scale=(w + 0.05, BARREL_RADIUS * 3, BARREL_RADIUS + 0.2)
        )
        apply_bool(sup, bpy.context.active_object)

        # Hollow inside
        bpy.ops.mesh.primitive_cylinder_add(
            radius=BARREL_RADIUS - 0.01, depth=w + 0.02,
            vertices=32, location=(x, 0, BARREL_RADIUS),
            rotation=(0, math.pi/2, 0)
        )
        apply_bool(sup, bpy.context.active_object)

        # Flat bottom
        bpy.ops.mesh.primitive_cube_add(size=1,
            location=(x, 0, -0.25),
            scale=(w + 0.05, BARREL_RADIUS * 3, 0.5)
        )
        apply_bool(sup, bpy.context.active_object)

        sup.name = 'support_leg'
        sup.data.materials.append(mats['wood_ext'])
        to_collection(sup, 'Supports')


def build_bands(mats):
    """Metal bands around barrel."""
    positions = [-1.2, -0.5, 0.5, 1.2]
    for i, x in enumerate(positions):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=BARREL_RADIUS + 0.003,
            minor_radius=0.006,
            major_segments=48, minor_segments=8,
            location=(x, 0, BARREL_RADIUS),
            rotation=(0, math.pi/2, 0)
        )
        b = bpy.context.active_object
        b.name = f'metal_band_{i}'
        b.data.materials.append(mats['metal'])
        to_collection(b, 'Barrel')


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
print("=== BARREL SAUNA v2 ===")
clear_scene()

# Materials
print("Creating materials...")
mats = {
    'wood_ext':   make_wood_mat('Wood_Exterior',
                    base_color=(0.76, 0.58, 0.35, 1),
                    ring_color=(0.52, 0.35, 0.15, 1), scale=10),
    'wood_int':   make_wood_mat('Wood_Interior',
                    base_color=(0.68, 0.48, 0.26, 1),
                    ring_color=(0.40, 0.25, 0.10, 1), scale=12),
    'wood_bench': make_wood_mat('Wood_Bench',
                    base_color=(0.80, 0.62, 0.38, 1),
                    ring_color=(0.58, 0.38, 0.18, 1), scale=6),
    'glass':      make_glass_mat('Glass'),
    'metal':      make_simple_mat('Metal', (0.30, 0.30, 0.32, 1), 0.30, 0.9),
    'heater':     make_simple_mat('Heater', (0.08, 0.08, 0.08, 1), 0.45, 0.7),
    'stone':      make_simple_mat('Stone',  (0.42, 0.42, 0.40, 1), 0.90, 0.0),
    'shingles':   make_simple_mat('Shingles', (0.12, 0.12, 0.12, 1), 0.85, 0.0),
    'metal_roof': make_simple_mat('MetalRoof', (0.35, 0.38, 0.40, 1), 0.35, 0.8),
}

# Build
print("Building barrel...")
build_barrel(mats)

print("Building end walls...")
build_end_wall(mats, BARREL_LENGTH/2, 'front_wall', door_hole=True)
build_end_wall(mats, -BARREL_LENGTH/2, 'back_wall')

print("Building doors...")
d_wood = build_door(mats, 'door_wooden', 'wooden')
d_glass = build_door(mats, 'door_fullglass', 'fullglass')
d_pano = build_door(mats, 'door_panoramic', 'panoramic')
d_glass.hide_set(True); d_glass.hide_render = True
d_pano.hide_set(True); d_pano.hide_render = True
# Hide fullglass frame too
fg_frame = bpy.data.objects.get('door_fullglass_frame')
if fg_frame:
    fg_frame.hide_set(True); fg_frame.hide_render = True

print("Building benches...")
build_benches(mats)

print("Building heaters...")
h1 = build_heater(mats, 'heater_harvia', 'harvia')
h2 = build_heater(mats, 'heater_huum', 'huum')
h2.hide_set(True); h2.hide_render = True
# Hide huum base
hb = bpy.data.objects.get('heater_huum_base')
if hb:
    hb.hide_set(True); hb.hide_render = True

print("Building roof...")
build_roof(mats, 'roof_shingles', 'shingles')
build_roof(mats, 'roof_metal', 'metal')
bpy.data.objects['roof_metal'].hide_set(True)
bpy.data.objects['roof_metal'].hide_render = True

print("Building supports...")
build_supports(mats)

print("Building bands...")
build_bands(mats)

# Deselect all
bpy.ops.object.select_all(action='DESELECT')

print(f"\nDone! {len(bpy.context.scene.objects)} objects created.")
print(f"Collections: {[c.name for c in bpy.data.collections]}")

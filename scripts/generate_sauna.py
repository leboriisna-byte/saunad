"""
Barrel Sauna 3D Model Generator for Tesler.ee Configurator
===========================================================
Generates a complete barrel sauna model with named, swappable parts.
Sent to Blender via MCP socket connection.

Dimensions based on Tesler 3.3m barrel sauna specifications:
- Overall length: 3300mm
- Barrel diameter: 2050mm  (radius 1025mm)
- Stave width: ~90mm
- Stave thickness: 42mm
"""
import bpy
import math
import bmesh

# ═══════════════════════════════════════════════════════════
# CONFIGURATION — All dimensions in METERS (Blender units)
# ═══════════════════════════════════════════════════════════
BARREL_LENGTH   = 3.300     # 3300mm
BARREL_RADIUS   = 1.025     # 2050mm diameter / 2
STAVE_THICKNESS = 0.042     # 42mm
STAVE_WIDTH     = 0.090     # ~90mm
STAVE_COUNT     = 36        # Number of staves around barrel

DOOR_WIDTH      = 0.700     # 700mm opening
DOOR_HEIGHT     = 1.650     # 1650mm opening
DOOR_THICKNESS  = 0.042     # Same as stave

BENCH_DEPTH     = 0.500     # 500mm
BENCH_THICKNESS = 0.042     # Plank thickness
BENCH_HEIGHT    = 0.450     # 450mm from floor

SUPPORT_WIDTH   = 0.150     # Support cradle width
SUPPORT_THICK   = 0.060     # Support thickness

FLOOR_Y         = -BARREL_RADIUS + STAVE_THICKNESS  # Interior floor level

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

def create_material(name, color, roughness=0.7, metallic=0.0):
    """Create a simple PBR material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

def assign_material(obj, mat):
    """Assign material to object."""
    obj.data.materials.append(mat)

def set_smooth(obj):
    """Set smooth shading on an object."""
    for poly in obj.data.polygons:
        poly.use_smooth = True

def move_to_collection(obj, collection_name):
    """Move object to a named collection, creating it if needed."""
    if collection_name not in bpy.data.collections:
        col = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(col)
    else:
        col = bpy.data.collections[collection_name]

    # Unlink from current collections
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)

# ═══════════════════════════════════════════════════════════
# MATERIALS
# ═══════════════════════════════════════════════════════════

def create_materials():
    """Create all materials used in the sauna."""
    mats = {}
    # Light pine wood (staves, exterior)
    mats['wood_light']    = create_material('Wood_Light',    (0.76, 0.58, 0.36, 1), 0.65)
    # Darker pine (end walls, interior)
    mats['wood_dark']     = create_material('Wood_Dark',     (0.62, 0.42, 0.22, 1), 0.60)
    # Interior cedar tone
    mats['wood_interior'] = create_material('Wood_Interior', (0.72, 0.50, 0.30, 1), 0.55)
    # Glass for doors
    mats['glass']         = create_material('Glass',         (0.85, 0.92, 0.95, 0.3), 0.05)
    mats['glass'].blend_method = 'BLEND' if hasattr(mats['glass'], 'blend_method') else None
    # Metal bands
    mats['metal']         = create_material('Metal_Band',    (0.25, 0.25, 0.28, 1), 0.35, 0.9)
    # Roof shingles
    mats['shingles']      = create_material('Roof_Shingles', (0.15, 0.15, 0.15, 1), 0.85)
    # Metal roof
    mats['metal_roof']    = create_material('Roof_Metal',    (0.35, 0.38, 0.40, 1), 0.40, 0.8)
    # Heater body
    mats['heater']        = create_material('Heater',        (0.10, 0.10, 0.10, 1), 0.50, 0.7)
    # Stone
    mats['stone']         = create_material('Stone',         (0.40, 0.40, 0.40, 1), 0.90)
    # Door frame
    mats['frame']         = create_material('Door_Frame',    (0.55, 0.35, 0.18, 1), 0.60)
    return mats


# ═══════════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════════

def build_barrel_body(mats):
    """
    Create the barrel shell from individual stave-like segments.
    Uses a thick-walled cylinder approach for performance.
    """
    # Outer cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=BARREL_RADIUS,
        depth=BARREL_LENGTH,
        vertices=STAVE_COUNT,
        location=(0, 0, BARREL_RADIUS),
        rotation=(0, math.pi/2, 0)
    )
    outer = bpy.context.active_object
    outer.name = 'barrel_body'

    # Create inner void (boolean subtract)
    inner_radius = BARREL_RADIUS - STAVE_THICKNESS
    bpy.ops.mesh.primitive_cylinder_add(
        radius=inner_radius,
        depth=BARREL_LENGTH + 0.01,  # Slightly longer for clean boolean
        vertices=STAVE_COUNT,
        location=(0, 0, BARREL_RADIUS),
        rotation=(0, math.pi/2, 0)
    )
    inner = bpy.context.active_object
    inner.name = '_inner_void'

    # Boolean difference
    bool_mod = outer.modifiers.new(name='Hollow', type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = inner
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier='Hollow')

    # Delete the inner void helper
    bpy.data.objects.remove(inner, do_unlink=True)

    # Cut the bottom flat (remove the lower part so it sits on ground)
    # Create a cutting box below the floor line
    cut_height = BARREL_RADIUS * 0.15  # Cut about 15% from bottom
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, -cut_height/2),
        scale=(BARREL_LENGTH + 0.1, BARREL_RADIUS * 2.2, cut_height)
    )
    cutter = bpy.context.active_object
    cutter.name = '_bottom_cutter'

    bool_cut = outer.modifiers.new(name='FlatBottom', type='BOOLEAN')
    bool_cut.operation = 'DIFFERENCE'
    bool_cut.object = cutter
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier='FlatBottom')
    bpy.data.objects.remove(cutter, do_unlink=True)

    set_smooth(outer)
    assign_material(outer, mats['wood_light'])
    move_to_collection(outer, 'Barrel')
    return outer


def build_end_wall(mats, x_pos, name, has_door_cutout=False):
    """Create a circular end wall (optionally with door cutout)."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=BARREL_RADIUS - STAVE_THICKNESS - 0.005,
        depth=STAVE_THICKNESS,
        vertices=48,
        location=(x_pos, 0, BARREL_RADIUS),
        rotation=(0, math.pi/2, 0)
    )
    wall = bpy.context.active_object
    wall.name = name

    if has_door_cutout:
        # Create door opening
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x_pos, 0, BARREL_RADIUS * 0.5 + 0.1),
            scale=(STAVE_THICKNESS + 0.02, DOOR_WIDTH, DOOR_HEIGHT)
        )
        door_cut = bpy.context.active_object
        door_cut.name = '_door_cutout'

        bool_mod = wall.modifiers.new(name='DoorCut', type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = door_cut
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier='DoorCut')
        bpy.data.objects.remove(door_cut, do_unlink=True)

    set_smooth(wall)
    assign_material(wall, mats['wood_dark'])
    move_to_collection(wall, 'Barrel')
    return wall


def build_door(mats, name, door_type='wooden'):
    """
    Create a door mesh at the front end wall position.
    door_type: 'wooden', 'fullglass', or 'panoramic'
    """
    x_pos = BARREL_LENGTH / 2

    if door_type == 'wooden':
        # Solid wooden door with small window
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x_pos + STAVE_THICKNESS/2, 0, BARREL_RADIUS * 0.5 + 0.1),
            scale=(DOOR_THICKNESS, DOOR_WIDTH - 0.02, DOOR_HEIGHT - 0.02)
        )
        door = bpy.context.active_object
        door.name = name
        assign_material(door, mats['wood_dark'])

        # Small window in door
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x_pos + STAVE_THICKNESS/2 + 0.001, 0, BARREL_RADIUS * 0.7),
            scale=(DOOR_THICKNESS + 0.005, 0.25, 0.25)
        )
        window = bpy.context.active_object
        window.name = f'{name}_window'
        assign_material(window, mats['glass'])
        move_to_collection(window, 'Doors')

    elif door_type == 'fullglass':
        # Full glass door with wooden frame
        # Frame
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x_pos + STAVE_THICKNESS/2, 0, BARREL_RADIUS * 0.5 + 0.1),
            scale=(DOOR_THICKNESS, DOOR_WIDTH - 0.02, DOOR_HEIGHT - 0.02)
        )
        door = bpy.context.active_object
        door.name = name
        assign_material(door, mats['glass'])

    elif door_type == 'panoramic':
        # Wide panoramic glass door
        panoramic_width = DOOR_WIDTH * 1.4
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x_pos + STAVE_THICKNESS/2, 0, BARREL_RADIUS * 0.5 + 0.1),
            scale=(DOOR_THICKNESS, panoramic_width, DOOR_HEIGHT - 0.02)
        )
        door = bpy.context.active_object
        door.name = name
        assign_material(door, mats['glass'])

    move_to_collection(door, 'Doors')
    return door


def build_benches(mats):
    """Create interior benches on both sides."""
    inner_r = BARREL_RADIUS - STAVE_THICKNESS - 0.01
    bench_length = BARREL_LENGTH * 0.85  # Slightly shorter than barrel

    for side, y_sign in [('left', -1), ('right', 1)]:
        # Main bench plank
        y_pos = y_sign * (BENCH_DEPTH / 2 + 0.05)
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, y_pos, BENCH_HEIGHT + BARREL_RADIUS * 0.15),
            scale=(bench_length, BENCH_DEPTH, BENCH_THICKNESS)
        )
        bench = bpy.context.active_object
        bench.name = f'bench_{side}'

        assign_material(bench, mats['wood_interior'])
        move_to_collection(bench, 'Interior')

        # Bench support legs (2 per side)
        for x_off in [-bench_length * 0.3, bench_length * 0.3]:
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(x_off, y_pos, BENCH_HEIGHT / 2 + BARREL_RADIUS * 0.15 - 0.05),
                scale=(0.05, 0.05, BENCH_HEIGHT)
            )
            leg = bpy.context.active_object
            leg.name = f'bench_{side}_leg'
            assign_material(leg, mats['wood_interior'])
            move_to_collection(leg, 'Interior')


def build_heater(mats, name, heater_type='harvia'):
    """Create a heater mesh."""
    # Position near the back wall
    x_pos = -BARREL_LENGTH / 2 + 0.3

    if heater_type == 'harvia':
        # Harvia-style cylindrical heater
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.18,
            depth=0.50,
            vertices=16,
            location=(x_pos, 0, 0.25 + BARREL_RADIUS * 0.15)
        )
        heater = bpy.context.active_object
        heater.name = name
        assign_material(heater, mats['heater'])

        # Stone basket on top
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.15,
            location=(x_pos, 0, 0.55 + BARREL_RADIUS * 0.15)
        )
        stones = bpy.context.active_object
        stones.name = f'{name}_stones'
        stones.scale = (1, 1, 0.6)
        assign_material(stones, mats['stone'])
        move_to_collection(stones, 'Heaters')

    elif heater_type == 'huum':
        # Huum-style modern spherical heater
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.22,
            location=(x_pos, 0, 0.35 + BARREL_RADIUS * 0.15)
        )
        heater = bpy.context.active_object
        heater.name = name
        assign_material(heater, mats['heater'])

        # Thin pedestal
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.08,
            depth=0.20,
            vertices=16,
            location=(x_pos, 0, 0.10 + BARREL_RADIUS * 0.15)
        )
        pedestal = bpy.context.active_object
        pedestal.name = f'{name}_pedestal'
        assign_material(pedestal, mats['metal'])
        move_to_collection(pedestal, 'Heaters')

    set_smooth(heater)
    move_to_collection(heater, 'Heaters')
    return heater


def build_roof(mats, name, roof_type='shingles'):
    """Create a roof cover on top of the barrel."""
    # Roof is a curved shell sitting on the top portion of the barrel
    # Approximate with a flattened cylinder arc
    arc_angle = math.radians(120)  # Cover top 120 degrees
    roof_radius = BARREL_RADIUS + 0.015  # Slightly above barrel

    # Create using bmesh for precise arc control
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    segments = 24
    length_segments = 8

    for j in range(length_segments + 1):
        x = -BARREL_LENGTH / 2 + (j / length_segments) * BARREL_LENGTH
        for i in range(segments + 1):
            angle = math.pi/2 - arc_angle/2 + (i / segments) * arc_angle
            y = roof_radius * math.cos(angle)
            z = roof_radius * math.sin(angle) + BARREL_RADIUS
            bm.verts.new((x, y, z))

    bm.verts.ensure_lookup_table()

    # Create faces
    cols = segments + 1
    for j in range(length_segments):
        for i in range(segments):
            v1 = bm.verts[j * cols + i]
            v2 = bm.verts[j * cols + i + 1]
            v3 = bm.verts[(j + 1) * cols + i + 1]
            v4 = bm.verts[(j + 1) * cols + i]
            bm.faces.new([v1, v2, v3, v4])

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    if roof_type == 'shingles':
        assign_material(obj, mats['shingles'])
    else:
        assign_material(obj, mats['metal_roof'])

    # Add solidify modifier for thickness
    solid = obj.modifiers.new(name='Thickness', type='SOLIDIFY')
    solid.thickness = 0.015
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier='Thickness')
    obj.select_set(False)

    set_smooth(obj)
    move_to_collection(obj, 'Roof')
    return obj


def build_support_legs(mats):
    """Create wooden cradle/support legs."""
    for x_pos in [-BARREL_LENGTH * 0.3, BARREL_LENGTH * 0.3]:
        # Curved cradle piece (approximated with a thick arc)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=BARREL_RADIUS + 0.05,
            depth=SUPPORT_WIDTH,
            vertices=32,
            location=(x_pos, 0, BARREL_RADIUS),
            rotation=(0, math.pi/2, 0)
        )
        cradle = bpy.context.active_object

        # Cut the top half off to make a U-shape cradle
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x_pos, 0, BARREL_RADIUS + BARREL_RADIUS/2 + 0.1),
            scale=(SUPPORT_WIDTH + 0.1, BARREL_RADIUS * 3, BARREL_RADIUS)
        )
        cutter = bpy.context.active_object

        bool_mod = cradle.modifiers.new(name='TopCut', type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cutter
        bpy.context.view_layer.objects.active = cradle
        bpy.ops.object.modifier_apply(modifier='TopCut')
        bpy.data.objects.remove(cutter, do_unlink=True)

        # Also cut inner part to make it hollow
        bpy.ops.mesh.primitive_cylinder_add(
            radius=BARREL_RADIUS - 0.02,
            depth=SUPPORT_WIDTH + 0.02,
            vertices=32,
            location=(x_pos, 0, BARREL_RADIUS),
            rotation=(0, math.pi/2, 0)
        )
        inner_cut = bpy.context.active_object

        bool_mod2 = cradle.modifiers.new(name='InnerCut', type='BOOLEAN')
        bool_mod2.operation = 'DIFFERENCE'
        bool_mod2.object = inner_cut
        bpy.context.view_layer.objects.active = cradle
        bpy.ops.object.modifier_apply(modifier='InnerCut')
        bpy.data.objects.remove(inner_cut, do_unlink=True)

        # Cut bottom flat
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x_pos, 0, -0.3),
            scale=(SUPPORT_WIDTH + 0.1, BARREL_RADIUS * 3, 0.5)
        )
        bottom_cut = bpy.context.active_object

        bool_mod3 = cradle.modifiers.new(name='BottomCut', type='BOOLEAN')
        bool_mod3.operation = 'DIFFERENCE'
        bool_mod3.object = bottom_cut
        bpy.context.view_layer.objects.active = cradle
        bpy.ops.object.modifier_apply(modifier='BottomCut')
        bpy.data.objects.remove(bottom_cut, do_unlink=True)

        cradle.name = 'support_leg'
        assign_material(cradle, mats['wood_dark'])
        move_to_collection(cradle, 'Supports')


def build_metal_bands(mats):
    """Create decorative metal bands around the barrel."""
    band_positions = [-BARREL_LENGTH * 0.35, -BARREL_LENGTH * 0.1,
                      BARREL_LENGTH * 0.1, BARREL_LENGTH * 0.35]
    for i, x_pos in enumerate(band_positions):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=BARREL_RADIUS + 0.005,
            minor_radius=0.008,
            major_segments=48,
            minor_segments=8,
            location=(x_pos, 0, BARREL_RADIUS),
            rotation=(0, math.pi/2, 0)
        )
        band = bpy.context.active_object
        band.name = f'metal_band_{i}'
        assign_material(band, mats['metal'])
        move_to_collection(band, 'Barrel')


# ═══════════════════════════════════════════════════════════
# MAIN BUILD
# ═══════════════════════════════════════════════════════════

print("========================================")
print("  BARREL SAUNA MODEL GENERATOR")
print("  Tesler.ee 3.3m Configurator")
print("========================================")

# Step 1: Clean the scene
print("Clearing scene...")
clear_scene()

# Step 2: Create all materials
print("Creating materials...")
mats = create_materials()

# Step 3: Build barrel body
print("Building barrel body...")
barrel = build_barrel_body(mats)

# Step 4: Build end walls
print("Building end walls...")
front_wall = build_end_wall(mats, BARREL_LENGTH/2, 'front_wall', has_door_cutout=True)
back_wall  = build_end_wall(mats, -BARREL_LENGTH/2, 'back_wall', has_door_cutout=False)

# Step 5: Build door variants (only 'wooden' visible by default)
print("Building door variants...")
door_wooden   = build_door(mats, 'door_wooden',   'wooden')
door_fullglass = build_door(mats, 'door_fullglass', 'fullglass')
door_panoramic = build_door(mats, 'door_panoramic', 'panoramic')
# Hide non-default variants
door_fullglass.hide_set(True)
door_fullglass.hide_render = True
door_panoramic.hide_set(True)
door_panoramic.hide_render = True

# Step 6: Build interior
print("Building interior benches...")
build_benches(mats)

# Step 7: Build heater variants
print("Building heater variants...")
heater_harvia = build_heater(mats, 'heater_harvia', 'harvia')
heater_huum   = build_heater(mats, 'heater_huum',  'huum')
heater_huum.hide_set(True)
heater_huum.hide_render = True

# Step 8: Build roof variants
print("Building roof variants...")
roof_shingles = build_roof(mats, 'roof_shingles', 'shingles')
roof_metal    = build_roof(mats, 'roof_metal',    'metal')
roof_metal.hide_set(True)
roof_metal.hide_render = True

# Step 9: Build support legs
print("Building support legs...")
build_support_legs(mats)

# Step 10: Build metal bands
print("Building metal bands...")
build_metal_bands(mats)

# Step 11: Set up camera and lighting
print("Setting up camera and lighting...")

# Camera
bpy.ops.object.camera_add(
    location=(4.5, -3.5, 2.5),
    rotation=(math.radians(65), 0, math.radians(52))
)
cam = bpy.context.active_object
cam.name = 'ConfiguratorCamera'
bpy.context.scene.camera = cam

# Sun light
bpy.ops.object.light_add(
    type='SUN',
    location=(3, -2, 5),
    rotation=(math.radians(45), math.radians(15), math.radians(30))
)
sun = bpy.context.active_object
sun.name = 'SunLight'
sun.data.energy = 3.0

# Finish
bpy.ops.object.select_all(action='DESELECT')
print("")
print("========================================")
print("  MODEL COMPLETE!")
print("========================================")
print(f"  Total objects: {len(bpy.context.scene.objects)}")
print(f"  Collections: {[c.name for c in bpy.data.collections]}")
print(f"  Materials: {len(bpy.data.materials)}")
print("")
obj_names = [o.name for o in bpy.context.scene.objects]
print(f"  Objects: {obj_names}")
print("========================================")

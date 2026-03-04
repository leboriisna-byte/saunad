# Quick test: clear the scene and create a simple cube to verify connection
import bpy

# Delete default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a test cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
obj = bpy.context.active_object
obj.name = "TEST_CONNECTION"

print(f"SUCCESS: Created object '{obj.name}' in Blender")
print(f"Scene objects: {[o.name for o in bpy.context.scene.objects]}")

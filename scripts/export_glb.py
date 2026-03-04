# List all objects and collections in the scene for verification
import bpy
import os

print("=== SCENE VERIFICATION ===")
print(f"Total objects: {len(bpy.context.scene.objects)}")
print("")

# List collections
print("COLLECTIONS:")
for col in bpy.data.collections:
    obj_names = [o.name for o in col.objects]
    print(f"  [{col.name}] ({len(obj_names)} objects): {obj_names}")

print("")
print("ALL OBJECTS:")
for obj in bpy.context.scene.objects:
    hidden = " [HIDDEN]" if obj.hide_get() else ""
    mats = [slot.material.name for slot in obj.material_slots if slot.material]
    print(f"  {obj.name} ({obj.type}){hidden} - materials: {mats}")

# Export GLB
print("")
print("=== EXPORTING GLB ===")
export_path = r"C:\Users\Raian\Desktop\saunapask\public\models\sauna_model.glb"
os.makedirs(os.path.dirname(export_path), exist_ok=True)

# Make all objects visible for export
hidden_objects = []
for obj in bpy.context.scene.objects:
    if obj.hide_get():
        hidden_objects.append(obj.name)
        obj.hide_set(False)

# Select all mesh objects for export
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type in ('MESH', 'EMPTY'):
        obj.select_set(True)

bpy.ops.export_scene.gltf(
    filepath=export_path,
    export_format='GLB',
    use_selection=False,
    export_apply=True,
    export_materials='EXPORT',
)

# Re-hide objects that were hidden
for name in hidden_objects:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_set(True)

file_size = os.path.getsize(export_path)
print(f"Exported to: {export_path}")
print(f"File size: {file_size / 1024:.1f} KB")
print("=== DONE ===")

import bpy
import sys
import os

argv = sys.argv
argv = argv[argv.index("--") + 1 :]

input_path = argv[0]
output_path = argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
ext = os.path.splitext(input_path)[1].lower()

if ext == ".obj":
    bpy.ops.wm.obj_import(filepath=input_path)
elif ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=input_path)
elif ext == ".blend":
    with bpy.data.libraries.load(input_path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)
else:
    print(f"Unsupported file format: {ext}")
    sys.exit(1)

for obj in bpy.context.scene.objects:
    obj.select_set(True)

bpy.ops.export_scene.gltf(filepath=output_path, export_format="GLB", export_apply=True)

print(f"Exported: {output_path}")

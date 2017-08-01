
from os.path import join, dirname
import bpy

blendfile = bpy.data.filepath
dir = join(dirname(blendfile), 'gradients')
mat = bpy.data.materials["Shadeless"]
tslot = mat.texture_slots[0]

for tex in bpy.data.textures:
    tslot.texture = tex
    filepath = join(dir, tex.name + ".png")
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
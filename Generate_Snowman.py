"""
Author = "Alex Combas"
Copyright = "Copyright (C) 2022 Alex Combas"
License = "GNU GPL"
Version = "0.1"

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import bpy, bmesh
from math import radians
from bmesh.types import BMVert

class MESH_OT_Generate_Snowman(bpy.types.Operator):
    """Generate a Snowman, uses the real_snow addon that comes with Blender"""
    bl_idname = "mesh.generate_snowman"
    bl_label = "Generate Snowman"
    bl_options = {'REGISTER', 'UNDO'}

    # turn on bloom and ambiant occlusion if using Eevee
    if (bpy.data.scenes['Scene'].render.engine == 'BLENDER_EEVEE'):
        bpy.data.scenes["Scene"].eevee.use_bloom = True
        bpy.data.scenes["Scene"].eevee.use_gtao = True

    #turn on real_snow addon
    bpy.ops.preferences.addon_enable(module="real_snow")

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def generate_arm(self):
        bpy.ops.mesh.primitive_cube_add(size=0.05)
        bpy.ops.object.mode_set(mode='EDIT')
        ao_d = bpy.context.active_object.data
        bm = bmesh.from_edit_mesh(ao_d)
        bm.faces.ensure_lookup_table()

        ext = bmesh.ops.extrude_face_region(bm, geom=[bm.faces[1]])
        bmesh.ops.translate(bm, vec=(0, 0.8, -0.2), verts=[v for v in ext["geom"] if isinstance(v, BMVert)])

        bm.faces.ensure_lookup_table()
        ext2 = bmesh.ops.extrude_face_region(bm, geom=[bm.faces[6]])
        bmesh.ops.translate(bm, vec=(0, 0.5, -0.7), verts=[v for v in ext2["geom"] if isinstance(v, BMVert)])

        bm.normal_update()
        bmesh.update_edit_mesh(ao_d, True, True)
        bpy.ops.object.mode_set(mode='OBJECT')

        ao = bpy.context.active_object
        ao.location = (0, 0, 2.2)

        ao.modifiers.new("My Mir", 'MIRROR')
        ao.modifiers["My Mir"].use_axis[0] = False
        ao.modifiers["My Mir"].use_axis[1] = True
        bpy.ops.object.modifier_apply(modifier="My Mir")

        if self.check_mat('Stick'):
            ao.data.materials.append(bpy.data.materials['Stick'])
        else:
            new_mat = bpy.data.materials.new(name="Stick")
            new_mat.diffuse_color = (0.1, 0.04, 0.01, 1)
            ao.data.materials.append(new_mat)



    def check_mat(self, name):
        if name in bpy.data.materials:
            return True
        return False

    def eye_of_coal(self, offset):
        bpy.ops.mesh.primitive_uv_sphere_add()
        bpy.ops.object.shade_smooth()
        ao = bpy.context.active_object
        ao.scale = (0.08, 0.08, 0.08)
        ao.location = (0.35, offset, 2.8)
        if self.check_mat('Coal'):
            ao.data.materials.append(bpy.data.materials['Coal'])
        else:
            new_mat = bpy.data.materials.new(name='Coal')
            new_mat.diffuse_color = (0, 0, 0, 1)
            ao.data.materials.append(new_mat)

    def carrot_nose(self):
        bpy.ops.mesh.primitive_cone_add()
        bpy.ops.object.shade_smooth()
        ao = bpy.context.active_object
        ao.scale = (0.08, 0.08, 0.3)
        ao.location = (0.6, 0, 2.7)
        ao.rotation_euler[1] = radians(90)
        if self.check_mat('Carrot'):
            ao.data.materials.append(bpy.data.materials['Carrot'])
        else:
            new_mat = bpy.data.materials.new(name="Carrot")
            new_mat.diffuse_color = (1, 0.25, 0, 1)
            ao.data.materials.append(new_mat)

    def execute(self, context):
        # create gound mesh and cover with snow
        bpy.ops.mesh.primitive_plane_add()
        ao = context.active_object
        ao.scale = (2, 2, 2)
        bpy.ops.snow.create()

        # magic numbers
        sb_location = 0.5
        sb_scale = 0.95
        sb_rotation = 45
        snow_balls = 0 

        # create three spheres, give them clouds displacement and move them around
        # append snow texture to each sphere, the snow texture comes from bpy.ops.snow.create()
        # index variable 'snow_balls' starts at zero so that it can also be used in rotation_euler 0, 1, 2
        while (snow_balls < 3):
            bpy.ops.mesh.primitive_uv_sphere_add()
            ao = context.active_object
            ao.location[2] = sb_location
            ao.rotation_euler[snow_balls] += radians(sb_rotation)
            ao.scale = (sb_scale, sb_scale, sb_scale)
            mod_subsurf = ao.modifiers.new("My Modifier", 'SUBSURF')
            mod_subsurf.levels = 2
            bpy.ops.object.shade_smooth()
            mod_displace = ao.modifiers.new("My Displacement", 'DISPLACE')

            # try to get the clouds texture, but if it doesn't exist then create it
            cloud_tex = bpy.data.textures.get('Clouds')
            if ( not cloud_tex):
                cloud_tex = bpy.data.textures.new(name='Clouds', type='CLOUDS')
                cloud_tex.noise_scale = 2.0
                mod_displace.texture = cloud_tex
            else:
                mod_displace.texture = bpy.data.textures['Clouds']

            ao.data.materials.append(bpy.data.materials['Snow'])
            snow_balls += 1
            sb_scale -= 0.2
            sb_location += 1.05

        # call class methods to create nose and eyes
        self.carrot_nose()
        self.eye_of_coal(0.1)
        self.eye_of_coal(-0.1)
        self.generate_arm()

        return {'FINISHED'}

def register():
    bpy.utils.register_class(MESH_OT_Generate_Snowman)

def unregister():
    bpy.utils.unregister_class(MESH_OT_Generate_Snowman)

if __name__ == '__main__':
    register()

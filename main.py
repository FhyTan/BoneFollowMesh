import bpy
import bpy_extras


bl_info = {
    "name": "Bone Follow Mesh",
    "author": "FhyTan",
    "version": (1, 0),
    "blender": (2, 93, 1),
    "location": "View3D > Sidebar > Edit Tab",
    "description": "A handy way to make cloth or soft body simulation to the bone",
    "warning": "",
    "doc_url": "https://github.com/FhyTan/BoneFollowMesh",
    "category": "Object",
}


class OBJECT_OT_bone_follow_mesh(bpy.types.Operator):
    bl_idname = "object.bone_follow_mesh"
    bl_label = "Bone Follow Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return isinstance(bpy.context.active_object.data, bpy.types.Armature)

    def execute(self, context):
        bone_vert_map = {}  # {bone.name: (head_vert_index, end_vert_index)}

        # create mesh
        mesh = bpy.data.meshes.new('Bone Mesh')
        verts = []
        edges = []

        obj = context.active_object
        armature = obj.data
        for bone in armature.bones:
            head_vert_index = 0
            if bone.parent is None:
                head_vert_index = len(verts)
                verts.append(bone.head_local + obj.location)
            else:
                head_vert_index = bone_vert_map[bone.parent.name][1]

            tail_vert_index = len(verts)
            verts.append(bone.tail_local + obj.location)

            bone_vert_map[bone.name] = (head_vert_index, tail_vert_index)
            edges.append(bone_vert_map[bone.name])

        mesh.from_pydata(verts, edges, [])
        mesh_object = bpy_extras.object_utils.object_data_add(context, mesh)

        # create vertex group
        vertex_groups = mesh_object.vertex_groups
        vertex_groups.clear()
        for i in range(len(verts)):
            si = str(i)
            vertex_groups.new(name=si)
            vertex_groups[si].add([i], 1, 'ADD')

        # create bone constraints
        for bone in obj.pose.bones:
            copy_location = bone.constraints.get(
                'Copy Location') or bone.constraints.new(type='COPY_LOCATION')
            copy_location.target = mesh_object
            copy_location.subtarget = str(bone_vert_map[bone.name][0])

            damped_track = bone.constraints.get(
                'Damped Track') or bone.constraints.new(type='DAMPED_TRACK')
            damped_track.target = mesh_object
            damped_track.subtarget = str(bone_vert_map[bone.name][1])

        return {'FINISHED'}


class OBJECT_PT_bone_follow_mesh(bpy.types.Panel):
    bl_idname = "OBJECT_PT_bone_follow_mesh"
    bl_label = "Bone Follow Mesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator('object.bone_follow_mesh')


def register():
    bpy.utils.register_class(OBJECT_OT_bone_follow_mesh)
    bpy.utils.register_class(OBJECT_PT_bone_follow_mesh)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_bone_follow_mesh)
    bpy.utils.unregister_class(OBJECT_PT_bone_follow_mesh)


if __name__ == "__main__":
    register()

import bpy
import re
import time
import json
import os
from math import radians

from bpy.types import Operator, Panel
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    CollectionProperty,
    EnumProperty
)

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper
)
from . import FixCSGO


class Import_Export_PT_QC_SMD_panel(Panel):
    bl_idname = "IMPORT_EXPORT_PT_QC_SMD_panel"
    bl_label = "QC and SMD"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "QC and SMD"

    def draw(self, context):
        layout = self.layout
        layout.operator("imp.qc_smd_")
        layout.operator("opr.make_camera")
        layout.operator("exp.fbx_ue")


def _pick_object(action):
    obj = bpy.context.object
    scene = bpy.context.scene

    if action == "pick_animation":
        scene.animation_skeleton = obj.name
    elif action == "pick_arms":
        scene.arms_skeleton = obj.name
    elif action == "pick_weapon":
        scene.weapon_skeleton = obj.name


class CCSGO_OT_pick_object(bpy.types.Operator):
    bl_idname = "arp.pick_object"
    bl_label = "pick_object"
    bl_options = {'UNDO'}

    action: bpy.props.EnumProperty(
        items=(
            ('pick_arms', 'pick_arms', ''),
            ('pick_weapon', 'pick_weapon', ''),
            ('pick_animation', 'pick_animation', ''),
        )
    )

    @classmethod
    def poll(cls, context):
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            _pick_object(self.action)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class Import_Export_PT_Constrains_panel(Panel):
    bl_idname = "IMPORT_EXPORT_PT_Constrains_panel"
    bl_label = "Constrains builder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "QC and SMD"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Arms:")
        row = layout.row(align=True)
        row.prop_search(scene, "arms_skeleton", bpy.data, "armatures", text="")
        row.operator("arp.pick_object", text="", icon='EYEDROPPER').action = 'pick_arms'

        layout.label(text="Weapon:")
        row = layout.row(align=True)
        row.prop_search(scene, "weapon_skeleton", bpy.data, "armatures", text="")
        row.operator("arp.pick_object", text="", icon='EYEDROPPER').action = 'pick_weapon'

        layout.label(text="Animation:")
        row = layout.row(align=True)
        row.prop_search(scene, "animation_skeleton", bpy.data, "armatures", text="")
        row.operator("arp.pick_object", text="", icon='EYEDROPPER').action = 'pick_animation'

        layout.row(align=True)

        col = layout.column(align=True)
        col.operator("opr.constrains_builder", text="Make constrains")


class Import_QC_SMD_(Operator, ImportHelper):
    bl_idname = "imp.qc_smd_"
    bl_label = "Import QC/SMD file"

    filename_ext = ""

    filepath: StringProperty(name="File Path", description="File filepath used for importing the SMD/VTA/DMX/QC file", maxlen=1024, default="", options={'HIDDEN'})
    files: CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN'})
    directory: StringProperty(maxlen=1024, default="", subtype='FILE_PATH', options={'HIDDEN'})
    filter_folder: BoolProperty(name="Filter Folders", description="", default=True, options={'HIDDEN'})
    filter_glob: StringProperty(default="*.smd;*.qc", options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        filepath = self.filepath
        fps = 30
        is_qc_file = filepath.endswith('.qc')

        if not is_qc_file:  # find fps values for animation in qc file
            smdfile_list_path = filepath.split('\\')
            qc_path = '\\'.join(smdfile_list_path[:-2])
            if qc_file := [q for q in os.listdir(qc_path) if q.endswith('.qc')]:
                qc_filepath = qc_path + '\\' + qc_file[0]
                if os.path.isfile(qc_filepath):
                    with open(qc_filepath) as file:
                        qc_lines = file.readlines()
                        for index, line in enumerate(qc_lines):
                            if smdfile_list_path[-1].replace('.smd', '') in line:
                                last_lines = qc_lines[index:]
                                fps_line = next(x for x in last_lines if 'fps' in x)
                                fps = int(fps_line.replace('	fps ', ''))
                                file.close()
                                break
            else:
                self.report({'ERROR'}, "Can't find fps")

        bpy.context.scene.render.fps = fps

        mesh_type = 'arms' if ('arms' in os.path.basename(filepath) or
                               'glove' in os.path.basename(filepath) or
                               'watch' in os.path.basename(filepath) or
                               'sleeve' in os.path.basename(filepath)) else ''

        # get previously imported objects and armatures
        scene_objects = list(bpy.data.objects)
        scene_armatures = list(bpy.data.armatures)

        if is_qc_file:
            bpy.ops.import_scene.smd(filepath=filepath, doAnim=False, append='NEW_ARMATURE')
            FixCSGO.v_model(filepath, is_animation=False, mtype=mesh_type, objects_to_ignore=scene_objects, armatures_to_ignore=scene_armatures)
        else:
            bpy.ops.import_scene.smd(filepath=filepath, doAnim=True, append='NEW_ARMATURE')
            FixCSGO.v_model(filepath, is_animation=True, mtype=mesh_type, objects_to_ignore=scene_objects, armatures_to_ignore=scene_armatures)

        return {'FINISHED'}

    def draw(self, context):
        pass


class Export_FBX_UE(Operator, ExportHelper):
    bl_idname = "exp.fbx_ue"
    bl_label = "Export selected"

    # ExportHelper mixin class uses this
    filename_ext = ""

    filepath: StringProperty(
        name="File Path",
        description="",
        maxlen=1024, default="", options={'HIDDEN'})
    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,
    )
    skeleton_name: StringProperty(
        name='Skeleton name',
        description='Skeleton name',
        default='root',
    )
    change_scale: FloatProperty(
        name='Export scale',
        description='Scales model',
        min=0.01, max=100000.0,
        soft_min=0.023, soft_max=100.0,
        default=0.023,
    )
    object_type: bpy.props.EnumProperty(  # type: ignore
        name="Type",
        description="Static or Animated object",
        items=(
            ('ANIMATION', "Animation", "Exports only animation"),
            ('MESH', "Mesh", "Exports mesh and animation")
        ),
        default='ANIMATION',
    )

    @classmethod
    def description(cls, context, properties):
        return "Exports a FBX file that can later be used in Unreal"

    def execute(self, context):
        def export(name, o_type):
            bpy.ops.export_scene.fbx(
                filepath=name,
                check_existing=True,
                use_selection=True,
                bake_anim=True,
                bake_anim_use_nla_strips=False,
                bake_anim_use_all_actions=False,
                bake_anim_simplify_factor=0,
                mesh_smooth_type='FACE',
                add_leaf_bones=False,
                object_types=o_type,
                global_scale=self.change_scale)

        if bpy.context.active_object and bpy.context.active_object.mode in ['POSE', 'EDIT']:
            bpy.ops.object.mode_set(mode='OBJECT')
        selected_obj = bpy.context.selected_objects[0]
        default_name = selected_obj.name
        for child in selected_obj.children:
            child.select_set(True)
        selected_obj.name = self.skeleton_name
        if self.object_type == 'ANIMATION':
            export(f'{self.filepath}.fbx', {'ARMATURE'})
        elif self.object_type == 'STATIC':
            export(f'{self.filepath}.fbx', {'MESH'})
        selected_obj.name = default_name  # revert name
        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}

    def draw(self, context):
        pass


class MENU_PT_export_fbx_qc_settings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Export settings"

    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXP_OT_fbx_ue"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        sfile = context.space_data
        operator = sfile.active_operator
        layout.prop(operator, 'skeleton_name')
        layout.prop(operator, "change_scale")
        layout.prop(operator, "object_type", expand=True)


class Constrains_Builder(Operator):
    bl_idname = "opr.constrains_builder"
    bl_label = "Make constrains"

    @classmethod
    def description(cls, context, properties):
        return "Apply animation to the arms and weapon"

    def execute(self, context):
        arms_skeleton = bpy.data.armatures.get(context.scene.arms_skeleton)
        weapon_skeleton = bpy.data.armatures.get(context.scene.weapon_skeleton)
        animation_skeleton = bpy.data.armatures.get(context.scene.animation_skeleton)

        if arms_skeleton is None or weapon_skeleton is None or animation_skeleton is None:
            self.report({'ERROR'}, 'Please choose all skeletons')
            return {'FINISHED'}

        arms_armature = arms_skeleton.name
        weapon_armature = weapon_skeleton.name
        animation_armature = animation_skeleton.name

        bone_list_arms_armature = [bone.name for bone in arms_skeleton.bones]
        bone_list_weapon_skeleton = [bone.name for bone in weapon_skeleton.bones]
        bone_list_animation_armature = [bone.name for bone in animation_skeleton.bones]
        cross_set_arms = set(bone_list_arms_armature) & set(bone_list_animation_armature)
        cross_set_weapon = set(bone_list_weapon_skeleton) & set(bone_list_animation_armature)

        print(f'\nbones in {arms_armature}: {len(bone_list_arms_armature)}, bones in {animation_armature}: {len(bone_list_animation_armature)}, same bones: {len(cross_set_arms)}')
        print(f'bones in {weapon_armature}: {len(bone_list_weapon_skeleton)}, bones in {animation_armature}: {len(bone_list_animation_armature)}, same bones: {len(cross_set_weapon)}')

        def constrains(armature_name, cross_set):
            for bone in cross_set:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.armatures[armature_name].bones[bone].select = 1
                bpy.ops.object.mode_set(mode='POSE')
                armature_pose = bpy.data.objects[armature_name].pose
                ik_bone_pose = armature_pose.bones[bone]
                pose_bones_constraints = ik_bone_pose.constraints

                pose_bones_constraints.new(type='COPY_TRANSFORMS')
                pose_bones_constraints['Copy Transforms'].target = bpy.data.objects[animation_armature]
                pose_bones_constraints['Copy Transforms'].subtarget = bone

                # print(f'binded {armature_name} {bone} to {animation_armature} {bone}')

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.armature.select_all(action='DESELECT')

        constrains(arms_armature, cross_set_arms)
        constrains(weapon_armature, cross_set_weapon)

        bpy.ops.object.mode_set(mode='POSE')
        return {'FINISHED'}

    def draw(self, context):
        pass


class Make_Camera(Operator):
    bl_idname = "opr.make_camera"
    bl_label = "Make FPV Camera"

    @classmethod
    def description(cls, context, properties):
        return "Create first-person camera"

    def execute(self, context):
        scn = bpy.context.scene

        # create the first camera
        camera = bpy.data.cameras.new("Camera")
        camera.lens = 16
        camera.display_size = 12.5

        # create the first camera object
        camera_obj = bpy.data.objects.new("FPV Camera", camera)
        camera_obj.location = (2, -2, 2)
        camera_obj.rotation_euler = (radians(-90), radians(180), 0)
        scn.collection.objects.link(camera_obj)

        return {'FINISHED'}

    def draw(self, context):
        pass


def register():
    bpy.types.Scene.arms_skeleton = bpy.props.StringProperty(name="Arms", default="", description="Source rig armature to take action from")
    bpy.types.Scene.weapon_skeleton = bpy.props.StringProperty(name="Weapon", default="", description="Source rig armature to take action from")
    bpy.types.Scene.animation_skeleton = bpy.props.StringProperty(name="Animation", default="", description="Destination armature to re-target the action")


def unregister():
    del bpy.types.Scene.arms_skeleton
    del bpy.types.Scene.weapon_skeleton
    del bpy.types.Scene.animation_skeleton

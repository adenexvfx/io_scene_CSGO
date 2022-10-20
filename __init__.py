import contextlib

bl_info = {
    "name": "io_scene_CSGO",
    "category": "Import-Export",
    "author": "adenex",
    "version": (1, 2, 71),
    "blender": (2, 90, 0),
    "description": "This tool can convert CS:GO's .QC files to .FBX, clean and export your scene",
    "location": "File > Import, Side Panel"
}

import bpy
import re
import time
import json
import os
from bpy.types import Operator, Panel
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    CollectionProperty,
)

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper
)
from . import Convert_QC
from . import FixCSGO


def menu_draw_convert(self, context):
    self.layout.operator("exp.qc_smd_cnv", text="Batch convert CSGO's QC files")


PROPS = [
    ('sp_float_value', bpy.props.FloatProperty(name="Float value", min=0.001, max=1000.0, default=0.0)),
    ('sp_bool_value', bpy.props.BoolProperty(name="Bool value", description="", default=False, )),
    ('sp_string_value', bpy.props.StringProperty(name='String value', description='', default='value', )),
    ('sp_int_value', bpy.props.IntProperty(name='Int value', description='', min=0, max=1000, soft_min=0, soft_max=1000, default=0, )),

    ('remove_w_knives', bpy.props.BoolProperty(name='Remove w_knives', default=True, description='Deletes all knives (except pov)')),
    ('remove_dropped_knives', bpy.props.BoolProperty(name='Remove *dropped* knives', default=True, description='Deletes all *dropped* knives')),
    ('remove_w_guns', bpy.props.BoolProperty(name='Remove w_guns', default=True, description='Deletes all guns (except pov)')),
    ('remove_dropped_guns', bpy.props.BoolProperty(name='Remove *dropped* guns', default=False, description='Deletes all *dropped* guns')),
    ('remove_w_pistols', bpy.props.BoolProperty(name='Remove w_pistols', default=True, description='Deletes all pistols (except pov)')),
    ('remove_dropped_pistols', bpy.props.BoolProperty(name='Remove *dropped* pistols', default=False, description='Deletes all *dropped* pistols')),
    ('remove_w_nades', bpy.props.BoolProperty(name='Remove nades', default=True, description='Deletes all grenades (except pov)')),
    ('remove_dropped_nades', bpy.props.BoolProperty(name='Remove *dropped* nades', default=True, description='Deletes all *dropped* grenades')),
    ('remove_w_c4', bpy.props.BoolProperty(name='Remove c4', default=False, description='Deletes c4 (except pov)')),
    ('remove_dropped_c4', bpy.props.BoolProperty(name='Remove *dropped* c4', default=False, description='Deletes *dropped* c4')),
    ('remove_pov', bpy.props.BoolProperty(name='Remove POV', default=False, description='Completely removes POV (viewmodels)')),
    ('remove_duplicates', bpy.props.BoolProperty(name='Remove duplicates', default=True, description='Removes all duplicated gloves and sleeves')),
    ('remove_misc', bpy.props.BoolProperty(name='Remove useless models', default=True, description='Removes stickers, defuser kits and stattrack models')),
    ('place_animations', bpy.props.BoolProperty(name='Place all animations at (0,0,0)', default=True, description='Prevents animations from appearing in other sequences. This option will take some time to process')),
    ('offset', bpy.props.IntProperty(name='Z Offset', default=-5)),
]


def all_objects():
    if bpy.context.active_object:
        if bpy.context.active_object.mode in ['POSE', 'EDIT']:
            bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    selected_anims = bpy.context.selected_objects
    armatures_list = []
    cameras_list = []
    for i in selected_anims:
        if i.type == 'ARMATURE':
            armatures_list.append(i)
        elif i.type == 'CAMERA':
            cameras_list.append(i)
    bpy.ops.object.select_all(action='DESELECT')
    return armatures_list, cameras_list


def diselect():
    arm_list = all_objects()[0]
    first_armature = arm_list[0]
    bpy.context.view_layer.objects.active = first_armature
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')


def fixer():  # fix bad naming
    diselect()
    for obj in bpy.context.scene.objects:
        if re.match(r'afx.\w+.\w+.+', obj.name):
            with contextlib.suppress(Exception):
                obj.name = re.sub(r'(afx.\w+.\w+)(.+)', r'\1.mdl', obj.name)


def remover(f_name, mesh_pattern_list, dropped=False):
    diselect()
    print(f'\nRemoving: {f_name}')

    def remover_helper():
        with contextlib.suppress(Exception):
            mesh.select_set(True)
            for child_mesh in mesh.children:
                child_mesh.select_set(True)
            print(f'Removed mesh: {mesh.name}')
            bpy.ops.object.delete()

    for pattern in mesh_pattern_list:
        for mesh in bpy.data.objects:
            if mesh.type == 'ARMATURE' and pattern in mesh.name:
                if dropped:
                    if 'dropped' in mesh.name:
                        remover_helper()
                else:
                    if 'dropped' not in mesh.name:
                        remover_helper()


def w_knives():
    remover('w_knives', ['w_knife_'])


def w_knives_dropped():
    remover('w_knives_dropped', ['w_knife_'], dropped=True)


def w_guns():
    remover('w_guns', ['w_rif_', 'w_mach_', 'w_shot_', 'w_smg_', 'w_snip_'])


def w_guns_dropped():
    remover('w_guns_dropped', ['w_rif_', 'w_mach_', 'w_shot_', 'w_smg_', 'w_snip_'], dropped=True)


def w_pistols():
    remover('w_pistols', ['w_pist_'])


def w_pistols_dropped():
    remover('w_pistols_dropped', ['w_pist_'], dropped=True)


def w_nades():
    remover('w_nades', ['w_eq_'])


def w_nades_dropped():
    remover('w_nades_dropped', ['w_eq_'], dropped=True)


def w_c4():
    remover('w_c4', ['w_ied'])


def w_c4_dropped():
    remover('w_c4_dropped', ['w_ied'], True)


def pov():
    remover('pov', ['v_'])


def duplicates():
    print(f'\nRemoving duplicates')

    def duplicate_finder(pattern_word):
        diselect()
        bpy.ops.object.select_all(action='SELECT')
        selected_anims = bpy.context.selected_objects
        arm_list = []
        sel_anims = []
        for i in selected_anims:
            if i.type == 'ARMATURE':
                arm_list.append(i)
        bpy.ops.object.select_all(action='DESELECT')
        for arm in arm_list:
            if pattern_word in arm.name:
                sel_anims.append(arm)
        print(f'\ntotal {pattern_word}: {len(sel_anims)}')
        if len(sel_anims) > 1:
            del_list = sel_anims[1:]
            print(f'Detected {len(del_list)} duplicates')
            for mesh in del_list:
                with contextlib.suppress(Exception):
                    mesh.select_set(True)
                    for child_mesh in mesh.children:
                        child_mesh.select_set(True)
                    print(f'Removed duplicate: {mesh.name}')
                    bpy.ops.object.delete()
        bpy.ops.object.select_all(action='DESELECT')

    duplicate_finder('v_glove')
    duplicate_finder('v_sleeve')


def misc():
    remover('misc', ['defuser', 'decal', 'sticker', 'uid', 'stattrack'])


def z_offset(name, value):
    bpy.data.objects[name].location.z = value


def anims_zero():
    print('\n\nCleaning done, now working with keyframes...')
    diselect()
    bpy.ops.object.select_pattern(pattern='*.mdl*', case_sensitive=False, extend=True)
    bpy.context.scene.frame_current = 1
    selected_anims = bpy.context.selected_objects
    sel_anims = [i.name for i in selected_anims]
    for a in sel_anims:
        bpy.ops.anim.keyframe_insert_menu(type='Location')
        bpy.data.objects[a].location = (0, 0, 0)
        z_offset(a, bpy.context.scene.offset)
        bpy.ops.anim.keyframe_insert_menu(type='Location')
    bpy.ops.object.select_all(action='DESELECT')
    print('\nYour scene is ready for export')


class Export_FBX_Vis(Operator, ExportHelper):
    bl_idname = "exp.fbx_vis"
    bl_label = "Export the scene"

    # ExportHelper mixin class uses this
    filename_ext = ""

    filter_glob: StringProperty(
        default="",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    skeleton_name: StringProperty(
        name='Skeleton name',
        description='Skeleton name',
        default='root',
    )
    change_scale: FloatProperty(
        name='Export scale',
        description='Scales model_paths and animations',
        min=0.01, max=100000.0,
        soft_min=0.01, soft_max=100.0,
        default=1.0,
    )
    fixbones: BoolProperty(
        name='Fix bones',
        description='Use this only when you converted models with QC converter',
        default=True,
    )
    export_FBX: BoolProperty(
        name='Export FBX',
        description='Export all animations as fbx',
        default=True,
    )
    export_visibility: BoolProperty(
        name='Export visibility',
        description='Export visibility .json file',
        default=True,
    )

    @classmethod
    def description(cls, context, properties):
        return "Exports a JSON file that can later be used in Unreal"

    def execute(self, context):
        if not self.filepath.endswith("\\"):
            self.filepath = self.filepath.rsplit(sep="\\", maxsplit=1)[0] + "\\"

        if self.export_FBX:
            self.agr_to_fbx()
        if self.export_visibility:
            self.visibility_export()
        print(f'\nFINISHED')
        return {'FINISHED'}

    def agr_to_fbx(self):
        scn = bpy.context.scene

        def export_fbx(object_type, scale=1.0):
            bpy.ops.export_scene.fbx(
                filepath=fbx_filepath,
                use_selection=True,
                bake_anim_use_nla_strips=False,
                bake_anim_use_all_actions=False,
                bake_anim_simplify_factor=0,
                object_types={object_type},
                add_leaf_bones=False,
                global_scale=scale)

        diselect()

        print(f'Export starting...\nstart frame: {scn.frame_start}, end frame: {scn.frame_end}')

        mesh_id = 0
        data_objects = bpy.data.objects
        total_armatures = len(
            [arm for arm in data_objects
             if (arm.name.startswith('afx.') and arm.type == 'ARMATURE')
             or arm.name.startswith('camera') or arm.name == 'afxCam'])

        for mesh in data_objects:
            fbx_filepath = f'{self.filepath}\\{mesh.name}.fbx'
            if mesh.name.startswith('afx.') and mesh.type == 'ARMATURE':
                with contextlib.suppress(Exception):
                    mesh.select_set(True)
                    old_root_name = mesh.name
                    bpy.context.view_layer.objects.active = mesh
                    if self.fixbones:
                        FixCSGO.bones(True, True)
                        if 'pirate' in mesh.data.name:
                            # fix for pirates
                            FixCSGO.pirates()
                    if '_skeleton' in mesh.data.name:
                        mesh.name = self.skeleton_name
                    mesh_id += 1
                    self.print_percentage(mesh_id, total_armatures)
                    export_fbx('ARMATURE', self.change_scale)
                    mesh.name = old_root_name
                    mesh.select_set(False)

            if mesh.name.startswith('camera') or mesh.name == 'afxCam':
                bpy.context.view_layer.objects.active = mesh
                with contextlib.suppress(Exception):
                    mesh.select_set(True)
                    bpy.data.objects[mesh.name].scale = (0.01, 0.01, 0.01)
                    scn.frame_current = scn.frame_start
                    bpy.ops.anim.keyframe_insert_menu(type='Scaling')
                    mesh_id += 1
                    self.print_percentage(mesh_id, total_armatures)
                    export_fbx('CAMERA', self.change_scale)
                    bpy.data.objects[mesh.name].scale = (1, 1, 1)
                    bpy.ops.anim.keyframe_insert_menu(type='Scaling')
                    mesh.select_set(False)

    def print_percentage(self, mesh_id, total_armatures):
        percentage = 100 * mesh_id / total_armatures
        print('\n{:.2f} %'.format(percentage))

    def visibility_export(self):
        time_start = time.time()
        print(f'\n\nExporting the visibility data...')
        diselect()
        scn = bpy.context.scene  # current scene
        sel_anims = []
        vis_dict = {}

        for mdl in bpy.context.scene.objects:
            if mdl.name.endswith('.mdl'):
                sel_anims.append(mdl.name)

        start_frame = scn.frame_start

        for frame in range(start_frame, start_frame + 1):
            scn.frame_set(frame)  # loop for frames
            for a in sel_anims:  # loop for selected anims
                vis_dict[a] = {}
                vis_dict[a][scn.frame_current] = str(scn.objects[a].hide_render)

        for frame in range(start_frame + 1, scn.frame_end):
            scn.frame_set(frame)  # loop for frames
            for a in sel_anims:  # loop for selected anims
                vis_dict[a][scn.frame_current] = str(bpy.context.scene.objects[a].hide_render)

        def clean(value, temp_dict):
            for k in temp_dict[:-1]:
                del value[k]

        def process(value):
            p = None
            temp_dict = []
            for k in list(value.keys()):
                if value[k] == p:
                    temp_dict.append(k)
                else:
                    clean(value, temp_dict)
                    p = value[k]
                    temp_dict = []
            clean(value, temp_dict)

        def second_pass():  # remove useless keys
            for animation, keys_values in vis_dict.items():
                remove_list = []
                keys = keys_values.keys()
                list_keys = list(keys)
                for first_value, second_value in zip(list_keys, list_keys[1:]):
                    if int(first_value) == int(second_value) - 1:
                        remove_list.append(first_value)
                if remove_list:
                    for item in remove_list:
                        del keys_values[item]

        print('Cleaning JSON file...')
        for values in vis_dict.values():
            process(values)
        second_pass()
        print('Done.')

        with open(self.filepath + '\\' + 'visibility.json', 'w') as export_file:
            json.dump(vis_dict, export_file, sort_keys=False, indent=2)
        print('\nJSON file was exported in {:.2f} seconds'.format(time.time() - time_start))

    def draw(self, context):
        pass


class MENU_PT_export_fbx_settings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Export FBX files"

    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXP_OT_fbx_vis"

    def draw_header(self, context):
        sfile = context.space_data
        operator = sfile.active_operator

        self.layout.prop(operator, "export_FBX", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator
        layout.enabled = operator.export_FBX
        layout.prop(operator, 'skeleton_name')
        layout.prop(operator, "change_scale")
        layout.prop(operator, "fixbones")


class MENU_PT_export_visibility_settings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Export vsibility"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXP_OT_fbx_vis"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator
        layout.prop(operator, "export_visibility")


class CleanButton(Operator):
    bl_idname = 'opr.start_clean'
    bl_label = 'Clean'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        fixer()
        if context.scene.remove_w_knives:
            w_knives()
        if context.scene.remove_dropped_knives:
            w_knives_dropped()
        if context.scene.remove_w_guns:
            w_guns()
        if context.scene.remove_dropped_guns:
            w_guns_dropped()
        if context.scene.remove_w_pistols:
            w_pistols()
        if context.scene.remove_dropped_pistols:
            w_pistols_dropped()
        if context.scene.remove_w_nades:
            w_nades()
        if context.scene.remove_dropped_nades:
            w_nades_dropped()
        if context.scene.remove_w_c4:
            w_c4()
        if context.scene.remove_dropped_c4:
            w_c4_dropped()
        if context.scene.remove_pov:
            pov()
        if context.scene.remove_duplicates:
            duplicates()
        if context.scene.remove_misc:
            misc()
        if context.scene.place_animations:
            anims_zero()

        return {'FINISHED'}


class T_SidePanel(Panel):
    bl_idname = 'VIEW3D_PT_AGRtools_panel'
    bl_label = 'AGR tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AGR tools'

    def draw(self, context):
        layout = self.layout.column(align=True)
        scene = context.scene

        def row_ui(row_prop, row1_prop):
            row = layout.column(align=True).row(align=True)
            row.prop(scene, row_prop)
            row1 = row.row()
            row1.prop(scene, row1_prop)

        def row_operator(row_operator, row1_operator):
            row = layout.column(align=True).row(align=True)
            row.operator(row_operator)
            row.operator(row1_operator)

        layout.label(text='Presets:')
        row_operator('opr.select_all', 'opr.deselect_all')
        row_operator('opr.pist_preset', 'opr.rif_preset')
        row_operator('opr.remove_all_w_preset', 'opr.remove_dropped_preset')
        row_operator('opr.pl_and_pov_preset', 'opr.pl_only_preset')
        row_operator('opr.save_user_preset', 'opr.load_user_preset')
        layout.separator()

        layout.label(text='World weapons (thirdperson):')
        row_ui('remove_w_knives', 'remove_dropped_knives')
        row_ui('remove_w_guns', 'remove_dropped_guns')
        row_ui('remove_w_pistols', 'remove_dropped_pistols')
        row_ui('remove_w_nades', 'remove_dropped_nades')
        row_ui('remove_w_c4', 'remove_dropped_c4')
        layout.separator()

        layout.label(text='Viewmodels (POV):')
        row_ui('remove_duplicates', 'remove_pov')
        layout.separator()

        layout.label(text='Misc:')
        layout.prop(scene, 'remove_misc')
        layout.prop(scene, 'place_animations')
        row = layout.column(align=True).row(align=True)
        row.enabled = scene.place_animations
        row.prop(scene, 'offset', text='Z Offset')
        layout.separator()

        layout.operator('opr.start_clean')
        layout.operator('exp.fbx_vis')


class PresetSelectAll(Operator):
    bl_idname = "opr.select_all"
    bl_label = "Select all"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.remove_w_knives = True
        context.scene.remove_dropped_knives = True
        context.scene.remove_w_guns = True
        context.scene.remove_dropped_guns = True
        context.scene.remove_w_pistols = True
        context.scene.remove_dropped_pistols = True
        context.scene.remove_w_nades = True
        context.scene.remove_dropped_nades = True
        context.scene.remove_w_c4 = True
        context.scene.remove_dropped_c4 = True
        context.scene.remove_pov = True
        context.scene.remove_misc = True
        context.scene.remove_duplicates = True
        context.scene.place_animations = True
        context.area.tag_redraw()
        return {'FINISHED'}


class PresetDeselectAll(Operator):
    bl_idname = "opr.deselect_all"
    bl_label = "Deselect all"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.remove_w_knives = False
        context.scene.remove_dropped_knives = False
        context.scene.remove_w_guns = False
        context.scene.remove_dropped_guns = False
        context.scene.remove_w_pistols = False
        context.scene.remove_dropped_pistols = False
        context.scene.remove_w_nades = False
        context.scene.remove_dropped_nades = False
        context.scene.remove_w_c4 = False
        context.scene.remove_dropped_c4 = False
        context.scene.remove_pov = False
        context.scene.remove_misc = False
        context.scene.remove_duplicates = False
        context.scene.place_animations = False
        context.area.tag_redraw()
        return {'FINISHED'}


class PresetPistolPreset(Operator):
    bl_idname = "opr.pist_preset"
    bl_label = "Pistol Kills"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.remove_w_knives = False
        context.scene.remove_dropped_knives = True
        context.scene.remove_w_guns = False
        context.scene.remove_dropped_guns = False
        context.scene.remove_w_pistols = False
        context.scene.remove_dropped_pistols = False
        context.scene.remove_w_nades = True
        context.scene.remove_dropped_nades = True
        context.scene.remove_w_c4 = False
        context.scene.remove_dropped_c4 = False
        context.scene.remove_pov = False
        context.scene.remove_misc = True
        context.scene.remove_duplicates = True
        context.scene.place_animations = True
        context.area.tag_redraw()
        return {'FINISHED'}


class PresetRifflePreset(Operator):
    bl_idname = "opr.rif_preset"
    bl_label = "Riffle kills"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.remove_w_knives = False
        context.scene.remove_dropped_knives = True
        context.scene.remove_w_guns = False
        context.scene.remove_dropped_guns = False
        context.scene.remove_w_pistols = True
        context.scene.remove_dropped_pistols = True
        context.scene.remove_w_nades = True
        context.scene.remove_dropped_nades = True
        context.scene.remove_w_c4 = False
        context.scene.remove_dropped_c4 = False
        context.scene.remove_pov = False
        context.scene.remove_misc = True
        context.scene.remove_duplicates = True
        context.scene.place_animations = True
        context.area.tag_redraw()
        return {'FINISHED'}


class PresetRemoveAllWPreset(Operator):
    bl_idname = "opr.remove_all_w_preset"
    bl_label = "Remove all weapons"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.remove_w_knives = False
        context.scene.remove_dropped_knives = False
        context.scene.remove_w_guns = True
        context.scene.remove_dropped_guns = False
        context.scene.remove_w_pistols = True
        context.scene.remove_dropped_pistols = False
        context.scene.remove_w_nades = True
        context.scene.remove_dropped_nades = False
        context.scene.remove_w_c4 = True
        context.scene.remove_dropped_c4 = False
        context.scene.remove_pov = False
        context.scene.remove_misc = True
        context.scene.remove_duplicates = True
        context.scene.place_animations = True
        context.area.tag_redraw()
        return {'FINISHED'}


class PresetRemoveAllDropped(Operator):
    bl_idname = "opr.remove_dropped_preset"
    bl_label = "Remove all dropped"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.remove_w_knives = False
        context.scene.remove_dropped_knives = True
        context.scene.remove_w_guns = False
        context.scene.remove_dropped_guns = True
        context.scene.remove_w_pistols = False
        context.scene.remove_dropped_pistols = True
        context.scene.remove_w_nades = False
        context.scene.remove_dropped_nades = True
        context.scene.remove_w_c4 = False
        context.scene.remove_dropped_c4 = True
        context.scene.remove_pov = False
        context.scene.remove_misc = True
        context.scene.remove_duplicates = True
        context.scene.place_animations = True
        context.area.tag_redraw()
        return {'FINISHED'}


class PresetPlayersAndPov(Operator):
    bl_idname = "opr.pl_and_pov_preset"
    bl_label = "Players and POV"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.remove_w_knives = True
        context.scene.remove_dropped_knives = True
        context.scene.remove_w_guns = True
        context.scene.remove_dropped_guns = True
        context.scene.remove_w_pistols = True
        context.scene.remove_dropped_pistols = True
        context.scene.remove_w_nades = True
        context.scene.remove_dropped_nades = True
        context.scene.remove_w_c4 = True
        context.scene.remove_dropped_c4 = True
        context.scene.remove_pov = False
        context.scene.remove_misc = True
        context.scene.remove_duplicates = True
        context.scene.place_animations = True
        context.area.tag_redraw()
        return {'FINISHED'}


class PresetPlayersOnly(Operator):
    bl_idname = "opr.pl_only_preset"
    bl_label = "Players only"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.remove_w_knives = True
        context.scene.remove_dropped_knives = True
        context.scene.remove_w_guns = True
        context.scene.remove_dropped_guns = True
        context.scene.remove_w_pistols = True
        context.scene.remove_dropped_pistols = True
        context.scene.remove_w_nades = True
        context.scene.remove_dropped_nades = True
        context.scene.remove_w_c4 = True
        context.scene.remove_dropped_c4 = True
        context.scene.remove_pov = True
        context.scene.remove_misc = True
        context.scene.remove_duplicates = True
        context.scene.place_animations = True
        context.area.tag_redraw()
        return {'FINISHED'}


class SaveUserPreset(Operator):
    bl_idname = "opr.save_user_preset"
    bl_label = "Save user preset"

    def execute(self, context):
        addon_folder = os.path.dirname(os.path.realpath(__file__))
        context.area.tag_redraw()
        user_settings = {
            'remove_w_knives': context.scene.remove_w_knives,
            'remove_dropped_knives': context.scene.remove_dropped_knives,
            'remove_w_guns': context.scene.remove_w_guns,
            'remove_dropped_guns': context.scene.remove_dropped_guns,
            'remove_w_pistols': context.scene.remove_w_pistols,
            'remove_dropped_pistols': context.scene.remove_dropped_pistols,
            'remove_w_nades': context.scene.remove_w_nades,
            'remove_dropped_nades': context.scene.remove_dropped_nades,
            'remove_w_c4': context.scene.remove_w_c4,
            'remove_dropped_c4': context.scene.remove_dropped_c4,
            'remove_pov': context.scene.remove_pov,
            'remove_misc': context.scene.remove_misc,
            'remove_duplicates': context.scene.remove_duplicates,
            'place_animations': context.scene.place_animations
        }

        settings_folder = os.path.join(addon_folder, 'Settings')
        if not os.path.exists(settings_folder):
            os.makedirs(settings_folder)
        with open(settings_folder + '\\' + 'UserSettings.json', 'w') as export_file:
            json.dump(user_settings, export_file, sort_keys=False, indent=2)
        print(f'\nUser settings saved in {settings_folder}')

        return {'FINISHED'}


class LoadUserPreset(Operator):
    bl_idname = "opr.load_user_preset"
    bl_label = "Load user preset"

    def execute(self, context):
        addon_folder = os.path.dirname(os.path.realpath(__file__))
        settings_folder = os.path.join(addon_folder, 'Settings')
        if os.path.exists(settings_folder + '\\' + 'UserSettings.json'):
            with open(settings_folder + '\\' + 'UserSettings.json') as json_file:
                self.load_user_data(json_file, context)
        else:
            print('User settings not found')

        return {'FINISHED'}

    def load_user_data(self, json_file, context):
        user_data = json.load(json_file)
        # load data
        context.scene.remove_w_knives = user_data['remove_w_knives']
        context.scene.remove_dropped_knives = user_data['remove_dropped_knives']
        context.scene.remove_w_guns = user_data['remove_w_guns']
        context.scene.remove_dropped_guns = user_data['remove_dropped_guns']
        context.scene.remove_w_pistols = user_data['remove_w_pistols']
        context.scene.remove_dropped_pistols = user_data['remove_dropped_pistols']
        context.scene.remove_w_nades = user_data['remove_w_nades']
        context.scene.remove_dropped_nades = user_data['remove_dropped_nades']
        context.scene.remove_w_c4 = user_data['remove_w_c4']
        context.scene.remove_dropped_c4 = user_data['remove_dropped_c4']
        context.scene.remove_pov = user_data['remove_pov']
        context.scene.remove_misc = user_data['remove_misc']
        context.scene.remove_duplicates = user_data['remove_duplicates']
        context.scene.place_animations = user_data['place_animations']


cLasses = [
    Export_FBX_Vis,
    MENU_PT_export_fbx_settings,
    MENU_PT_export_visibility_settings,
    T_SidePanel,
    CleanButton,
    PresetSelectAll,
    PresetDeselectAll,
    PresetPistolPreset,
    PresetRifflePreset,
    PresetRemoveAllWPreset,
    PresetRemoveAllDropped,
    PresetPlayersAndPov,
    PresetPlayersOnly,
    SaveUserPreset,
    LoadUserPreset,
    Convert_QC.QC_SMD_Convert,
    Convert_QC.QC_SMD_MENU_PT_convert_general_setings,
    Convert_QC.QC_SMD_MENU_PT_convert_model_setings,
    Convert_QC.QC_SMD_MENU_PT_convert_animation_setings
]


def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)
    for cls in cLasses:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_draw_convert)


def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)
    for cls in cLasses:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(menu_draw_convert)


if __name__ == '__main__':
    unregister()
    register()

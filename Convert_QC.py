import bpy
import time
import os
from . import FixCSGO
from . import Sorter
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator, Panel


class QC_SMD_Convert(Operator, ExportHelper):
    bl_idname = "exp.qc_smd_cnv"
    bl_label = "Convert"

    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    filepath: bpy.props.StringProperty(
        subtype='DIR_PATH'
    )
    filename_ext = ".qc"
    skeleton_name: bpy.props.StringProperty(
        name='Skeleton name',
        description='Skeleton name',
        default='root',
    )
    change_scale: bpy.props.FloatProperty(
        name='Scale',
        description='Scales models and animations (0.01 = default, 0.023 = UE scale)',
        min=0.000001, max=100000.0,
        soft_min=0.00001, soft_max=1.0,
        default=0.01,
    )
    set_fps: bpy.props.BoolProperty(
        name='Set fps from QC file',
        description='Read fps values for animation from qc file. If disabled or qc file is missing, fps will be set to 30',
        default=True,
    )
    filter_models: bpy.props.BoolProperty(
        name='Filter models',
        description='Will skip useless models',
        default=True,
    )
    sort_models: bpy.props.BoolProperty(
        name='Sort models',
        description='Will sort models between folders',
        default=True,
    )
    convert_models: bpy.props.BoolProperty(
        name='Convert models',
        description='Convert model from .qc file',
        default=True,
    )
    convert_animations: bpy.props.BoolProperty(
        name='Convert animations',
        description='Convert animations from .smd files',
        default=True,
    )
    convert_v_animations: bpy.props.BoolProperty(
        name='V animations',
        description='Convert POV animations from .smd file',
        default=True,
    )
    convert_w_animations: bpy.props.BoolProperty(
        name='W animations',
        description='Convert third person (worldmodel) animations from .smd files',
        default=False,
    )
    convert_player_animations: bpy.props.BoolProperty(
        name='Players animations',
        description='Convert players animation from .smd files (will take long time)',
        default=False,
    )
    fix_zero_length_anims: bpy.props.BoolProperty(
        name='Fix zero length animations',
        description='If .smd file contains only 1 frame of animation, it will add 2 more frames, '
                    'so unreal engine will import it correctly. It can fix some idle animations (e.g. for sg556)',
        default=True,
    )
    rotate_model: bpy.props.BoolProperty(
        name='Rotate players and W models',
        description='Rotate players and W models by 90 degrees',
        default=True,
    )
    remove_useless: bpy.props.BoolProperty(
        name='Remove useless parts of models',
        description='Remove holster strap and holiday wrap at the c4 model',
        default=True,
    )
    rename_gloves: bpy.props.BoolProperty(
        name='Rename gloves slots',
        description='Renames gloves slots to HD version',
        default=True,
    )
    export_path: bpy.props.StringProperty(
        name='Export Path',
        description='Directory path to export FBX files',
        default='',
    )
    verbose: bpy.props.BoolProperty(
        name='Verbose',
        description='Verbose mode',
        default=False,
    )
    fix_bones: bpy.props.BoolProperty(
        name='Fix bones',
        description='',
        default=True,
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        time_start = time.time()

        if self.filepath.endswith('\\'):
            self.filepath = self.filepath.rsplit('\\', 1)[0]

        if os.path.isfile(self.filepath):
            self.filepath = os.path.dirname(self.filepath)

        if self.verbose:
            print(f'checking filepath: {self.filepath}')

        def qc():
            qc_file = os.path.join(dirpath, filename)
            if self.verbose:
                print(f'qc file {filename} will be imported: {qc_file}')
            if filename.startswith('ctm_') or filename.startswith('tm_'):
                self.qc_import(qc_file, filename, True, 'player')
            else:
                self.qc_import(qc_file, filename, True, '')

        def smd():
            smd_file = os.path.join(dirpath, filename)
            # get prefix from qc's folders name
            smd_prefix = dirpath.split('\\')[-2]
            # replace _anim in prefix name
            if smd_prefix.endswith('_anim'):
                smd_prefix = smd_prefix.replace('_anim', '')
            if self.convert_v_animations:
                if smd_prefix.startswith('v_'):
                    if self.verbose:
                        print(f'SMD file {filename} will be imported: {smd_file}')
                    self.qc_import(smd_file, filename, False, smd_prefix)
            if self.convert_w_animations:
                if smd_prefix.startswith('w_'):
                    if self.verbose:
                        print(f'SMD file {filename} will be imported: {smd_file}')
                    self.qc_import(smd_file, filename, False, smd_prefix)
            if self.convert_player_animations:
                if 'player' in dirpath:
                    if self.verbose:
                        print(f'SMD file {filename} will be imported: {smd_file}')
                    self.qc_import(smd_file, filename, False, '')

        for dirpath, dirs, files in os.walk(self.filepath):
            for filename in files:

                useless_animation = len(files) < 2

                if self.convert_models:
                    if filename.endswith('.qc') and not filename.endswith('_anim.qc') and not filename.endswith('_animations.qc') and 'bullet' not in dirpath:
                        if self.filter_models:
                            if ((filename.startswith('ctm_') or filename.startswith('tm_')) and 'custom_player' in dirpath) or filename.startswith('v_') \
                                    or filename.startswith('w_') or 'arms' in filename:
                                if (
                                        '_icon' not in filename and not filename.endswith('_inspect.qc')
                                        and not filename.endswith('_mag.qc') and 'knife_gg' not in dirpath
                                        and 'knife_ghost' not in dirpath and '_scopelensmask' not in filename
                                        and filename != 'v_knife.qc' and 'wristband' not in dirpath and 'w_glove' not in filename
                                ):
                                    qc()

                        else:
                            qc()

                if self.convert_animations:
                    if self.convert_v_animations or self.convert_w_animations or self.convert_player_animations:
                        if self.filter_models:
                            if (
                                    not any(x.endswith('.qc') for x in files) and filename.endswith('.smd')
                                    and not useless_animation and 'test' not in filename
                                    and 'ragdoll' not in filename and 'arms' not in dirpath
                                    and 'pedestal' not in dirpath and 'knife_gg' not in dirpath and 'knife_ghost' not in dirpath
                                    and 'corrective' not in filename and not filename.startswith('default')
                                    and 'v_knife_anims' not in dirpath and not filename.startswith('test')
                                    and not dirpath.endswith('t_animations_anims')
                            ):
                                smd()
                        else:
                            smd()

        print('\n\nFinished in {:.2f} seconds'.format(time.time() - time_start))
        self.filepath = ''
        return {'FINISHED'}

    def remove_useless_parts(self, physics=False):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        if physics:
            bpy.ops.object.select_pattern(pattern='*physics', case_sensitive=False, extend=True)
        else:
            bpy.ops.object.select_pattern(pattern='*holsterstrap', case_sensitive=False, extend=True)
            bpy.ops.object.select_pattern(pattern='*_compass', case_sensitive=False, extend=True)
            bpy.ops.object.select_pattern(pattern='*_gift', case_sensitive=False, extend=True)
        bpy.ops.object.delete(use_global=True)
        bpy.ops.object.select_all(action='SELECT')

    def qc_import(self, valve_file_full_path, valve_filename, is_qc_file, prefix):
        scn = bpy.context.scene

        qc_type = ''

        fps = 30

        if self.set_fps and not is_qc_file:  # find fps values for animation in qc file
            smdfile_list_path = valve_file_full_path.split('\\')
            smdfolder = smdfile_list_path[-2]  # anims folder
            qc_folder = smdfile_list_path[-3]  # folder with qc file
            qc_path = '\\'.join(smdfile_list_path[:-3])  # D:\Distrib\3d stuff\csgo_models\QC_SOURCE\models\weapons
            qcfile = os.path.join(qc_path, qc_folder) + '\\' + qc_folder.replace('_anims', '') + '.qc'

            line_to_find = smdfolder + '\\' + valve_filename

            if os.path.isfile(qcfile):
                with open(qcfile) as file:
                    qc_lines = file.readlines()
                    for index, line in enumerate(qc_lines):
                        if line_to_find in line:
                            last_lines = qc_lines[index:len(qc_lines)]  # the rest of qc file after match
                            fps_line = next(x for x in last_lines if 'fps' in x)
                            fps = fps_line.replace('	fps ', '')
                            if self.verbose:
                                print(f'animation: {valve_filename}, fps: {fps}')
                            file.close()

        if is_qc_file:
            if self.verbose:
                print('This is mesh model, animation will not be imported')
            bpy.ops.import_scene.smd(filepath=valve_file_full_path, doAnim=False)
            if valve_filename.startswith('ctm_') or valve_filename.startswith('tm_'):
                qc_type = 'player'
            elif 'arms' in valve_file_full_path:
                qc_type = 'merged_arms'
                if 'arms' not in valve_filename:
                    qc_type = 'arms'
            elif 'arms' in valve_filename and 'arms' not in valve_file_full_path:
                qc_type = 'arms'
            elif valve_filename.startswith('v_'):
                qc_type = 'v_weapon'
            elif valve_filename.startswith('w_'):
                qc_type = 'w_weapon'
            else:
                qc_type = 'misc'
            if self.verbose:
                print(f'MESH TYPE: {qc_type}')

        if not is_qc_file:
            if self.verbose:
                print('This is animation file, animation will be imported')
            # sets fps
            bpy.context.scene.render.fps = int(fps)
            bpy.ops.import_scene.smd(filepath=valve_file_full_path, doAnim=True)

        for i in bpy.data.objects:
            if i.name == 'smd_bone_vis':
                bpy.data.objects.remove(i)

        for i in bpy.data.objects:
            if i.type == 'ARMATURE':
                if (qc_type == 'player' and self.rotate_model
                        and 'legacy' in valve_file_full_path
                        and i.name.endswith('_skeleton')):
                    i.rotation_euler = (1.5708, 0, 0)

        if qc_type == 'arms':
            self.qc_export(valve_file_full_path, prefix, 'agr_' + valve_filename, cleaning=False, is_static=True)
            if self.fix_bones:
                FixCSGO.bones(animation_file=False, verbose=self.verbose)
            self.qc_export(valve_file_full_path, prefix, valve_filename, is_static=True)

        elif qc_type == 'merged_arms':
            if self.fix_bones:
                FixCSGO.bones(animation_file=False, verbose=self.verbose)
            self.qc_export(valve_file_full_path, prefix, valve_filename, is_static=True)

        else:
            if qc_type == 'player':
                if self.rename_gloves:
                    for mesh in bpy.data.objects:
                        for materials in mesh.material_slots:
                            if 'fullfinger' in materials.name:
                                materials.material.name = 'glove_fullfinger'
                            elif 'w_ct_' in materials.name:
                                materials.material.name = 'glove_hardknuckle'
                            elif 'fingerless' in materials.name:
                                materials.material.name = 'glove_fingerless'
                            if 'arm' in materials.name:
                                if materials.name.endswith('_44'):
                                    materials.material.name = 'bare_arm_44'
                                elif materials.name.endswith('_55'):
                                    materials.material.name = 'bare_arm_55'
                                elif materials.name.endswith('_66'):
                                    materials.material.name = 'bare_arm_66'
                                elif materials.name.endswith('_78'):
                                    materials.material.name = 'bare_arm_78'
                                elif materials.name.endswith('_103'):
                                    materials.material.name = 'bare_arm_103'
                                elif materials.name.endswith('_133'):
                                    materials.material.name = 'bare_arm_133'
                                elif materials.name.endswith('_135'):
                                    materials.material.name = 'bare_arm_135'
                                elif 'base_arms_' in materials.name:
                                    materials.material.name = 'v_model_base_arms'
                if 'pirate' in valve_filename and 'custom_player' in valve_filename:
                    # fix for pirates (only new models)
                    FixCSGO.pirates()

            elif qc_type == 'w_weapon':
                if valve_filename.endswith('_dropped.qc'):
                    if self.remove_useless:
                        self.remove_useless_parts()
                else:
                    if self.rotate_model:
                        for i in bpy.data.objects:
                            if i.type == 'ARMATURE' and i.name.endswith('_skeleton'):
                                i.rotation_euler = (1.5708, 0, 0)

            elif qc_type == 'v_weapon':
                if self.remove_useless:
                    self.remove_useless_parts()
                if self.fix_bones:
                    FixCSGO.bones(animation_file=False, verbose=self.verbose)

            elif qc_type == 'misc':
                if self.fix_bones:
                    FixCSGO.bones(animation_file=False, verbose=self.verbose)

            if not is_qc_file:
                if self.fix_bones:
                    FixCSGO.bones(animation_file=True, verbose=self.verbose)
                if scn.frame_start == scn.frame_end and self.fix_zero_length_anims:
                    if 'v_' in valve_file_full_path:
                        FixCSGO.zero_frame('v_weapon.Bip01_L_Forearm')
                    elif 'player' in valve_file_full_path or 'w_' in valve_file_full_path:
                        FixCSGO.zero_frame('spine_0')

            self.qc_export(valve_file_full_path, prefix, valve_filename, is_static=is_qc_file)

    def qc_export(self, full_path, prefix, filename, cleaning=True, is_static=False):

        for i in bpy.data.objects:
            if i.type == 'ARMATURE' and i.name.endswith('_skeleton'):
                i.name = self.skeleton_name

        if prefix.startswith('w_') or prefix.startswith('v_') and self.remove_useless:
            self.remove_useless_parts(physics=False)

        self.remove_useless_parts(physics=True)

        temp_model_path = full_path.split(self.filepath)[1]
        export_model_path = os.path.dirname(temp_model_path.split(sep="\\", maxsplit=1)[1])
        fbx_export_path = os.path.join(self.export_path, export_model_path)

        fbx_name = filename.rsplit('.')[0]

        if not is_static and 'player' not in full_path:
            if fbx_name.startswith('a_'):  # fix animation's name for revolver
                fbx_name = fbx_name.replace('a_', '')
            elif fbx_name.startswith('ak47_'):  # fix animation's name for ak47
                fbx_name = fbx_name.replace('ak47_', '')
            elif fbx_name.startswith('awp_'):  # fix animation's name for awp
                fbx_name = fbx_name.replace('awp_', '')
            elif fbx_name.startswith('bizon_'):  # fix animation's name for bizon
                fbx_name = fbx_name.replace('bizon_', '')
            elif fbx_name.startswith('glock_'):  # fix animation's name for glock
                fbx_name = fbx_name.replace('glock_', '')
            elif fbx_name.startswith('mac10_'):  # fix animation's name for mac10
                fbx_name = fbx_name.replace('mac10_', '')
            fbx_name = prefix + '_' + fbx_name

        # Export as fbx
        def export(name, clean=True):
            bpy.ops.export_scene.fbx(
                filepath=name,
                use_selection=False,
                bake_anim_use_nla_strips=False,
                bake_anim_use_all_actions=False,
                bake_anim_simplify_factor=0,
                mesh_smooth_type='FACE',
                add_leaf_bones=False,
                global_scale=self.change_scale)
            if clean:
                cleanup()

        def cleanup():
            for data_objects in bpy.data.objects:
                bpy.data.objects.remove(data_objects)
            for data_actions in bpy.data.actions:
                bpy.data.actions.remove(data_actions)
            for data_armatures in bpy.data.armatures:
                bpy.data.armatures.remove(data_armatures)
            for data_meshes in bpy.data.meshes:
                bpy.data.meshes.remove(data_meshes)
            for data_materials in bpy.data.materials:
                bpy.data.materials.remove(data_materials)
            for data_collections in bpy.data.collections:
                bpy.data.collections.remove(data_collections)

        if self.sort_models:
            sorted_model_path = Sorter.model_sorter(export_model_path, fbx_name)
            fbx_export_path = os.path.join(self.export_path, sorted_model_path)

        if not os.path.exists(fbx_export_path):
            os.makedirs(fbx_export_path)

        export(os.path.join(fbx_export_path, fbx_name + '.fbx'), cleaning)

    def draw(self, context):
        pass


class QC_SMD_MENU_PT_convert_general_setings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Main settings"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXP_OT_qc_smd_cnv"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator
        layout.prop(operator, "skeleton_name")
        layout.prop(operator, "change_scale")
        layout.prop(operator, "export_path")
        layout.prop(operator, 'filter_models')
        layout.prop(operator, "fix_bones")
        layout.prop(operator, "sort_models")
        layout.prop(operator, "verbose")


class QC_SMD_MENU_PT_convert_model_setings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Convert models"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXP_OT_qc_smd_cnv"

    def draw_header(self, context):
        sfile = context.space_data
        operator = sfile.active_operator

        self.layout.prop(operator, "convert_models", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator
        layout.enabled = operator.convert_models
        layout.prop(operator, 'rotate_model')
        layout.prop(operator, "remove_useless")
        layout.prop(operator, "rename_gloves")


class QC_SMD_MENU_PT_convert_animation_setings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Convert animations"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXP_OT_qc_smd_cnv"

    def draw_header(self, context):
        sfile = context.space_data
        operator = sfile.active_operator

        self.layout.prop(operator, "convert_animations", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator
        layout.enabled = operator.convert_animations
        layout.prop(operator, 'set_fps')
        layout.prop(operator, "convert_v_animations")
        layout.prop(operator, "convert_w_animations")
        layout.prop(operator, "convert_player_animations")
        layout.prop(operator, "fix_zero_length_anims")

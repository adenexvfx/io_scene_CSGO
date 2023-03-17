import os.path
from math import radians
import bpy
import contextlib


def clear_selection():
    if bpy.context.active_object and bpy.context.active_object.mode in ['POSE', 'EDIT']:
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')


def unparent_bone(bones, armature=None):
    if armature is None:
        armature = bpy.data.armatures[0]
    for bone in bones:
        clear_selection()
        bpy.ops.object.mode_set(mode='OBJECT')
        with contextlib.suppress(KeyError):
            armature.bones[bone].select = 1
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.parent_clear()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.select_all(action='DESELECT')
            print(f'{bone} unparented')


def parent_bone(bone, bone_p='v_weapon.Bip01_R_Hand', armature=None):
    if armature is None:
        armature = bpy.data.armatures[0]
    clear_selection()
    bpy.ops.object.mode_set(mode='EDIT')
    with contextlib.suppress(KeyError):
        armature.edit_bones.active = armature.edit_bones[bone]
        armature.edit_bones.active = armature.edit_bones[bone_p]
        bpy.ops.armature.parent_set(type='OFFSET')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        print(f'{bone} parented to {bone_p}')


def remove_bone(bones):
    for bone in bones:
        for armature in bpy.data.armatures:
            clear_selection()
            with contextlib.suppress(KeyError):
                armature.bones[bone].select = 1
                for bones in armature.bones[bone].children_recursive:
                    bones.select = 1
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.armature.delete()
                print(f'{bone} removed')


def set_bone_name(name, armature, new_name='', endswith=False):
    if new_name == '':
        new_name = name
    for bone in armature.bones:
        if name not in bone.name.lower():
            continue
        if endswith and not bone.name.lower().endswith(name):
            continue
        if bone.parent:
            if (bone.parent.name.lower().endswith('_parent') or bone.parent.name.lower().endswith('.parent')) and bone.parent.parent.name.endswith('R_Hand'):
                bone.parent.name = 'v_weapon.R_parent'
                print(f"> renamed {bone.name} to {new_name}")
                bone.name = new_name
            if bone.parent.name.lower().endswith('l_parent') and bone.parent.parent.name.endswith('L_Hand'):
                bone.parent.name = 'v_weapon.L_parent'
                print(f"> renamed {bone.name} to L_{new_name}")
                bone.name = f'L_{new_name}'


def force_set_bone_name(name, armature, new_name):
    with contextlib.suppress(KeyError):
        armature.bones[name].name = new_name
        print(f"> renamed {name} to {new_name}")


def bones_renamer(armature):
    # rename root bone for knives
    force_set_bone_name('v_weapon.knife', armature, 'v_weapon.R_parent')
    force_set_bone_name('Mesh', armature, 'v_weapon.R_parent')

    set_bone_name('stattrack', armature)
    set_bone_name('uid', armature)
    set_bone_name('flash', armature)
    set_bone_name('shelleject', armature)
    set_bone_name('hammer', armature)
    set_bone_name('trigger', armature)
    set_bone_name('clip', armature, endswith=True)
    set_bone_name('cliprelease', armature, endswith=True)
    set_bone_name('_shell', armature, 'shell', endswith=True)
    set_bone_name('_loader', armature, 'loader', endswith=True)
    set_bone_name('slide', armature)
    set_bone_name('bolt', armature)
    set_bone_name('chargehandle', armature)
    set_bone_name('сhamber', armature)
    set_bone_name('.handle', armature, 'handle')
    set_bone_name('ammobox', armature)
    set_bone_name('latch', armature)
    set_bone_name('plate', armature)
    set_bone_name('chargehandle', armature)
    set_bone_name('release', armature)
    set_bone_name('magazine', armature)
    set_bone_name('mag', armature, 'magazine', endswith=True)
    set_bone_name('silencer', armature)
    set_bone_name('pump', armature)
    set_bone_name('hinge', armature)
    set_bone_name('wing1', armature)
    set_bone_name('wing2', armature)
    set_bone_name('.cap', armature, 'cap')
    set_bone_name('button', armature)
    set_bone_name('switch', armature, endswith=True)
    set_bone_name('switchcover', armature)
    set_bone_name('needle_enclosure', armature, 'enclosure')
    set_bone_name('.pin', armature, 'pin')
    set_bone_name('.pin', armature, 'pin')
    set_bone_name('blade1', armature, 'blade')
    set_bone_name('blade', armature)
    set_bone_name('crane', armature)
    set_bone_name('collar', armature)
    set_bone_name('flap', armature, endswith=True)

    # cases
    force_set_bone_name('v_weapon.M4A1_Bullets', armature, 'bullets')
    force_set_bone_name('v_weapon.Ring', armature, 'ring')
    force_set_bone_name('v_weapon.lighter_flame1', armature, 'lighter_flame1')
    force_set_bone_name('v_weapon.lighter_flame2', armature, 'lighter_flame2')
    force_set_bone_name('v_weapon.lighter_flame3', armature, 'lighter_flame3')
    force_set_bone_name('v_weapon.lighter_flame4', armature, 'lighter_flame4')
    force_set_bone_name('v_weapon.lighter_flame5', armature, 'lighter_flame5')
    force_set_bone_name('v_weapon.lighter_lever', armature, 'lighter_lever')
    force_set_bone_name('v_weapon.lighter_wheel', armature, 'lighter_wheel')
    force_set_bone_name('v_weapon.jiggle_rag_up0', armature, 'jiggle_rag_up0')
    force_set_bone_name('v_weapon.jiggle_rag_up1', armature, 'jiggle_rag_up1')
    force_set_bone_name('v_weapon.jiggle_rag_up2', armature, 'jiggle_rag_up2')
    force_set_bone_name('v_weapon.jiggle_rag_up3', armature, 'jiggle_rag_up3')
    force_set_bone_name('v_weapon.doorL', armature, 'doorL')
    force_set_bone_name('v_weapon.doorR', armature, 'doorR')


def fix_bones(is_animation: bool, bones: list, must_be_parented: bool, bone_p: str, model_object, armature):
    scn = bpy.context.scene

    def get_source_matrix(source):
        return source.id_data.convert_space(
            pose_bone=source,
            matrix=source.matrix,
            from_space='POSE', )

    def set_matrix(matrix_source, target):
        target.matrix = target.id_data.convert_space(
            pose_bone=target,
            matrix=matrix_source,
            to_space='POSE',
        )

    bpy.ops.object.mode_set(mode='POSE')

    for bone in bones:
        if not is_animation:
            if must_be_parented:
                parent_bone(bone, bone_p, armature=armature)
            else:
                unparent_bone([bone], armature=armature)

        else:

            scn.frame_set(scn.frame_start)
            # create dict with matrix in it
            matrix_dict = {scn.frame_current: get_source_matrix(model_object.pose.bones[bone])}

            for frame in range(1, scn.frame_end + 2):
                scn.frame_set(frame)
                matrix_dict[scn.frame_current] = get_source_matrix(model_object.pose.bones[bone])

            if must_be_parented:
                parent_bone(bone, bone_p, armature=armature)
            else:
                unparent_bone([bone], armature=armature)

            bpy.ops.object.mode_set(mode='POSE')
            # get all items from dictionary
            kv = list(matrix_dict.items())
            # unpack values
            first_key, _ = kv[0]
            last_key, _ = kv[-1]
            armature.bones[bone].select = 1

            for frame in range(first_key, last_key):
                scn.frame_set(frame)
                matrix_keyframe = matrix_dict.get(frame)

                # paste values from matrix in dictionary
                set_matrix(matrix_keyframe, model_object.pose.bones[bone])

                # make a keyframe
                bpy.ops.anim.keyframe_insert_menu(type='Location')
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bpy.ops.anim.keyframe_insert_menu(type='Scaling')

            armature.bones[bone].select = 0
            scn.frame_set(scn.frame_start)


def v_model(filename: str, is_animation: bool, objects_to_ignore: list, armatures_to_ignore: list, mtype='', converter=False):

    model_object = None
    armature = None

    if converter:
        model_object = bpy.data.objects[0]
    else:
        for a in bpy.data.objects:
            if a not in objects_to_ignore and a.name != 'smd_bone_vis':
                model_object = a

    if model_object is None:
        return

    if converter:
        armature = bpy.data.armatures[0]
    else:
        for a in bpy.data.armatures:
            if a not in armatures_to_ignore:
                armature = a

    if armature is None:
        return

    # detect weapon
    if is_animation:
        dirname = os.path.dirname(filename)
        if dirname.split('\\')[-2].endswith('_anim'):  # knife
            filename = dirname.split('\\')[-2].replace('_anim', '')
        else:
            filename = dirname.split('\\')[-2]
    else:
        filename = os.path.basename(filename).replace('.qc', '')
    print(f'> filename: {filename}')
    print(f'> is_animation: {is_animation}')

    def fix_arms():
        fix_bones(is_animation, ['v_weapon.Bip01_R_Forearm', 'v_weapon.Bip01_R_ForeTwist',
                                 'v_weapon.Bip01_L_Forearm', 'v_weapon.Bip01_L_ForeTwist'], False, '', model_object, armature)

    if filename in {'v_pist_tec9', 'v_mach_negev', 'v_sonar_bomb'} or mtype in {'arms', 'merged_arms'}:
        fix_arms()

    if filename == 'v_eq_molotov':
        fix_bones(is_animation, ['v_weapon.molotov_Parent'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        fix_bones(is_animation, ['v_weapon.lighter_wheel', 'v_weapon.lighter_lever',
                                 'v_weapon.lighter_hinge', 'v_weapon.lighter_flame1'], True, 'v_weapon.molotov_Parent', model_object, armature)

    if filename == 'v_eq_taser':
        fix_bones(is_animation, ['v_weapon.parent'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)

    if filename == 'v_fists':
        fix_arms()
        fix_bones(is_animation, ['money_root'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        fix_bones(is_animation, ['root'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)

    if filename == 'v_hammer':
        fix_arms()
        fix_bones(is_animation, ['Mesh'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)

    if filename == 'v_healthshot':
        fix_arms()
        fix_bones(is_animation, ['v_weapon.adrenaline_parent'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)

    if filename == 'v_ied':
        fix_bones(is_animation, ['v_weapon.c4'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        force_set_bone_name('v_weapon.c4', armature, 'v_weapon.R_parent')


    # KNIVES
    if filename in {'v_knife_bayonet', 'v_knife_css', 'v_knife_default_ct', 'v_knife_default_t',
                    'v_knife_flip', 'v_knife_gut', 'v_knife_karam', 'v_knife_m9_bay',
                    'v_knife_skeleton', 'v_knife_survival_bowie', 'v_knife_tactical',
                    'v_knife_ursus', 'v_knife_widowmaker'}:
        fix_bones(is_animation, ['v_weapon.knife'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)

    if filename == 'v_knife_push':
        fix_arms()
        fix_bones(is_animation, ['v_weapon.knife_R'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        fix_bones(is_animation, ['v_weapon.knife_L'], True, 'v_weapon.Bip01_L_Hand', model_object, armature)
        force_set_bone_name('v_weapon.knife_R', armature, 'v_weapon.R_parent')
        force_set_bone_name('v_weapon.knife_L', armature, 'v_weapon.L_parent')

    if filename == 'v_knife_butterfly':
        fix_bones(is_animation, ['v_weapon.blade1'], True, 'v_weapon.knife', model_object, armature)
        fix_bones(is_animation, ['v_weapon.knife'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        remove_bone(['v_weapon.front'])
        force_set_bone_name('v_weapon.rear', armature, 'rear')
        force_set_bone_name('v_weapon.lock', armature, 'lock')
        force_set_bone_name('v_weapon.uid', armature, 'uid_butterfly')
        force_set_bone_name('v_weapon.stattrack', armature, 'stattrack_1')

    if filename in {'v_knife_falchion_advanced', 'v_knife_gypsy_jackknife', 'v_knife_outdoor', 'v_knife_stiletto'}:
        fix_arms()
        fix_bones(is_animation, ['v_weapon.knife'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        force_set_bone_name('v_weapon.stattrack', armature, 'stattrack_1')

    if filename == 'v_knife_flip':
        fix_arms()
        fix_bones(is_animation, ['v_weapon.knife'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)

    # PISTOLS
    if filename == 'v_pist_223':
        force_set_bone_name('v_weapon.uid', armature, 'uid_223')
    if filename == 'v_pist_cz_75':
        force_set_bone_name('v_weapon.uid', armature, 'uid_cz_75')
    if filename == 'v_pist_revolver':
        fix_arms()
        fix_bones(is_animation, ['v_weapon.deagle_parent'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        fix_bones(is_animation, ['v_weapon.loader_handle'], True, 'v_weapon.Bip01_L_Hand', model_object, armature)

    # SHOTGUNS
    if filename == 'v_shot_xm1014':
        force_set_bone_name('v_weapon.xm1014_Shell1', armature, 'shell_00')
        force_set_bone_name('v_weapon.xm1014_Shell2', armature, 'shell_01')
        force_set_bone_name('v_weapon.xm1014_Shell3', armature, 'shell_02')
        force_set_bone_name('v_weapon.xm1014_Shell4', armature, 'shell_03')

    # SMGs
    if filename == 'v_smg_mp5sd':
        fix_arms()
        fix_bones(is_animation, ['v_weapon.mp5sd_parent'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        remove_bone(['camera_inventory', 'v_weapon.mp7_parent'])

    # SNIPERS
    if filename == 'v_snip_awp':
        force_set_bone_name('v_weapon.awp_bolt_action', armature, 'bolt_awp')
    if filename == 'v_snip_ssg08':
        fix_arms()
        force_set_bone_name('v_weapon.weapon_bolt', armature, 'bolt_ssg')

    # MISC
    if filename == 'v_repulsor':
        fix_arms()
        fix_bones(is_animation, ['repulsor'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        force_set_bone_name('repulsor', armature, 'v_weapon.R_parent')
    if filename == 'v_spanner':
        fix_arms()
        fix_bones(is_animation, ['Mesh'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        force_set_bone_name('Mesh', armature, 'v_weapon.R_parent')
    if filename == 'v_shield':
        fix_arms()
        fix_bones(is_animation, ['shield'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        force_set_bone_name('shield', armature, 'v_weapon.R_parent')
    if filename == 'v_tablet':
        fix_arms()
        force_set_bone_name('tablet', armature, 'v_weapon.R_parent')
    if filename == 'v_axe':
        fix_arms()
        clear_selection()
        bpy.ops.object.mode_set(mode='OBJECT')
        axe_mesh = bpy.data.objects['axe_ref']
        axe_mesh.select_set(True)
        axe_mesh.rotation_euler = (radians(90), radians(90), radians(-180))
        clear_selection()
        fix_bones(is_animation, ['v_melee_root'], True, 'v_weapon.Bip01_R_Hand', model_object, armature)
        force_set_bone_name('v_melee_root', armature, 'v_weapon.R_parent')

    remove_bone(['v_weapon', 'v_weapon.v_weapon', 'v_weapon.Bip01_R_Clavicle',
                 'v_weapon.Bip01_L_Clavicle', 'v_weapon.Bip01', 'cam_driver',
                 'hammer_ref1', 'v_weapon.Bip01_Prop1', 'spanner_ref'])
    bones_renamer(armature)


def zero_frame(bone_name):
    scn = bpy.context.scene
    bpy.ops.object.mode_set(mode='POSE')
    scn.frame_end = 3
    for bones in bpy.data.armatures[0].bones:  # check if bone exists
        if bones.name == bone_name:
            bpy.data.armatures[0].bones[bone_name].select = 1
            for frame in range(scn.frame_start, 3):
                scn.frame_set(frame)
                bpy.ops.anim.keyframe_insert_menu(type='Location')
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bpy.ops.anim.keyframe_insert_menu(type='Scaling')
                bpy.ops.anim.keyframe_insert_menu(type='Location')
            bpy.data.armatures[0].bones[bone_name].select = 0
            bpy.ops.object.mode_set(mode='OBJECT')


def pirates():
    def fix(bone_to_fix):
        bpy.ops.object.mode_set(mode='OBJECT')
        with contextlib.suppress(KeyError):  # old pirate model
            bpy.data.armatures[0].bones[bone_to_fix].select = 1
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.parent_clear()
            print(f'{bone_to_fix} unparented')
            bpy.data.armatures[0].edit_bones.active = bpy.data.armatures[0].edit_bones[bone_to_fix]
            with contextlib.suppress(KeyError):  # old pirate model
                bpy.data.armatures[0].edit_bones.active = bpy.data.armatures[0].edit_bones['spine_2']
                bpy.ops.armature.parent_set(type='OFFSET')
                print(f'{bone_to_fix} parented to spine_2')
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.armature.select_all(action='DESELECT')

    fix('JiggleBone_F_tassle_1')
    fix('JiggleBone_B_tassle_5')
    fix('primary_jiggle_jnt')

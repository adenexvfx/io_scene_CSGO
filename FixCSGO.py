import bpy
import re


def bones(animation_file, verbose):
    scn = bpy.context.scene

    is_spanner = False
    is_push_knife = False

    bone_list = []  # the only way i've found to prevent blender's crashes
    for bone in bpy.data.armatures[0].bones:
        if bone.name.startswith('spanner_'):
            is_spanner = True
        elif bone.name.endswith('.knife_R'):
            is_push_knife = True
        bone_list.append(bone.name)

    def fix_animations(bone_to_fix, parent=False):
        parented_bone = True

        for bones in bpy.data.armatures[0].bones:
            # checking if bone is parented or not
            if (bone_to_fix == bones.name and
                    parent is False and not bones.parent):
                if verbose:
                    print(f'{bones.name} is already unparented, skipping')
                parented_bone = False
            # checking for the specific model
            elif (bone_to_fix == bones.name and
                  parent is True and bones.parent and
                  not is_spanner and not is_push_knife):
                if verbose:
                    print(f'{bones.name} is already parented, skipping')
                parented_bone = False

        if parented_bone:
            skeleton = bpy.data.objects[0]
            matrix_dict = {}

            bpy.ops.object.mode_set(mode='POSE')

            def get_source_matrix(source):
                matrix_source = source.id_data.convert_space(
                    pose_bone=source,
                    matrix=source.matrix,
                    from_space='POSE',
                )
                return matrix_source

            def set_matrix(matrix_source, target):
                target.matrix = target.id_data.convert_space(
                    pose_bone=target,
                    matrix=matrix_source,
                    to_space='POSE',
                )

            if bone_to_fix in bpy.data.armatures[0].bones:

                if animation_file:
                    scn.frame_set(scn.frame_start)

                    for frame in range(1):
                        scn.frame_set(frame)
                        # create dict with matrix in it
                        matrix_dict = {scn.frame_current: get_source_matrix(skeleton.pose.bones[bone_to_fix])}

                    for frame in range(1, scn.frame_end + 2):
                        scn.frame_set(frame)
                        matrix_dict[scn.frame_current] = get_source_matrix(skeleton.pose.bones[bone_to_fix])

                def unparent_bone():
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.data.armatures[0].bones[bone_to_fix].select = 1
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.armature.parent_clear()
                    if verbose:
                        print(f'{bone_to_fix} unparented')

                def parent_bone(bone_to_parent):
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.data.armatures[0].edit_bones.active = bpy.data.armatures[0].edit_bones[bone_to_parent]
                    bpy.data.armatures[0].edit_bones.active = bpy.data.armatures[0].edit_bones['v_weapon.Bip01_R_Hand']
                    bpy.ops.armature.parent_set(type='OFFSET')
                    if verbose:
                        print(f'{bone_to_parent} parented')

                if parent:
                    parent_bone(bone_to_fix)
                else:
                    unparent_bone()

                if animation_file:
                    bpy.ops.object.mode_set(mode='POSE')
                    # get all items from dictionary
                    kv = list(matrix_dict.items())
                    # unpack values
                    last_key, last_value = kv[-1]

                    for frame in range(scn.frame_start, last_key):
                        scn.frame_set(frame)
                        matrix_keyframe = matrix_dict.get(frame)
                        # paste values from matrix in dictionary
                        set_matrix(matrix_keyframe, skeleton.pose.bones[bone_to_fix])
                        # make a keyframe
                        bpy.ops.anim.keyframe_insert_menu(type='Location')
                        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                        bpy.ops.anim.keyframe_insert_menu(type='Scaling')

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.armature.select_all(action='DESELECT')

    # if verbose:
    # print(f'\nstart frame: {scn.frame_start}, end frame: {scn.frame_end}')

    fix_animations('v_weapon.Bip01_R_Forearm')
    fix_animations('v_weapon.Bip01_R_ForeTwist')
    fix_animations('v_weapon.Bip01_L_Forearm')
    fix_animations('v_weapon.Bip01_L_ForeTwist')

    # check if we need to parent this bone
    if is_spanner:
        r = re.compile('Mesh')
        temp_list = list(filter(r.match, bone_list))
        if temp_list:
            fix_animations(temp_list[0], True)

    else:
        r = re.compile('.*_parent')
        temp_list = list(filter(r.match, bone_list))
        if temp_list:
            fix_animations(temp_list[0], True)

    def remove_bones(bone_name):
        bpy.ops.object.mode_set(mode='OBJECT')
        if bone_name in bpy.data.armatures[0].bones:
            bpy.data.armatures[0].bones[bone_name].select = 1
            for bones in bpy.data.armatures[0].bones[bone_name].children_recursive:
                bones.select = 1
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.delete()
            if verbose:
                print(f'{bone_name} removed')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.select_all(action='DESELECT')

    remove_bones('v_weapon.Bip01_L_Clavicle')
    remove_bones('v_weapon.Bip01_R_Clavicle')
    remove_bones('v_weapon.v_weapon')
    remove_bones('v_weapon.Bip01')

    remove_bones('v_weapon.Bip01_Prop1')
    remove_bones('spanner_ref')

    bpy.ops.object.mode_set(mode='POSE')


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
        try:
            bpy.data.armatures[0].bones[bone_to_fix].select = 1
        except KeyError:  # old pirate model
            pass
        else:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.parent_clear()
            print(f'{bone_to_fix} unparented')
            bpy.data.armatures[0].edit_bones.active = bpy.data.armatures[0].edit_bones[bone_to_fix]
            try:
                bpy.data.armatures[0].edit_bones.active = bpy.data.armatures[0].edit_bones['spine_2']
                bpy.ops.armature.parent_set(type='OFFSET')
                print(f'{bone_to_fix} parented to spine_2')
            except KeyError:  # old pirate model
                pass
            else:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.armature.select_all(action='DESELECT')

    fix('JiggleBone_F_tassle_1')
    fix('JiggleBone_B_tassle_5')
    fix('primary_jiggle_jnt')

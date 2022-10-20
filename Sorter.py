def model_sorter(export_model_path, fbx_name):
    sorted_path = ''
    sorted_subtype_path = sorted_path
    model_type = 'MISC'
    if fbx_name.startswith('ctm_') or fbx_name.startswith('tm_'):
        model_type = 'PLAYER'
    elif 'player' in export_model_path and 'anim' in export_model_path:
        model_type = 'PLAYER_ANIMS'
    elif fbx_name.startswith('v_') and 'arms' not in export_model_path:
        if 'anims' not in export_model_path:
            model_type = 'V'
        else:
            model_type = 'V_ANIMS'
    elif fbx_name.startswith('w_') and 'arms' not in export_model_path:
        if 'anims' not in export_model_path:
            model_type = 'W'
        else:
            model_type = 'W_ANIMS'
    elif 'arms' in export_model_path:
        if fbx_name.startswith('v_') or fbx_name.startswith('agr_'):
            model_type = 'ARMS'
        else:
            model_type = 'ARMS_MERGED'

    # define sub-type
    if model_type == 'PLAYER':
        player_name_list = fbx_name.split('_', 2)  # ['ctm', 'diver', 'varianta']
        player_name_list_length = len(player_name_list)
        if player_name_list_length == 3:
            player_team, model_skin, variant = player_name_list  # ctm diver varianta
        else:
            player_team, model_skin = player_name_list
        sorted_subtype_path = 'players\\' + player_team + '\\' + model_skin

    if model_type == 'PLAYER_ANIMS':
        animation_folder = export_model_path.split('\\')[-1]
        sorted_subtype_path = 'animations\\players\\' + animation_folder

    def vw(model_type):
        if model_type in {'V', 'W'}:
            p = 'weapons'
        elif model_type == 'V_ANIMS':
            p = 'animations\\weapons\V'
        elif model_type == 'W_ANIMS':
            p = 'animations\\weapons\W'
        if '_ied' in fbx_name or 'c4' in fbx_name:
            s_path = p + '\\c4'
        elif '_eq' in fbx_name:
            s_path = p + '\\eq'
        elif '_knife' in fbx_name:
            s_path = p + '\\knives'
        elif '_mach' in fbx_name:
            s_path = p + '\\machguns'
        elif '_pist' in fbx_name:
            s_path = p + '\\pistols'
        elif '_rif' in fbx_name:
            s_path = p + '\\riffles'
        elif '_shot' in fbx_name:
            s_path = p + '\\shotguns'
        elif '_smg' in fbx_name:
            s_path = p + '\\smgs'
        elif '_snip' in fbx_name:
            s_path = p + '\\snipers'
        else:
            s_path = p + '\\misc'

        return s_path

    if model_type in {'V', 'W', 'V_ANIMS', 'W_ANIMS'}:
        sorted_path = vw(model_type)
        model_folder = export_model_path.split('\\')[-1]
        if model_folder == '' or 'ied' in fbx_name or 'c4' in fbx_name:
            sorted_subtype_path = sorted_path
        else:
            if model_folder == 'v_t_knife_anim_anims':
                model_folder = model_folder.replace('v_t_knife_anim_anims', 'v_knife_default_t')
            if model_folder == 'v_ct_knife_anim_anims':
                model_folder = model_folder.replace('v_ct_knife_anim_anims', 'v_knife_default_ct')
            if model_folder.endswith('_anim_anims'):
                model_folder = model_folder.replace('_anim_anims', '')
            if model_folder.endswith('_anims'):
                model_folder = model_folder.replace('_anims', '')

            m_name_list = model_folder.split('_', 2)

            if len(m_name_list) == 3:
                mtype, msubtype, weapon = m_name_list
            elif len(m_name_list) == 2:
                mtype, weapon = m_name_list
            else:
                weapon = m_name_list
            model_folder = weapon

            sorted_subtype_path = sorted_path + '\\' + model_folder

    if model_type == 'ARMS':
        if fbx_name.startswith('v_'):
            sorted_path = 'hands\\V'
        else:
            sorted_path = 'hands\\AGR'
        sorted_subtype_path = sorted_path

    if model_type == 'ARMS_MERGED':
        sorted_path = 'hands\\merged'
        sorted_subtype_path = sorted_path

    if sorted_subtype_path.endswith('_dropped'):
        sorted_subtype_path = sorted_subtype_path.replace('_dropped', '')
    if sorted_subtype_path.endswith('_thrown'):
        sorted_subtype_path = sorted_subtype_path.replace('_thrown', '')

    if model_type == 'MISC':
        sorted_subtype_path = 'misc'

    return sorted_subtype_path

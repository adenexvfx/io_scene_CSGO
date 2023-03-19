# io_scene_CSGO MasterWeapons branch
Bones fixing addon for Blender for later usage in Unreal Engine.

[PREVIEW](https://youtu.be/q6eHmEuyc-8)

Basically these are two addons merged together. 
- The first you can find in ```File > Import > Batch convert CSGO's QC files```. 
- The second is ```at the side panel```.

# Download and install
You can download it [here](https://github.com/adenexvfx/io_scene_CSGO/releases/tag/v1.0).
[Blender Source Tools](http://steamreview.org/BlenderSourceTools/) addon is required for io_scene_CSGO

# Batch QC converter
This part of the addon can batch convert QC and SMD files in the folder. It fixes all the bones of the model

## Features
- Can fix all the bones in V models (scout, mp5sd, revolver, etc). 
- Can remove useless parts of W models during the convertion (hoster strap and holiday wrap for ied).
- You can rotate players models (will affect only new players models in the 'legacy' folder) and W weapons by 90 degrees.
- Can fix idle animations for weapons and players (with only one keyframe inside it). Basically it will add two more keyframes, so Unreal Engine will import it correctly.
- Set fps of the animation automatically, from reading the QC file. If this option is disabled, or QC file is missing, fps will be set to 30.
- With this master skeleton you need only one set of animations, you can even use/blend animations from other weapons. 

![Settings](https://i.imgur.com/jq8lgFM.png)

## How to use
1. Go to ```File > Import > Batch convert CSGO's QC files```

    ![ph01](https://i.imgur.com/xhuu6xG.png)

2. Select the folder with QC and SMD files, choose scale and output path for the converted FBX files.
3. Import some V_hands file inside Unreal (e.g. `v_bare_hands.fbx`).
4. Remove the hands' skeletal mesh, leave only skeleton. Rename the skeleton to `V_Master`
    
    ![ph02](https://i.imgur.com/6nXIEpE.png)

5. Import all hands (except some with the `agr_` prefix) and v_models, choose `V_Master` as the skeleton.

    ![ph03](https://i.imgur.com/intqgDF.png)

6. Import all animations, choose `V_Master_` as the skeleton.

# AGR tools
This part of the addon can be useful when it comes to exporting all models from the Blender scene. It's also export .JSON file for visibility keyframes, which can be used later with my widget for Unreal Engine.
## Features
- Can clean up your Blender scene 
- Can export all models and visibility keyframes from the scene
- Fixes bones during the export

![AGR tools](https://i.imgur.com/SAsVlQU.png)

# If you want to fix or create an animation
- Go to the side panel and open the menu called "QC and SMD"

    ![QC and SMD](https://i.imgur.com/sqz4rhn.png)

- Import hands, weapon and animation you want to use
- Choose hands, weapon and animation in the dropdown menu and press the button "Make constrains"

    ![Constrains](https://i.imgur.com/WltTJrv.gif)

- Edit / create the animation
- Choose the animiation skeleton and click on the "Export selected". Now you can choose scale and the skeleton's root name
- Import the created animation to the Unreal Engine using `V_Master` skeleton

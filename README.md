# io_scene_CSGO
Bones fixing addon for Blender for later usage in Unreal Engine.

Basically these are two addons merged together. 
- The first you can find in ```File > Import > Batch convert CSGO's QC files```. 
- The second is ```at the side panel```.

# Download and install
You can download it [here](https://github.com/adenexvfx/io_scene_CSGO/releases). I also released the [tutorial](https://youtu.be/9r7T2mFlLV4) about this addon and my UE widget.
[Blender Source Tools](http://steamreview.org/BlenderSourceTools/) addon is required for io_scene_CSGO

# Batch QC converter
This part of the addon can batch convert QC and SMD files in the folder. It fixes all the bones of the model

## Features
- Can fix all the bones in V models (scout, mp5sd, revolver, etc). 
- Can remove useless parts of W models during the convertion (hoster strap and holiday wrap for ied).
- You can rotate players models (will affect only new players models in the 'legacy' folder) and W weapons by 90 degrees.
- Can fix idle animations for weapons and players (with only one keyframe inside it). Basically it will add two more keyframes, so Unreal Engine will import it correctly.
- Set fps of the animation automatically, from reading the QC file. If this option is disabled, or QC file is missing, fps will be set to 30.

![Settings](https://i.imgur.com/jq8lgFM.png)

## Thanks to
[Darkhandrob](https://github.com/Darkhandrob) for the main idea (this project started as a branch of AIOX), [Zamb](https://www.youtube.com/channel/UCYx-EP6nZloVJc5gRrSce1g) for some major bugreports, [kitmvm](https://www.youtube.com/c/kitmvm) for providing information about fps values in QC files, [lasa01](https://github.com/lasa01) who pushed me in the right direction so I could fix random Blender crashes.

![Fixed revolver](https://i.imgur.com/bqTW7KL.png)

# AGR tools
This part of the addon can be useful when it comes to exporting all models from the Blender scene. It's also export .JSON file for visibility keyframes, which can be used later with my widget for Unreal Engine.
## Features
- Can clean up your Blender scene 
- Can export all models and visibility keyframes from the scene
- Fixes bones during the export

![AGR tools](https://i.imgur.com/SAsVlQU.png)

# Changelog
v 1.2.8
- Now weird skeleton names must be renamed too during export
- Some refactoring

v 1.2.7
- Fixed pirates (again)

v 1.2.6
- Fixed rotate for skeleton knife
- 'Wristband' sleeve will be skipped now, because it breaks skeleton in UE
- Minor fixes

v 1.2.2
- Added user presets
- Fixed some major bugs
- Sorter function for Batch qc converter now have it's own switch
- Json file with the visibility data now stores correct amount of keyframes

v 1.1.0
- Added the sorter function
- Pirates are fixed now

v 1.0.0
- Changed the method of creating the visibility data dictionary
- Added C4 in cleaner tool
- Only new player models (instead of new and old together) will be converted with the 'filter models' parameter 

v 0.0.2
- AfxCamera now exports correctly
- Fixed animations rotations of v_ knives
- The script won't skip the mag7 anymore
- Added "Fix bones" option to the main settings

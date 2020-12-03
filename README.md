# CS148Project
![Alt text](photon_map.png?raw=true "Title")

Project for Stanford CS148 Fall 2020

### Environment:
Blender 2.90.0 with built-in Python

### Requirements:
numpy, skimage, plyfile, pyntcloud

To install the required libraries to Blender built-in Python easily, refer to the second answer in https://blender.stackexchange.com/questions/5287/using-3rd-party-python-modules

### Instructions:
1. cd to the root folder and open the project: `Blender project.blend`
2. Run `simpleRT_plugin` and `simpleRT_UIpanels`. This will setup the SimpleRT engine. An optional step is to change configurations
4. Run `build_photon_map` to find the pkl files (for the maps) and ply files (to visualize the locations and directions) in `./results` folder
5. (Optional) Visualize the ply photon maps using Point cloud visualizer: https://github.com/daavoo/pyntcloud
6. Run global_illumination to render the photon maps, and find the outcomes in `./results/depth6_c*.png` and `./results/all_channel_path.png`
7. Run `render_light` to show the light, and find the outcomes in `./results/lights.png`
8. Run `combine_images` to get the final image, and find the outcomes in `./results/export.png`

If you have any questions, please contact the authors:

Zhejin Huang: zhejinh@stanford.edu

Pramod Srinivasan: pramods@stanford.edu

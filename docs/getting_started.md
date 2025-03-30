# Getting started
GFAM needs video inputs and a JSON settings file to run.

## Video inputs
GFAM has been tested on a HERO9 Black camera. Videos are assumed to be in .MP4 format. You can submit a single .MP4 file or a directory path that contains multiple .MP4 files.

## Settings
You can use this template to configure the JSON settings.
```
{
    "input_vid":"/path/to/video",
    "project_dir": "/path/to/output",
    "nth_frame": 30,
    "js_path": "/go_forth_and_measure/supplementary_files/telemetry_extraction_hero9.js",
    "rescale_z": true,
    "min_z": none,
    "max_z": none,
    "ori": true,
    "sfm": "RC",
    "prefix": "",
    "north_hem": true,
    "west_hem": true,
    "clean_up": true,
    "config_file": "/go_forth_and_measure/supplementary_files/pix4d.config"
}
```
### input_vid
Filepath to video(s) input.
### project_dir
Filepath for GFAM outputs. GFAM will make this directory. If you pass a non-empty directory, GFAM will error out.
### nth_frame
GFAM will extract every nth frame from the video. i.e. if your video was recorded at 30 FPS and you select`nth_frame=30`, GFAM will extract 1 frame per second. 
### js_path
The available GoPro telemetry streams, as well as their formatting and axes conventions, can change between cameras. If you have a different camera, you can use this as a starting point and consult the [GoPro gpmf-parser GitHub](https://github.com/gopro/gpmf-parser) to make the appropriate modifications.
### rescale_z, min_z, max_z
I have found that the z-axis from the GPS can be quite noisy. If you enable this option GFAM will rescale the z values to be more consistent. If you pass values for `min_z` and `max_z` all GPS values will be rescaled to that range. If you don't include those, it will simply all z levels with the mean. I recommend this for relatively flat areas where the elevation change is less than the noise in the GPS.
### ori
If you enable this, GFAM will include the orientation data and format it for the corresponding SfM software. The HERO9 Black does not have a magnetometer, so this telemetry is not as useful as it otherwise would be. When exporting for Pix4D, it will apply roll, pitch, and yaw as extra tags (this requires the config file). The yaw will be relative to the video beginning, not to true north. You can mitigate this by looking directly north when you begin filming, but you won't be able to account for sensor drift over time. When exporting for RealityCapture, it will create a gravity .xmp file for each image that is used to orient the roll and pitch of images.
### sfm
You can select Pix4D (requires config file) or RealityCapture. If you want to modify this for a different software, you may have to write your own .config file. The orientation axes and metadata tags will be important.
### prefix
You can provide a prefix for images.
### north_hem, west_hem
These are used by ExifTool to write the GPS tags. The default values are True for both. Setting them to False switches to the other hemisphere.
### clean_up
This is an option to clean up the intermediate outputs created by GFAM and to organize multiple videos into a single directory. I recommend leaving this on for almost all scenarios, however it can be helpful to disable it during troubleshooting.
### config_file
Non-standard Exif tags will require a .config file. 
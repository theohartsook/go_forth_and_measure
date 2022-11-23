This is some code that turns GoPro videos into images with the appropriate tags for geolocation and orientation. You can run it by supplying a .JSON modified from this template: \
```
{
    "input_vid": "/path/to/gopro.MP4",
    "project_dir": "/path/for/outputs,
    "nth_frame": int(how many frames you wish to subsample),
    "js_path": "/path/to/go_forth_and_measure/supplementary_files/telemetry_extraction_hero9.js",
    "rescale_z": true,
    "min_z": float(smallest elevation),
    "max_z": float(largest elevation),
    "sfm": "P4D",
    "config_file": "path/to/go_forth_and_measure/supplementary_files/pix4d.config"
}
```
\
Currently only the Hero 9 camera is supported for metadata extraction.
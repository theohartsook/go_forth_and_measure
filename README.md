This is some code that turns GoPro videos into images with the appropriate tags for geolocation and orientation. You can run it by supplying a .JSON modified from this template: \
```
{
    "input_vid":"/path/to/video",
    "project_dir": "/path/to/output",
    "nth_frame": 5,
    "js_path": "/go_forth_and_measure/supplementary_files/telemetry_extraction_hero9.js",
    "gps_tag": true,
    "imu_tag": true,
    "config_file": "/go_forth_and_measure/supplementary_files/pix4d.config"
}
```
\
Currently only the Hero 9 camera is supported for metadata extraction, but please feel free to test on other models.

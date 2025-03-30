This is some code that turns GoPro videos into images with the appropriate tags for structure from motion software. It can export images for Pix4D and RealityCapture. 
<div class="sketchfab-embed-wrapper"> <iframe title="IGARSS 2023 Pix4D - Plot" frameborder="0" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true" allow="autoplay; fullscreen; xr-spatial-tracking" xr-spatial-tracking execution-while-out-of-viewport execution-while-not-rendered web-share src="https://sketchfab.com/models/47c6adf0fc1c40c0926b61d8545163ec/embed"> </iframe> <p style="font-size: 13px; font-weight: normal; margin: 5px; color: #4A4A4A;"> <a href="https://sketchfab.com/3d-models/igarss-2023-pix4d-plot-47c6adf0fc1c40c0926b61d8545163ec?utm_medium=embed&utm_campaign=share-popup&utm_content=47c6adf0fc1c40c0926b61d8545163ec" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> IGARSS 2023 Pix4D - Plot </a> by <a href="https://sketchfab.com/thunr?utm_medium=embed&utm_campaign=share-popup&utm_content=47c6adf0fc1c40c0926b61d8545163ec" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> thunr </a> on <a href="https://sketchfab.com?utm_medium=embed&utm_campaign=share-popup&utm_content=47c6adf0fc1c40c0926b61d8545163ec" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;">Sketchfab</a></p></div>
GFAM uses a JSON file to read the desired settings. Here is an example template: 
```
{
    "input_vid":"/path/to/video",
    "project_dir": "/path/to/output",
    "nth_frame": 30,
    "js_path": "/go_forth_and_measure/supplementary_files/telemetry_extraction_hero9.js",
    "rescale_z": true,
    "min_z": none,
    "max_z": none,
    "imu": true,
    "sfm": "RC",
    "prefix": "",
    "north_hem": true,
    "west_hem": true,
    "clean_up": true,
    "config_file": "/go_forth_and_measure/supplementary_files/pix4d.config"
}
```
You can run GFAM from the CLI by running `python3 gfam_exec.py -i /path/to/settings.json`
You can run GFAM from a GUI by runnning `python3 gfam_gui.py`. This will allow you to load and create new pipelines and run them from the GUI.
\
Currently only the Hero 9 camera is supported for metadata extraction, but please feel free to test on other models.

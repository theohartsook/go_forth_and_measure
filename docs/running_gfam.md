# Running GFAM
## Command Line
You can run GFAM from the CLI by running `python3 gfam_exec.py -i /path/to/settings.json`. This is useful for programmatically processing many videos.
## GUI
You can run GFAM from a GUI by runnning `python3 gfam_gui.py`. This will allow you to load, createm and save new JSON files. You can also run them from the GUI, which will run `gfam_exec.py` in the background. I recommend this as a good starting place, especially if you're just processing one or two videos.
## Docker
This is also made available as a container on DockerHub, available by running `docker pull thunr/gfam-container:latest`.
### Command Line
You can run from the command line by using docker `run -it --rm -v $(pwd):/app/workdir username/gfam-container python gfam_exec.py workdir/gfam_settings.json`.
### GUI
You can run the GUI from the Docker as well using:
```
docker run -it --rm \
    -e DISPLAY=host.docker.internal:0 \
    -v $(pwd):/app/workdir \
    username/gfam-container \
    python gfam_gui.py
```
However, you will probably need to run some extra steps to allow Docker to create the window. I don't make any promises on how to best do that. If you plan on using the frequently, I recommend cloning the repo.
#### MacOS
1) Ensure XQuartz is installed and connections from network clients is enabled (Preferences -> Security)
2) Ensure Xquartz listens to TCP port `defaults write org.xquartz.X11 nolisten_tcp -bool false`
3) Set Display `export DISPLAY=:0`
4) Give Docker access to XQuartz `xhost +127.0.0.1` (each time you restart XQuartz)
5) Run gfam_gui command
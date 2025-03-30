# Notes on collecting videos
## Video settings
I converged on 4K videos at 30 FPS, a 4:3 aspect ratio, and wide lens, which is equivalent to a focal length of 28mm. This produces:
| Field of view    | Degrees |
| -------- | ------- |
| Horizontal  | 92    |
| Vertical | 70    |
| Diagonal    | 113    |
I enable HyperSmooth to stabilize the video a little more. I use an ISO min/max of 100/1600.

## Collecting videos
### Camera placement
We experimented with head-mounted, chest-mounted, and hand-held video collection. The best option is to use a hand-held gimbal. In general, pick whatever you can to stabilize the camera. We found that wearing the camera on the chest produced better results than the head, while allowing hands to be used for fieldwork. This is in line with the initial vision of the project, where you do the fieldwork you were already planning to do and get some video footage/3D reconstructions as a bonus.

### Best practices
- Turn the camera on and let it run for 5-15 minutes before filming.
  - This will minimize GPS error while you film.
- If possible, begin filming with the camera level and pointed north.
  - This gives you a frame of reference for the orientation data.
- After filming has started, verbally state technician name, plot location, and any other important information.
  - Each time you start a recording, by default the camera will create a file named something like `GH016146.MP4`. This is the first video file in the recording `6146`. When the video file becomes too large, a second video will be created with a name like `GH026146.MP4`. These increments in the first two digits show that these videos are all different parts of one recording `6146`. Once you stop filming and start a second recording, a new video file will be created like `GH016147.MP4`.
  - The verbal callout is a quicker and more immediately obvious way to know which videos correspond to what site.
- Avoid large, rapid illumination changes if possible.
- Minimize time with the camera obscured
  - There are some [creative ways to filter unhelpful frames](https://ui.adsabs.harvard.edu/abs/2023AGUFM.B51D1801H/abstract), but the best way is to not generate them in the first place. Each obstruction makes it more difficult for the SfM to track keypoints. If you anticipate them, for instance you need to carry equipment, it's often better to stop recording, and start again once you've finished.
- Use control points where possible
  - GCPs will greatly improve the [accuracy and quality of the reconstruction](ieeexplore.ieee.org/abstract/document/10282278/)
  - Non geo-referenced control points are still helpful, constraining potential camera angles.
- Calibrate the camera in a well-lit environment.
  - Some examples of calibration targets: https://www.tangramvision.com/resources/sensor-calibration-targets 
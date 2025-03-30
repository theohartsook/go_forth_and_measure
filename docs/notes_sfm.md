# Notes on parameterizing SfM
## GPS accuracy
You can use the GPS telemetry to estimate the accuracy on this, but I would suggest 50-100m as a starting point for the horizontal accuracy. Consult the elevation rescaling setting for vertical accuracy recommendations.
## IMU accuracy
This confidence will always be low. In many cases it may be better to allow for the SfM to solve for these directly instead of offering priors.
## Internal camera parameters
Ensure that your chosen camera model accomodates a fisheye lens. If you calibrated the camera previously, use those parameters as an approximate starting place.
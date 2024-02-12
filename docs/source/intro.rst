================
Introduction
================

Hi, welcome to the GFAM documentation!

------------
Installation
------------

There are several dependencies that must first be installed.

Python
======
* numpy
* pandas

Javascript
==========
* fast-csv
* fs
* gpfm-extract
* gopro-telemetry


FFmpeg
======


Exiftool
========

---------------
Getting started
---------------

JSON configuration
------------------
In order to use GFAM, you must record a video using a GoPro camera that contains a GPS, such as Bones or HERO12. After recording your video
configure a JSON file using this template:

.. code-block:: JSON
    :linenos:

    {
        "input_vid":"/path/to/video",
        "project_dir": "/path/to/output",
        "nth_frame": 5,
        "js_path": "/go_forth_and_measure/supplementary_files/telemetry_extraction_hero9.js",
        "gps_tag": true,
        "imu_tag": true,
        "config_file": "/go_forth_and_measure/supplementary_files/pix4d.config"
    }

A few notes on these settings:

* project_dir must be a non-existent directory otherwise GFAM will return an error. This is to avoid accidental overwrites.
* nth_frame will extract every nth frame from the video, functionally it reduces your frame rate and number of images at export.
  For instance if you recorded a video with a frame rate of 30 FPS and use nth_frame=5, the functional frame rate would be 6 FPS,
  so a 1 minute video would produce 360 images.

.. math::

    \text{video length} \times \left(\frac{\text{frames per second}}{nth frame} \right) = \text{number of output images}

* feel free to modify the .js script in supplementary_files to extract additional metadata. I suspect that this script will work for
  additional camera models, but I don't have them to test. You can check your camera and available metadata on the `gpfm-parser repository <https://github.com/gopro/gpmf-parser>`_.
* The GPS and IMU tags control whether or not the extracted images will be tagged, but the metadata will be extracted every time regardless.
  The GPS time is used to provide the write timestamp on each frame (ignoring time zone).
* Exiftool uses this config_file to apply the metadata. If you use a different structure from motion software you may need to modify this.

Running GFAM
------------
Once you've created your JSON configuration file, it's as simple as:

.. code-block:: bash
    gfam_exec.py -i settings.json

GFAM is quite aggressive when it comes to error handling in the settings file and setting up the project. After that, it should
be able to run safely given there are no issues with Exiftool or FFmpeg.

The outputs
-----------
GFAM creates two directories within the specified output. The first is a frame directory that contains the extracted images and their
metadata. These are ready to be used in structure from motion software. The second is a telemetry directory that contains all the telemetry
streams extracted from the GoPro. Only GPS and image orientation (IORI) are used to tag the frames, but the rest are included in case
you would like to utilize them.
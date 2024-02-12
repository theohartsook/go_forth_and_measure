import os
import logging
import sys
import json

from .frame_extraction import extractNthFrames, extractFPS
from .telemetry_cleaning_hero9 import nodeWrapperHERO9, cleanHERO9
from .apply_tags_hero9 import applyTags

def generateDefaultPrefix(input_vid):
    """ Generates a default prefix using the video name.

    :param input_vid: Filepath to input video
    :type input_vid: str

    :return: frame prefix
    :rtype: str
    """
    prefix = os.path.basename(input_vid)
    prefix = os.path.splitext(prefix)[0]
    logging.debug('Generated default prefix ', prefix)

    return prefix

def processVideo(data):
    """ Processes an individual video using JSON settings.

    :param data: Settings import from user-supplied JSON file.
    :type data: dict

    :return: returns 0 after processing is complete
    :rtype: int
    """
    frame_dir, telem_dir = createProjectDirectory(data['project_dir'])
    extractNthFrames(data['input_vid'], frame_dir, data['nth_frame'])
    processTelemetry(data['input_vid'], telem_dir, data['js_path'])
    tagFrames(frame_dir, telem_dir, data['nth_frame'], data['input_vid'], data['gps_tag'], data['imu_tag'], data['config_file'])

    return 0

def processDirectory(data):
    """ Runs processVideo() on all videos in a directory using JSON settings.
    """
    # future function

    return None

def importJSON(json_path):
    """ Imports a user-supplied JSON.

    :param json_path: filepath to JSON file
    :type json_path: str

    :return: returns settings
    :rtype: dict
    """
    with open(json_path) as json_file:
        data = json.load(json_file)
    return data


def createProjectDirectory(project_dir):
    """ Creates the frames and telemetry subdirectories.

    :param project_dir: filepath to project_dir
    :type project_dir: str

    :return: returns filepaths to frame_dir and telem_dir, else terminates
    :rtype: str, str
    """
    frame_dir = os.path.join(project_dir, 'frames')
    telem_dir = os.path.join(project_dir, 'telem')
    os.makedirs(frame_dir, exist_ok=True)
    os.makedirs(telem_dir, exist_ok=True)
    if os.path.exists(frame_dir):
        if os.path.exists(telem_dir):
            return frame_dir, telem_dir
        else:
            logging.error('telem_dir could not be made.')
            sys.exit(1)
    else:
        logging.error('frame_dir could not be made.')
        sys.exit(1)
    

def processTelemetry(input_vid, telem_dir, js_path):
    """ Extracts telemetry from video metadata using JS and gpmf-parser, then cleans the files.

    :param input_vid: filepath to input_vod provided by user
    :type input_vid: str
    :param telem_dir: filepath to telem_dir produced by createProjectDirectory()
    :type telem_dir: str
    :param js_path: Filepath to the JS script
    :type js_path: str

    :return: returns 0 if successful
    :rtype: int
    """
    nodeWrapperHERO9(input_vid,
                     os.path.join(telem_dir, 'GPS.csv'),
                     os.path.join(telem_dir, 'ACCL.csv'),
                     os.path.join(telem_dir, 'GYRO.csv'),
                     os.path.join(telem_dir, 'GRAV.csv'),
                     os.path.join(telem_dir, 'CORI.csv'),
                     os.path.join(telem_dir, 'IORI.csv'),
                     js_path)
    cleanHERO9(telem_dir)

    return 0

def tagFrames(frame_dir, telem_dir, nth_frame, input_vid, gps_tag, imu_tag, config_file):
    """ Tags frames using exiftool
    
    :param frame_dir: filepath frame_dir produced by createProjectDirectory()
    :type frame_dir: str
    :param telem_dir: filepath to telem_dir produced by createProjectDirectory()
    :type telem_dir: str
    :param nth_frame: nth_frame in user-supplied settings
    :type nth_frame: int
    :param input_vid: input_vid in user-supplied settings
    :type input_vid: str
    :param gps_tag: gps_tag in user-supplied settings
    :type gps_tag: bool
    :param imu_tag: imu_tag in user-supplied settings
    :type imu_tag: bool
    :param config_file: config_file in user-supplied settings
    :type config_file: str

    :return: returns 0 if successful
    :rype: int
    """
    fps = extractFPS(input_vid)
    applyTags(frame_dir, telem_dir, nth_frame, gps_tag=gps_tag, imu_tag=imu_tag, fps=fps, config_file=config_file)

    return 0

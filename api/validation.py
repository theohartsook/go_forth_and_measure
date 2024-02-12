import logging
import os
import sys

from .project_management import generateDefaultPrefix

def validateArguments(data):
    """ Wrapper function to validate all data imported with importJSON().

    :param data: Settings import from user-supplied JSON file.
    :type data: dict

    :return: Returns data with optional arguments supplied
    :rtype: dict
    """
    validateJSON(data)
    validateInputVid(data['input_vid'])
    validateJSPath(data['js_path'])
    if data.get('config_file'):
        validateConfigFile(data['config_file'])
    if data.get('prefix') is None:
        data['prefix'] = generateDefaultPrefix(data['input_vid'])
    validateProjectDir(data['project_dir'])
    return data


def validateJSON(data):
    """ Validates that JSON file has all necessary arguments and supplies necessary default arguments.
    
    :param data: Settings imported from user-supplied JSON file.
    :type data: dict

    :return: Returns data if all mandatory arguments included, else terminates.
    :rtype: dict
    """

    if 'input_vid' not in data:
        logging.error('Please specify the path to an input video in the settings JSON. Use "input_vid" as the key.')
        sys.exit(1) 
    if 'project_dir' not in data:
        logging.error('Please specify the path to a new project directory in the settings JSON. Use "project_dir" as the key.')
        sys.exit(1)
    if 'nth_frame' not in data:
        logging.error('Please specify the rate of frame extraction in the settings JSON. Use "nth_frame" as the key.')
        sys.exit(1) 
    if 'js_path' not in data:
        logging.error('Please specify a path to the JavaScript file in the settings JSON. Use "js_path" as the key.')
        sys.exit(1) 
    if 'gps_tag' not in data:
        data['gps_tag'] = False
        logging.warning('No decision on GPS tagging found in the settings JSON, so defaulting to false.'
                        '\nPlease include "gps_tag":"true" if you would like the images to be tagged with GPS coordinates.')
    if 'imu_tag' not in data:
        data['imu_tag'] = False
        logging.warning('No decision on IMU tagging found in the settings JSON, so defaulting to false.'
                        '\nPlease include "imu_tag":"true" if you would like the images to be tagged with IMU estimates.')
    if 'prefix' not in data:
        data['prefix'] = None
        logging.info('No prefix included in the settings JSON.')
    if 'config_file' not in data:
        data['config_File'] = None
        logging.info('No configuration file included the settings JSON.')
        
    return data

def validateInputVid(input_vid, file_ending='.MP4'):
    """ Validates that the input video 1) exists 2) is the correct format.
    
    :param input_vid: Filepath to input_vid in JSON settings.
    :type input_vid: str
    :param file_ending: File format of the input video, defaults to .MP4
    :type file_ending: str

    :return: returns 0 if video passed, else terminates.
    :rtype: int
    """    
    if not os.path.exists(input_vid):
        logging.error('Could not find ', input_vid)
        sys.exit(1)
    if not input_vid.upper().endswith(file_ending):
        logging.error(file_ending, 'is not a supported file format')
        sys.exit(1)
    else:
        logging.info('input_vid validated.')
        return 0

def validateJSPath(js_path):
    """ Validates that the JavaScript path 1) exists 2) is a .js
    
    :param js_path: Filepath to js_path in JSON settings.
    :type js_path: str

    :return: returns 0 if JS path passed, else terminates.
    :rtype: int
    """    
    if not os.path.exists(js_path):
        logging.error('Could not find ', js_path)
        sys.exit(1)
    if not js_path.lower().endswith('.js'):
        logging.error('The only current support file format is .js')
        sys.exit(1)
    else:
        logging.info('js_path validated.')
        return 0

def validateProjectDir(project_dir):
    """ Validates that project dir 1) does not already exist 2) makes directory.

    :param project_dir: Filepath to project_dir
    :type project_dir: str

    :return: returns 0 if project_dir successfully made, else terminates.
    :rtype: int
    """
    if os.path.exists(project_dir):
        logging.error('project_dir already exists.')
        sys.exit(1)
    else:
        os.mkdir(project_dir)
        if os.path.exists(project_dir):
            logging.info('project_dir successfully created.')
            return 0
        else:
            logging.error('project dir could not be made.')
            sys.exit(1)

def validateConfigFile(config_file):
    """ Validates that the supplied config_file 1) exists 2) is a .config
    
    :param config_file: Filepath to config_file in JSON settings.
    :type config_file: str

    :return: returns 0 if config file passes, else terminates.
    :rtype: int
    """    
    if not os.path.exists(config_file):
        logging.error('Could not find ', config_file)
        sys.exit(1)
    if not config_file.lower().endswith('.config'):
        logging.error('The only current supported file format is .config.')
        sys.exit(1)
    else:
        logging.info('config_file validated.')
        return 0


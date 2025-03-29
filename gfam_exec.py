import os, json, argparse, logging

from code.frame_extraction import extractAllFrames, selectNthFrames
from code.telemetry_cleaning_hero9 import cleanHERO9, nodeWrapperHERO9
from code.apply_tags_hero9 import applyTags, cleanUpIntermediate

def processVideo(input_video, project_dir, settings):
    """ Wrapper function to process a single video.

    :param input_video: Filepath to the target video
    :type input_video: str
    :param project_dir: Filepath to the directory where frames are processed
    :type project_dir: str
    :param settings: dictionary extracted from JSON settings file
    :type settings: dictonary
    """

    if os.path.exists(project_dir):
        if len(os.listdir(project_dir)) > 0:
            logging.error(f"Project {project_dir} already exists and is non empty.")
        else:
            logging.warning(f"Project {project_dir} already exists, but is empty.")
    else:
        os.makedirs(project_dir)
    
    frame_dir = os.path.join(project_dir, 'frames')
    os.mkdir(frame_dir)
    extractAllFrames(input_video, frame_dir, prefix=settings['prefix'])

    subsample_dir = os.path.join(project_dir, f"subsample_{settings['nth_frame']}_frames")
    os.mkdir(subsample_dir)
    selectNthFrames(frame_dir, subsample_dir, settings['nth_frame'])

    telem_dir = os.path.join(project_dir, 'telem')
    os.mkdir(telem_dir)

    if settings['sfm'] == 'P4D':
        if settings['ori'] == True:
            nodeWrapperHERO9(
                input_video,
                output_gps = os.path.join(telem_dir, 'GPS.csv'),
                output_accl = os.path.join(telem_dir, 'ACCL.csv'),
                output_gyro = os.path.join(telem_dir, 'GYRO.csv'),
                output_iori = os.path.join(telem_dir, 'IORI.csv'),
                js_path = settings['js_path']
            )
        else:
            nodeWrapperHERO9(
                input_video,
                output_gps = os.path.join(telem_dir, 'GPS.csv'),
                js_path = settings['js_path']
            )
    elif settings['sfm'] == 'RC':
        if settings['ori'] == True:
            nodeWrapperHERO9(
                input_video,
                output_gps = os.path.join(telem_dir, 'GPS.csv'),
                output_grav = os.path.join(telem_dir, 'GRAV.csv'),
                js_path = settings['js_path']
            )
        else:
            nodeWrapperHERO9(
                input_video,
                output_gps = os.path.join(telem_dir, 'GPS.csv'),
                js_path = settings['js_path']
            )

    cleanHERO9(telem_dir, rescale_z=settings['rescale_z'], min_z=settings['min_z'], max_z=settings['max_z'])

    if settings['sfm'] == 'P4D':
        if settings['ori'] == True:
            gyro_csv = os.path.join(telem_dir, 'GYRO.csv') if settings['ori'] else None
            applyTags(
                subsample_dir,
                gps_csv=os.path.join(telem_dir, 'GPS.csv'),
                ori_csv=gyro_csv,
                sfm=settings['sfm'],
                north_hem=settings['north_hem'],
                west_hem=settings['west_hem'],
                config_file=settings['config_file']
            )
    elif settings['sfm'] == 'RC' and settings['ori'] == True:
        grav_csv = os.path.join(telem_dir, 'GRAV.csv') if settings['ori'] else None
        applyTags(
        subsample_dir,
        gps_csv=os.path.join(telem_dir, 'GPS.csv'),
        ori_csv=grav_csv,
        sfm=settings['sfm'],
        north_hem=settings['north_hem'],
        west_hem=settings['west_hem']
        )
    elif settings['sfm'] == 'RC' and settings['ori'] == False:
        applyTags(
        subsample_dir,
        gps_csv=os.path.join(telem_dir, 'GPS.csv'),
        north_hem=settings['north_hem'],
        sfm=settings['sfm'],
        west_hem=settings['west_hem']
        )
    else:
        applyTags(
        subsample_dir,
        gps_csv=os.path.join(telem_dir, 'GPS.csv'),
        north_hem=settings['north_hem'],
        west_hem=settings['west_hem']
        )
    logging.info(f"Finished processing {input_video}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help='path to JSON settings', type=str)
    args = parser.parse_args()

    with open(args.i) as json_file:
        data = json.load(json_file)
    input_path = data['input_vid']
    project_dir = data['project_dir']

    settings = {
        'nth_frame': data['nth_frame'],
        'js_path': data['js_path'],
        'rescale_z': data['rescale_z'],
        'min_z': data['min_z'],
        'max_z': data['max_z'],
        'ori': data['ori'],
        'sfm': data['sfm'],
        'prefix': data['prefix'],
        'north_hem': data['north_hem'],
        'west_hem': data['west_hem'],
        'clean_up': data['clean_up'],
        'config_file': data['config_file']
    }

    if not settings['prefix'].endswith('_'):
        if settings['prefix'] == '':
            logging.info('No prefix provided.')
        else:
            logging.warning(f"Adding trailing underscore to prefix: {settings['prefix']}.")
            settings['prefix'] = settings['prefix']  + '_'

    if os.path.isdir(input_path):
        video_extensions = ('.MP4')
        video_files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.upper().endswith(video_extensions)
        ]
        if not video_files:
            logging.error(f"No compatible video files found in the specified directory {input_path}.")
        else:
            for video_file in video_files:
                video_name = os.path.splitext(os.path.basename(video_file))[0]
                video_project_dir = os.path.join(project_dir, video_name)
                logging.info(f"Processing video: {video_file} -> Project directory: {video_project_dir}")
                video_settings = settings.copy()
                video_settings['prefix'] = f"{video_name}_{video_settings['prefix']}"
                
                processVideo(video_file, video_project_dir, video_settings)
    else:
        video_name = os.path.splitext(os.path.basename(input_path))[0]
        video_project_dir = os.path.join(project_dir, video_name)
        video_settings = settings.copy()
        video_settings['prefix'] = f"{video_name}_{video_settings['prefix']}"
        logging.info(f"Processing video: {input_path} -> Project directory: {video_project_dir}")
        processVideo(input_path, video_project_dir, video_settings)

    if settings['clean_up'] == True:
        cleanUpIntermediate(project_dir, settings['nth_frame'])

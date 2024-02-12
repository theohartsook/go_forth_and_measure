import os, json, argparse

from code.frame_extraction import extractAllFrames, selectNthFrames
from code.telemetry_cleaning_hero9 import cleanHERO9, nodeWrapperHERO9
from code.apply_tags_hero9 import applyTags

parser = argparse.ArgumentParser()
parser.add_argument('-i', help='path to JSON settings', type=str)
args = parser.parse_args()

if __name__ == "__main__":
    with open(args.i) as json_file:
        data = json.load(json_file)
    input_vid = data['input_vid']
    project_dir = data['project_dir']
    nth_frame = data['nth_frame']
    js_path = data['js_path']
    rescale_z = data['rescale_z']
    min_z = data['min_z']
    max_z = data['max_z']
    imu = data['imu']
    sfm = data['sfm']
    prefix = data['prefix']
    config_file = data['config_file']

    settings = {'input_vid':input_vid,
                'project_dir':project_dir,
                'nth_frame':nth_frame,
                'js_path':js_path,
                'rescale_z':rescale_z,
                'min_z':min_z,
                'max_z':max_z,
                'imu':imu,
                'sfm':sfm,
                'prefix': prefix,
                'config_file':config_file}
    json_object = json.dumps(settings, indent=4)
    
    if os.path.exists(project_dir):
        print('project already exists')
    else:
        os.mkdir(project_dir)

    frame_dir = project_dir +'/frames'
    os.mkdir(frame_dir)

    extractAllFrames(input_vid, frame_dir, prefix=prefix)

    subsample_dir = project_dir + '/subsample_' + str(nth_frame) + '_frames'
    os.mkdir(subsample_dir)

    selectNthFrames(frame_dir, subsample_dir, nth_frame)

    telem_dir = project_dir + '/telem'
    os.mkdir(telem_dir)

    nodeWrapperHERO9(input_vid,
                        telem_dir + '/GPS.csv',
                        telem_dir + '/ACCL.csv',
                        telem_dir + '/GYRO.csv',
                        telem_dir + '/GRAV.csv',
                        telem_dir + '/CORI.csv',
                        telem_dir + '/IORI.csv',
                        js_path)
 
    cleanHERO9(telem_dir, rescale_z=rescale_z, min_z=min_z, max_z=max_z)

    if imu is True:
        gyro_csv = telem_dir + '/GYRO.csv'
        
    else:
        gyro_csv = None

    if sfm == 'P4D':
        applyTags(subsample_dir,
                  gps_csv = telem_dir + '/GPS.csv',
                  gyro_csv = gyro_csv,
                  for_P4D=True,
                  config_file=config_file)

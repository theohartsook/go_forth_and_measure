import os

from frame_extraction import extractAllFrames, selectNthFrames
from telemetry_cleaning_hero9 import cleanHERO9, nodeWrapperHERO9
from apply_tags_hero9 import applyTags

#####
# Enter your values here!
#####

input_vid = '/Users/theo/Pictures/quad_telem_test/GH011541.MP4'
project_dir = '/Users/theo/Desktop/cool_beans'
nth_frame = 30
js_path = '/Users/theo/Documents/GitHub/go_forth_and_measure/supplementary_files/telemetry_extraction_hero9.js'
flatten_z = True
sfm = 'P4D'
config_file = '/Users/theo/Documents/GitHub/go_forth_and_measure/supplementary_files/pix4d.config'

#####

if os.path.exists(project_dir):
    print('project already exists')
else:
    os.mkdir(project_dir)

frame_dir = project_dir +'/frames'
os.mkdir(frame_dir)

extractAllFrames(input_vid, frame_dir)

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


cleanHERO9(telem_dir, flatten_z=flatten_z)

if sfm == 'P4D':
    applyTags(subsample_dir,
                gps_csv = telem_dir + '/GPS.csv', 
                gyro_csv = telem_dir + '/GYRO.csv',
                for_P4D=True,
                config_file=config_file)

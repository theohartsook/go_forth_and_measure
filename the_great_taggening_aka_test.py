
from post_processing import selectNthFrames
from telemetry_extraction import extractTelemetry
from frame_extraction import extractAllFrames, timeStampFrames
from tag_frames import applyTags

input_video = '/Users/theo/Pictures/GP_20211016_NV_WHITELL_GROUP4_PLOT1/mp4/GH011526.MP4'

frame_dir = '/Users/theo/Desktop/hootananny/frames'
gyro_csv = '/Users/theo/Desktop/hootananny/gyro.csv'
gps_csv = '/Users/theo/Desktop/hootananny/gps.csv'
accl_csv = '/Users/theo/Desktop/hootananny/accl.csv'
magn_csv = '/Users/theo/Desktop/hootananny/magn.csv'

labeled_dir = '/Users/theo/Desktop/hootananny/labeled_frames'

js_path = '/Users/theo/Documents/GitHub/go_forth_and_measure/supplementary_files/telemetry_extraction.js'
config_file = '/Users/theo/Documents/GitHub/go_forth_and_measure/supplementary_files/pix4d.config'

out_dir = '/Users/theo/Desktop/hootananny/out'

extractTelemetry(input_video, gyro_csv, accl_csv, magn_csv, gps_csv, js_path)

#extractAllFrames(input_video, frame_dir, prefix='frame_', sig_fig=7, file_ending='.jpg')

timeStampFrames(input_video, frame_dir, labeled_dir)

applyTags(labeled_dir, gyro_csv, gps_csv, config_file, file_ending='.jpg', west_hem=True, for_P4D=True)

selectNthFrames(labeled_dir, out_dir)
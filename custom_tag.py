from gopro_telemetry_extraction import tagFrames

input_vid = '/Users/theo/Desktop/manzanita_park_test/mp4/GH011553.MP4'

frame_dir = '/Users/theo/Desktop/manzanita_park_test/frames/vid_3'

output_dir = '/Users/theo/Desktop/manzanita_park_test/geotagged_images/vid_3'

gyro_csv = '/Users/theo/Desktop/manzanita_park_test/IMU/GYRO/filtered_gyro_3.csv'

gps_csv = '/Users/theo/Desktop/manzanita_park_test/gps/filtered_gps_3.csv'

config = '/Users/theo/Documents/GitHub/go_forth_and_measure/supplementary_files/pix4d.config'

tagFrames(input_vid, frame_dir, gyro_csv, gps_csv, output_dir, config)
import argparse, os, sys

from gooey import Gooey
from gopro_telemetry_extraction import videosToFrames

@Gooey
def main():
    parser = argparse.ArgumentParser(description='Convert GoPro MP4s to images with telemetry')
    parser.add_argument('video_dir', type=str,
                        help='Filepath to the directory with videos')
    parser.add_argument('imu_root', type=str,
                        help='Filepath to the directory where IMU data will be stored for each video')
    parser.add_argument('gps_root', type=str,
                        help='Filepath to the directory where GPS data will be stored for each video')
    parser.add_argument('js_path', type=str,
                        help='Filepath to the JS script')
    parser.add_argument('temp_root', type=str,
                        help='Filepath to a root directory where temporary frames will be stored')
    parser.add_argument('output_root', type=str,
                        help='Filepath to the directory where the tagged frames will be stored')
    parser.add_argument('config_file', type=str,
                        help='Filepath to the config file for exif_tool.')
    parser.add_argument('--final_dir', type=str,
                        help='One directory for all frames')
    parser.add_argument('--file_ending', type=str,
                        help='Target ending for the videos')

    args = parser.parse_args()

    videosToFrames(args.video_dir, args.imu_root, args.gps_root, args.js_path, args.temp_root, args.output_root, args.final_dir, args.file_ending)

if __name__ == '__main__':
    main()
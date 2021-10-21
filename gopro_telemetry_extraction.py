import logging
import subprocess
import shutil
import os

import numpy as np
import pandas as pd

from bisect import bisect_left

# High level

def videosToFrames(video_dir, imu_root, gps_root, js_path, temp_root, output_root, config_file, final_dir=None, file_ending='.MP4'):
    """ Converts a directory of GoPro videos and converts them to frames tagged with GPS and IMU. 

    :param video_dir: Filepath to the directory with videos
    :type video_dir: str
    :param imu_root: Filepath to the directory where IMU data will be stored for each video.
    :type imu_root: str
    :param gps_root: Filepath to the directory where GPS data will be stored for each video.
    :type gps_root: str
    :param js_path: Filepath to the JS script.
    :type js_path: str
    :param temp_root: Filepath to a root directory where temporary frames will be stored.
    :type temp_root: str
    :param output_root: Filepath to the directory where the tagged frames will be stored.
    :type output_root: str
    :param config_file: Filepath to the config file for exif_tool.
    :type imu_root: str
    :param final_dir: If a filepath is supplied, all frames are saved in one directory, defaults to None. 
    :type final_dir: str
    :param file_ending: Target ending for the videos, defaults to '.MP4'
    :type file_ending: str
    """

    logging.info('Begin videosToFrames.')

    counter = 1
    if not os.path.exists(imu_root):
        logging.warning('Making directory %s', imu_root)
        os.makedirs(imu_root)
    if not os.path.exists(gps_root):
        logging.warning('Making directory %s', gps_root)
        os.makedirs(gps_root)
    for i in sorted(os.listdir(video_dir)):
        if not i.endswith(file_ending):
            continue
        logging.info('Processing video %s', counter)
        input_video = video_dir + '/' + i
        logging.debug('Processing video %s', input_video)
        imu_csv = imu_root + '/imu_' + str(counter) + '.csv'
        gps_csv = gps_root + '/gps_' + str(counter) + '.csv'
        temp_dir = temp_root + '/temp_' + str(counter)
        output_dir = output_root + '/vid_' + str(counter)
        if not os.path.exists(temp_dir):
            logging.warning('Making directory %s', temp_dir)
            os.makedirs(temp_dir)
        if not os.path.exists(output_dir):
            logging.warning('Making directory %s', output_dir)
            os.makedirs(output_dir)
        buildAndTagFrames(input_video, imu_csv, gps_csv, js_path, temp_dir, output_dir, config_file)
        counter += 1
    if final_dir == True:
        if not os.path.exists(final_dir):
            logging.warning('Making directory %s', final_dir)
            os.makedirs(final_dir)
        saveFinalOutputs(output_root, final_dir)

def buildAndTagFrames(input_video, imu_csv, gps_csv, js_path, temp_dir, output_dir, config_file):
    """ Extracts frames from a GoPro video and tags them with GPS and IMU data. 

    :param input_video: Filepath to the target video
    :type input_video: str
    :param imu_csv: Filepath where IMU data will be saved.
    :type imu_csv: str
    :param gps_csv: Filepath where GPS data will be saved.
    :type gps_csv: str
    :param js_path: Filepath to the JS script.
    :type js_path: str
    :param temp_dir: Filepath to a temp directory where frames will be stored.
    :type temp_dir: str
    :param output_dir: Filepath to the directory where the tagged frames will be stored.
    :type output_dir: str
    :param config_file: Filepath to the config file for exif_tool.
    :type imu_root: str
    """

    nodeWrapper(input_video, imu_csv, gps_csv, js_path)
    logging.debug('Node finished')
    temp_imu = temp_dir + '/imu.csv'
    temp_gps = temp_dir + '/gps.csv'
    cleanIMU(imu_csv, temp_imu)
    cleanGPS(gps_csv, temp_gps)

    extractAllFrames(input_video, temp_dir)

    fps = extractFPS(input_video)

    labelFramesWithCTS(temp_dir, output_dir, fps=fps)

    applyTags(output_dir, temp_imu, temp_gps, config_file)


def applyTags(input_dir, imu_csv, gps_csv, config_file, file_ending='.jpg', west_hem=True):
    """ Tags a directory of cts labelled frames with their GPS and IMU data using exif_tool.

    :param input_dir: Filepath to the directory of labelled frames.
    :type input_video: str
    :param imu_csv: Filepath to the IMU data (must be cleaned with cleanIMU())
    :type imu_csv: str
    :param gps_csv: Filepath to the GPS data (must be cleaned with cleanGPS())
    :type gps_csv: str
    :param fps: FPS of the original video.
    :type fps: int
    :param config_file: Filepath to the config file for exif_tool.
    :type imu_root: str
    :param file_ending: Target ending for the frames, defaults to '.jpg'
    :type file_ending: str
    :param west_hem: Controls whether longitude is written in W hemisphere, defaults to True
    :type west_hem: bool
    """

    for i in sorted(os.listdir(input_dir)):
        if not i.endswith(file_ending):
            logging.debug('Skipping %s', i)
            continue
        frame = input_dir + '/' + i
        info = i.split('_')
        cts = info[-1]
        cts = int(cts[:-4])
        #
        imu_df = pd.read_csv(imu_csv)
        imu_cts = sorted(imu_df['cts'])
        gps_df = pd.read_csv(gps_csv)
        gps_cts = sorted(gps_df['cts'])
        closest_imu = findClosestCTS(cts, imu_cts)
        imu_row = imu_df.loc[imu_df['cts'] == closest_imu]
        closest_gps = findClosestCTS(cts, gps_cts)
        gps_row = gps_df.loc[gps_df['cts'] == closest_gps]
        lat = gps_row['lat'].iloc[0]
        lon = gps_row['lon'].iloc[0]
        elev = gps_row['elev'].iloc[0]
        pitch = imu_row['pitch'].iloc[0]
        roll = imu_row['roll'].iloc[0]
        yaw = imu_row['yaw'].iloc[0]
        logging.debug('Found telemetry tags')
        tagging_call = ['exiftool', '-config', config_file, '-GPSLatitude ='+str(lat), '-GPSLongitude ='+str(lon), '-GPSAltitude ='+str(elev), '-Pitch='+str(pitch), '-Roll='+str(roll), '-Yaw='+str(yaw), frame]
        if west_hem == True:
            tagging_call.append('-GPSLongitudeRef=West')
        subprocess.run(tagging_call)

def saveFinalOutputs(input_root, output_dir, file_ending='.jpg'):
    """ Saves the fully tagged and labelled frames with unique filenames.
    :param input_root: Filepath to the input root created by videosToFrames()
    :type fps: str
    :param output_dir: Filepath to the final output directory.
    :type output_dir: str
    :param file_ending: Target ending for the frames, defaults to '.jpg'
    :type file_ending: str
    """

    for i in sorted(os.listdir(output_dir)):
        if not os.path.isdir(input_root + '/' + i):
            logging.debug('Skipping %s', i)
            continue
        vid_tag = i
        input_dir = input_root + '/' + i
        for j in sorted(os.listdir(input_dir)):
            if not j.endswith(file_ending):
                logging.debug('Skipping %s', j)
                continue
            old_img = input_dir + '/' + j
            new_img = output_dir + '/' + vid_tag + '_' + j
            shutil.copy(old_img, new_img)
            logging.debug('Final output saved %s', new_img)

# Low level

def labelFramesWithCTS(input_dir, output_dir, fps=60, file_ending='.jpg'):
    """ Labels a directory of frames with their approximate camera time.

    :param input_dir: Filepath to the directory of frames.
    :type input_video: str
    :param output_dir: Filepath to the directory where the labelled frames will be stored.
    :type output_dir: str
    :param fps: FPS of the original video.
    :type fps: int
    :param file_ending: Target ending for the frames, defaults to '.jpg'
    :type file_ending: str
    """

    cts_per_frame = 1/(fps/1000)
    logging.debug('CTS per frame: %s', cts_per_frame)
    counter = 0
    for i in sorted(os.listdir(input_dir)):
        if not i.endswith(file_ending):
            continue
        info = i.split('_')
        frame = info[-1]
        frame = frame[:-4]
        if int(frame) >= counter and int(frame) < counter*cts_per_frame:
            old_file = input_dir + '/' + i
            new_file = output_dir + '/frame_' + str(frame) + '_cts_' + str(int(counter)) + '.jpg'
            shutil.copy(old_file, new_file)
        else:
            counter += cts_per_frame
            old_file = input_dir + '/' + i
            new_file = output_dir + '/frame_' + str(frame) + '_cts_' + str(int(counter)) + '.jpg'
            shutil.copy(old_file, new_file)
        logging.debug('Frame %s labelled', counter)


def findClosestCTS(cts, cts_list):
    """ Uses bisection search to find the nearest neighbor for a CTS.

    :param cts: The camera time (ms) to match.
    :type cts: int
    :param cts_list: A list of all CTS
    :type cts_list: list of ints

    :return: the matched cts.
    :rtype: int
    """

    logging.debug('Bisection search starts for %s', cts)
    pos = bisect_left(cts_list, cts)
    if pos == 0:
        return cts_list[0]
    if pos == len(cts_list):
        return cts_list[-1]
    before = cts_list[pos - 1]
    after = cts_list[pos]
    if after - cts < cts - before:
        logging.debug('Found CTS %s', after)
        return after
    else:
        logging.debug('Found CTS %s', before)
        return before



def cleanGPS(input_gps, output_gps):
    """ Reformats the JS extraction outputs.

    :param input_gps: Filepath to the GPS output from nodeWrapper()
    :type input_gps: str
    :param output_gps: Filepath to where the reformated GPS will be stored.
    :type output_gps: str
    """

    gps_in = pd.read_csv(input_gps)
    gps_in['lat'] = 0
    gps_in['lon'] = 0
    gps_in['elev'] = 0

    for index, row in gps_in.iterrows():
        info = row['value'].split(',')
        gps_in.loc[index, 'lat'] = info[0]
        gps_in.loc[index, 'lon'] = info[1]
        gps_in.loc[index, 'elev'] = info[2]
    gps_out = gps_in.drop('value', 1)
    gps_out.to_csv(output_gps, index=False)
    logging.debug('GPS data cleaned.')

def cleanIMU(input_imu, output_imu):
    """ Reformats the JS extraction outputs.

    :param input_imu: Filepath to the IMU output from nodeWrapper()
    :type input_imu: str
    :param output_imu: Filepath to where the reformated IMU will be stored.
    :type output_imu: str
    """

    imu_in = pd.read_csv(input_imu)
    imu_in['lat'] = 0
    imu_in['lon'] = 0
    imu_in['elev'] = 0

    for index, row in imu_in.iterrows():
        info = row['value'].split(',')
        imu_in.loc[index, 'pitch'] = info[0]
        imu_in.loc[index, 'roll'] = info[1]
        imu_in.loc[index, 'yaw'] = info[2]
    imu_out = imu_in.drop('value', 1)
    imu_out.to_csv(output_imu, index=False)
    logging.debug('IMU data cleaned.')

# Wrappers

def extractFPS(input_video):
    """ Wrapper for ffmpeg to get the true FPS of a video. 

    :param input_video: Filepath to the target video
    :type input_video: str

    :return: returns the FPS of the input video.
    :rtype: int
    """

    command = ['ffprobe', '-v', '0', '-of', 'csv=p=0' ,'-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', input_video]
    info = subprocess.check_output(command).decode("utf-8")
    info = info.strip()
    info = info.split('/')
    fps = int(info[0])/int(info[1])
    logging.debug('FPS: %s', fps)

    return fps

def nodeWrapper(input_video, output_imu, output_gps, js_path):
    """ Wrapper to call JS script. 

    :param input_video: Filepath to the target video
    :type input_video: str
    :param output_imu: Filepath where IMU data will be saved.
    :type output_imu: str
    :param output_gps: Filepath where GPS data will be saved.
    :type output_gps: str
    :param js_path: Filepath to the JS script.
    :type js_path: str
    """

    extract_telemetry = ['node', js_path, input_video, output_imu, output_gps]
    subprocess.run(extract_telemetry)

def extractAllFrames(input_video, output_dir, prefix='frame_', sig_fig=7, file_ending='.jpg'):
    """ Extracts all frames from a video using ffmpeg. 

    :param input_video: Filepath to the target video
    :type input_video: str
    :param output_dir: Filepath to the directory where the tagged frames will be stored.
    :type output_dir: str
    :param prefix: Prefix for the extracted frames, defaults to 'frame_'
    :type prefix: str
    :param sig_fig: Controls the length of the frame IDs, defaults to 7 (i.e. 0000001-9999999)
    :type sig_fig: int
    :param file_ending: Sets the frame output format, defaults to '.jpg'
    :type file_ending: str
    """

    logging.debug('Frame extraction starts')
    output_frames = output_dir + '/' + prefix + '%' + str(sig_fig) + 'd' + file_ending
    frame_extraction_call = ['ffmpeg', '-i', input_video,  output_frames]
    subprocess.call(frame_extraction_call)
    logging.debug('Frame extraction finished.')


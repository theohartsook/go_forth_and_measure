
import pandas as pd
import numpy as np
import os
import logging
import subprocess
from bisect import bisect_left

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

def applyTags(input_dir, gps_csv=None, gyro_csv=None, for_P4D=False, fps=30, file_ending='.jpg', west_hem=True, config_file=None):
    """ Tags a directory of cts labelled frames with their GPS and GYRO data using exif_tool.

    :param input_dir: Filepath to the directory of labelled frames.
    :type input_video: str

    :param gps_csv: Filepath to the GPS data (must be cleaned with cleanGPS())
    :type gps_csv: str
    :param gyro_csv: Filepath to the GYRO data (must be cleaned with cleanGYRO()), defaults to None
    :type gyro_csv: str
    :param fps: FPS of the original video.
    :type fps: int
    :param config_file: Filepath to the config file for exif_tool.
    :param file_ending: Target ending for the frames, defaults to '.jpg'
    :type file_ending: str
    :param west_hem: Controls whether longitude is written in W hemisphere, defaults to True
    :type west_hem: bool
    :param for_P4D: Modifies GYRO values for inputs to Pix4D, defaults to False
    :type for_P4D: bool
    """

    if gps_csv is not None:
        gps_df = pd.read_csv(gps_csv)
    if gyro_csv is not None:
        gyro_df = pd.read_csv(gyro_csv)

    for i in sorted(os.listdir(input_dir)):
        if not i.endswith(file_ending):
            logging.debug('Skipping %s', i)
            continue
        frame = input_dir + '/' + i
        info = i.split('_')
        cts = info[-1]
        cts = float(cts[:-4])/fps*1000
        tagging_call = ['exiftool']
        if gps_csv is not None:
            gps_cts = sorted(gps_df['cts'])
            closest_gps = findClosestCTS(cts, gps_cts)
            gps_row = gps_df.loc[gps_df['cts'] == closest_gps]
            lat = gps_row['lat'].iloc[0]
            lon = gps_row['lon'].iloc[0]
            elev = gps_row['elev'].iloc[0]
            logging.debug('Found telemetry tags')
            tagging_call.extend(['-GPSLatitude ='+str(lat), '-GPSLongitude ='+str(lon), '-GPSAltitude ='+str(elev)])
            if west_hem == True:
                tagging_call.append('-GPSLongitudeRef=West')    
        if gyro_csv is not None:
            gyro_cts = sorted(gyro_df['cts'])
            closest_gyro = findClosestCTS(cts, gyro_cts)
            gyro_row = gyro_df.loc[gyro_df['cts'] == closest_gyro]
            if for_P4D == True:
                rY = ((gyro_row['rX'].iloc[0])/np.pi*180)+90
                rX = (gyro_row['rY'].iloc[0])/np.pi*180
                rZ = (gyro_row['rZ'].iloc[0])/np.pi*180
            else:
                rY = gyro_row['rY'].iloc[0]
                rX = gyro_row['rX'].iloc[0]
                rZ = gyro_row['rZ'].iloc[0]
            tagging_call.insert(1, '-config')
            tagging_call.insert(2, config_file)
            tagging_call.extend(['-Pitch ='+str(rY), '-Roll ='+str(rX), '-Yaw ='+str(rZ)])
        tagging_call.extend(['-overwrite_original', frame])
        subprocess.run(tagging_call)


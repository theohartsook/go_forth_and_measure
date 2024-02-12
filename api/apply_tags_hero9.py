
import pandas as pd
import numpy as np
import os
import logging
import subprocess
from bisect import bisect_left

# . makes them relative paths
from .telemetry_cleaning_hero9 import convertGPSTimeForEXIFTool
from .telemetry_filters import convertIORItoEuler

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
    
def applyTags(input_dir, telem_dir, nth_frame, fps=30, gps_tag=True, imu_tag=False, file_ending='.jpg', west_hem=True, config_file=None):
    # load relevant data
    gps_csv = os.path.join(telem_dir, 'GPS.csv')
    gps_df = pd.read_csv(gps_csv)
    gps_cts = sorted(gps_df['cts'])
    if imu_tag is True:
        iori_csv = os.path.join(telem_dir, 'IORI.csv')
        iori_df = pd.read_csv(iori_csv)
        iori_df = convertIORItoEuler(iori_df)
        imu_cts = sorted(iori_df['cts'])

    counter = 0
    for i in sorted(os.listdir(input_dir)):
        if not i.endswith(file_ending):
            logging.debug('Skipping %s', i)
            continue
        frame = input_dir + '/' + i
        cts = (nth_frame/fps*1000*counter)+1
        tagging_call = ['exiftool']
        closest_gps = findClosestCTS(cts, gps_cts)
        gps_row = gps_df.loc[gps_df['cts'] == closest_gps]

        timestamp = convertGPSTimeForEXIFTool(gps_row['date'].iloc[0])
        if timestamp is not None:
            tagging_call.append('-DateTimeOriginal=' + timestamp)
        else:
            # Handle the case where timestamp couldn't be parsed
            logging.error('Could not parse timestamp for frame: ' + str(i))
        logging.debug('Found telemetry tags')
        if gps_tag is True:
            logging.info('Applying GPS tag')
            lat = gps_row['lat'].iloc[0]
            lon = gps_row['lon'].iloc[0]
            elev = gps_row['elev'].iloc[0]
            tagging_call.extend(['-GPSLatitude ='+str(lat), '-GPSLongitude ='+str(lon), '-GPSAltitude ='+str(elev)])
            if west_hem == True:
                tagging_call.append('-GPSLongitudeRef=West')      
        if imu_tag is True:
            logging.info('Applying orientation tag')
            closest_imu = findClosestCTS(cts, imu_cts)
            iori_row = iori_df.loc[iori_df['cts'] == closest_imu]
            roll = iori_row['roll'].iloc[0]
            pitch = iori_row['pitch'].iloc[0]
            yaw = iori_row['yaw'].iloc[0]
            tagging_call.insert(1, '-config')
            tagging_call.insert(2, config_file)
            tagging_call.extend(['-Pitch ='+str(pitch), '-Roll ='+str(roll), '-Yaw ='+str(yaw)])
        logging.debug(tagging_call)
        tagging_call.extend(['-overwrite_original', frame])
        subprocess.run(tagging_call)
        counter +=1
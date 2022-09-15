import logging, subprocess

import numpy as np
import pandas as pd

from scipy.signal import savgol_filter

def extractTelemetry(input_video, gyro_csv, accl_csv, magn_csv, gps_csv, js_path):
    """ Cleans the GPS and IMU data and extracts frames from a GoPro video

    :param input_video: Filepath to the target video
    :type input_video: str
    :param gyro_csv: Filepath where GYRO data will be saved.
    :type gyro_csv: str
    :param accl_csv: Filepath where ACCL data will be saved.
    :type accl_csv: str
    :param gps_csv: Filepath where GPS data will be saved.
    :type gps_csv: str
    :param magn_csv: Filepath where MAGN data will be saved.
    :type magn_csv: str
    :param js_path: Filepath to the JS script.
    :type js_path: str
    :param temp_dir: Filepath to a temp directory where frames will be stored.
    :type temp_dir: str
    """

    nodeWrapper(input_video, gyro_csv, accl_csv, magn_csv, gps_csv, js_path)
    logging.debug('Node finished')
    cleanGYRO(gyro_csv)
    cleanGPS(gps_csv)
    smoothGPS(gps_csv)
    cleanACCL(accl_csv)
    #cleanMAGN(magn_csv)

def cleanGPS(gps_csv):
    """ Reformats the JS extraction outputs.

    :param gps_csv: Filepath to the GPS output from nodeWrapper()
    :type input_gps: str
    """

    gps_in = pd.read_csv(gps_csv)
    gps_in['lat'] = 0
    gps_in['lon'] = 0
    gps_in['elev'] = 0

    for index, row in gps_in.iterrows():
        info = row['value'].split(',')
        gps_in.loc[index, 'lat'] = info[0]
        gps_in.loc[index, 'lon'] = info[1]
        gps_in.loc[index, 'elev'] = info[2]
    gps_out = gps_in.drop('value', 1)
    gps_out.to_csv(gps_csv, index=False)
    logging.debug('GPS data cleaned.')

def cleanACCL(accl_csv):
    """ Reformats the JS extraction outputs. 

    :param accl_csv: Filepath to the ACCL output from nodeWrapper()
    :type accl_csv: str
    """

    accl_in = pd.read_csv(accl_csv)
    accl_in['AY'] = 0
    accl_in['AX'] = 0
    accl_in['AZ'] = 0
    for index, row in accl_in.iterrows():
        info = row['value'].split(',')
        accl_in.loc[index, 'AY'] = info[0]
        accl_in.loc[index, 'AX'] = info[1]
        accl_in.loc[index, 'AZ'] = info[2]
    accl_out = accl_in.drop('value', 1)
    accl_out.to_csv(accl_csv, index=False)
    logging.debug('ACCL data cleaned.')

def cleanGYRO(gyro_csv):
    """ Reformats the JS extraction outputs.

    :param gyro_csv: Filepath to the GYRO output from nodeWrapper()
    :type gyro_csv: str
    """

    gyro_in = pd.read_csv(gyro_csv)
    gyro_in['rY'] = 0
    gyro_in['rX'] = 0
    gyro_in['rZ'] = 0

    for index, row in gyro_in.iterrows():
        info = row['value'].split(',')
        gyro_in.loc[index, 'rY'] = info[0]
        gyro_in.loc[index, 'rX'] = info[1]
        gyro_in.loc[index, 'rZ'] = info[2]
    gyro_out = gyro_in.drop('value', 1)
    gyro_out.to_csv(gyro_csv, index=False)
    logging.debug('GYRO data cleaned.')

def cleanMAGN(magn_csv):
    """ Reformats the JS extraction outputs.

    :param magn_csv: Filepath to the MAGN output from nodeWrapper()
    :type magn_csv: str
    """

    magn_in = pd.read_csv(magn_csv)
    magn_in['mY'] = 0
    magn_in['mX'] = 0
    magn_in['mZ'] = 0

    for index, row in magn_in.iterrows():
        info = row['value'].split(',')
        magn_in.loc[index, 'rY'] = info[0]
        magn_in.loc[index, 'rX'] = info[1]
        magn_in.loc[index, 'rZ'] = info[2]
    magn_out = magn_in.drop('value', 1)
    magn_out.to_csv(magn_csv, index=False)
    logging.debug('MAGN data cleaned.')


def nodeWrapper(input_video, output_gyro, output_accl, output_magn, output_gps, js_path):
    """ Wrapper to call JS script. 

    :param input_video: Filepath to the target video
    :type input_video: str
    :param output_gyro: Filepath where GYRO data will be saved.
    :type output_gyro: str
    :param output_accl: Filepath where ACCL data will be saved.
    :type output_accl: str
    :param output_magn: Filepath where MAGN data will be saved.
    :type output_magn: str
    :param output_gps: Filepath where GPS data will be saved.
    :type output_gps: str
    :param js_path: Filepath to the JS script.
    :type js_path: str
    """

    extract_telemetry = ['node', js_path, input_video, output_gyro, output_accl, output_magn, output_gps]
    subprocess.run(extract_telemetry)


def smoothGPS(input_gps, window_size=15):
    """  Uses a moving average to filter the input GPS.

    :param gps_csv: Filepath to the GPS output from cleanGPS()
    :type input_gps: str
    :param window_size: The size of the moving average. Affected by walking speed and frame rate.
    :type window_size: int
    """

    gps_df = pd.read_csv(input_gps)

    smoothed_lat = savgol_filter(gps_df['lat'], window_size, 3, mode='nearest')
    smoothed_lon = savgol_filter(gps_df['lon'], window_size, 3, mode='nearest')
    smoothed_elev = savgol_filter(gps_df['elev'], window_size, 3, mode='nearest')

    # trying out different smoothing techniques
    '''def moving_average(x, w): # this is a helper function
        return np.convolve(x, np.ones(w), 'same') / w

    

    smoothed_lat = moving_average(gps_df['lat'], window_size)
    smoothed_lon = moving_average(gps_df['lon'], window_size)
    smoothed_elev = moving_average(gps_df['elev'], window_size)'''

    gps_df['lat'] = smoothed_lat
    gps_df['lon'] = smoothed_lon
    gps_df['elev'] = smoothed_elev
    gps_df.to_csv(input_gps, index=False)
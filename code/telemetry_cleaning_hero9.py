import logging, os, subprocess
import pandas as pd

def nodeWrapperHERO9(input_video, output_gps, output_accl, output_gyro, output_grav, output_cori, output_iori, js_path):
    """ Wrapper to call JS script. 

    :param input_video: Filepath to the target video
    :type input_video: str
    :param output_gps: Filepath where GPS stream will be saved.
    :type output_gps: str
    :param output_accl: Filepath where ACCL stream will be saved.
    :type output_accl: str
    :param output_gyro: Filepath where GYRO stream will be saved.
    :type output_gyro: str
    :param output_grav: Filepath where GRAV stream will be saved.
    :type output_grav: str
    :param output_cori: Filepath where CORI stream will be saved.
    :type output_cori: str
    :param output_iori: Filepath where IORI stream will be saved.
    :type output_iori: str
    :param js_path: Filepath to the JS script.
    :type js_path: str
    """

    extract_telemetry = ['node', js_path, input_video, output_gps, output_accl, output_gyro, output_grav, output_cori, output_iori]
    subprocess.run(extract_telemetry)


def smoothGPS(input_gps, window_sec=3, sample_hz=20, rescale_z = False, min_z=None, max_z=None):
    """  Uses a moving average to filter the input GPS.

    :param gps_csv: Filepath to the GPS output from cleanGPS()
    :type input_gps: str
    :param window_sec: The length of the moving window in seconds, defaults to 3 seconds.
    :type window_sec: int
    :param sample_hz: The sampling frequency of the GPS in Hz, defaults to 20 Hz.
    :param rescale_z: Scales the z axis using min_z and max_z arguments, or +/- 1 around the mean. Defaults to False.
    :type rescale_z: bool
    :param min_z: The lowest known elevation in the plot, used for rescaling. Defaults to None.
    :type min_z: float
    :param max_z: The highest known elevation in the plot, used for rescaling. Defaults to None.
    :type max_z: float
    """

    gps_df = pd.read_csv(input_gps)


    gps_df['lat'] = gps_df['lat'].rolling(window=window_sec*sample_hz, min_periods=1).mean()
    gps_df['lon'] = gps_df['lon'].rolling(window=window_sec*sample_hz, min_periods=1).mean()
    gps_df['elev'] = gps_df['elev'].rolling(window=window_sec*sample_hz, min_periods=1).mean()
    if rescale_z == True:
        z_min = gps_df['elev'].min()
        z_max = gps_df['elev'].max()
        if min_z is None:
            a = gps_df['elev'].mean() - 1
        else:
            a = min_z
        if max_z is None:
            b = gps_df['elev'].mean() + 1
        else:
            b = z_max
        gps_df['elev'] = ((b-a)*(gps_df['elev']-z_min)/(z_max-z_min) + a)

    gps_df.to_csv(input_gps, index=False)

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

def smoothACCL(accl_csv, window_sec=3, sample_hz=200):
    """  Uses a moving average to filter the input ACCL.

    :param accl_csv: Filepath to the ACCL output from cleanACCL()
    :type input_accl: str
    :param window_sec: The length of the moving window in seconds, defaults to 3 seconds.
    :type window_sec: int
    :param sample_hz: The sampling frequency of the IMU in Hz, defaults to 200 Hz.
    """

    accl_df = pd.read_csv(accl_csv)

    accl_df['AX'] = accl_df['AX'].rolling(window=window_sec*sample_hz, min_periods=1).mean()
    accl_df['AY'] = accl_df['AY'].rolling(window=window_sec*sample_hz, min_periods=1).mean()
    accl_df['AZ'] = accl_df['AZ'].rolling(window=window_sec*sample_hz, min_periods=1).mean()
    accl_df.to_csv(accl_csv, index=False)

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
    logging.debug('ACCL stream cleaned.')

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
    logging.debug('GYRO stream cleaned.')

def cleanCORI(cori_csv):
    """ Reformats the JS extraction outputs.

    :param cori_csv: Filepath to the CORI output from nodeWrapper()
    :type cori_csv: str
    """
    
    cori_in = pd.read_csv(cori_csv)
    
    cori_in['w'] = 0
    cori_in['x'] = 0
    cori_in['y'] = 0
    cori_in['z'] = 0
    for index, row in cori_in.iterrows():
        info = row['value'].split(',')
        cori_in.loc[index, 'w'] = info[0]
        cori_in.loc[index, 'x'] = info[1]
        cori_in.loc[index, 'y'] = info[2]
        cori_in.loc[index, 'z'] = info[3]
    cori_out = cori_in.drop('value', 1)
    cori_out.to_csv(cori_csv, index=False)
    logging.debug('CORI stream cleaned.')

def cleanIORI(iori_csv):
    """ Reformats the JS extraction outputs.

    :param iori_csv: Filepath to the IORI output from nodeWrapper()
    :type iori_csv: str
    """
    
    iori_in = pd.read_csv(iori_csv)
    
    iori_in['w'] = 0
    iori_in['x'] = 0
    iori_in['y'] = 0
    iori_in['z'] = 0
    for index, row in iori_in.iterrows():
        info = row['value'].split(',')
        iori_in.loc[index, 'w'] = info[0]
        iori_in.loc[index, 'x'] = info[1]
        iori_in.loc[index, 'y'] = info[2]
        iori_in.loc[index, 'z'] = info[3]
    iori_out = iori_in.drop('value', 1)
    iori_out.to_csv(iori_csv, index=False)
    logging.debug('IORI stream cleaned.')

def cleanGRAV(grav_csv):
    """ Reformats the JS extraction outputs.

    :param grav_csv: Filpath to the GRAV output from nodeWrapper()
    :type grav_csv: str
    """
    grav_in = pd.read_csv(grav_csv)
    
    grav_in['x'] = 0
    grav_in['y'] = 0
    grav_in['z'] = 0
    for index, row in grav_in.iterrows():
        info = row['value'].split(',')
        grav_in.loc[index, 'y'] = info[0]
        grav_in.loc[index, 'x'] = info[1]
        grav_in.loc[index, 'z'] = info[2]
    grav_out = grav_in.drop('value', 1)
    grav_out.to_csv(grav_csv, index=False)
    logging.debug('GRAV stream cleaned.')

def cleanHERO9(telem_dir, rescale_z = False, min_z=None, max_z=None):
    for i in sorted(os.listdir(telem_dir)):
        input = telem_dir + '/' + i
        if i.endswith('GPS.csv'):
            cleanGPS(input)
            smoothGPS(input, rescale_z=rescale_z, min_z=min_z, max_z=max_z)
        elif i.endswith('ACCL.csv'):
            cleanACCL(input)
            smoothACCL(input)
        elif i.endswith('GYRO.csv'):
            cleanGYRO(input)
        elif i.endswith('CORI.csv'):
            cleanCORI(input)
        elif i.endswith('IORI.csv'):
            cleanIORI(input)
        elif i.endswith('GRAV.csv'):
            cleanGRAV(input)
        else:
            continue


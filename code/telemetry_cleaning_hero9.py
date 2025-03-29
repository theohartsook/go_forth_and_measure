import logging, os, subprocess
import pandas as pd

def nodeWrapperHERO9(input_video, output_gps=None, output_accl=None, output_gyro=None,
                       output_grav=None, output_iori=None, js_path=None):
    """Wrapper to call the JS script.

    :param input_video: Filepath to the target video.
    :param output_gps: Filepath where GPS stream will be saved. Defaults to None.
    :param output_accl: Filepath where ACCL stream will be saved. Defaults to None.
    :param output_gyro: Filepath where GYRO stream will be saved. Defaults to None.
    :param output_grav: Filepath where GRAV stream will be saved. Defaults to None.
    :param output_iori: Filepath where IORI stream will be saved. Defaults to None.
    :param js_path: Filepath to the JS script.
    """
    # If an output argument is None, substitute with an empty string.
    extract_telemetry = [
        'node', js_path, input_video,
        output_gps or '',
        output_accl or '',
        output_gyro or '',
        output_grav or '',
        output_iori or ''
    ]
    subprocess.run(extract_telemetry)


def cleanGPS(gps_csv, rescale_z=False, min_z=None, max_z=None):
    """ Reformats the JS extraction outputs.

    :param gps_csv: Filepath to the GPS output from nodeWrapper().
    :type input_gps: str
    :param rescale_z: Scales the z axis using min_z and max_z arguments, or to the mean. Defaults to False.
    :type rescale_z: bool
    :param min_z: The lowest known elevation in the plot, used for rescaling. Defaults to None.
    :type min_z: float
    :param max_z: The highest known elevation in the plot, used for rescaling. Defaults to None.
    :type max_z: float
    """

    gps_in = pd.read_csv(gps_csv)
    gps_in['lat'] = 0.0
    gps_in['lon'] = 0.0
    gps_in['elev'] = 0.0
    for index, row in gps_in.iterrows():
        info = row['value'].split(',')
        gps_in.loc[index, 'lat'] = float(info[0])
        gps_in.loc[index, 'lon'] = float(info[1])
        gps_in.loc[index, 'elev'] = float(info[2])
    gps_out = gps_in.drop(columns='value')
    logging.debug("GPS stream cleaned.")
    if rescale_z == True:
        z_min = gps_out['elev'].min()
        z_max = gps_out['elev'].max()
        if min_z is not None and max_z is not None:
            if z_min == z_max:
                gps_out['elev'] = z_min
                logging.warning("GPS values are all the same, the GPS telemetry on this video is probably not good.")
            else:
                a = min_z
                b = max_z
                logging.info(f"Rescaling z values between {a} and {b}.")
                gps_out['elev'] = (((b-a)*(gps_out['elev']-z_min))/(z_max-z_min)) + a
        else:
            gps_out['elev'].mean()
    gps_out.to_csv(gps_csv, index=False)
    logging.debug("GPS data cleaned.")

def cleanACCL(accl_csv):
    """ Reformats the JS extraction outputs. 

    :param accl_csv: Filepath to the ACCL output from nodeWrapper().
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
    accl_out = accl_in.drop(columns='value')
    accl_out.to_csv(accl_csv, index=False)
    logging.debug('ACCL stream cleaned.')

def cleanGYRO(gyro_csv):
    """ Reformats the JS extraction outputs.

    :param gyro_csv: Filepath to the GYRO output from nodeWrapper().
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
    gyro_out = gyro_in.drop(columns='value')
    gyro_out.to_csv(gyro_csv, index=False)
    logging.debug("GYRO stream cleaned.")

def cleanIORI(iori_csv):
    """ Reformats the JS extraction outputs.

    :param iori_csv: Filepath to the IORI output from nodeWrapper()/
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
    iori_out = iori_in.drop(columns='value')
    iori_out.to_csv(iori_csv, index=False)
    logging.debug("IORI stream cleaned.")

def cleanGRAV(grav_csv):
    """ Reformats the JS extraction outputs.

    :param grav_csv: Filpath to the GRAV output from nodeWrapper().
    :type grav_csv: str
    """
    grav_in = pd.read_csv(grav_csv)
    
    grav_in['x'] = 0
    grav_in['y'] = 0
    grav_in['z'] = 0
    for index, row in grav_in.iterrows():
        info = row['value'].split(',')
        grav_in.loc[index, 'y'] = info[0]
        grav_in.loc[index, 'x'] = info[1]*-1
        grav_in.loc[index, 'z'] = info[2]
    grav_out = grav_in.drop(columns='value')
    grav_out.to_csv(grav_csv, index=False)
    logging.debug("GRAV stream cleaned.")

def cleanHERO9(telem_dir, rescale_z=False, min_z=None, max_z=None):
    """ Wrapper function for cleaning HERO9 camera telemetry.

    :param telem_dir: Filepath to telemetry directory
    :type telem_dir: str
    :param rescale_z: Scales the z axis using min_z and max_z arguments, or to the mean. Defaults to False.
    :type rescale_z: bool
    :param min_z: The lowest known elevation in the plot, used for rescaling. Defaults to None.
    :type min_z: float
    :param max_z: The highest known elevation in the plot, used for rescaling. Defaults to None.
    :type max_z: float
    """
    for i in sorted(os.listdir(telem_dir)):
        input = os.path.join(telem_dir, i)
        if i.endswith('GPS.csv'):
            cleanGPS(input, rescale_z=rescale_z, min_z=min_z, max_z=max_z)
        elif i.endswith('ACCL.csv'):
            cleanACCL(input)
        elif i.endswith('GYRO.csv'):
            cleanGYRO(input)
        elif i.endswith('IORI.csv'):
            cleanIORI(input)
        elif i.endswith('GRAV.csv'):
            cleanGRAV(input) 
        else:
            continue
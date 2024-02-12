from datetime import datetime
import logging, os, subprocess, sys
import pandas as pd

def nodeWrapperHERO9(input_video, output_gps, output_accl, output_gyro, output_grav, output_cori, output_iori, js_path):
    """ Wrapper to call JS script. Terminates if GPS is not saved successfully, otherwise warns.

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

    :return: returns 0 if successful, terminates if GPS steam not saveed.
    :rtype: int
    """

    extract_telemetry = ['node', js_path, input_video, output_gps, output_accl, output_gyro, output_grav, output_cori, output_iori]
    subprocess.run(extract_telemetry)

    if not os.path.exists(output_gps):
        logging.error('Failed to save GPS stream.')
        sys.exit(1)
    if not os.path.exists(output_accl):
        logging.warning('Failed to save ACCL stream.')
    if not os.path.exists(output_gyro):
        logging.warning('Failed to save GYRO stream.')
    if not os.path.exists(output_grav):
        logging.warning('Failed to save GRAV stream.')
    if not os.path.exists(output_cori):
        logging.warning('Failed to save CORI stream.')
    if not os.path.exists(output_iori):
        logging.warning('Failed to save IORI stream.')

    return 0

def cleanGPS(gps_csv):
    """ Reformats the JS extraction outputs.

    :param gps_csv: Filepath to the GPS output from nodeWrapper()
    :type input_gps: str
    """

    gps_in = pd.read_csv(gps_csv)
    cleaned_cols = gps_in['value'].str.split(',', expand=True)
    cleaned_cols.columns = ['lat', 'lon', 'elev', 'speed_2d', 'speed_3d']
    gps_out = pd.concat([cleaned_cols, gps_in.drop('value', axis=1)], axis=1)    
    gps_out.to_csv(gps_csv, index=False)
    logging.debug('GPS stream cleaned.')



def cleanACCL(accl_csv):
    """ Reformats the JS extraction outputs. 

    :param accl_csv: Filepath to the ACCL output from nodeWrapper()
    :type accl_csv: str
    """

    accl_in = pd.read_csv(accl_csv)
    cleaned_cols = accl_in['value'].str.split(',', expand=True)
    cleaned_cols.columns = ['AZ', 'AX', 'AY']
    accl_out = pd.concat([cleaned_cols, accl_in.drop('value', axis=1)], axis=1)    
    accl_out.to_csv(accl_csv, index=False)
    logging.debug('ACCL stream cleaned.')

def cleanGYRO(gyro_csv):
    """ Reformats the JS extraction outputs.

    :param gyro_csv: Filepath to the GYRO output from nodeWrapper()
    :type gyro_csv: str
    """

    gyro_in = pd.read_csv(gyro_csv)
    cleaned_cols = gyro_in['value'].str.split(',', expand=True)
    cleaned_cols.columns = ['rZ', 'rX', 'rY']
    gyro_out = pd.concat([cleaned_cols, gyro_in.drop('value', axis=1)], axis=1)    
    gyro_out.to_csv(gyro_csv, index=False)
    logging.debug('GYRO stream cleaned.')

def cleanGRAV(grav_csv):
    """ Reformats the JS extraction outputs.

    :param grav_csv: Filpath to the GRAV output from nodeWrapper()
    :type grav_csv: str
    """

    grav_in = pd.read_csv(grav_csv)
    cleaned_cols = grav_in['value'].str.split(',', expand=True)
    cleaned_cols.columns = ['x', 'z', 'y']
    grav_out = pd.concat([cleaned_cols, grav_in.drop('value', axis=1)], axis=1)
    grav_out['z'] = grav_out['z'] * -1
    grav_out['y'] = grav_out['y'] * -1
    grav_out.to_csv(grav_csv, index=False)
    logging.debug('GRAV stream cleaned.')

def cleanCORI(cori_csv):
    """ Reformats the JS extraction outputs.

    :param cori_csv: Filepath to the CORI output from nodeWrapper()
    :type cori_csv: str
    """

    cori_in = pd.read_csv(cori_csv)
    cleaned_cols = cori_in['value'].str.split(',', expand=True)
    cleaned_cols.columns = ['w', 'x', 'z', 'y']
    cori_out = pd.concat([cleaned_cols, cori_in.drop('value', axis=1)], axis=1)    
    cori_out.to_csv(cori_csv, index=False)
    logging.debug('CORI stream cleaned.')

def cleanIORI(iori_csv):
    """ Reformats the JS extraction outputs.

    :param iori_csv: Filepath to the IORI output from nodeWrapper()
    :type iori_csv: str
    """
    
    iori_in = pd.read_csv(iori_csv)
    cleaned_cols = iori_in['value'].str.split(',', expand=True)
    cleaned_cols.columns = ['w', 'x', 'z', 'y']
    iori_out = pd.concat([cleaned_cols, iori_in.drop('value', axis=1)], axis=1)    
    iori_out.to_csv(iori_csv, index=False)
    logging.debug('IORI stream cleaned.')


def cleanHERO9(telem_dir):
    """ Wrapper to clean all HERO9 telemtry streams

    :param telem_dir: telem_dir produced by createProjectDirectory()
    :type telem_dir: str
    """
    for i in sorted(os.listdir(telem_dir)):
        input = os.path.join(telem_dir, i)
        if i.endswith('GPS.csv'):
            cleanGPS(input)
        elif i.endswith('ACCL.csv'):
            cleanACCL(input)
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

def convertGPSTimeForEXIFTool(date_str):
    """ Converts GPS time for use with exiftool (strips time zone)

    :param date_str: Date time str provided by gpfm-parser
    :type date_str: str

    :return: returns reformated string if successful, else None
    :rtype: str, None
    """
    try:
        dt = datetime.strptime(date_str[0:25].strip(), '%a %b %d %Y %H:%M:%S')
        return dt.strftime('%Y:%m:%d %H:%M:%S')
    except ValueError as e:
        logging.error('Error parsing date string:', e)
        return None


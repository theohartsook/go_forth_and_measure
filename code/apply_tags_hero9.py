import pandas as pd
import numpy as np
import os
import logging
import subprocess
import shutil
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

def applyTags(input_dir, gps_csv=None, ori_csv=None, sfm='P4D', fps=30, file_ending='.jpg', north_hem=True, west_hem=True, config_file=None):
    """ Tags a directory of cts labelled frames with their GPS and GYRO data using exif_tool.

    :param input_dir: Filepath to the directory of labelled frames.
    :type input_video: str

    :param gps_csv: Filepath to the GPS data, must be cleaned with cleanGPS(). Defaults to None.
    :type gps_csv: str
    :param ori_csv: Filepath to the GYRO data (P4D) or GRAV data (RC), must be cleaned with their respective function. Defaults to None.
    :type ori_csv: str
    ;param sfm: Applies orientation data for the designed sfm software. Defaults to P4D.
    :type sfm: str
    :param fps: FPS of the original video. Defaults to 30.
    :type fps: int
    :param file_ending: Target ending for the frames. Defaults to '.jpg'.
    :type file_ending: str
    :param north_hem: Controls whether latitude is written in N hemisphere. Defaults to True.
    :type north_hem: bool
    :param west_hem: Controls whether longitude is written in W hemisphere. Defaults to True.
    :type west_hem: bool
    :param config_file: Filepath to the config file for extra EXIF tags. Defaults to None.
    :type config_file: str
    """

    if gps_csv is not None:
        gps_df = pd.read_csv(gps_csv)
    if ori_csv is not None:
        ori_df = pd.read_csv(ori_csv)

    for i in sorted(os.listdir(input_dir)):
        if not i.endswith(file_ending):
            logging.debug(f"Skipping {i}.")
            continue
        frame = os.path.join(input_dir, i)
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
            logging.debug("Found telemetry tags")
            tagging_call.extend(['-GPSLatitude ='+str(lat), '-GPSLongitude ='+str(lon), '-GPSAltitude ='+str(elev)])
            if north_hem == True:
                tagging_call.append('-GPSLatitudeRef=North')
            else:    
                tagging_call.append('-GPSLatitudeRef=South')
            if west_hem == True:
                tagging_call.append('-GPSLongitudeRef=West')
            else:    
                tagging_call.append('-GPSLongitudeRef=East')
        if ori_csv is not None:
            ori_cts = sorted(ori_df['cts'])
            closest_ori = findClosestCTS(cts, ori_cts)
            ori_row = ori_df.loc[ori_df['cts'] == closest_ori]
            if sfm == 'P4D':
                rY = ((ori_row['rX'].iloc[0])/np.pi*180)+90
                rX = (ori_row['rY'].iloc[0])/np.pi*180
                rZ = (ori_row['rZ'].iloc[0])/np.pi*180       
                tagging_call.insert(1, '-config')
                tagging_call.insert(2, config_file)
                tagging_call.extend(['-Pitch ='+str(rY), '-Roll ='+str(rX), '-Yaw ='+str(rZ)])
            elif sfm == 'RC':
                grav_X = ori_row['x'].iloc[0]
                grav_Y = ori_row['y'].iloc[0]
                grav_Z = ori_row['z'].iloc[0]
                grav_vector = [grav_X, grav_Y, grav_Z]
                createGravityXMP(frame, grav_vector)
        tagging_call.extend(['-overwrite_original', frame])
        subprocess.run(tagging_call)

def createGravityXMP(img_path, gravity_vector):
    """ Creates an XMP sidecar file containing a gravity vector for RealityCapture.

    :param img_path: Filepath to the image.
    :type img_path: str
    :param gravity_vector: The corresponding gravity vector for the image.
    :type gravity_vector: list

    """
    base, _ = os.path.splitext(img_path)
    xmp_path = f"{base}.xmp"

    gravity_str = f"{gravity_vector[0]:.4f} {gravity_vector[1]:.4f} {gravity_vector[2]:.4f}"

    xmp_content = f'''<x:xmpmeta xmlns:x="adobe:ns:meta/">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description xmlns:xcr="http://www.capturingreality.com/ns/xcr/1.1#"
                        xcr:Version="3" xcr:PosePrior="initial" xcr:Coordinates="absolute">
        <xcr:Gravity>{gravity_str}</xcr:Gravity>
    </rdf:Description>
    </rdf:RDF>
    </x:xmpmeta>'''

    with open(xmp_path, 'w') as xmp_file:
        xmp_file.write(xmp_content)

    logging.info(f"XMP sidecar created at: {xmp_path}")


def generateRCFlightLog(input_dir, gps_csv, gyro_csv, output_csv, fps=30, file_ending='.jpg', north_hem=True, west_hem=True):
    """Generates a flight log for RealityCapture to read IMU data.

    :param input_dir: Directory of labelled frames.
    :type input_dir: str
    :param gps_csv: Filepath to the GPS data (must be cleaned with cleanGPS())
    :type gps_csv: str
    :param gyro_csv: Filepath to the GYRO data (must be cleaned with cleanGYRO())
    :type gyro_csv: str
    :param output_csv: Path to the output flight log CSV.
    :type output_csv: str
    :param fps: FPS of the original video. Defaults to 30
    :type fps: int
    :param file_ending: Target ending for the frames. Defaults to '.jpg'
    :type file_ending: str
    :param north_hem: Controls whether latitude is written in N hemisphere. Defaults to True.
    :type north_hem: bool
    :param west_hem: Controls whether longitude is written in W hemisphere. Defaults to True.
    :type west_hem: bool
    """

    gps_df = pd.read_csv(gps_csv)
    gyro_df = pd.read_csv(gyro_csv)

    flight_log_entries = []

    for i in sorted(os.listdir(input_dir)):
        if not i.endswith(file_ending):
            logging.debug(f"Skipping {i}")
            continue

        frame = input_dir + '/' + i
        info = i.split('_')
        cts = info[-1]
        cts = float(cts[:-4])/fps*1000

        gps_cts = sorted(gps_df['cts'])
        closest_gps = findClosestCTS(cts, gps_cts)
        gps_row = gps_df.loc[gps_df['cts'] == closest_gps]

        lat = gps_row['lat'].iloc[0]
        lon = gps_row['lon'].iloc[0]
        elev = gps_row['elev'].iloc[0]

        if west_hem and lon > 0:
            lon = -lon

        gyro_cts = sorted(gyro_df['cts'])
        closest_gyro = findClosestCTS(cts, gyro_cts)
        gyro_row = gyro_df.loc[gyro_df['cts'] == closest_gyro]

        rY = ((gyro_row['rX'].iloc[0])/np.pi*180)
        rX = (gyro_row['rY'].iloc[0])/np.pi*180
        rZ = (gyro_row['rZ'].iloc[0])/np.pi*180     

        flight_log_entries.append({
            'Image': frame,
            'Latitude': lat,
            'Longitude': lon,
            'Altitude': elev,
            'Yaw': rZ,
            'Pitch': rX,
            'Roll': rY
        })

    flight_log_df = pd.DataFrame(flight_log_entries)
    flight_log_df.to_csv(output_csv, index=False)

    logging.info(f"Flight log saved to f{output_csv}")

def cleanUpIntermediate(project_dir, nth=30):
    """ Helper function to organize GFAM outputs and delete extraneous files. Creates an images folder and a telemetry folder.

    :param project_dir: Filepath to the project directory.
    :type project_dir: str
    :param nth: The amount of frames extracted during processing, used to identify subsample directory. Defaults to 30.
    :type nth: int.

    """
    output_dir = os.path.join(project_dir, 'gfam_outputs')
    os.mkdir(output_dir)
    output_images = os.path.join(output_dir, 'images')
    os.mkdir(output_images)
    output_telemetry = os.path.join(output_dir, 'telemetry')
    os.mkdir(output_telemetry)
    
    n_img = 0
    n_img_copies = 0

    n_telem = 0
    n_telem_copies = 0

    for i in os.listdir(project_dir):
        if i == 'gfam_outputs':
            continue
        if os.path.isdir(os.path.join(project_dir, i)):
            current_dir = os.path.join(project_dir, i)
            subsample_dir = os.path.join(current_dir, 'subsample_' + str(nth) + '_frames')
            telem_dir = os.path.join(current_dir, 'telem')
            n_img += len(os.listdir(subsample_dir))
            n_telem += len(os.listdir(telem_dir))
            video_name = i
            for j in os.listdir(subsample_dir):
                src_img = os.path.join(subsample_dir, j)
                dest_img = os.path.join(output_images, j)
                shutil.move(src_img, dest_img)
                if not os.path.exists(dest_img):
                    logging.error(f"Failed to copy {src_img}.")
                else:
                    n_img_copies +=1
            if len(os.listdir(output_images)) != n_img:
                if n_img != n_img_copies:
                    logging.error("Not all images were copied correctly during cleanup.")
                else:
                    logging.warning("Size of directory is not the same before and after cleanup.")
            
            for j in os.listdir(telem_dir):
                src_telem = os.path.join(telem_dir, j)
                dst_telem = os.path.join(output_telemetry, video_name + '_' + j)
                shutil.move(src_telem, dst_telem)
                if not os.path.exists(dst_telem):
                    logging.error(f"Failed to copy {src_telem}.")
                else:
                    n_telem_copies += 1
            if len(os.listdir(output_telemetry)) != n_telem:
                if n_telem != n_telem_copies:
                    logging.error("Not all telemetry were copied correctly during cleanup.")
                else:
                    logging.warning("Size of directory is not the same before and after cleanup.")
            shutil.rmtree(current_dir, ignore_errors=True)
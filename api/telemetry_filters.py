import math
import numpy as np
import pandas as pd

def quaternionToEuler(w, x, y, z, human_perspective=True):
    """ Converts quaternion into Euler angles.
    roll is rotation around x axis (+north, -south)
    pitch is rotation around y axis (+east, -west)
    and yaw is rotation around z axis (+down, -up).
    
    :param w: Quaternion component
    :type w: float
    :param x: Quaternion component
    :type: float
    :param y: Quaternion component
    :type: float
    :param z: Quaternion component
    :type: float
    :param human_perspective: Rotates yaw forward 90 degrees, defaults to True
    :type human_perspective: bool
    :return: roll, pitch, yaw
    :rtype: float, float, float
    """

    norm = math.sqrt(w * w + x * x + y * y + z * z)
    w, x, y, z = w / norm, x / norm, y / norm, z / norm

    # Roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation) adjustment
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)
    if human_perspective == True:
        pitch += math.pi / 2  

    # Yaw (z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw

def convertIORItoEuler(iori_df):
        """ Adds roll, pitch, and yaw to iori_df for alternative orientation measure.

        :param iori_df: produced by CleanIORI()
        :type iori_df: pandas df

        :return: Returns updated iori_df
        :rtype: pandas df
        """
        w = iori_df['w'].to_numpy()
        x = iori_df['x'].to_numpy()
        y = iori_df['y'].to_numpy()
        z = iori_df['z'].to_numpy()

        roll = np.zeros(len(iori_df))
        pitch = np.zeros(len(iori_df))
        yaw = np.zeros(len(iori_df))

        for i in range(len(iori_df)):
            roll[i], pitch[i], yaw[i] = quaternionToEuler(w[i], x[i], y[i], z[i])

        iori_df['roll'] = roll
        iori_df['pitch'] = pitch
        iori_df['yaw'] = yaw

        return iori_df

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


# this is modified from cleanGyro
gyro_csv = '/Users/theo/data/gopro_telemetry/stationary_GYRO.csv'
gyro_in = pd.read_csv(gyro_csv)
gyro_in['rY'] = 0
gyro_in['rX'] = 0
gyro_in['rZ'] = 0

print(gyro_in['rX'].max())

for index, row in gyro_in.iterrows():
    info = row['value'].split(',')
    gyro_in.loc[index, 'rY'] = info[0]*-1
    gyro_in.loc[index, 'rX'] = info[1]
    gyro_in.loc[index, 'rZ'] = info[2]*-1
gyro_out = gyro_in.drop('value', 1)

print(gyro_out['rX'].max())

gyro_out['rX'] = savgol_filter(gyro_out['rX'], 1999, 1, mode='constant')

print(gyro_out['rX'].mean())
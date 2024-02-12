import logging
import subprocess

def extractFPS(input_video):
    """ Wrapper for ffmpeg to get the true FPS of a video. 

    :param input_video: Filepath to the target video
    :type input_video: str

    :return: returns the FPS of the input video.
    :rtype: float
    """

    command = ['ffprobe', '-v', '0', '-of', 'csv=p=0' ,'-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', input_video]
    info = subprocess.check_output(command).decode("utf-8")
    info = info.strip()
    info = info.split('/')
    fps = int(info[0])/int(info[1])
    logging.debug('FPS: %s', fps)

    return fps

def extractVideoStartTime(input_video):
    """ Function to extract video start time courtesy of https://video.stackexchange.com/questions/33551/get-metadata-for-video-start-time-with-ffmpeg

    :param input_video: Filepath to the target video
    :type input_video: str

    :return: returns the start time of the input video, or None if unavailable 
    :rtype: int
    """

    command = ['ffprobe', '-v', '0', '-show_entries', 'format=start_time', '-of', 'compact=p=0:nk=1', input_video]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    start_time = result.stdout.decode().strip()
    return start_time if start_time else None

def extractNthFrames(input_video, output_dir, nth, prefix='frame_', sig_fig=4, file_ending='.jpg'):
    """ Extracts nth frames from a video using ffmpeg. 

    :param input_video: Filepath to the target video
    :type input_video: str
    :param output_dir: Filepath to the directory where the tagged frames will be stored.
    :type output_dir: str
    :param nth: Controls how many frames are selected, defaults to 15
    :type nth: int
    :param prefix: Prefix for the extracted frames, defaults to ``'frame_'``
    :type prefix: str
    :param sig_fig: Controls the length of the frame IDs, defaults to 7 (i.e. 0000001-9999999)
    :type sig_fig: int
    :param file_ending: Sets the frame output format, defaults to '.jpg'
    :type file_ending: str

    :return: returns 0 if successful
    :rtype: int
    """

    logging.debug('Frame extraction starts')
    output_frames = f"{output_dir}/{prefix}%0{sig_fig}d{file_ending}"
    frame_extraction_call = ['ffmpeg', '-i', input_video,  output_frames]
    frame_extraction_call = [
        'ffmpeg',
        '-i', input_video,
        '-vf', f"select=not(mod(n\,{nth}))",
        '-vsync', 'vfr', 
        output_frames
    ]
    subprocess.call(frame_extraction_call)
    logging.debug('Frame extraction finished.')

    return 0
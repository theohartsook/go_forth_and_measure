import logging, os, shutil, subprocess

def timeStampFrames(input_video, frame_dir, output_dir):
    """ Tags frames with their CTS timestamp (used for telemetry matching).
    
    :param input_video: Filepath to the target video
    :type input_video: str
    :param frame_dir: Filepath to the directory where frames are stored.
    :type frame_dir: str
    :param output_dir: Filepath to the directory where the timestamped frames will be stored.
    :type output_dir: str
    """
    fps = extractFPS(input_video)

    labelFramesWithCTS(frame_dir, output_dir, fps=fps)

def labelFramesWithCTS(input_dir, output_dir, fps=60, file_ending='.jpg'):
    """ Labels a directory of frames with their approximate camera time.

    :param input_dir: Filepath to the directory of frames.
    :type input_video: str
    :param output_dir: Filepath to the directory where the labelled frames will be stored.
    :type output_dir: str
    :param fps: FPS of the original video.
    :type fps: int
    :param file_ending: Target ending for the frames, defaults to '.jpg'
    :type file_ending: str
    """

    cts_per_frame = 1/(fps/1000)
    logging.debug('CTS per frame: %s', cts_per_frame)
    counter = 0
    for i in sorted(os.listdir(input_dir)):
        if not i.endswith(file_ending):
            continue
        info = i.split('_')
        frame = info[-1]
        frame = frame[:-4]
        if int(frame) >= counter and int(frame) < counter*cts_per_frame:
            old_file = input_dir + '/' + i
            new_file = output_dir + '/frame_' + str(frame) + '_cts_' + str(int(counter)) + '.jpg'
            shutil.copy(old_file, new_file)
        else:
            counter += cts_per_frame
            old_file = input_dir + '/' + i
            new_file = output_dir + '/frame_' + str(frame) + '_cts_' + str(int(counter)) + '.jpg'
            shutil.copy(old_file, new_file)
        logging.debug('Frame %s labelled', counter)

def extractFPS(input_video):
    """ Wrapper for ffmpeg to get the true FPS of a video. 

    :param input_video: Filepath to the target video
    :type input_video: str

    :return: returns the FPS of the input video.
    :rtype: int
    """

    command = ['ffprobe', '-v', '0', '-of', 'csv=p=0' ,'-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', input_video]
    info = subprocess.check_output(command).decode("utf-8")
    info = info.strip()
    info = info.split('/')
    fps = int(info[0])/int(info[1])
    logging.debug('FPS: %s', fps)

    return fps

def extractAllFrames(input_video, output_dir, prefix='frame_', sig_fig=7, file_ending='.jpg'):
    """ Extracts all frames from a video using ffmpeg. 

    :param input_video: Filepath to the target video
    :type input_video: str
    :param output_dir: Filepath to the directory where the tagged frames will be stored.
    :type output_dir: str
    :param prefix: Prefix for the extracted frames, defaults to 'frame_'
    :type prefix: str
    :param sig_fig: Controls the length of the frame IDs, defaults to 7 (i.e. 0000001-9999999)
    :type sig_fig: int
    :param file_ending: Sets the frame output format, defaults to '.jpg'
    :type file_ending: str
    """

    logging.debug('Frame extraction starts')
    output_frames = output_dir + '/' + prefix + '%' + str(sig_fig) + 'd' + file_ending
    frame_extraction_call = ['ffmpeg', '-i', input_video,  output_frames]
    subprocess.call(frame_extraction_call)
    logging.debug('Frame extraction finished.')

def selectNthFrames(input_dir, output_dir, nth=15):
    """
    :param input_dir: Filepath to input directory from extractAllFrames
    :type input_dir: str
    :param output_dir: Filepath to output directory
    :type output_dir: str
    :param nth: Controls how many frames are selected, defaults to 15
    :type nth: int

    """

    counter = 0
    for i in sorted(os.listdir(input_dir)):
        if counter % nth == 0:
            input_img = input_dir + '/' + i
            output_img = output_dir + '/' + i
            shutil.move(input_img, output_img)
            counter +=1
        else:
            counter +=1
            continue
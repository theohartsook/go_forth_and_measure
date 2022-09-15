import os, shutil

def selectNthFrames(input_dir, output_dir, nth=15):
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
        
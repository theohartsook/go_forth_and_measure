import numpy as np
import matplotlib.pyplot as plt
import exifread
import os
import shutil
from matplotlib.patches import Ellipse
from shapely import geometry
from pyproj import Transformer

# CONSTANTS
TARGET_EPSG = 'EPSG:3310'
SOURCE_EPSG = 'EPSG:4326'
MINIMUM_IMG = 50
CELL_HEIGHT = 5
CELL_WIDTH = 5
IMG_FORMAT = '.jpg' # update this to ignore case, also jpg, jpeg, etc. probably should just error handle if it dont open


# I found this code snippets on StackOverflow, which linked to this GitHub.
# I made some slight modifications to fit my conventions
# https://gist.github.com/snakeye/fdc372dbf11370fe29eb 
def convert_to_degrees(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    I found this code snippets on StackOverflow, which linked to this GitHub.
    I made some slight modifications to fit my conventions
    https://gist.github.com/snakeye/fdc372dbf11370fe29eb 

    :param value: DMS lat/lon from exifread
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)

def getGPS(img_path):
    """
    Returns dictionary with lat/lon and ref, or an empty dictionary if metadata unavailable.

    :param img_path: Filepath to image
    :type img_path: str
    return: GPS data in decimal degrees
    rtype: dict
    """

    with open(img_path, 'rb') as f:
        tags = exifread.process_file(f)
        latitude = tags.get('GPS GPSLatitude')
        latitude_ref = tags.get('GPS GPSLatitudeRef')
        longitude = tags.get('GPS GPSLongitude')
        longitude_ref = tags.get('GPS GPSLongitudeRef')
        if latitude:
            lat_value = convert_to_degrees(latitude)
            if latitude_ref is not None:
                if latitude_ref.values != 'N':
                    lat_value = -lat_value
                else:
                    lat_value = lat_value
        else:
            return {}
        if longitude:
            lon_value = convert_to_degrees(longitude)
            if longitude_ref is not None:
                if longitude_ref.values != 'E':
                    lon_value = -lon_value
                else:
                    lon_value = lon_value
        else:

            return {}
        return {'longitude': lon_value, 'latitude': lat_value}
    return {}

def getProjectedImgCoord(img_path, source_crs, target_crs):
    """
    Returns dictionary with lat/lon and ref, or an empty dictionary if metadata unavailable.

    :param img_path: Filepath to image, must have GPS EXIF tags
    :type img_path: str
    :param source_crs: The EPSG code for desired CRS, for example  'EPSG:3310'
    :type source_crs: str
    :param target_crs: The EPSG code for original CRS, for example  'EPSG:4326'
    :type target_crs: str

    :return: The transformed coordinates
    :rtype: float, float
    """

    gps = getGPS(img_path)
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    x, y = transformer.transform(gps['longitude'], gps['latitude'])
    return (x,y)

def getBBFromDirectory(img_dir, source_crs, target_crs):
    """
    Calculates the projected bounding box for all images in a directory.

    :param img_dir: Filepath to image directory
    :type img_dir: str
    :param source_crs: The EPSG code for desired CRS, for example  'EPSG:3310'
    :type source_crs: str
    :param target_crs: The EPSG code for original CRS, for example  'EPSG:4326'
    :type target_crs: str    

    :return: Returns a nested list with the lower left and upper right corners
    :rtype: [[float, float], [float, float]]
    
    """

    first_flag = True
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    for i in os.listdir(img_dir):
        if not i.endswith(IMG_FORMAT):
            continue
        img = img_dir + '/' + i
        x_i, y_i = getProjectedImgCoord(img, source_crs, target_crs)

        if first_flag == True:
            min_x = x_i
            max_x = x_i
            min_y = y_i
            max_y = y_i
            first_flag = False
        else:
            if x_i> max_x:
                max_x = x_i
            if x_i < min_x:
                min_x = x_i
            if y_i> max_y:
                max_y = y_i
            if y_i < min_y:
                min_y = y_i
    return [[min_x, min_y], [max_x, max_y]]

def calculateCellsRequired(min_x, min_y, max_x, max_y, cell_width, cell_height):
    """
    Calculates the number of cells required to cover an area given a width and height.

    :param min_x: X coordinate of lower left
    :type min_x: float
    :param min_y: Y coordinate of lower left
    :type min_y: float
    :param max_x: X coordinate of upper right
    :type max_x: float
    :param max_y: Y coordinate of upper right
    :type max_y: float
    :param cell_width: width of cell
    :type cell_width: float
    :param cell_height: height of cell
    :type cell_height: float

    :return: number of cells required
    :rtype: int

    """

    bb_width = max_x - min_x
    bb_height = max_y - min_y

    num_cells = int(np.ceil(bb_width/cell_width) * np.ceil(bb_height/cell_height))

    return (num_cells)


def findCellCenters(x_o, y_o, cell_width, cell_height):
    """
    Finds the center of a cell given the lower left coordinates

    :param x_o: X coordinate of lower left
    :type x_o: float
    :param y_o: Y coordinate of lower left
    :type y_o: float
    :param cell_width: width of cell
    :type cell_width: float
    :param cell_height: height of cell
    :type cell_height: float

    :return: the center x and y coordinate
    :rtype: float, float
    """

    cell_x = []
    cell_y = []
    for i in range(0, cell_width):
        for j in range(0, cell_height):
            cell_x.append((x_o + cell_width*i) + (cell_width/2))
            cell_y.append((y_o + cell_height*j) + (cell_height/2))

    return(cell_x, cell_y)

def selectPhotosWithinCell(x, y, cell_width, cell_height, img_dir):
    """
    Selects all photos from a directory that are contained within the given location.

    :param x: X coordinate of the cell's center
    :type x: float
    :param y: Y coordinate of the cell's center
    :type y: float
    :param cell_width: width of cell
    :type cell_width: float
    :param cell_height: height of cell
    :type cell_height: float
    :param img_dir: Filepath to image directory
    :type img_dir: str

    :return: a list of all contained images
    :rtype: [str, str, ..., str]
    """

    selected_list = []
    buffer = circumscribeCellWithEllipse(x, y, cell_width, cell_height)
    vertices = buffer.get_verts()     # get the vertices from the ellipse object
    selection_area = geometry.Polygon(vertices)
    for i in sorted(os.listdir(img_dir)):
        img = img_dir + '/' + i
        x_i, y_i = getProjectedImgCoord(img, SOURCE_EPSG, TARGET_EPSG)
        img_point = geometry.Point(x_i, y_i)
        if selection_area.contains(img_point) == True:
            selected_list.append(img)
    return(selected_list)


def circumscribeCellWithEllipse(x, y, cell_width, cell_height):
    """
    Calculates the ellipse that circumscribes a cell given its width and height.

    :param x: X coordinate of the cell's center
    :type x: float
    :param y: Y coordinate of the cell's center
    :type y: float
    :param cell_width: width of cell
    :type cell_width: float
    :param cell_height: height of cell
    :type cell_height: float

    :return: the circumscribing ellipse
    :rtype: matplotlib.patches.Ellipse
    """
    r1 = np.sqrt((cell_width/2)**2 * (1+(cell_height/2)/(cell_width/2)))
    r2 = np.sqrt((cell_height/2)**2 * (1+(cell_width/2)/(cell_height/2)))
    selection_buffer = Ellipse((x,y), r1*2, r2*2)

    return(selection_buffer)

def selectAllPhotosInDirectory(input_dir, num_cells, cell_x, cell_y, cell_height, cell_width, min_img):
    """
    Uses selectPhotosWithinCell over an entire directory. Returns all images that were contained by the cell.

    :param input_dir: Filepath to the directory
    :type input_dir: str
    :param num_cells: The number of cells for the target area.
    :type num_cells: int
    :param cell_x: X coordinate of the cell's center
    :type cell_x: float
    :param cell_y: Y coordinate of the cell's center
    :type cell_y: float
    :param cell_width: width of cell
    :type cell_width: float
    :param cell_height: height of cell
    :type cell_height: float
    :param min_img: A threshold for minimum number of images needed to accept a cell.
    :type min_img: int

    :return: a list of all contained images or None, if not enough photos were found.
    :rtype: [str, str, ..., str]

    """
    for i in range(0, num_cells):
        image_list = selectPhotosWithinCell(cell_x[i], cell_y[i], cell_height, cell_width, input_dir)
        if len(image_list) < min_img:
            return None
        else:
            return(image_list)

def findLargestBB(input_root, source_crs, target_crs):
    """
    Calculates the bounding box for a nested directory of images (depth of 1). Returns the
    composite bounding box.

    :param img_dir: Filepath to nested image directory
    :type img_dir: str
    :param source_crs: The EPSG code for desired CRS, for example  'EPSG:3310'
    :type source_crs: str
    :param target_crs: The EPSG code for original CRS, for example  'EPSG:4326'
    :type target_crs: str    

    :return: Returns a nested list with the lower left and upper right corners
    :rtype: [[float, float], [float, float]]
    """
    min_x = []
    max_x = []
    min_y = []
    max_y = []

    for i in sorted(os.listdir(input_root)):
        current_dir = input_root + '/' + i
        if not os.path.isdir(current_dir):
            continue
        current_bb = getBBFromDirectory(current_dir, source_crs, target_crs)
        print(i, ':', current_bb)
        min_x.append(current_bb[0][0])
        min_y.append(current_bb[0][1])
        max_x.append(current_bb[1][0])
        max_y.append(current_bb[1][1])
    
    min_x = min(min_x)
    max_x = max(max_x)
    min_y = min(min_y)
    max_y = max(max_y)

    return [[min_x, min_y], [max_x, max_y]]

def selectFromNestedDirectory(input_root, output_root, source_crs, target_crs, cell_height, cell_width, min_img):
    """
    This is a convenience function to generate cells and select photos from multiple directories.

    :param input_root: Filepath to the nested directory
    :type input_root: str
    :param output_root: Filepath to the desired output directory.
    :type output_root: str
    :param source_crs: The EPSG code for desired CRS, for example  'EPSG:3310'
    :type source_crs: str
    :param target_crs: The EPSG code for original CRS, for example  'EPSG:4326'
    :type target_crs: str    
    :type cell_y: float
    :param cell_width: width of cell
    :type cell_width: float
    :param cell_height: height of cell
    :type cell_height: float
    :param min_img: A threshold for minimum number of images needed to accept a cell.
    :type min_img: int
    """
    [ll, ur] = findLargestBB(input_root, source_crs, target_crs)
    num_cells = calculateCellsRequired(ll[0],ll[1], ur[0], ur[1], cell_height, cell_width)
    cell_x, cell_y = findCellCenters(ll[0], ll[1], cell_height, cell_width)
    for i in sorted(os.listdir(input_root)):
        current_dir = input_root + '/' + i
        if not os.path.isdir(current_dir):
            continue
        for j in range(0, num_cells):
            img_list = selectPhotosWithinCell(cell_x[j], cell_y[j], cell_height, cell_width, current_dir)
            if len(img_list) < min_img:
                continue
            output_dir = output_root + '/' + str(j)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            counter  = 0
            for k in img_list:
                new_file = output_dir + '/' + str(j) + '_' + str(counter) + '.jpg'
                shutil.copy(k, new_file)
                counter += 1

test_root = '/Users/theo/Desktop/whitell_1_frames_n_30'


selectFromNestedDirectory(test_root, output_root, SOURCE_EPSG, TARGET_EPSG, 10, 10, 50)

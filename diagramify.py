import cv2 as cv
import math
from filled_shape import filled_shape as fs
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--image", "-i", type=argparse.FileType('r'),
                    dest="image_path", help="Use image as source")
parser.add_argument("--cam", "-c", dest='cam', default=False, action='store_true', help="Use cam as source")
parser.add_argument("--debug", default=False, action='store_false', help="show more contours and points")

arg = parser.parse_args()

def distance(x2, x1, y2, y1):
    print(((x2 - x1) ** 2) + ((y2 - y1) ** 2))
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
def construct_graph(shapes, all_lines):
    dicts = []

    for line_coords in all_lines:
        for coords in line_coords[1]:
            for shape in shapes:
                shape_x = shape[2]
                shape_y = shape[3]
                shape_id = shape[0]
                shape_name = shape[1]

                line_x = coords[0]
                line_y = coords[1]
                line_id = line_coords[0]

                print(distance(line_x, shape_x, line_y, shape_y))
                if distance(line_x, shape_x, line_y, shape_y) <= 200:
                    # line is close to shape

                    does_dict_exist = False
                    for dict in dicts:
                        if dict['line_id'] == line_id:
                            # line exsists in dicts

                            # check if connected on both ends
                            # assuming from is specified
                            if dict['to'] is None and shape_id != dict['from']:
                                # not connected on one end of line
                                dict['to'] = shape_id
                                does_dict_exist = True
                                break
                            elif dict['to'] is not None:
                                does_dict_exist = True
                                break

                    if not does_dict_exist: 
                        dicts.append({
                            'line_id': line_id,
                            'from': shape_id,
                            'to': None,
                        })
                        
    print(dicts)

            
            

if arg.cam and arg.image_path is not None:
    raise Exception("Cam and Image cannot be used simultaneously")
if arg.cam:
    cap = cv.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            fs.capture(frame, arg.debug)

        k = cv.waitKey(30) & 0xFF
        if k == 27:
            break
    cap.release()
    cv.destroyAllWindows()
elif arg.image_path is not None:
    frame = cv.imread(arg.image_path.name)
    # shapes -> [gid, x-co-ord, y-co-ord]

    shapes,lines = fs.capture(frame, arg.debug)

    construct_graph(shapes, lines)
    cv.waitKey(0)
    cv.destroyAllWindows()
else:
    parser.parse_args(['--help'])





# def find_closest_shape_to_line():

import cv2 as cv
import uuid
import numpy as np
import matplotlib.pyplot as plt

font = cv.FONT_HERSHEY_SIMPLEX

class FilledShape:
    def __init__(self, img):
        self.img = img

    def gen_uuid(self):
        return uuid.uuid1()

    def detect(self, contour, debug):
        shape = "undefined"
        epsilon = (0.03 * cv.arcLength(contour, True)) 
        approx = cv.approxPolyDP(contour, epsilon, True)
        x, y, w, h = cv.boundingRect(contour)

        cv.rectangle(self.img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv.rectangle(self.img, (x, y-10), (x + w, y + 10), (0, 0, 255), -1)
        number = ""
        if debug:
            cv.drawContours(self.img, [contour], 0, (0, 255, 0), 2)

            for pt in approx:
                cv.circle(self.img, (pt[0][0], pt[0][1]), 5, (255, 0, 0), -1)
            number = str(len(approx)) + " "
        if len(approx) == 3:
            shape = "triangle"
        elif len(approx) == 4:
            # print(w, h, w / h)
            if 0.95 < w / h < 1.05:
                shape = "Square"
            else:
                shape = "Rectangle"
        else:
            return

        cv.putText(self.img, shape + number, (x, y), font, 1, (255, 123, 255), 1, cv.LINE_AA)
        return [self.gen_uuid(), x, y]
        


    def preprocessing_image(self):
        img_gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        ret, thresh = cv.threshold(img_gray, 127, 255, 0)
        kernel = np.ones((5, 5), np.uint8)
        cv.dilate(thresh, kernel, iterations=1)
        thresh = cv.GaussianBlur(thresh, (15, 15), 0)

        contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        return thresh, contours

    def process_circles(self):
        # detect circles in the image
        img_gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)

        circles = cv.HoughCircles(img_gray, cv.HOUGH_GRADIENT, 0.2, 800)

        # ensure at least some circles were found
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")

            # loop over the (x, y) coordinates and radius of the circles
            for (a, b, r) in circles:
                cv.circle(self.img, (a, b), r, (0, 255, 0), 4)
                cv.rectangle(self.img, (a - 5, b - 5), (a + 5, b + 5), (0, 128, 255), -1)
                cv.putText(self.img, "circle", (a, b), font, 2, (255, 123, 255), 1, cv.LINE_AA)


    def process_lines(self):
        img_gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        edges = cv.Canny(img_gray,50,150,apertureSize = 3)
        minLineLength = 500
        maxLineGap = 5
        lines = cv.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)

        all_coords = []
        
        
        for x in  range(0, len(lines) - 1): 
            line_coords = []

            # prev_coords = [lines[x][0][0], lines[x][0][1]]

            for x1,y1,x2,y2 in lines[x]:
                print('mosss: ', lines[x])
                line_coords.append([x1, y1])

                # if abs(x1 - prev_coords[0]) <= 10:
                #     prev_coords = [x1, y1]
                #     break

                # prev_coords = [x1, y1]
                # line_coords.append([x2, y2])


                cv.line(self.img,(x1,y1),(x2,y2),(123,255,3),2)
            all_coords.append(line_coords)

        return self.max(all_coords)


    def max(self, all_coords):
        all_groups = []
        temp_group = []
        for i in range(0, len(all_coords) - 1):
            mini_line = all_coords[i][0]
            temp_x = mini_line[0]
            temp_y = mini_line[1]

            next_x = all_coords[i+1][0][0]
            next_y = all_coords[i+1][0][1]

            if abs(next_x - temp_x) <= 40:
                temp_group.append([temp_x, temp_y])
            elif abs(next_y - temp_y) <= 40:
                temp_group.append([temp_x, temp_y])
            else:
                temp_group.append([temp_x, temp_y])
                cv.putText(self.img, "group", (temp_x, temp_y), font, 1, (255, 123, 255), 1, cv.LINE_AA)
                all_groups.append(temp_group)
                temp_group = []

        return all_groups



def capture(frame, debug=False):
    img_object = FilledShape(frame)
    _, contours = img_object.preprocessing_image()

    all_lines = img_object.process_lines()

    all_shapes = []
    for contour in contours:
        shape_coords = img_object.detect(contour, debug)
        all_shapes.append(shape_coords)
    


    cv.imshow('Original', frame)

    return all_lines, all_shapes,
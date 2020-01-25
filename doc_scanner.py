# import the necessary packages
from transform import four_point_transform
from skimage.filters import threshold_local

import numpy as np
import argparse
import cv2
import imutils
 

def get_args():
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required = True,
		help = "Path to the image to be scanned")
	args = vars(ap.parse_args())
	return args

def get_raw_img_with_vals(args):
	# load the image and compute the ratio of the old height
	# to the new height, clone it, and resize it
	image = cv2.imread(args["image"])
	ratio = image.shape[0] / 500.0
	print(ratio)
	orig = image.copy()
	image = imutils.resize(image, height = 500)
	return image, ratio, orig

def get_edged_image(image):
	print("STEP 1: Edge Detection")
	# convert the image to grayscale, blur it, and find edges
	# in the image
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 75, 200)
	return edged

def get_contoured_image(image):
	print("STEP 2: Find contours of paper")
	# find the contours in the edged image, keeping only the
	# largest ones, and initialize the screen contour
	cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

	screenCnt = cv2.CHAIN_APPROX_SIMPLE


	# loop over the contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)

		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break


	if screenCnt is None:
		print("does not contain 4 verticies or already framed image") 
	else:
		cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
	
	return image, screenCnt

def perspective_tranform(screenCnt, ratio, orig):
	print("STEP 3: Apply perspective transform")
	# apply the four point transform to obtain a top-down
	# view of the original image
	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
	# convert the warped image to grayscale, then threshold it
	# to give it that 'black and white' paper effect
	warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
	T = threshold_local(warped, 25, offset = 15, method = "gaussian")
	warped = (warped > T).astype("uint8") * 255
	return warped
	
	

def render_results(image, edged, contoured, warped):
	# show the original image and the edge detected image
	cv2.imshow("Image", image)
	cv2.imshow("Edged", edged)
	# show the contour (outline) of the piece of paper
	cv2.imshow("Outline", contoured)
	

	# show the original and scanned images
	cv2.imshow("Scanned", imutils.resize(warped, height = 650))


if __name__ == "__main__":
	pass
	args = get_args()
	raw_img, ratio, orig = get_raw_img_with_vals(args)

	edged = get_edged_image(raw_img)
	countoured, screenCnt = get_contoured_image(edged)

	warped = perspective_tranform(screenCnt, ratio, orig)

	render_results(raw_img, edged, countoured, warped)

	cv2.waitKey(0)
	cv2.destroyAllWindows()

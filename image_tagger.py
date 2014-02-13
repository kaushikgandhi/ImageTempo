import cv2
import sys
import numpy as np
import Image
def process_image():
	#img = cv2.imread('uploads/images.jpeg',cv2.CV_LOAD_IMAGE_COLOR)
	img = Image.open( 'uploads/images.jpeg' )
	img.load()
	data = np.asarray( img, dtype="int32" )
	img = Image.fromarray( np.asarray( np.clip(data,0,255), dtype="int32"), "L" )
	img.save( 'uploads/images2.jpeg' )
	if img==None:
		print 'not found'
	print data
	#cv2.cvtColor(src, dest,CV_RGB2HSV)
	return "Done"

if __name__ == '__main__':
	process_image()
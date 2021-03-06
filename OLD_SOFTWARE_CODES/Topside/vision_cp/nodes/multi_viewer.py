#!/usr/bin/env python2

# Tool to help with viewing different types of filters

import roslib; roslib.load_manifest('vision_cp')
import rospy
from sensor_msgs.msg import Image

import Tkinter as tk
import PIL.Image as PImage
import ImageTk

import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError


# Helper function to get a readable timestamp
def get_timestamp():
	import time
	return time.strftime('%Y-%m-%d-%H%M%S')


# Helper function to draw a histogram image
def get_hist_img(cv_img):
	hist_bins = 256
	hist_ranges = [(0,255)]

	#hist = cv2.calcHist([cv_img], [0], np.zeros([0,0]), [256], [[0,255]])
	hist, _ = np.histogram(cv_img, hist_bins, (0, 255))
	maxVal = np.max(hist)

	histImg = np.array( [255] * (hist_bins * hist_bins), dtype=np.uint8 ).reshape([hist_bins, hist_bins])
	hpt = int(0.9 * hist_bins)

	for h in range(hist_bins):
		binVal = float(hist[h])
		intensity = int(binVal * hpt / maxVal)
		cv2.line(histImg, (h, hist_bins), (h, hist_bins-intensity), 0)

	return histImg


# Helper class for the various filters
class FilterFrame:
	thumbnail_size = (180, 180)
	image = None

	def __init__(self, filter_name, tkparent):
		self.img_filter = None
		self.filter_name = filter_name

		self.tkout = tk.Label(tkparent, text=filter_name)

	def grid(self, column, row):
		self.tkout.grid(column=column, row=row)

	def got_frame(self, cv_img):
		if self.img_filter:
			self.image = self.img_filter(cv_img)
		else:
			self.image = cv_img

		filtered_pil = PImage.fromarray(self.image)
		filtered_pil.thumbnail(self.thumbnail_size, PImage.ANTIALIAS)
		tkfiltered = ImageTk.PhotoImage(filtered_pil)

		self.tkout.config({'image': tkfiltered})
		self.tkout.photo = tkfiltered # prevent garbage collection


class MultiViewer:
	# Convert a ROS Image to the Numpy matrix used by cv2 functions
	def rosimg2cv(self, ros_image):
		# Convert from ROS Image to old OpenCV image
		frame = self.cvbridge.imgmsg_to_cv(ros_image, ros_image.encoding)
		# Convert from old OpenCV image to Numpy matrix
		return np.array(frame, dtype=np.uint8) #TODO: find out actual dtype



	def __init__(self, tkroot, videoname=''):
		tkframe = tk.Frame(tkroot)
		tkframe.pack()

		tkvidframe = tk.Frame(tkframe)
		tkvidframe.pack(side=tk.TOP)

		tkbtnframe = tk.Frame(tkframe)
		tkbtnframe.pack(side=tk.BOTTOM)

		self.rec_btn = tk.Button(tkbtnframe, text="REC", command=self.got_rec)
		self.rec_btn.pack(side=tk.LEFT)

		self.vid_writer = None

		self.snap_btn = tk.Button(tkbtnframe, text="Snap", command=self.got_snap)
		self.snap_btn.pack(side=tk.RIGHT)

		self.img_label = tk.Label(tkvidframe, text="Webcam feed")
		self.img_label.pack()

		self.cvbridge = CvBridge()
		self.cur_ros_img = None


		# If there's a video, we use it (and do our own event)
		if videoname != '':
			video = cv2.VideoCapture(videoname)
			def vid_callback():
				retval, frame = video.read()
				self.got_frame(frame)
				tkroot.after(30, vid_callback)
			tkroot.after(50, vid_callback)


		# Set up frames for filtered videos
		tkfilters = tk.Frame(tkroot)
		tkfilters.pack(fill=tk.Y)

		# Set up scrollbar
		tkscroll = tk.Scrollbar(tkfilters)
		tkscroll.pack(side=tk.RIGHT, fill=tk.Y)

		tkfilterframe = tk.Canvas(tkfilters)
		tkfilterframe.pack()


		# Setting up the actual filters
		# Dictionary for easy access to filters
		self.filters = { }
		# Array for ordered calling of filters
		self.filter_list = [ ]

		# No filter at all
		nullfilter = FilterFrame('null', tkfilterframe)
		self.filters['null'] = nullfilter

		# Grayscale filter
		grayfilter = FilterFrame('gray', tkfilterframe)
		grayfilter.img_filter = lambda (cv_img): cv2.cvtColor(cv_img, cv2.cv.CV_RGB2GRAY)
		self.filters['gray'] = grayfilter

		# Conversion to HSV
		hsvfilter = FilterFrame('hsv', tkfilterframe)
		hsvfilter.img_filter = lambda (cv_img): cv2.cvtColor(cv_img, cv2.cv.CV_RGB2HSV)
		self.filters['hsv'] = hsvfilter

		# Histogram of the grayscale image
		grayhistfilter = FilterFrame('grayhist', tkfilterframe)
		grayhistfilter.img_filter = lambda (_): get_hist_img(grayfilter.image)
		self.filters['grayhist'] = grayhistfilter

		# Grayscale image that has its histogram equalized
		equalhistfilter = FilterFrame('equalhist', tkfilterframe)
		equalhistfilter.img_filter = lambda (_): cv2.equalizeHist(grayfilter.image)
		self.filters['equalhist'] = equalhistfilter

		# Original image - its Laplacian
		tmpkernel = np.array([[0., -1., 0.],[-1., 5., -1.], [0., -1., 0.]])
		sublaplacefilter = FilterFrame('sublaplace', tkfilterframe)
		sublaplacefilter.img_filter = lambda (cv_img): cv2.filter2D(cv_img, -1, tmpkernel)
		self.filters['sublaplace'] = sublaplacefilter

		# Canny (edge detection)
		cannyfilter = FilterFrame('canny', tkfilterframe)
		cannyfilter.img_filter = lambda (_): cv2.threshold(cv2.Canny(grayfilter.image, 125, 350), 128, 255, cv2.THRESH_BINARY_INV)[1]
		self.filters['canny'] = cannyfilter

		# R,G,B
		rfilter = FilterFrame('r_only', tkfilterframe)
		rfilter.img_filter = lambda (cv_img): cv2.split(cv_img)[0]
		self.filters['r_only'] = rfilter

		gfilter = FilterFrame('g_only', tkfilterframe)
		gfilter.img_filter = lambda (cv_img): cv2.split(cv_img)[1]
		self.filters['g_only'] = gfilter

		bfilter = FilterFrame('b_only', tkfilterframe)
		bfilter.img_filter = lambda (cv_img): cv2.split(cv_img)[2]
		self.filters['b_only'] = bfilter

		# R,G,B Histogram
		rhistfilter = FilterFrame('rhist', tkfilterframe)
		rhistfilter.img_filter = lambda (_): get_hist_img(rfilter.image)
		self.filters['rhist'] = rhistfilter

		ghistfilter = FilterFrame('ghist', tkfilterframe)
		ghistfilter.img_filter = lambda (_): get_hist_img(gfilter.image)
		self.filters['ghist'] = ghistfilter

		bhistfilter = FilterFrame('bhist', tkfilterframe)
		bhistfilter.img_filter = lambda (_): get_hist_img(bfilter.image)
		self.filters['bhist'] = bhistfilter

		# Mult equal gray hist with orig
		#TODO: figure out the more optimized (or simpler code) version
		def eqcolor(cv_img):
			result = np.empty_like(cv_img)
			for r in range(cv_img.shape[0]):
				for c in range(cv_img.shape[1]):
					factor = (equalhistfilter.image[r,c] / 255.)
					result[r,c] = cv_img[r,c] * factor
			return result
		equalcolorfilter = FilterFrame('equalcolor', tkfilterframe)
		equalcolorfilter.img_filter = eqcolor
		self.filters['equalcolor'] = equalcolorfilter

		# RGB to Lab
		labfilter = FilterFrame('lab', tkfilterframe)
		labfilter.img_filter = lambda (cv_img): cv2.cvtColor(cv_img, cv2.cv.CV_RGB2Lab)
		self.filters['lab'] = labfilter

		# RGB to Luv
		luvfilter = FilterFrame('luv', tkfilterframe)
		luvfilter.img_filter = lambda (cv_img): cv2.cvtColor(cv_img, cv2.cv.CV_RGB2Luv)
		self.filters['luv'] = luvfilter


		# Array for ordered calling of filters
		# All the filters
		ordered_list = ['null', 'gray', 'hsv', 'grayhist', 'equalhist', 'sublaplace', 'canny',
				'r_only', 'g_only', 'b_only', 'rhist', 'ghist', 'bhist',
				'equalcolor']
#		ordered_list = ['null', 'gray', 'hsv', 'grayhist', 'equalhist', 'sublaplace', 'canny']
#		ordered_list = ['r_only', 'g_only', 'b_only', 'rhist', 'ghist', 'bhist']
#		ordered_list = ['lab', 'luv']
		# Set up the on-screen positions of the filters
		index, max_col = 0, 3
		for name in ordered_list:
			cur_row, cur_col = index // max_col, index % max_col
			self.filters[name].grid(column=cur_col, row=cur_row)
			self.filter_list.append(self.filters[name])
			index += 1

		# Set up scrollbar
		tkfilterframe.config(yscrollcommand=tkscroll.set)
		tkscroll.config(command=tkfilterframe.yview)


	# Callback for subscribing to Image topic
	def got_ros_frame(self, ros_image):
		self.cur_ros_img = ros_image
		cvimg = self.rosimg2cv(ros_image)
		self.got_frame(cvimg)

	def got_frame(self, cvimg):
		rgbimg = np.empty_like(cvimg)
		cv2.mixChannels([cvimg], [rgbimg], [0,2, 1,1, 2,0])

		tmpimg = PImage.fromarray(rgbimg)
		tmpimg.thumbnail((300, 300), PImage.ANTIALIAS)

		tkimage = ImageTk.PhotoImage(tmpimg)
		self.img_label.config({'image': tkimage})
		self.img_label.photo = tkimage # prevent garbage collection

		# Resize the image for display (or maybe should resize each output image)
		if self.vid_writer:
			self.vid_writer.write(rgbimg)

		for tkfilter in self.filter_list:
			tkfilter.got_frame(rgbimg)


	# Callback when Snap button is pressed
	def got_snap(self):
		if self.cur_ros_img:
			cvimg = self.rosimg2cv(self.cur_ros_img)
			filename = 'snapshot-' + get_timestamp() + '.jpg'
			cv2.imwrite(filename, cvimg)


	# Callback when Rec button is pressed
	def got_rec(self):
		if self.vid_writer:
			# Stop recording
			self.vid_writer = None
			self.rec_btn.config({'text': 'Rec'})
		else:
			# Start recording
			self.rec_btn.config({'text': 'Stop'})
			filename = 'recording-' + get_timestamp() + '.mpg'
			self.vid_writer = cv2.VideoWriter(filename, cv2.cv.CV_FOURCC(*'PIM1'), 24, (320, 240)) #TODO: use actual video framerate, width, height


if __name__ == '__main__':
	rospy.init_node('multi_viewer', anonymous=True)
	video = ''
	if rospy.has_param('~video'):
		video = rospy.get_param('~video')

	tkroot = tk.Tk()
	app = MultiViewer(tkroot, video)

	# Only subscribe to the camera topic if we aren't given a video
	if video == '':
		rospy.Subscriber("/camera/rgb/image_color", Image, app.got_ros_frame)

	tkroot.mainloop()

import os
import math
import numpy as np
import tensorflow as tf
import pickle
import cv2
from HandTrackingModule import HandDetector
from tensorflow.keras.preprocessing import image

offset = 20
img_size = 64


model = tf.keras.models.load_model('vgg16_model4.h5')

cap  = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)

with open('categories.pkl') as file:
	categories = eval(file.read())


while True:
	if cv2.waitKey(10) & 0xFF == 27: # press ESC to exit
		break

	success, img = cap.read()
	hands, img = detector.findHands(img)
	img = cv2.flip(img, 1) # flip the frame horizontally


	if hands:
		hand = hands[0]
		x, y, w, h = hand['bbox']
		
		imgCrop = img[y-offset : y+h+offset, -x-w+offset-35 : -x+offset]
		imgWhite = np.ones((img_size, img_size, 3), np.uint8)*255

		aspectRation = h/w

		if aspectRation > 1:
			try:
				k = img_size / h
				wCal = math.ceil(k*w)

				imgResize = cv2.resize(imgCrop, (wCal, img_size))
				imgResizeShape = imgResize.shape
				wGap = math.ceil((img_size - wCal) / 2)
				imgWhite[:, wGap : wCal+wGap] = imgResize

			except Exception as e:
				pass

		else:
			try:
				k = img_size / w
				hCal = math.ceil(k*h)

				imgResize = cv2.resize(imgCrop, (img_size, hCal))
				imgResizeShape = imgResize.shape
				hGap = math.ceil((img_size - hCal) / 2)
				imgWhite[hGap : hCal+hGap, :] = imgResize


			except Exception as e:
				pass


		try:
			pass
			# cv2.imshow('', imgWhite)

		except Exception as e:
			pass

		my_image_arr = image.img_to_array(imgWhite)
		my_image_pixel = np.expand_dims(my_image_arr, axis=0)
		my_image_pixel = my_image_pixel / 255
		prediction = model.predict(my_image_pixel, verbose=False)
		prediction_class = np.argmax(prediction, axis=1)
		# prediction_class = np.argmax(prediction[0])
		c = categories[tuple(prediction_class)[0]]

		cv2.putText(img, c, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)
	
	cv2.imshow('Image', img)
	key = cv2.waitKey(1)

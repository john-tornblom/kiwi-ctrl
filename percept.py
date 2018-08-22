#!/usr/bin/env python2
# encoding: utf-8
# Copyright (C) 2018 John Törnblom
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import threading
import sysv_ipc
import numpy
import math
import cv2
import logging

logger = logging.getLogger(__name__)


class Perseption(object):
    running = False
    evt_handler = None
    thread = None
    
    def __init__(self, evt_handler):
        self.evt_handler = evt_handler

    def stop(self):
        self.running = False
        self.thread.join()

    def start(self):
        assert self.running is False
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    
class CameraPerseption(Perseption):
    name = None
    
    def __init__(self, evt_handler, name='/tmp/img.argb'):
        Perseption.__init__(self, evt_handler)
        self.name = name
                
    def _run(self):
        # Obtain the keys for the shared memory and semaphores.
        keySharedMemory = sysv_ipc.ftok(self.name, 1, True)
        keySemMutex = sysv_ipc.ftok(self.name, 2, True)
        keySemCondition = sysv_ipc.ftok(self.name, 3, True)
        
        # Instantiate the SharedMemory and Semaphore objects.
        shm = sysv_ipc.SharedMemory(keySharedMemory)
        mutex = sysv_ipc.Semaphore(keySemCondition)
        cond = sysv_ipc.Semaphore(keySemCondition)

        while self.running:
            try:
                cond.Z(timeout=1)
            except:
                continue
            
            # with statement???
            mutex.acquire()
            shm.attach()
            buf = shm.read()
            shm.detach()
            mutex.release()

            img = numpy.frombuffer(buf, numpy.uint8).reshape(480, 640, 4)
            self.on_data(img)

    def on_data(self, argb):
	# one kind of green supposed to represent the post-it
	hsv_mask = (80, 150, 150)
	# allow some deviation in color
	threshold = 0.24

	upper_mask = (int(min(hsv_mask[0]*(1+threshold), 179)),
		      int(min(hsv_mask[1]*(1+threshold), 255)),
		      int(min(hsv_mask[2]*(1+threshold), 255)))
	lower_mask = (int(max(hsv_mask[0]*(1-threshold), 0)),
		      int(max(hsv_mask[1]*(1-threshold), 0)),
		      int(max(hsv_mask[2]*(1-threshold), 0)))


	### Assuming ARGB input
	img = argb
	# apply some blurring to help edge detection
	img_blurred = cv2.GaussianBlur(img, (5, 5), 0)
	hsv = cv2.cvtColor(img_blurred, cv2.COLOR_RGB2HSV)
	# finds color mask between lower green color and upper green color
	mask = cv2.inRange(hsv, lower_mask, upper_mask)
	kernel = np.ones((5,5),np.uint8)
	eroded_mask = cv2.erode(mask,kernel,iterations = 5)
	dilated_mask = cv2.dilate(mask,kernel,iterations = 5)
	# only take the pixels allowed by the mask
	dilated_img = cv2.bitwise_and(img_blurred, img_blurred, mask=dilated_mask)
	ret, thresh = cv2.threshold(mask, 40, 255, 0)
	im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
						    cv2.CHAIN_APPROX_NONE)

	if len(contours) != 0:
            cv2.drawContours(img, contours, -1, 255, 3)
	    c = max(contours, key = cv2.contourArea)
	    x,y,w,h = cv2.boundingRect(c)

            cv2.rectangle(masked_img,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.imshow("image", masked_img);
            cv2.waitKey(2);
            
	    height, width, _ = masked_img.shape
	    ### TODO: Calculate correct distance using lens eye calculations
	    d = 0.05 / (y+h)
	    delta = width/2.-(x+w)/2.
	    theta = math.atan2(delta, d) 

	    # send distance and angle to handlers
            self.evt_handler(d, theta) # distance and angle to object
            


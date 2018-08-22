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

from opendlv_standard_message_set_v0_9_6_pb2 import \
    opendlv_proxy_GroundSteeringRequest as GroundSteeringRequest, \
    opendlv_proxy_PedalPositionRequest as PedalPositionRequest


import logging
import numpy


logger = logging.getLogger(__name__)


class PlatoonController(object):
    session = None
    distance = None
    angle = None
    
    # Camera frequency
    # if last reading (last found contour) too long ago, reset d error

    
    # Controller parameters

    self.Kp_theta = 0.5
    self.Kp_acc   = 1.0
    self.Kd_acc   = 1.0
 
    # Position error for the derivating part
    self.prev_err = 0.0
    self.last_received_error = 0.0 # should be time

    # Action clipping
    max_ang = 38.0/360. * 2 * math.pi
    max_thrust_forward = 0.25
    max_thrust_backward = 1.
    
    def __init__(self, session):
        self.session = session

    def on_front_camera(self, distance, angle):
        '''
        Handle camera signal (ARGB)
        '''
        logger.info('front camera: %2.2f, %2.2f', distance, angle)
    
    def on_front_ultrasonic(self, value):
        '''
        Handle front-facing ultrasonic sensor (distance in meters)
        '''
        logger.info('front ultrasonic: %2.2f', value)

    def on_rear_ultrasonic(self, value):
        '''
        Handle rear-facing ultrasonic sensor (distance in meters)
        '''
        logger.info('rear ultrasonic: %2.2f', value)

    def on_left_infrared(self, value):
        '''
        Handle left infrared sensor (???)
        '''
        logger.info('left infrared: %2.2f', value)

    def on_right_infrared(self, value):
        '''
        Handle right infrared sensor (???)
        '''
        logger.info('right infrared: %2.2f', value)
    
    def emit(self):
        '''
        Emit control signal
        '''
        # range: +38deg (left) .. -38deg (right).
        # radians (DEG/180. * PI).
	
        steer_req = GroundSteeringRequest()
	if angle != 0:
	    if angle > 0:
	        steering = min(max_ang, self.Kp_theta * angle)
            else:
		steering = max(-max_ang, self.Kp_theta * angle)
	steering = 0
        steer_req.groundSteering = steering

        # range: +0.25 (forward) .. -1.0 (backwards).
        pedal_req = PedalPositionRequest()
        pedal_req.position = 0

        self.session.send(1086, pedal_req.SerializeToString());
        self.session.send(1090, steer_reg.SerializeToString());
        

    

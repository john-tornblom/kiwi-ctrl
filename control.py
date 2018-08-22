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
import numpy as np


logger = logging.getLogger(__name__)


class PlatoonController(object):
    session = None

    # Sensor states
    cam_angle = None
    cam_distance = None
    front_distance = None
    left_distance = None
    rear_distance = None     
    right_distance = None
    
    # Controller parameters
    Kp_theta = 0.5
    Kp_acc   = 1.0
    Kd_acc   = 1.0

    # Controller clipping thresholds
    max_angle = 38.0/360.0 * 2 * np.pi
    min_angle = -max_angle
    
    max_pedal_position = 0.25
    min_pedal_position = -1.0
    
    def __init__(self, session):
        self.session = session

    def on_front_camera(self, distance, angle):
        '''
        Handle distance and angle estimates from camera (distance in meters, angle in radians)
        '''
        logger.info('front camera: %2.2f, %2.2f', distance, angle)
        if angle is not None:
            self.cam_angle = angle
            
        self.distance = distance

        self.emit_ground_steering()
        
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

    def emit_ground_steering(self):
        '''
        Emit ground steering control signal
        '''
        angle = self.cam_angle * self.Kp_theta
        angle = min(self.max_angle, angle)
        angle = max(self.min_angle, angle)
        req = GroundSteeringRequest()
        req.groundSteering = angle
        self.session.send(1090, req.SerializeToString());
        
    def emit_pedal_position(self):
        '''
        Emit pedal position control signal
        '''
	position = 0
        position = min(self.max_pedal_position, position)
        position = max(self.min_pedal_position, position)
        
        req = PedalPositionRequest()
        req.position = position
        self.session.send(1086, req.SerializeToString());
        

    

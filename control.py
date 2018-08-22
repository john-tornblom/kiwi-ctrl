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

    
    # Controller parameters
    Kp   = 0.5
    Kd   = 0.0
    setpoint = 0.3
    cam_filter_weight = 0.3
    
    # Sensor states
    cam_angle = 0
    cam_distance = setpoint
    front_distance = setpoint
    
    # Platooning parameters
    min_distance_front = 0.3 # minimum distance to object ahead
    min_distance_rear  = 0.3 # minimum distance to object behind
    proximity_threshold = 0.1 # don't run into walls or closeby trafiic
    
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
        if angle is not None:
            self.cam_angle = ((self.cam_filter_weight * self.cam_angle) +
                              (1 - self.cam_filter_weight) * angle)
            
        self.cam_distance = distance
        self.emit_ground_steering()
        
    def on_front_ultrasonic(self, value):
        '''
        Handle front-facing ultrasonic sensor (distance in meters)
        '''
        if value < self.proximity_threshold:
            self.max_pedal_position = 0.0
        else:
            self.max_pedal_position = PlatoonController.max_pedal_position

        self.front_distance = value
        self.emit_pedal_position()
            
    def on_rear_ultrasonic(self, value):
        '''
        Handle rear-facing ultrasonic sensor (distance in meters)
        '''
        if value < self.proximity_threshold:
            self.min_pedal_position = 0.0
        else:
            self.min_pedal_position = PlatoonController.min_pedal_position
            
    def on_left_infrared(self, value):
        '''
        Handle left infrared sensor (distance in meters)
        '''
        if value < self.proximity_threshold:
            self.min_angle = 0.0
        else:
            self.min_angle = PlatoonController.min_angle
        
    def on_right_infrared(self, value):
        '''
        Handle right infrared distance in meters)
        '''
        if value < self.proximity_threshold:
            self.max_angle = 0.0
        else:
            self.max_angle = PlatoonController.max_angle
        
    def emit_ground_steering(self):
        '''
        Emit ground steering control signal
        '''            
        angle = self.cam_angle
        angle = min(self.max_angle, angle)
        angle = max(self.min_angle, angle)
        req = GroundSteeringRequest()
        req.groundSteering = angle
        self.session.send(1090, req.SerializeToString());
        
    def emit_pedal_position(self):
        '''
        Emit pedal position control signal
        '''
        error = self.front_distance - self.setpoint
        delta = 0
        
	position = self.Kp * error + self.Kd * delta
        position = min(self.max_pedal_position, position)
        position = max(self.min_pedal_position, position)

        req = PedalPositionRequest()
        req.position = position
        self.session.send(1086, req.SerializeToString());
        

    

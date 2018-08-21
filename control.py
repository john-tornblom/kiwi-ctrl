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


logger = logging.getLogger(__name__)


class PlatoonController(object):
    session = None
    distance = None
    angle = None
    
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
        steer_req.groundSteering = 0

        # range: +0.25 (forward) .. -1.0 (backwards).
        pedal_req = PedalPositionRequest()
        pedal_req.position = 0

        self.session.send(1086, pedal_req.SerializeToString());
        self.session.send(1090, steer_reg.SerializeToString());
        

    

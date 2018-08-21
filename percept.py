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
import cv2


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
        # TODO: Add some image processing logic here.
        self.evt_handler(0) # distance
            


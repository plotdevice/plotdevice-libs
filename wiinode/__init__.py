# WIINODE - last updated for NodeBox 1.9.4
# Author: Frederik De Bleser <frederik@pandora.be>
# Copyright (c) 2007 by Frederik De Bleser.
# See LICENSE.txt for details.

import osc

class WiiMote(object):
    
    """A wrapper class around OSC, for interfacing with the WiiMote.

    The interfacing works with a program called OSCulator, which is required.
    A settings file for the program (settings.oscd) is included.

    http://www.osculator.net/wiki/
    
    In your NodeBox animation, initialize the WiiMote object in your setup method,
    and call the WiiMote's update() method in your animation's update() method.

    This class is not NodeBox-specific -- you can use it in any Python project.
    """

    def __init__(self, address='127.0.0.1', port=9000, prefix='/wii/1'):
        if osc.outSocket == 0: # Only init once.
            osc.init()
        self.address = address
        self.port = port
        self.listener = osc.createListener(address, port)
        osc.bind(self._wii_pry, "/wii/1/accel/pry")
        osc.bind(self._wii_xyz, "/wii/1/accel/xyz")
        osc.bind(self._wii_a, "/wii/1/button/A")
        osc.bind(self._wii_b, "/wii/1/button/B")
        self.prefix = prefix
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.accel = 0.0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.a = False
        self.b = False
        
    def _wii_pry(self, data, xx):

        """Callback method that registers the pitch, roll, yaw and rotation acceleration"""

        address, ffff, pitch, roll, yaw, accel = data
        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw
        self.accel = accel

    def _wii_xyz(self, data, xx):

        """Callback method that registers the x, y, and z acceleration"""

        global wm
        address, ffff, x, y, z = data
        self.x = x
        self.y = y
        self.z = z
    
    def _wii_a(self, data, xx):

        """Callback method that registers the A button"""

        address, f, a = data
        self.a = a and True or False

    def _wii_b(self, data, xx):

        """Callback method that registers the B button"""

        address, f, b = data
        self.b = b and True or False
        
    def update(self):
        
        """This performs all registered callbacks.
        If used in a NodeBox animation, put a call to the upate method
        in your animation's update method."""
        
        osc.getOSC(self.listener)
    
    def stop(self):

        """This needs to be called at the end of each script.
        If used in a NodeBox animation, put a call to the stop method
        inside the stop method, which gets called when the animation is
        stopped."""

        self.listener.close()

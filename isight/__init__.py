# Copyright (c) 2007 Tom De Smedt.
# See LICENSE.txt for details.

import os

def grab(width=320, height=240):

    """ Calls Axel Bauer's command line tool for the iSight
    and returns the path where the image is located.
    http://www.intergalactic.de/hacks.html
    """
    
    path = os.path.dirname(__file__).replace(" ", "\ ")
    img = os.path.join(path, "grab.jpg")
    
    cmd  = os.path.join(path, ".", "isightcapture")
    cmd += " -w " + str(width)
    cmd += " -h " + str(height)
    cmd += " -t jpg " + img
    
    os.system(cmd)
    
    return img.replace("\ ", " ")
    
    
### MATHTEX ##########################################################################################
# Author: Tom De Smedt, Cedric Foellmi.
# Copyright (c) 2008 by Tom De Smedt, Cedric Foellmi.
# See LICENSE.txt for details.

from url import URLAccumulator
from urllib import quote
from cache import Cache

def clear_cache():
    Cache("mathtex").clear()

class mathTeX(URLAccumulator):
    
    """ The mathTeX server returns a GIF or PNG-image for a LaTeX math expression.
    http://www.forkosh.com/mathtex.html
    """
    
    def __init__(self, eq, type="png", dpi=120, color="", wait=10, asynchronous=False):
        
        eq = "\\"+type+" "+eq
        eq = "\dpi{"+str(dpi)+"} " + eq
        if color: 
            eq = "\usepackage{color} \color{"+color+"} " + eq
        
        print eq
        url = "http://www.forkosh.dreamhost.com/mathtex.cgi?"+quote(eq)
        URLAccumulator.__init__(self, url, wait, asynchronous, "mathtex", type="."+type, throttle=1)

    def load(self, data):
        
        # Provide the path to the image stored in cache.
        self.image = self._cache.hash(self.url)

def gif(eq, dpi=120, color=""):
    
    return mathTeX(eq, type="gif", dpi=dpi, color=color).image

def png(eq, dpi=120, color=""):
    
    return mathTeX(eq, type="png", dpi=dpi, color=color).image

def png300(eq, color=""):
    
    return png(eq, color, 300)

#eq = "E = hf = \frac{hc}{\lambda} \,\! "
#image(gif(eq), 10, 10)
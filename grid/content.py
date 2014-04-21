# Copyright (c) 2008 Tom De Smedt.
# See LICENSE.txt for details.

import os
import text
from style import draw_text, draw_image
from types import MethodType, FunctionType

#### CONTENT #########################################################################################
# Grid content, either text, number, image(s) or command.
# This is a "depletion object": 
# each time a cell calls for content, a bit of content is chipped away.
# This way, flowing text or consecutive images can be shared between different cells.

CONTENT_NONE     = "none"
CONTENT_TEXT     = "text"
CONTENT_NUMBER   = "number"
CONTENT_IMAGE    = "image"
CONTENT_FUNCTION = "function"

class content(object):
    
    def __init__(self, _ctx, data):
        
        """ Stores a text or a list of images to spread around a grid.
        If it contains both, uses only the text and not the images.
        """
        
        text._ctx    = _ctx # text module needs the drawing context
        self._ctx    = _ctx
        self.parent  = None # the container grid
        
        # Disambiguate between custom draw() command,
        # list of images, single image, number text string.
        self._type = None
        self._data = None
        if type(data) in (MethodType, FunctionType):
            self._type = CONTENT_FUNCTION
            self._data = data
            self.draw  = data
        elif isinstance(data, (int, float)):
            self._type = CONTENT_NUMBER
            self._data = data
        elif isinstance(data, (list, tuple)):
            self._type = CONTENT_IMAGE
            self._data = list(data)
        elif self.is_image_path(data):
            self._type = CONTENT_IMAGE
            self._data = [data]
        elif data == None:
            self._type = CONTENT_NONE
            self._data = data  
        else:
            self._type = CONTENT_TEXT
            try: data = data.decode("utf-8")
            except:
                pass
            self._data = data
        
        # The remainder is what content has not been drawn.
        if self._type == CONTENT_IMAGE:
            self._remainder = list(self._data)
        else:
            self._remainder = self._data
            
        self.widows  = 1
        self.orphans = 1
        self.forward = True
        self.repeat  = False
        
        # If a grid has child cells, content is distributed to the cells.
        # This occurs when the grid is drawn - or when grid.distribute() is called.
        # If that happens, the child cells get a new content object with a portion
        # of the parent content. This object will have content._distributed = True.
        self._distributed = False

    def _get_remainder(self):
        return self._remainder
    remainder = property(_get_remainder)

    def copy(self, parent=None):
        """ Returns a copy of the content.
        Copies of a custom draw() method all refer to the same function. 
        """
        c = content(self._ctx, self._data)
        c.parent  = parent
        c.widows  = self.widows
        c.orphans = self.orphans
        c.forward = self.forward
        c.repeat  = self.repeat
        return c

    def is_image_path(self, path):
        """ Disambiguate between image path and text string.
        """
        return (
            isinstance(path, str) and \
            path[-4:].lower() in [".gif",".jpg",".png",".tif",".eps",".pdf",".ai",".psd"] and \
            os.path.exists(path)
        )

    def is_text(self)    : return self._type == CONTENT_TEXT
    def is_number(self)  : return self._type == CONTENT_NUMBER
    def is_image(self)   : return self._type == CONTENT_IMAGE
    def is_command(self) : return self._type == CONTENT_FUNCTION
    is_numeric = is_number

    def has_text(self)   : return self.is_text()   and self._remainder != ""
    def has_number(self) : return self.is_number() and self._remainder != None
    def has_image(self)  : return self.is_image()  and len(self._remainder) > 0

    def text(self, width, height):
        """ Yields the next portion of text that fits width and height.
        """
        if self.has_text():
            block1, block2 = text.split(self._remainder, width, height, 
                self.widows, self.orphans, self.forward
            )
            self._remainder = block2
            return block1

    def number(self, width, height):
        """ Yields the number as a string if it fits the given width and height.
        """
        if self.has_number():
            block1, block2 = text.split(str(self._remainder), width, height)
            if block2 == "":
                self._remainder = None
                return block1
            return ""

    def image(self):
        """ Yields the next image.
        """
        if self.has_image():
            img = self._remainder.pop(0)
            if self.repeat:
                self._remainder.append(img)
            return img
                
    def next(self, width, height):
        """ Yields the next portion of whatever content is defined.
        """
        width += 10 # XXX fixes a bug in _ctx.text()
        if self.is_text()    : 
            if self.parent.style and self.parent.styles[self.parent.style].fit:
                return self.remainder
            return self.text(width, height)
        if self.is_number()  : return self.number(width, height)
        if self.is_image()   : return self.image()
        if self.is_command() : return self.draw
    
    def default_draw(self, x, y, width, height, style=None):
        
        """ Fills the given box with text, number or image.
        This method will be called from style.draw().
        This method is here and not in the style module so that 
        a custom drawing function can be added to a content object.
        """
        
        if self.has_text() \
        or self.has_number():    
            if style and style.fit:
                # Take all of the content and scale the fontsize
                # so it fits in the given box.
                if self.is_text(): 
                    txt, self._remainder = self._remainder, ""
                if self.is_number(): 
                    txt, self._remainder = str(self._remainder), None
            else:
                # Take a portion of the content that fits the box.
                width += 10 # XXX fixes a bug in _ctx.text()
                if self.is_text(): 
                    txt = self.text(width, height)
                if self.is_number():
                    txt = self.number(width, height)
            txt = txt.rstrip("\n") # XXX fixes a bug in _ctx.text()
            if style == None:
                draw_text(self._ctx, txt, x, y, width, height)
            else:
                draw_text(
                    self._ctx, 
                    txt, 
                    x, 
                    y, 
                    width, 
                    height, 
                    style.horizontal, 
                    style.fit
                )

        elif self.has_image():
            if style == None:
                draw_image(self._ctx, self.image(), x, y, width, height)   
            else:
                draw_image(
                    self._ctx,
                    self.image(),
                    x,
                    y,
                    width,
                    height,
                    style.horizontal,
                    style.vertical,
                    1.0,
                    style.fit,
                    style.opacity
                )
                
    draw = default_draw

    def _unpack(self, v):
        if isinstance(v, content): return v._data
        return v

    # Comparison.
    def __eq__(self, v)   : return self._data == self._unpack(v)
    def __ne__(self, v)   : return not self.__eq__(v)
    def __lt__(self, v)   : return self._data < self._unpack(v) 
    def __gt__(self, v)   : return self._data > self._unpack(v) 

    # Content representations as a string, number and list.
    def __str__(self)     : 
        try: return self._data.encode("utf-8")
        except:
            return self._data
    def __unicode__(self) : return self._data
    def __iter__(self)    : return self._data.__iter__()
    def __float__(self)   : return float(self._data)
    def __int__(self)     : return int(self._data)
    
    # Mathematical operators.
    def __add__(self, v)  : return self._data + self._unpack(v)
    def __sub__(self, v)  : return self._data - self._unpack(v)
    def __mul__(self, v)  : return self._data * self._unpack(v)
    def __div__(self, v)  : return self._data / self._unpack(v)
    def __abs__(self)     : return abs(self._data)
    # Note: when you do 'grid.content += value', 
    # __add__() will first be called and a new content object assigned to the grid,
    # since 'grid.content = something' is defined as grid._set_content().

    # Sequence operators.
    def __len__(self)         : return len(self._data)
    def __contains__(self, v) : return self._unpack(v) in self._data
    def __getitem__(self, i)  : return self._data[i]
    def __setitem__(self, i, v): 
        self._data[i] = self._unpack(v)

    # Call operator.
    def __call__(self, x, y, width, height, style=None):
        self.draw(x, y, width, height, style)
        
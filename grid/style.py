# Copyright (c) 2008 Tom De Smedt.
# See LICENSE.txt for details.

import warnings
import text

#### ATTRIBUTES WITH ATTRIBUTES ######################################################################

class attributes_with_attributes(list):
    # On a styles object, we can set styles.fontsize = 12, 
    # which will set the fontsize in all the style objects it contains.
    # We can't do styles.padding.left = 2 because the styles object has no padding attribute to get.
    # Therefore, we return a list of all the style objects' "padding" attributes
    # with the possibility to then set the "left" of each item in the list.
    def __setattr__(self, a, v):
        for x in self:
            setattr(x, a, v)

#### STYLES ##########################################################################################

class styles(dict):
    
    def __init__(self, _ctx, grob):
        self._ctx = _ctx
        self.guide = styleguide(grob)
        self.create("default")
    
    def apply(self):
        self.guide.apply()
    
    def create(self, stylename, **kwargs):
        """ Creates a new style which inherits from the default style,
        or any other style which name is supplied to the optional template parameter.
        """
        if stylename == "default":    
            self[stylename] = style(stylename, self._ctx, **kwargs)
            return self[stylename]
        k = kwargs.get("template", "default")
        s = self[stylename] = self[k].copy(stylename)
        for attr in kwargs:
            if s.__dict__.has_key(attr):
                s.__dict__[attr] = kwargs[attr]
        return s
    
    def append(self, style):
        self[style.name] = style
    
    def __getattr__(self, a):
        """ Keys in the dictionaries are accessible as attributes.
        """
        if self.has_key(a): 
            return self[a]
        if a in ("padding", "margin", "background", "strokewidth", "align"):
            return attributes_with_attributes([getattr(style, a) for style in self.values()])
        raise AttributeError, "'styles' object has no attribute '"+a+"'"
        
    def __setattr__(self, a, v):
        """ Setting an attribute is like setting it in all of the contained styles.
        """
        if   a == "_ctx"  : self.__dict__["_ctx"] = v
        elif a == "guide" : self.__dict__["guide"] = v
        elif hasattr(self.values()[0], a):
            for style in self.values(): 
                setattr(style, a, v)
        else:
            raise AttributeError, "'style' object has no attribute '"+a+"'"
            
    def copy(self, grob):
        """ Returns a copy of all styles and a copy of the styleguide.
        """
        s = styles(self._ctx, grob)
        s.guide = self.guide.copy(grob)
        dict.__init__(s, [(v.name, v.copy()) for v in self.values()])
        return s

#### STYLE GUIDE #####################################################################################
# Each graphical object gets the default colors, type and drawing functions.
# The guide defines how and when to apply other styles based on grob properties.
# It contains a set of style name keys linked to x(grob) functions.
# If such a function returns True for a grob, the style is applied to that grob.

class styleguide(dict):
    
    def __init__(self, grob):
        self.grob = grob
        self.order = []
    
    def append(self, stylename, function):
        """ The name of a style and a function that takes a grob.
        It returns True when the style should be applied to the given grob.
        """
        self[stylename] = function
    
    def clear(self):
        self.order = []
        dict.__init__(self)
    
    def apply(self):
        """ Check the rules for each grob and apply the style.
        We expect a grob to have an all() method that yields all grobs to check.
        """
        sorted = self.order + self.keys()
        unique = []; [unique.append(x) for x in sorted if x not in unique]
        for node in self.grob.all():
            for s in unique:
                if self.has_key(s) and self[s](grob): 
                    grob.style = s

    def copy(self, grob):
        """ Returns a copy of the styleguide for the given grob.
        """
        g = styleguide(grob)
        g.order = self.order
        dict.__init__(g, [(k, v) for k, v in self.iteritems()])
        return g

#### SPACING #########################################################################################       
# Left, top, right and bottom spacing in a container.

class spacing(list):
    
    def __init__(self, left=0, top=0, right=0, bottom=0):
        # You can also supply values as one list parameter.
        if isinstance(left, (list, tuple)):
            list.__init__(self, [v for v in left])
        else:
            list.__init__(self, [left, top, right, bottom])

    def copy(self):
        return spacing(self)

    def _get_l(self): return self[0]
    def _get_t(self): return self[1]
    def _get_r(self): return self[2]
    def _get_b(self): return self[3]
    
    def _set_l(self, v): self[0] = v
    def _set_t(self, v): self[1] = v
    def _set_r(self, v): self[2] = v
    def _set_b(self, v): self[3] = v
    
    left   = l = property(_get_l, _set_l)
    top    = t = property(_get_t, _set_t)
    right  = r = property(_get_r, _set_r)
    bottom = b = property(_get_b, _set_b)

#### BACKGROUND ######################################################################################       

class background():
    
    def __init__(self, clr, horizontal="left", vertical="top", scale=1.0, x=0, y=0):
        """ Background color and image attached according to given alignment and offset.
        """
        if isinstance(clr, str):
            self.color    = None
            self.image    = clr
            self.gradient = None
        elif isinstance(clr, tuple):
            self.color    = None
            self.image    = None
            self.gradient = clr                
        else:
            self.color    = clr
            self.image    = None
            self.gradient = None
        self.horizontal = horizontal
        self.vertical   = vertical
        self.scale = scale
        self.x = x
        self.y = y
        self.opacity = 1.0

    def copy(self):
        b = background(None, self.horizontal, self.vertical, self.scale, self.x, self.y)
        if self.color != None:
            b.color = self.color.copy()
        b.image = self.image
        if self.gradient != None:
            g = list(self.gradient)
            g[0], g[1] = g[0].copy(), g[1].copy()
            b.gradient = tuple(g)
        return b

    def _get_align(self):
        return self._align
    def _set_align(self, v):
        if isinstance(v, (tuple, list)):
            h, v = v
        else:
            h, v = v, v
        self.horizontal = h
        self.vertical = v
    align = property(_get_align, _set_align)
        
    def gradientfill(self, clr1, clr2, type="radial", 
                     dx=0, dy=0, spread=1.0, angle=0, alpha=1.0):
        self.color = None
        self.image = None
        self.gradient = clr1, clr2, type, dx, dy, spread, angle, alpha

    def draw(self, x, y, width, height, style=None):
        """ Override this method for custom background.
        """
        pass
    draw = None

#### STYLE ###########################################################################################

class style(object):
    
    def __init__(self, name, _ctx, **kwargs):

        self.name = name
        self._ctx = _ctx
        text._ctx = _ctx # text module needs the drawing context.
        
        # Defaults for colors and typography.
        self.background   = None
        self.fill         = _ctx.color(0)
        self.stroke       = None
        self.strokewidth  = 0
        self.font         = "Verdana"
        self.fontsize     = 9
        self.lineheight   = 1.2
        self.horizontal   = 0
        self.vertical     = 0
        self.roundness    = 0
        self._margin      = spacing(0, 0, 0, 0)
        self._padding     = spacing(0, 0, 0, 0)
        self._align       = ("top", "left")
        self.rotation     = 0
        self.opacity      = 1.0
        self.clipped      = True
        self.fit          = False
        self.delegate     = True
        
        # Each of the attributes is an optional named parameter in __init__().
        for attr in kwargs:
            if self.__dict__.has_key(attr):
                self.__dict__[attr] = kwargs[attr]

    def copy(self, name=None):
        """ Copy all attributes, link all monkey patch methods.
        """
        s = style(self.name, self._ctx)
        for attr in self.__dict__: 
            v = self.__dict__[attr]
            if isinstance(v, (background, spacing, self.fill.__class__)): v = v.copy()
            s.__dict__[attr] = v
        if name != None: 
            s.name = name
        
        return s

    def _get_background(self): return self._background
    def _set_background(self, v):
        if not isinstance(v, background):
            b = background(v)
        self._background = b
    
    background = property(_get_background, _set_background)

    def _get_strokewidth(self): return self._strokewidth
    def _set_strokewidth(self, v): 
        if not isinstance(v, (list, tuple)): 
            v = (v, v, v, v)
        self._strokewidth = spacing(v)
    
    strokewidth = property(_get_strokewidth, _set_strokewidth)

    def _get_margin(self): return self._margin
    def _set_margin(self, v): 
        if not isinstance(v, (list, tuple)): 
            v = (v, v, v, v)
        self._margin = spacing(v)
    
    margin = property(_get_margin, _set_margin)

    def _get_padding(self): return self._padding
    def _set_padding(self, v): 
        if not isinstance(v, (list, tuple)): 
            v = (v, v, v, v)
        self._padding = spacing(v)
    
    padding = property(_get_padding, _set_padding)

    def _get_align(self): return (self.horizontal, self.vertical)
    def _set_align(self, v):
        if isinstance(v, (list, tuple)):
            self.horizontal, self.vertical = v
        else:
            self.horizontal, self.vertical = v, "top"
            
    align = property(_get_align, _set_align)

#--- ALIGNMENT HELPER --------------------------------------------------------------------------------

LEFT    = 0
RIGHT   = 1
CENTER  = 2
JUSTIFY = 3
TOP     = 4
BOTTOM  = 5

def alignment(v):
    if v == "left"    : return LEFT
    if v == "right"   : return RIGHT
    if v == "center"  : return CENTER
    if v == "justify" : return JUSTIFY
    if v == "top"     : return TOP
    if v == "bottom"  : return BOTTOM
    return v 

#--- RECT WITH IMPROVED ROUNDNESS --------------------------------------------------------------------

from nodebox.graphics import BezierPath
def rect(_ctx, x, y, width, height, roundness=0.0, draw=True, **kwargs):
    """ Roundness is either a relative float between 0.0 and 1.0,
    or the absolute radius of the corners. 
    """
    BezierPath.checkKwargs(kwargs)
    p = _ctx.BezierPath(**kwargs)
    r = max(0, roundness)
    if r == 0.0:
        p.rect(x, y, width, height)
    else:
        if r <= 1.0 and isinstance(r, float):
            r = min(r*width/2, r*height/2)
        else:
            r = min(r, width/2, height/2)
        p.moveto(x, y+r)
        a, b, c, d = (x, y), (x+width, y), (x, y+height), (x+width, y+height)
        p._nsBezierPath.appendBezierPathWithArcFromPoint_toPoint_radius_(a, b, r)
        p._nsBezierPath.appendBezierPathWithArcFromPoint_toPoint_radius_(b, d, r)
        p._nsBezierPath.appendBezierPathWithArcFromPoint_toPoint_radius_(d, c, r)
        p._nsBezierPath.appendBezierPathWithArcFromPoint_toPoint_radius_(c, a, r)
        p.closepath()
    p.inheritFromContext(kwargs.keys())
    if draw:
        p.draw()
    return p       

#--- DRAW GROB ---------------------------------------------------------------------------------------

def begin_grob(style, grob, x, y):
    
    # Cells inherit the parent style.
    # This way you can set a style for a collection of peer cells.
    # An exception to this rule is when style.delegate is False,
    # then the style is drawn for the container and not used for the containing cells.
    # This is useful when you have a background that spans different rows and columns
    # (instead of the background being applied to each individual row/column).
    style._ctx.push()
    if (style.delegate and len(grob) > 0):
        style._ctx.translate(x, y)
        return (None, 0, 0)
    
    # Margin is the space around each cell.
    l, t, r, b = style.margin
    x += grob.x + l
    y += grob.y + t
    w, h = grob.width-r-l, grob.height-b-t
    if w <= 0: return (None, 0, 0)
    if h <= 0: return (None, 0, 0)
    
    # Padding is the space around the cell's content.
    l, t, r, b = style.padding
    
    # The cell path is a rounded rectangle.
    style._ctx.translate(x, y)
    p = rect(style._ctx, 0, 0, w, h, roundness=style.roundness, draw=False)
    
    if style.clipped:
        style._ctx.beginclip(p)
    
    draw_background(style, grob, p, 0, 0, w, h)    
    draw_content(style, grob, l, t, w-r-l, h-b-t)
        
    return (p, w, h)

def end_grob(style, grob, path, width, height):
    # End clipping masks and pushed transformations.
    # If defined, draw a border around this grid.
    if not style.delegate or len(grob) == 0:
        if width > 0 and height > 0:
            if style.clipped:
                style._ctx.endclip()
            draw_stroke(style, grob, path, width, height)
    style._ctx.pop()

#--- DRAW BACKGROUND ---------------------------------------------------------------------------------

def draw_background(style, grob, path, x, y, width, height):
    # If a background color is defined, draw a colored rectangle in the back.
    if style.background.color:
        style._ctx.nostroke()
        style._ctx.fill(style.background.color)
        style._ctx.drawpath(path)
    # If a background image is defined, draw it on top of the background color.
    # The image is stretched to fit or aligned at the LEFT, CENTER or RIGHT.
    if style.background.image:
        draw_image(
            style._ctx,
            style.background.image,
            style.background.x,
            style.background.y,
            width,
            height,
            style.background.horizontal,
            style.background.vertical,
            style.background.scale,
            style.fit,
            style.background.opacity
        )
    # If a background gradient is defined, attempt to import the Colors library.
    if style.background.gradient:
        try:
            colors = style._ctx.ximport("colors")
            g = style.background.gradient
            clr1   = g[0]
            clr2   = g[1]
            type   = g[2] if len(g) > 2 else "linear"
            dx     = g[3] if len(g) > 3 else 0
            dy     = g[4] if len(g) > 4 else 0
            spread = g[5] if len(g) > 5 else 1.0
            angle  = g[6] if len(g) > 6 else 0
            alpha  = g[7] if len(g) > 7 else 1.0
            colors.gradientfill(path, clr1, clr2, type, dx, dy, spread, angle, alpha)
        except:
            warnings.warn("the Colors library is needed to draw gradients.", Warning)
    if style.background.draw:
        style._ctx.push()
        style.background.draw(x, y, width, height, style)
        style._ctx.pop()

#--- DRAW CONTENT ------------------------------------------------------------------------------------

def draw_content(style, grob, x, y, width, height):
    # Draw the content in the given color and text properties.
    # Only cells that have no child cells draw content.
    style._ctx.push()
    style._ctx.fill(style.fill)
    style._ctx.font(style.font, style.fontsize)
    style._ctx.lineheight(style.lineheight)
    style._ctx.align(alignment(style.horizontal))
    # Content rotation.
    # If the content is rotated 90, -90 or 180 degrees,
    # we translate and rescale to simulate a "flip".
    style._ctx.transform(0) # corner-mode transformations
    style._ctx.translate(x, y)
    style._ctx.rotate(style.rotation)
    if style.rotation % 360 == 90:
        width, height = height, width
        style._ctx.translate(-width, 0)
    if style.rotation % 360 == 270:
        width, height = height, width
        style._ctx.translate(0, -height)
    if style.rotation % 360 == 180:
        style._ctx.translate(-width, -height)
    # Execute the grid.content.draw() callback.
    if grob.content != None and len(grob) == 0:
        grob.content.draw(0, 0, width, height, style)    
    style._ctx.pop()

#--- DRAW STROKE -------------------------------------------------------------------------------------

def draw_stroke(style, grob, path, width, height):
    # If a stroke is defined, draw a stroked, transparent rectangle on top.
    if style.stroke != None:
        style._ctx.stroke(style.stroke)
        l, t, r, b = style.strokewidth
        if l == t == r == b:
            style._ctx.nofill()
            style._ctx.strokewidth(l)
            style._ctx.drawpath(path.copy())
        else:
            w, h = width, height
            if l > 0:
                style._ctx.strokewidth(l)
                style._ctx.line(0, 0, 0, h)
            if r > 0:
                style._ctx.strokewidth(r)
                style._ctx.line(w, 0, w, h)
            if t > 0:
                style._ctx.strokewidth(t)
                style._ctx.line(0, 0, w, 0)
            if b > 0:
                style._ctx.strokewidth(b)
                style._ctx.line(0, h, w, h)     

#--- DRAW TEXT ---------------------------------------------------------------------------------------
# Used in content.draw()

def draw_text(_ctx, txt, x, y, w, h, horizontal=0, fit=False):
    # Small tweaks to get the position and size of text blocks right.
    if alignment(horizontal) == RIGHT  : x -= 10
    if alignment(horizontal) == CENTER : x -= 5
    if fit:
        _ctx.fontsize(text.fit_fontsize(txt, w, h))
        _ctx.lineheight(text.fit_lineheight(txt, w, h))
    _ctx.text(
        txt, 
        x, 
        y+_ctx.fontsize(), 
        w, 
        h
    )

#--- DRAW IMAGE --------------------------------------------------------------------------------------
# Used in begin_grob() and content.draw()

def draw_image(_ctx, img, x, y, w, h, horizontal=0, vertical=0, scale=1.0, fit=False, alpha=1.0):
    """ Draws the image at the given position.
    Horizontal and vertival (LEFT, RIGHT, CENTER, "bottom") are used to align the image,
    while fit determines if it will stretch to fill the given width and height.
    """
    r = _ctx.rect(x, y, w, h, draw=False)
    _ctx.beginclip(r)
    _ctx.push()
    img_w, img_h = _ctx.imagesize(img)
    if fit:
        d1 = float(w) / img_w
        d2 = float(h) / img_h
        if (img_w * d1 - w) >= -0.00001 and \
           (img_h * d1 - h) >= -0.00001:
            img_w *= d1
            img_h *= d1
        else:
            img_w *= d2
            img_h *= d2    
    if alignment(horizontal) == RIGHT  : x += 1.0 * (w-img_w)
    if alignment(horizontal) == CENTER : x += 0.5 * (w-img_w)
    if alignment(vertical)   == BOTTOM : y += 1.0 * (h-img_h)
    if alignment(vertical)   == CENTER : y += 0.5 * (h-img_h)
    _ctx.translate(x, y)
    _ctx.image(img, 0, 0, width=img_w, alpha=alpha)
    _ctx.pop()
    _ctx.endclip()

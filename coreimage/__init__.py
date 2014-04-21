### CREDITS ##########################################################################################

# Copyright (c) 2007 Tom De Smedt.
# See LICENSE.txt for details.

__author__    = "Tom De Smedt"
__version__   = "1.9.5"
__copyright__ = "Copyright (c) 2007 Tom De Smedt"
__license__   = "GPL"

### NODEBOX CORE IMAGE ###############################################################################

# The Core Image library for NodeBox adds image manipulation to NodeBox.
# It's like having control over Photoshop through simple Python programming commands.
# Core Image is a Mac OS X specific framework available from Mac OS X 1.4 (Tiger).

# The library depends on the Cocoa ObjC AppKit and Foundation modules (bundled with NodeBox),
# the Python math module, the Python NumPy module (bundled with NodeBox) for pixel operations,
# the Python Core Graphics module (installed on the Mac by default) for CMYK conversion,
# the nodebox.graphics module for drawing operations in NodeBox.
# However, all of the classes are loosely connected so it probably isn't that much work
# to make the library work in a different environment.
# Different renderers can also "easily" be implemented, for example in PIL.

# The library is currently in alpha stage and has some known issues and limitations,
# check the bottom of the documentation webpage (http://nodebox.net/code/index.php/Core_Image).
# The main issue: exporting image files leaks memory, which can result in kernel panic.
# I haven't found a solution yet, there's a problem when calling CIContext().drawImage. 
# For now, don't export movies/PDF's/images in batch or use an external screen capture tool.

### CONSTANTS ########################################################################################

# Layer types.
LAYER_FILE            = "file"
LAYER_FILL            = "fill"
LAYER_RADIAL_GRADIENT = "radial"
LAYER_LINEAR_GRADIENT = "linear"
LAYER_LAYERS          = "layers"
LAYER_PATH            = "path"
LAYER_PIXELS          = "pixels"
LAYER_CIIMAGEOBJECT   = "CIImageobject"
LAYER_NSIMAGEDATA     = "NSImageData"

# Layer ordering.
ARRANGE_UP         = "up"
ARRANGE_DOWN       = "down"
ARRANGE_FRONT      = "front"
ARRANGE_BACK       = "back"

# Layer transformation point.
ORIGIN_LEFT        = "left"
ORIGIN_TOP         = "top"
ORIGIN_BOTTOM      = "bottom"
ORIGIN_RIGHT       = "right"
ORIGIN_CENTER      = "center"

# Layer flip modes.
FLIP_HORIZONTAL    = "horizontal"
FLIP_VERTICAL      = "vertical"

# Layer blend modes.
BLEND_NORMAL       = "normal"
BLEND_LIGHTEN      = "lighten"
BLEND_DARKEN       = "darken"
BLEND_MULTIPLY     = "multiply"
BLEND_SCREEN       = "screen"
BLEND_OVERLAY      = "overlay"
BLEND_SOFTLIGHT    = "softlight"
BLEND_HARDLIGHT    = "hardlight"
BLEND_DIFFERENCE   = "difference"
BLEND_HUE          = "hue"
BLEND_COLOR        = "color"

# Export formats.
FILE_GIF           = ".gif"
FILE_PNG           = ".png"
FILE_JPEG          = ".jpg"
FILE_TIFF          = ".tif"

# Rendering order.
RENDER_OPACITY     = "opacity"
RENDER_CROP        = "crop"
RENDER_FILTERS     = "filters"
RENDER_ADJUSTMENTS = "adjustments"
RENDER_TRANSFORMS  = "transforms"
RENDER_MASK        = "mask"

# Controls how much extra space to leave between
# the actual path and its bounding box.
PATH_PADDING = 0

# Core Image constants.
kCIFormatARGB8  = 23
kCIFormatRGBA16 = 27
kCIFormatRGBAf  = 34
QUALITY_LOW     = "low"
QUALITY_HIGH    = "high"

INFINITY = 1e20

### EXCEPTIONS #######################################################################################

class CanvasToNodeBoxError: pass
class CanvasInCanvasRecursionError: pass

### GEOMETRY #########################################################################################

from math import sqrt, pow
from math import sin, cos, atan, pi, radians, degrees

def distance(x0, y0, x1, y1):
    return sqrt(pow(x1-x0, 2) + pow(y1-y0, 2))
    
def angle(x0, y0, x1, y1):
    a = degrees( atan((y1-y0) / (x1-x0+0.00001)) ) + 360
    if x1-x0 < 0: a += 180
    return 360 - a

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

### COLOR ############################################################################################

class Color:
    
    def __init__(self, r, g=None, b=None, a=None):
        """ Stores channel values for a color.
        If one value is given and it is a Color object, copy that.
        If one value is given, create a grayscale color.
        If two values are given, create a grayscale color with alpha.
        If three values are given, create an opaque color.
        """
        try: 
            is_nodebox_color = isinstance(r, _ctx.Color().__class__)
        except: 
            is_nodebox_color = False
        # One parameter, a Color object.
        if isinstance(r, Color) or is_nodebox_color:
            r, g, b, a = r.r, r.g, r.b, r.a
        if isinstance(r, (list, tuple)):
            if   len(r) == 2: r, g = r
            elif len(r) == 3: r, g, b = r
            elif len(r) == 4: r, g, b, a = r
        # No alpha means an opaque color.
        if a == None:
            a = 1.0
        # One parameter, a grayscale value.
        if g == None and b == None:    
            g, b = r, r
        # Two parameters, gray value and alpha.
        if b == None:
            a, g, b = g, r, r
        if isinstance(r, int): r = float(r) / 255
        if isinstance(g, int): g = float(g) / 255
        if isinstance(b, int): b = float(b) / 255
        if isinstance(a, int): a = float(a) / 255
        self.r = max(0.0, min(r, 1.0))
        self.g = max(0.0, min(g, 1.0))
        self.b = max(0.0, min(b, 1.0))
        self.a = max(0.0, min(a, 1.0))
        
    def __repr__(self):
        return "%s(%s, %s, %s, %s)" % (self.__class__.__name__, 
                self.r, self.g, self.b, self.a)

def color(r=None, g=None, b=None, a=None):
    return Color(r, g, b, a)

### TRANSPARENT ######################################################################################
  
class Transparent(Color):
    def __init__(self):
        Color.__init__(self, 0.0, 0.0, 0.0, 0.0)

def transparent():
    return Transparent()

### PATH #############################################################################################

class Path:
    
    def __init__(self, path):
        """ A wrapper for acceptable bezier paths.
        Transforms a given path to an NSBezierPath.
        Acceptable path parameters are currently:
        1) a NodeBox BezierPath which is the handiest format
        2) a list of points forming a polygon
        3) an NSBezierPath.
        """
        self.path = None
        # Path from BezierPath.
        try:
            b = isinstance(path, _ctx.BezierPath().__class__)
            if b: self.path = path._nsBezierPath
        except:
            pass
        # Path from list of points.
        if isinstance(path, list):
            p = NSBezierPath.bezierPath()
            first = True
            for i in range(len(path)/2):
                x = path[i*2]
                y = path[i*2+1]
                if first == True:
                    p.moveToPoint_((x, y))
                    first = False
                else:
                    p.lineToPoint_((x, y))
            self.path = p
        # Path from NSBezierPath.
        if isinstance(path, NSBezierPath):
            self.path = path
    
    def is_path(self):
        return (self.path != None)

### CANVAS ###########################################################################################

from os.path import splitext

class Canvas:
    
    def __init__(self, w, h, renderer):
        self.renderer = renderer
        self.layers = Layers()
        self._parent = None
        self.w = w
        self.h = h
    
    def copy(self):
        canvas = Canvas(self.w, self.h, self.renderer)
        canvas._parent = self._parent
        for layer in self.layers:
            canvas.layers.append(layer.copy())
        return canvas
    
    def layer(self, *args, **kwargs):
        
        """ Adds a new layer to the canvas.
        
        A new layer can be created from:
         1) layer(str)
         2) layer(clr1, clr2, type="linear", spread=0.0)
         3) layer(clr)
         4) layer(layer)
         5) layer(canvas)
         6) layer(path, background=None, fill=None, stroke=None, strokewidth=None)
         7) layer([clr1, clr2, clr3, ...], w, h)
         8) layer(layer.render())
         9) layer(canvas.render())
        10) layer(NSImage)
        11) layer(open(img).read())
        12) layer(movieframe)
        
        By default, layers are placed at the center of the canvas.
        
        When a width or height is given for an image file,
        the layer will store the original image's width and height and adjust its scaling.
        
        Layers have a default width and height equal to the canvas,
        except when given or the source image file has other dimensions.
                
        Always use Canvas.layer() to create new layers as this method
        initializes all the layer attributes in the correct way.
        
        """
        
        x = y = w = h = None
        if kwargs.has_key("x"): x = kwargs["x"]
        if kwargs.has_key("y"): y = kwargs["y"]
        if kwargs.has_key("w"): w = kwargs["w"]
        if kwargs.has_key("h"): h = kwargs["h"]
        
        name = ""
        type = ""
        if kwargs.has_key("name"): name = kwargs["name"]
        if kwargs.has_key("type"): type = kwargs["type"]

        # Creates a new Layer object in the Canvas.
        def _add_layer(data, type, x=None, y=None, w=None, h=None, s=Point(1.0,1.0)):
            if x == None: x = self.w/2
            if y == None: y = self.h/2
            if w == None: w = self.w
            if h == None: h = self.h
            layer = Layer(self, type, data, x, y, w, h, name)
            layer._scale = s
            self.layers.append(layer)
            return layer    

        # File: layer(str)
        # An image file is a pathname for which the renderer can calculate a size.
        # ------------------------------------------------------------------------
        try:
            w0, h0 = self.renderer.imagesize(args[0])
            type = LAYER_FILE
            s = Point(1.0, 1.0)
            if w != None: s.x = float(w) / w0
            if h != None: s.y = float(h) / h0
            w, h = w0, h0           
            return _add_layer(args[0], type, x, y, w, h, s)
        except: 
            pass    

        # Gradient: layer(clr1, clr2, type="linear", spread=0.0)
        # A gradient are two color objects and an optional spread parameter.
        # ------------------------------------------------------------------------
        try:
            r, g, b, a = args[0].r, args[0].g, args[0].b, args[0].a
            r, g, b, a = args[1].r, args[1].g, args[1].b, args[1].a
            if type == "radial":
                type = LAYER_RADIAL_GRADIENT
                if not kwargs.has_key("spread") \
                or kwargs["spread"] == None: 
                    kwargs["spread"] = 0.0        
                return _add_layer((args[0], args[1], float(kwargs["spread"])), type, x, y, w, h)
            else:
                type = LAYER_LINEAR_GRADIENT
                return _add_layer((args[0], args[1]), type, x, y, w, h)
        except: 
            pass

        # Fill color: layer(clr)
        # A fill is a single color object with r, g, b and a properties.
        # ------------------------------------------------------------------------
        try:
            r, g, b, a = args[0].r, args[0].g, args[0].b, args[0].a
            type = LAYER_FILL
            return _add_layer(args[0], type, x, y, w, h)
        except: 
            pass   

        # Layer: layer(layer)
        # A Layer copied from another canvas.
        # ------------------------------------------------------------------------
        try:
            c, b, f = args[0].canvas, args[0].blendmode, args[0].filters
            layer = args[0].copy()
            layer.canvas = self
            self.layers.append(layer)
            return layer
        except: 
            pass 
            
        # Canvas: layer(canvas)
        # A Canvas is identified by w, h and layers properties.
        # ------------------------------------------------------------------------
        try:
            w0, h0, n = args[0].w, args[0].h, len(args[0].layers)
            if args[0] == self: raise CanvasInCanvasRecursionError
            type = LAYER_LAYERS
            if w == None: w = args[0].w
            if h == None: h = args[0].h
            return _add_layer(args[0], type, x, y, w, h)
        except: 
            pass    

        # Path: 
        # layer(path, background=None, fill=None, stroke=None, strokewidth=None)
        # path can be: BezierPath, NSBezierPath, [x1, y1, x2, y2, ...]
        # A valid path can be used to initialize a coreimage.Path object.
        # ------------------------------------------------------------------------
        try:
            path = Path(args[0]).path
            (dx,dy), (w0,h0) = path.bounds()
            type = LAYER_PATH
            if x == None: x = self.w/2
            if y == None: y = self.h/2
            #x += dx
            #y += dy
            
            default_fill = Color(0.0)
            if self._parent != None and self._parent.mask == self: 
                default_fill = Color(1.0)
            
            colors = [
                kwargs.get("background", Transparent()),
                kwargs.get("fill", default_fill),
                kwargs.get("stroke", Transparent())
            ]
            for i in range(len(colors)):
                clr = colors[i]
                if isinstance(clr, int): clr = float(clr)
                if isinstance(clr, (list, tuple)):
                    clr = [float(v) for v in clr]
                colors[i] = Color(clr)
            background, fill, stroke = colors

            strokewidth = kwargs.get("strokewidth", 1.0)
            if stroke.a == 0: 
                strokewidth = 0.0
            strokewidth = max(0, strokewidth)
            
            if w == None: w = w0 + strokewidth + PATH_PADDING*2
            if h == None: h = h0 + strokewidth + PATH_PADDING*2
            return _add_layer((path, background, fill, stroke, strokewidth), type, x, y, w, h)
          
        except:
            pass  
        
        # Pixels: 
        # layer([clr1, clr2, clr3, ...], w, h)
        # Pixels are passed as a list of color objects and w and h parameters.
        # ------------------------------------------------------------------------
        try:
            r, g, b, a = args[0][0].r, args[0][0].g, args[0][0].b, args[0][0].a
            if len(args) >= 2: w = args[1]
            if len(args) == 3: h = args[2]
            w *= 1
            h *= 1
            type = LAYER_PIXELS
            return _add_layer((args[0], w, h), type, x, y, w, h)
        except: 
            pass
        
        # Core Image CIImage object: 
        # layer(layer.render())
        # layer(canvas.render())
        # A CIImage object has an extent() method.
        # ----------------------------------------------------------------------
        try:
            (x0, y0), (w0, h0) = args[0].extent()
            type = LAYER_CIIMAGEOBJECT
            return _add_layer(args[0], type, x, y, w0, h0)
        except: 
            pass
        
        # TIFF data extracted from Cocoa NSImage object, or byte data:
        # layer(NSImage)
        # layer(open(img).read())
        # layer(movieframe)
        # An image byte string can be passed to _ctx.Image() to create an NSImage.
        # An NSImage or a movieframe has size() and TIFFRepresentation methods.
        # ------------------------------------------------------------------------
        try:
            try:
                img = _ctx.Image(None, data=args[0])
                img = img._nsImage
            except:
                img = args[0]
            w0, h0 = img.size()
            img = img.TIFFRepresentation()
            type = LAYER_NSIMAGEDATA
            s = Point(1.0,1.0)
            if w != None: s.x = float(w) / w0
            if h != None: s.y = float(h) / h0
            w, h = w0, h0           
            return _add_layer(img, type, x, y, w, h, s)
        except: 
            pass          
    
    append = layer
        
    def layer_fill(self, clr=None, x=None, y=None, w=None, h=None, name=""):
        if clr == None:
            clr = Color(0.0)
            if self._parent != None and self._parent.mask == self:
                clr = Color(1.0)
        return self.layer(clr, x=x, y=y, w=w, h=h, name=name)    
    
    def layer_gradient(self, clr1=None, clr2=None, type="linear", spread=None, x=None, y=None, w=None, h=None, name=""):
        if clr1 == None: clr1 = Color(1.0)
        if clr2 == None: clr2 = Color(0.0)
        return self.layer(clr1, clr2, type=type, spread=spread, x=x, y=y, w=w, h=h, name=name)
        
    def layer_linear_gradient(self, clr1=None, clr2=None, x=None, y=None, w=None, h=None, name=""):
        return self.layer_gradient(clr1, clr2, x=x, y=y, w=w, h=h, name=name)

    def layer_radial_gradient(self, clr1=None, clr2=None, spread=0.0, x=None, y=None, w=None, h=None, name=""):
        return self.layer_gradient(clr1, clr2, type="radial", spread=spread, x=x, y=y, w=w, h=h, name=name)
    
    def layer_group(self, canvas, x=None, y=None, w=None, h=None, name=""):
        return self.layer(canvas, x=x, y=y, w=w, h=h)
    
    def layer_path(self, path, fill=None, background=None, stroke=None, strokewidth=None, x=None, y=None, w=None, h=None, name=""):
        return self.layer(path, fill=fill, background=background, stroke=stroke, strokewidth=strokewidth, x=x, y=y, w=w, h=h, name=name)

    def layer_pixels(self, colors, w, h, x=None, y=None, name=""):
        return self.layer(colors, w, h, x=x, y=y, name=name)
    
    def layer_bytes(self, data, x=None, y=None, w=None, h=None, name=""):
        return self.layer(data, x=x, y=y, w=w, h=h, name=name)
        
    fill     = add_fill     = layer_fill
    gradient = add_gradient = layer_gradient
    linear   = add_linear   = layer_linear_gradient
    radial   = add_radial   = layer_radial_gradient
    group    = add_group    = layer_group
    path     = add_path     = layer_path
    bytes    = add_bytes    = layer_bytes
    pixels   = add_pixels   = layer_pixels
            
    def find(self, index):
        """ Returns the layer with the given name or index.
        Browses the canvas recursively:
        if the index is a string, searches layer masks
        and composite layers from the given name as well.
        """
        return self.layers[index]
    
    def __getitem__(self, index): return self.find(index)
    def __getslice__(self, i, j): return self.layers.__getslice__(i, j)
    def __getattr__(self, index): return self.layers.__getattr__(index, cls="Canvas")
    def __iter__(self): return self.layers.__iter__()
    def __len__(self): return len(self.layers)
    
    def _render_shadows(self, layers=[]):
        """ A software layer dropshadow renderer.
        Each layer in the canvas has a Layer.dropshadow() method.
        If the canvas' renderer has no (faster) support for a layer's dropshadow,
        creates a copy of the layer, and translates/blackens/blurs it using
        the standard layer properties and methods, and then places the shadow underneath the layer.
        """
        l = Layers()
        if len(layers) == 0: 
            layers = self.layers
        for layer in layers:
            if layer.has_shadow:
                dx, dy, alpha, blur = layer._shadow
                shadow = layer.copy()
                shadow.adjust(-1, 0, 0)
                shadow.x += dx
                shadow.y += dy
                shadow.opacity *= alpha
                shadow.blur += blur
                shadow.blendmode = "multiply"
                shadow._shadow = None
                l.append(shadow)    
            l.append(layer)
        return l

    def render(self, layers=[], fast=True):
        """ Returned a rendered version of the canvas.
        Flattens the canvas, rendering all the transformed layers.
        You can feed the returned object back into a Canvas.layer().
        """
        if not self.renderer.can_render_shadows:
            layers = self._render_shadows(layers)
        return self.renderer.merge(self, layers, fast)
            
    flatten = render
    
    def draw(self, x=0, y=0, layers=[], fast=False, helper=False):
        """ Draws the flattened canvas to NodeBox.
        Draws the canvas at the given coordinates.
        Throws a CanvasToNodeBox error when unable to draw in NodeBox.
        """
        if not self.renderer.can_render_shadows:
            layers = self._render_shadows(layers)
        self.renderer.draw(self, x, y, layers, fast, helper)
        
    def export(self, name, type=FILE_PNG, compression=None, cmyk=False, layers=[]):
        """ Exports the flattened canvas to .jpg, .gif, .png or .tif.
        """
        if name.endswith(".jpg"): name = name[:-4]; type = FILE_JPEG
        if name.endswith(".gif"): name = name[:-4]; type = FILE_GIF
        if name.endswith(".png"): name = name[:-4]; type = FILE_PNG
        if name.endswith(".tif"): name = name[:-4]; type = FILE_TIFF
        if not self.renderer.can_render_shadows:
            layers = self._render_shadows(self.layers)  
        self.renderer.export(self, name+type, type, compression, cmyk, layers)

    def export_gif(self, name): 
        self.renderer.export(self, splitext(name)[0]+".gif", FILE_GIF)
    def export_png(self, name): 
        self.renderer.export(self, splitext(name)[0]+".png", FILE_PNG)
    def export_jpg(self, name, quality=1.0): 
        self.renderer.export(self, splitext(name)[0]+".jpg", FILE_JPEG, quality)
    def export_tif(self, name, lzw=False, cmyk=False): 
        self.renderer.export(self, splitext(name)[0]+".tif", FILE_TIFF, lzw, cmyk)

def canvas(w=None, h=None, renderer=None, quality=None):
    if not w: w = _ctx.WIDTH
    if not h: h = _ctx.HEIGHT
    if not renderer: renderer = CoreImageRenderer(quality)
    if not isinstance(w, (int, float)):
        try:
            w0, h0 = renderer.imagesize(w)
            canvas = Canvas(w0, h0, renderer)
            layer = canvas.layer(w)
            return canvas
        except:
            pass
    else:
        return Canvas(w, h, renderer)

### LAYERS ###########################################################################################
        
class Layers(list):

    def __getitem__(self, index):
        """ Extends the canvas.layers[] list so it indexes layers names.
        When the index is an integer, returns the layer at that index.
        When the index is a string, returns the first layer with that name.
        When a layer is a canvas, or when a layer's alpha mask is a canvas, searches recursively.
        """        
        # Layer by name, recursive.
        if isinstance(index, str):
            for layer in self:
                if layer.name == index: 
                    return layer
                if isinstance(layer.data, Canvas):
                    try: return layer.data.layers[index]
                    except:
                        pass
                if isinstance(layer.mask, Canvas):
                    try: return layer.data.layers[index]
                    except:
                        pass
            raise KeyError, index
        # Layer by index number.
        if isinstance(index, int):
            return list.__getitem__(self, index)
        raise IndexError, "list index out of range"
            
    def __getattr__(self, name, cls="Layers"):
        """ You can also do: canvas.layers.layer_name (without recursion).
        """
        for layer in self:
            if layer.name == name:
                return layer
        # This method is also called from the Canvas object,
        # In that case, the cls parameter will be "Canvas".
        raise AttributeError, cls+" instance has no attribute '"+name+"'"

### LAYER ############################################################################################

class Layer(object):
    
    def __init__(self, canvas, type, data, x, y, w, h, name=""):
        
        self.canvas = canvas
        self.type = type
        self.data = data
        self.name = name
        self.hidden = False
        
        # A layer can be a Canvas.
        self.layers = None
        if self.type == LAYER_LAYERS:
            self.layers = self.data.layers
            
        # Transformations.
        self.x  = x
        self.y  = y
        self._w = w
        self._h = h
        self._crop    = None
        self._origin  = Point(0.5, 0.5)
        self._flip    = (False, False)    
        self._distort = [Point(0.0, 0.0) for i in range(4)]
        self._scale   = Point(1.0, 1.0)
        self.rotation = 0
        
        # Compositing.
        self._opacity  = 1.0
        self.blendmode = BLEND_NORMAL
        
        # A mask is a grayscale canvas of layers owned by this layer,
        # and of the same width and height.
        # An alpha mask hides parts of the masked layer
        # where the mask is darker.
        self.mask = Canvas(self._w, self._h, self.canvas.renderer)
        self.mask._parent = self
        
        # Adjustments.
        self._brightness = 0.0
        self._contrast   = 1.0
        self._saturation = 1.0
        self.inverted    = False
        
        # Shadow.
        self._shadow = None
        
        # Filters.
        self.blur      = 0.0
        self.sharpness = 0.0
        self.filters   = []
        self._filters_first = True
    
    def _is_file(self)            : return (self.type == LAYER_FILE)
    def _is_fill(self)            : return (self.type == LAYER_FILL)    
    def _is_gradient(self)        : return (self.type == LAYER_LINEAR_GRADIENT or
                                            self.type == LAYER_RADIAL_GRADIENT)    
    def _is_linear_gradient(self) : return (self.type == LAYER_RADIAL_GRADIENT)
    def _is_radial_gradient(self) : return (self.type == LAYER_LINEAR_GRADIENT)    
    def _is_path(self)            : return (self.type == LAYER_PATH)
    def _is_pixels(self)          : return (self.type == LAYER_PIXELS)
    def _has_layers(self)         : return (self.type == LAYER_LAYERS)
    def _has_shadow(self)         : return (self._shadow != None)
    def _is_mask(self)            : return (self.canvas._parent != None and 
                                            self.canvas._parent.mask == self.canvas)
    
    is_file            = property(_is_file)
    is_fill            = property(_is_fill)
    is_gradient        = property(_is_gradient)
    is_linear_gradient = property(_is_linear_gradient)
    is_radial_gradient = property(_is_radial_gradient)
    is_linear          = property(_is_linear_gradient)
    is_radial          = property(_is_radial_gradient)
    is_path            = property(_is_path)
    is_pixels          = property(_is_pixels)
    is_group           = property(_has_layers)
    is_canvas          = property(_has_layers)
    has_layers         = property(_has_layers)
    has_shadow         = property(_has_shadow)
    is_mask            = property(_is_mask)
    
    def _index(self):
        """ Returns this layer's index in the canvas.layers[].
        Searches the position of this layer in the canvas' layers, return None when not found.
        """
        if self.canvas == None:
            return None
        return self.canvas.layers.index(self)
            
    index = property(_index)
    
    def arrange(self, where):
        """ Moves the layer either forwards or backwards.
        """
        i = self._index()
        j = None
        if where == ARRANGE_UP    : j = i+1
        if where == ARRANGE_DOWN  : j = i-1
        if where == ARRANGE_FRONT : j = len(self.canvas.layers)
        if where == ARRANGE_BACK  : j = 0
        if j != None:
            del self.canvas.layers[i]
            j = max(0, min(j, len(self.canvas.layers)))
            self.canvas.layers.insert(j, self)
            return j
           
    def arrange_up(self)    : return self.arrange(ARRANGE_UP)
    def arrange_down(self)  : return self.arrange(ARRANGE_DOWN)
    def arrange_front(self) : return self.arrange(ARRANGE_FRONT)
    def arrange_back(self)  : return self.arrange(ARRANGE_BACK)
    
    up, down = arrange_up, arrange_down
    to_front, to_back = arrange_front, arrange_back

    def hide(self):
        """ Hides the layer from the output.
        This is different than a completely transparent layer,
        which is rendered and might have sublayers that will also be rendered.
        A hidden layer is never rendered.
        """
        self.hidden = True

    def copy(self):
        
        """ Creates a copy of the layer.
        Creates and returns deep copy of the layer.
        This means for example that the layers in the mask are recursively copied, 
        that new copies are made of colors in the gradient.
        """
        
        # Determine the type of layer and copy image data.
        if self.type == LAYER_FILE:
            data = self.data
        if self.type == LAYER_FILL:
            data = Color(self.data)
        if self.type == LAYER_LINEAR_GRADIENT:
            data = (Color(self.data[0]), Color(self.data[1]))
        if self.type == LAYER_RADIAL_GRADIENT:
            data = (Color(self.data[0]), Color(self.data[1]), self.data[2])
        if self.type == LAYER_LAYERS:
            data = self.data.copy()
        if self.type == LAYER_PATH:
            data = (self.data[0].copy(), Color(self.data[1]), Color(self.data[2]), Color(self.data[3]), self.data[4])
        if self.type == LAYER_PIXELS:
            data = self.data
        if self.type == LAYER_CIIMAGEOBJECT:
            data = self.data
        if self.type == LAYER_NSIMAGEDATA:
            data = self.data
        layer = Layer(self.canvas, self.type, data, self.x, self.y, self._w, self._h)
        
        # Transformations.
        layer._origin = Point(self._origin.x, self._origin.y)
        layer._flip = self._flip
        layer._distort = [Point(self._distort[i].x, self._distort[i].y) for i in range(4)]
        layer._scale = Point(self._scale.x, self._scale.y)
        layer.rotation = self.rotation
        
        # Compositing.
        layer._opacity = self._opacity
        layer.blendmode = self.blendmode
        
        # Alpha mask.
        layer.mask = self.mask.copy()
        layer.mask._parent = layer
        
        # Adjustments.
        layer._brightness = self._brightness
        layer._contrast = self._contrast
        layer._saturation = self._saturation
        layer.inverted = self.inverted
        
        # Shadow.
        layer._shadow = self._shadow
        
        # Filters.
        layer.blur = self.blur
        layer.sharpness = self.sharpness
        layer.filters = [(filter, params) for filter, params in self.filters]
        return layer

    def duplicate(self):
        """ Adds a copy of the layer on top of this one.
        Creates a copy of this layer,
        appends it to the canvas right above this layer,
        and returns the index of the new layer.
        """
        i = self._index()
        layer = self.copy()
        self.canvas.layers.insert(i+1, layer)
        return layer

    def origin(self, x=None, y=None):
        """ Sets the transformation origin point.
        The origin point is the layer's anchor/pivot/orbit:
        it is placed at x and y and is the point
        around which the layer rotates,
        and from which the layer scales and flips.
        """
        def f(s):
            if s == ORIGIN_LEFT   : return 0.0
            if s == ORIGIN_TOP    : return 0.0
            if s == ORIGIN_RIGHT  : return 1.0
            if s == ORIGIN_BOTTOM : return 1.0
            if s == ORIGIN_CENTER : return 0.5
            return s    
        x = f(x)
        y = f(y)
        if y == None: y = x
        if isinstance(x, int): x = float(x) / self._w
        if isinstance(y, int): y = float(y) / self._h
        if isinstance(x, float): self._origin.x = x
        if isinstance(y, float): self._origin.y = y
        return (self._origin.x, self._origin.y)
    
    def origin_top_left(self)      : return self.origin(ORIGIN_LEFT   , ORIGIN_TOP)
    def origin_top_right(self)     : return self.origin(ORIGIN_RIGHT  , ORIGIN_TOP)
    def origin_top_center(self)    : return self.origin(ORIGIN_CENTER , ORIGIN_TOP)
    def origin_bottom_left(self)   : return self.origin(ORIGIN_LEFT   , ORIGIN_BOTTOM)
    def origin_bottom_right(self)  : return self.origin(ORIGIN_RIGHT  , ORIGIN_BOTTOM)
    def origin_bottom_center(self) : return self.origin(ORIGIN_CENTER , ORIGIN_BOTTOM)    
    def origin_left_center(self)   : return self.origin(ORIGIN_LEFT   , ORIGIN_CENTER)
    def origin_right_center(self)  : return self.origin(ORIGIN_RIGHT  , ORIGIN_CENTER)
    def origin_center(self)        : return self.origin(ORIGIN_CENTER , ORIGIN_CENTER)
    
    def bounds(self):
    
        """ Returns the left, top, right, bottom in pixels.
        
        Calculates the layer's bounding box based on its original size and position 
        modified by its scaling, rotation and origin point.
        Gets the coordinates of the corner points to calculate maximum extent.
        
        This method is also handy to check if the renderer
        is handling layer transformations correctly.
        
        When the canvas is scaled, we need to multiply left and right 
        by the canvas horizontal scaling,
        and top and bottom by the canvas vertical scaling to have the
        correct bounds for display purposes (but not so for editing).
        
        """

        if isinstance(self.canvas._parent, Layer):
            return self.canvas._parent.bounds()
            
        x, y, w, h = self.x, self.y, self._w, self._h
        
        # Crop.
        if self._crop != None:
            w = min(w, self._crop[2])
            h = min(h, self._crop[3])
            
        # Scale.
        w = w * self._scale.x
        h = h * self._scale.y
        
        # Origin.
        ox = x + self._origin.x * w
        oy = y + self._origin.y * h 
         
        # Rotate and distort.
        l = t = float( INFINITY)
        r = b = float(-INFINITY) 
        corners = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
        for i in range(len(corners)):
            dx, dy = corners[i]
            dx += self._distort[i].x * w
            dy += self._distort[i].y * h
            a = self.rotation - angle(ox, oy, dx, dy)
            d = distance(ox, oy, dx, dy)
            dx = x + d * cos(radians(a))
            dy = y + d * sin(radians(a))
            l = min(l, dx)
            r = max(r, dx)
            t = min(t, dy)
            b = max(b, dy)    
            
        return (l, t, r, b)
    
    def size(self):
        """ Returns the layer's size.
        Returns the width and height of the layer after it has been rotated and scaled
        (whereas the base width and height properties contain the size of the layer's data).    
        """
        l, t, r, b = self.bounds()
        return (r-l, b-t)
        
    def _get_w(self): return self.size()[0]
    def _get_h(self): return self.size()[1]
    w = width  = property(_get_w)
    h = height = property(_get_h)
    
    def center(self):
        """ Puts the origin point of the layer at the center of the canvas.
        """
        self.x = self.canvas.w/2
        self.y = self.canvas.h/2
    
    def translate(self, x, y):
        """ Places the layer at the given position.
        The width and height can be supplied as coordinates relative to the canvas size 
        (between 0.0 and 1.0), or as absolute coordinates in pixels.
        """
        if isinstance(x, float): x = x * self.canvas.w
        if isinstance(y, float): y = y * self.canvas.h        
        self.x = x
        self.y = y
    
    def scale(self, w=None, h=None):
        """ Scales the layer horizontally and vertically.
        The width and height can be supplied as relative coordinates (between 0.0 and 1.0), 
        or as absolute coordinates in pixels. 
        If only parameter is supplied, scales the layer proportionally.
        """
        if w != None and h == None: 
            if isinstance(w, float): h = w
            else: h = int( float(w) / self._w * self._h )
        if h != None and w == None: 
            if isinstance(h, float): w = h
            else: w = int( float(h) * self._w / self._h )
        if isinstance(w, float):
            self._scale.x = w
        if isinstance(h, float):
            self._scale.y = h
        if isinstance(w, int):
            self._scale.x = float(w) / self._w
        if isinstance(h, int):
            self._scale.y = float(h) / self._h
        return (self._scale.x, self._scale.y)
    
    def rotate(self, degrees):
        """ Sets the layer's angle to the given degrees.
        """
        self.rotation = degrees
        
    def flip(self, horizontal=False, vertical=False):
        """ Flips the layer horizontally or vertically.
        """
        if horizontal == True or horizontal in ("h", "horizontal"):
            self.flip_horizontal()
        if vertical == True or horizontal in ("v", "vertical"):
            self.flip_vertical()
        return self._flip
    
    def flip_horizontal(self):
        fx, fy = self._flip
        self._flip = (not fx, fy)
    
    def flip_vertical(self):
        fx, fy = self._flip
        self._flip = (fx, not fy)
        
    def distort(self, dx0=0.0, dy0=0.0, dx1=0.0, dy1=0.0, dx2=0.0, dy2=0.0, dx3=0.0, dy3=0.0):
        """ Distorts the layer by moving its corner points.
        The given coordinates can be either relative to the corner positions 
        (between 0.0 and 1.0), or absolute in pixels.
        """
        self._distort = [
            Point(dx0, dy0),
            Point(dx1, dy1),
            Point(dx2, dy2),
            Point(dx3, dy3)
        ]
        for pt in self._distort:
            if isinstance(pt.x, int):
                pt.x = float(pt.x) / self._w
            if isinstance(pt.y, int):
                pt.y = float(pt.y) / self._h
    
    def crop(self, x, y, w, h):
        """ Crops the layer to the given box.
        """
        if isinstance(x, float): x *= self._w
        if isinstance(y, float): y *= self._h
        if isinstance(w, float): w *= self._w
        if isinstance(h, float): h *= self._h
        if w < 0: w = self._w + w - x
        if h < 0: h = self._h + h - y
        self._crop = (x, y, w, h)
    
    def blend(self, opacity=None, mode=None):
        """ Applies transparency and compositing to the layer.
        Opacity ranges between 0.0 and 1.0, or 0 and 100.
        Standard blending modes (i.e. how this layer mixes with layers below) 
        are screen, multiply, overlay, hue and color; it is preferred
        the renderer knows how to handle lighten/darken, softlight/hardlight as well.
        """
        if isinstance(opacity, int): 
            self._opacity = max(0.0, min(opacity * 0.01, 1.0))
        if isinstance(opacity, float):
            self._opacity = max(0.0, min(opacity, 1.0))
        if isinstance(opacity, str):
            self.blendmode = opacity
        if mode != None:
            self.blendmode = mode
        return (self._opacity, self.blendmode)

    def blend_normal(self, opacity=None)     : self.blend(opacity, BLEND_NORMAL)
    def blend_lighten(self, opacity=None)    : self.blend(opacity, BLEND_LIGHTEN)
    def blend_darken(self, opacity=None)     : self.blend(opacity, BLEND_DARKEN)
    def blend_screen(self, opacity=None)     : self.blend(opacity, BLEND_SCREEN)
    def blend_multiply(self, opacity=None)   : self.blend(opacity, BLEND_MULTIPLY)
    def blend_overlay(self, opacity=None)    : self.blend(opacity, BLEND_OVERLAY)
    def blend_softlight(self, opacity=None)  : self.blend(opacity, BLEND_SOFTLIGHT)
    def blend_hardlight(self, opacity=None)  : self.blend(opacity, BLEND_HARDLIGHT)
    def blend_difference(self, opacity=None) : self.blend(opacity, BLEND_DIFFERENCE)
    def blend_hue(self, opacity=None)        : self.blend(opacity, BLEND_HUE)
    def blend_color(self, opacity=None)      : self.blend(opacity, BLEND_COLOR)
    
    def _get_opacity(self): return self._opacity
    def _set_opacity(self, value): self.blend(value)
    opacity = property(
        _get_opacity, 
        _set_opacity
    )
    
    lighten    = blend_lighten
    darken     = blend_darken
    screen     = blend_screen
    multiply   = blend_multiply
    overlay    = blend_overlay
    softlight  = blend_softlight
    hardlight  = blend_hardlight
    difference = blend_difference
    hue        = blend_hue
    color      = blend_color
    
    def adjust(self, brightness=None, contrast=None, saturation=None, invert=False):
        """ Applies color adjustments to the layer.
        Standard adjustments are brightness, contrast, saturation and invert.
        Brightness ranges between -1.0 and 1.0
        Contrast ranges between 0.25 and 4.0 (default is 1.0)
        Saturation ranges between 0.0 and 2.0 (default is 1.0)
        """
        if brightness != None:
            self.adjust_brightness(brightness)
        if contrast != None:
            self.adjust_contrast(contrast)
        if saturation != None:
            self.adjust_saturation(saturation)
        if invert != False:
            self.invert()
            
    def _get_brightness(self)            : return self._brightness
    def _get_contrast(self)              : return self._contrast
    def _get_saturation(self)            : return self._saturation
    
    def _set_brightness(self, value=0.0) : self._brightness = max(-1.0, min(value, 1.0))
    def _set_contrast(self, value=1.0)   : self._contrast   = max(0.25, min(value, 4.0))
    def _set_saturation(self, value=1.0) : self._saturation = max(0.00, min(value, 2.0))
    
    brightness = property(_get_brightness, _set_brightness)
    contrast   = property(_get_contrast, _set_contrast)
    saturation = property(_get_saturation, _set_saturation)

    adjust_brightness = _set_brightness
    adjust_contrast   = _set_contrast
    adjust_saturation = _set_saturation

    def desaturate(self):
        self._saturation = 0.0
        
    def invert(self):
        self.inverted = not self.inverted
    
    def dropshadow(self, dx=10, dy=10, alpha=0.75, blur=8):
        self._shadow = (dx, dy, alpha, blur)
        
    shadow = dropshadow
    
    def filter(self, name, **kwargs):
        
        """ Applies an effect filter to the layer.
        
        Standard filters are blur and sharpen.
        Blur ranges between 0.0 and 100.0
        Sharpen ranges between 0.0 and 100.0
        Ideally the canvas renderer uses Gaussian Blur and
        Unsharp Mask respectively to render the effects.
        
        Various other filters are renderer-dependent.
        You can use them by supplying a name parameter
        and other parameters specific to the effect.
        For example:
        canvas.layers[i].filter(name=canvas.renderer.FILTER_KALEIDOSCOPE, count=10, dx=-100)
    
        """

        if name == "blur":
            self.blur = kwargs["amount"]
            self.blur = max(0.0, min(self.blur, 100.0))
    
        elif name == "sharpen":
            self.sharpness = kwargs["amount"]
            self.sharpness = max(0.0, min(self.sharpness, 100.0))
            
        elif name != "":
            filter = name
            try: filter = self.canvas.renderer.aliases[filter]
            except: 
                pass
            params = {}
            for param in self.canvas.renderer.filters[filter]:
                if param in kwargs:
                    params[param] = kwargs[param]
                else:
                    params[param] = self.canvas.renderer.filters[filter][param]
            self.filters.append((filter, params))

    # Filters are renderer-dependent because it is highly unlikely 
    # a PIL-renderer would be able to perform exactly the same effects as Core Image.
    # The Layer class should be renderer independent,
    # which is why I'm not very happy with the following declarations.
    # But they are user-friendly though.

    def filter_blur(self, amount=10.0)           : self.filter("blur", **{"amount":amount})
    def filter_sharpen(self, amount=2.5)         : self.filter("sharpen", **{"amount":amount})
    
    def filter_zoomblur(self, **kwargs)          : self.filter(self.canvas.renderer.FILTER_ZOOMBLUR, **kwargs)
    def filter_motionblur(self, **kwargs)        : self.filter(self.canvas.renderer.FILTER_MOTIONBLUR, **kwargs)    
    def filter_noisereduction(self, **kwargs)    : self.filter(self.canvas.renderer.FILTER_NOISEREDUCTION, **kwargs) 
    def filter_bumpdistortion(self, **kwargs)    : self.filter(self.canvas.renderer.FILTER_BUMPDISTORTION, **kwargs)
    def filter_linearbump(self, **kwargs)        : self.filter(self.canvas.renderer.FILTER_BUMPDISTORTIONLINEAR, **kwargs)
    def filter_holedistortion(self, **kwargs)    : self.filter(self.canvas.renderer.FILTER_HOLEDISTORTION, **kwargs)
    def filter_circlesplash(self, **kwargs)      : self.filter(self.canvas.renderer.FILTER_CIRCLESPLASHDISTORTION, **kwargs)
    def filter_twirl(self, **kwargs)             : self.filter(self.canvas.renderer.FILTER_TWIRLDISTORTION, **kwargs)
    def filter_circularwrap(self, **kwargs)      : self.filter(self.canvas.renderer.FILTER_CIRCULARWRAP, **kwargs)
    def filter_kaleidoscope(self, **kwargs)      : self.filter(self.canvas.renderer.FILTER_KALEIDOSCOPE, **kwargs)
    def filter_triangletile(self, **kwargs)      : self.filter(self.canvas.renderer.FILTER_TRIANGLETILE, **kwargs)
    def filter_parallelogramtile(self, **kwargs) : self.filter(self.canvas.renderer.FILTER_PARALLELOGRAMTILE, **kwargs)
    def filter_perspectivetile(self, **kwargs)   : self.filter(self.canvas.renderer.FILTER_PERSPECTIVETILE, **kwargs)
    def filter_starshine(self, **kwargs)         : self.filter(self.canvas.renderer.FILTER_STARSHINEGENERATOR, **kwargs)
    def filter_checkerboard(self, **kwargs)      : self.filter(self.canvas.renderer.FILTER_CHECKERBOARDGENERATOR, **kwargs)
    def filter_pixelate(self, **kwargs)          : self.filter(self.canvas.renderer.FILTER_PIXELATE, **kwargs)
    def filter_crystallize(self, **kwargs)       : self.filter(self.canvas.renderer.FILTER_CRYSTALLIZE, **kwargs)
    def filter_dotscreen(self, **kwargs)         : self.filter(self.canvas.renderer.FILTER_DOTSCREEN, **kwargs)
    def filter_bloom(self, **kwargs)             : self.filter(self.canvas.renderer.FILTER_BLOOM, **kwargs)
    def filter_lighting(self, **kwargs)          : self.filter(self.canvas.renderer.FILTER_SPOTLIGHT, **kwargs)
    def filter_shading(self, **kwargs)           : self.filter(self.canvas.renderer.FILTER_SHADEDMATERIAL, **kwargs)
    def filter_levels(self, **kwargs)            : self.filter(self.canvas.renderer.FILTER_COLORMATRIX, **kwargs)
    def filter_edges(self, **kwargs)             : self.filter(self.canvas.renderer.FILTER_EDGES, **kwargs)
    def filter_lineoverlay(self, **kwargs)       : self.filter(self.canvas.renderer.FILTER_LINEOVERLAY, **kwargs)
    def filter_pagecurl(self, **kwargs)          : self.filter(self.canvas.renderer.FILTER_PAGECURLTRANSITION, **kwargs)
    def filter_histogram(self, **kwargs)         : self.filter(self.canvas.renderer.FILTER_HISTOGRAM, **kwargs)
    def filter_average(self, **kwargs)           : self.filter(self.canvas.renderer.FILTER_AVERAGE, **kwargs)

    filter_stretch = filter_linearbump
    filter_outline = filter_sketch = filter_lineoverlay
    filter_halftone = filter_dotscreen    

    def filters_first(self, b=None):
        """ Determines when filters are rendered on this layer.
        Either filters are applied to the layer before scaling, distorting and rotating it,
        or applied last, after having transformed the layer.
        """
        if isinstance(b, bool):
            self._filters_first = b
        return self._filters_first
        
    def pixels(self):
        """ Returns pixel-based information about the layer.
        Returns a Pixels object based on a render of this layer.
        """
        return self.canvas.renderer.pixels(self)

    def render(self, fast=True, crop=True):
        """ Returns a rendered version of the layer.
        All of the transformations, adjustments, blend modes
        and filters are applied to the returned object.
        You can feed the returned object back into a Canvas.layer().
        """
        return self.canvas.renderer.render(self, fast, crop)

### RENDERER #########################################################################################

from nodebox.graphics import Grob
class Renderer(Grob):
    
    """ A Canvas renderer interface.
    
    Since the canvas and layer model is non-destructive,
    merging and compositing layers is handled by a separate renderer.
    A renderer might be Core Image on Mac OS X or PIL on other platforms.
    
    A renderer has the following tasks:
    
     1) be able to identify an object it rendered
     2) be able to determine an image file's dimensions
     3) be able to produce a pixels array from the layer
     4) be able to render a layer
     5) be able to merge and composite rendered layers
     6) be able to draw a flattened image in NodeBox
     7) be able to export a flattened .png, .jpg and .tif
     8) have a dictionary of custom filters and their parameters
     9) have a name
    10) indicate whether it is able to render layer dropshadows
    
    A renderer is able to generate the following layers:
        
     1) image from file
     2) solid fill color
     3) linear gradient with two colors
     4) radial gradient with two colors and spread option
     5) vector path, at least straight line segments
     6) image from a list of pixel colors
     7) image from a Layer or Canvas
    
    A renderer supports the following compositing:
    
     1) adjustments: brightness, contrast, saturation, invert
     2) transparency, and alpha masks (defined by a Canvas)
     3) filters: blur and sharpen
     4) blend modes: multiply, screen, overlay, hue, color
    
    A renderer supports the following transformations:
    
     1) flip
     2) distort
     3) scale, handled before rotating
     4) rotate, handled before translating
     5) translate
    
    Transformations originate from
    the Layer's origin point and are processed
    after alpha masks.
    
    Adjustments, transparency, filters, transformations are rendered
    in the order defined in Layer.render_queue.
        
    """
    
    def __init__(self, quality=None):
        self.name = ""
        self.filters = {}
        self.render_queue = [
            RENDER_CROP,
            RENDER_FILTERS,
            RENDER_OPACITY, 
            RENDER_ADJUSTMENTS,
            RENDER_MASK,
            RENDER_TRANSFORMS,
        ]
        self.can_render_shadows = False
    
    def is_render(self, object):
        pass
    
    def imagesize(self, path):
        pass
    
    def pixels(self, layer):
        pass
    
    def render(self, layer, fast=False):
        pass
    
    def merge(self, canvas, layers=[], fast=False): 
        pass
    
    def draw(self, canvas, x, y, layers=[], fast=False): 
        pass
        
    def export(self, canvas, name, type, layers=[]):
        pass

### COREIMAGERENDERER ################################################################################

from AppKit import *
from Foundation import *

class CoreImageRenderer(Renderer):

    """ A Canvas Core Image renderer.
    """

    def __init__(self, quality=None):

        Renderer.__init__(self)
        self.name = "CoreImage"
        self.can_render_shadows = True

        # A helper draws visual feedback in NodeBox.
        self.helper = CoreImageHelper(self)
        
        # Filters available from Mac OS X 10.4:
        self.FILTER_COLORMATRIX            = "CIColorMatrix"                # color adjustment
        self.FILTER_EDGES                  = "CIEdges"
        self.FILTER_MOTIONBLUR             = "CIMotionBlur"                 # blur
        self.FILTER_ZOOMBLUR               = "CIZoomBlur"
        self.FILTER_NOISEREDUCTION         = "CINoiseReduction"
        self.FILTER_BUMPDISTORTION         = "CIBumpDistortion"             # distortion
        self.FILTER_HOLEDISTORTION         = "CIHoleDistortion"
        self.FILTER_CIRCLESPLASHDISTORTION = "CICircleSplashDistortion"
        self.FILTER_TWIRLDISTORTION        = "CITwirlDistortion"
        self.FILTER_CIRCULARWRAP           = "CICircularWrap"
        self.FILTER_KALEIDOSCOPE           = "CIKaleidoscope"               # tile
        self.FILTER_TRIANGLETILE           = "CITriangleTile"
        self.FILTER_PERSPECTIVETILE        = "CIPerspectiveTile"
        self.FILTER_STARSHINEGENERATOR     = "CIStarShineGenerator"         # generator
        self.FILTER_CHECKERBOARDGENERATOR  = "CICheckerboardGenerator"
        self.FILTER_BLOOM                  = "CIBloom"                      # stylize
        self.FILTER_PIXELATE               = "CIPixellate"
        self.FILTER_CRYSTALLIZE            = "CICrystallize"
        self.FILTER_DOTSCREEN              = "CIDotScreen"
        self.FILTER_SPOTLIGHT              = "CISpotLight"
        self.FILTER_SHADEDMATERIAL         = "CIShadedMaterial"
        self.FILTER_PAGECURLTRANSITION     = "CIPageCurlTransition"         # transition

        # Filters available from Mac OS X 10.5:
        self.FILTER_BUMPDISTORTIONLINEAR   = "CIBumpDistortionLinear"       # distortion
        self.FILTER_PARALLELOGRAMTILE      = "CIParallelogramTile"          # tile
        self.FILTER_LINEOVERLAY            = "CILineOverlay"                # stylize
        self.FILTER_HISTOGRAM              = "CIAreaHistogram"              # reduction
        self.FILTER_AVERAGE                = "CIAreaAverage" 
        
        # A property description list for each filter.
        self.filters = {
            self.FILTER_COLORMATRIX             : {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0},
            self.FILTER_EDGES                   : {"intensity": 1.0},
            self.FILTER_MOTIONBLUR              : {"radius": 20, "angle": 0},
            self.FILTER_ZOOMBLUR                : {"amount": 20, "dx": 0, "dy": 0},
            self.FILTER_NOISEREDUCTION          : {"noise": 0.02, "sharpness": 0.4},
            self.FILTER_BUMPDISTORTION          : {"dx": 0, "dy": 0, "radius": 300, "scale": 0.5},
            self.FILTER_BUMPDISTORTIONLINEAR    : {"dx": 0, "dy": 0, "radius": 300, "scale": 0.5, "angle": 0},
            self.FILTER_HOLEDISTORTION          : {"dx": 0, "dy": 0, "radius": 300},
            self.FILTER_CIRCLESPLASHDISTORTION  : {"dx": 0, "dy": 0, "radius": 150},
            self.FILTER_TWIRLDISTORTION         : {"dx": 0, "dy": 0, "radius": 150, "angle": 100},
            self.FILTER_CIRCULARWRAP            : {"radius": 150, "angle": 0},
            self.FILTER_KALEIDOSCOPE            : {"dx": 0, "dy": 0, "count": 10},
            self.FILTER_TRIANGLETILE            : {"dx": 0, "dy": 0, "angle": 0, "width": 100},
            self.FILTER_PARALLELOGRAMTILE       : {"dx": 0, "dy": 0, "angle": 0, "width": 100, "tilt": 90},
            self.FILTER_PERSPECTIVETILE         : {"dx0": 0, "dy0": 0, "dx1": 0, "dy1": 0, "dx2": 0, "dy2": 0, "dx3": 0, "dy3": 0},
            self.FILTER_STARSHINEGENERATOR      : {"dx": 0, "dy": 0, "radius": 25, "x_scale": 10, "x_angle": 0, "x_width": 0.5, "epsilon": -5.0},
            self.FILTER_CHECKERBOARDGENERATOR   : {"clr1": None, "clr2": None, "width": 80, "sharpness": 1.0},
            self.FILTER_BLOOM                   : {"radius": 10, "intensity": 1.0 },        
            self.FILTER_PIXELATE                : {"scale": 8},
            self.FILTER_CRYSTALLIZE             : {"radius": 20},
            self.FILTER_DOTSCREEN               : {"dx": 0, "dy": 0, "angle": 0, "width": 6, "sharpness": 0.7},
            self.FILTER_SPOTLIGHT               : {"dx0": 100, "dy0": 100, "dz0": 300, "dx1": 0, "dy1": 0, "brightness": 3.0, "concentration": 0.3, "color": None, "helper": False},
            self.FILTER_SHADEDMATERIAL          : {"dx": 0, "dy": 0, "radius": 20, "texture": None},
            self.FILTER_LINEOVERLAY             : {"noise": 0.07, "sharpness": 0.71, "intensity": 1.0, "threshold": 0.1, "contrast": 50},
            self.FILTER_PAGECURLTRANSITION      : {"time": 0.4, "radius": 75, "angle": 45, "back": None},
            self.FILTER_HISTOGRAM               : { },
            self.FILTER_AVERAGE                 : { },
        }
        
        # NodeBox sliders for each filter parameter.
        for filter in self.filters:
            self.filters[filter]["interface"] = False
        
        # Short names for each filter.
        # It's easier to write layer.filter("bloom")
        # than to write layer.filter(canvas.renderer.FILTER_BLOOM)
        self.aliases = {
            "levels"            : self.FILTER_COLORMATRIX,
            "edges"             : self.FILTER_EDGES,
            "motionblur"        : self.FILTER_MOTIONBLUR,
            "zoomblur"          : self.FILTER_ZOOMBLUR,
            "noisereduction"    : self.FILTER_NOISEREDUCTION,
            "bumpdistortion"    : self.FILTER_BUMPDISTORTION,
            "linearbump"        : self.FILTER_BUMPDISTORTIONLINEAR,
            "holedistortion"    : self.FILTER_HOLEDISTORTION,
            "circlesplash"      : self.FILTER_CIRCLESPLASHDISTORTION,
            "twirl"             : self.FILTER_TWIRLDISTORTION,
            "circularwrap"      : self.FILTER_CIRCULARWRAP,
            "kaleidoscope"      : self.FILTER_KALEIDOSCOPE,
            "triangletile"      : self.FILTER_TRIANGLETILE,
            "parallelogramtile" : self.FILTER_PARALLELOGRAMTILE,
            "perspectivetile"   : self.FILTER_PERSPECTIVETILE,
            "starshine"         : self.FILTER_STARSHINEGENERATOR,
            "checkerboard"      : self.FILTER_CHECKERBOARDGENERATOR,
            "bloom"             : self.FILTER_BLOOM,
            "pixelate"          : self.FILTER_PIXELATE,
            "crystallize"       : self.FILTER_CRYSTALLIZE,
            "dotscreen"         : self.FILTER_DOTSCREEN,
            "lighting"          : self.FILTER_SPOTLIGHT,
            "shading"           : self.FILTER_SHADEDMATERIAL,
            "lineoverlay"       : self.FILTER_LINEOVERLAY,
            "pagecurl"          : self.FILTER_PAGECURLTRANSITION,
            "histogram"         : self.FILTER_HISTOGRAM,
            "average"           : self.FILTER_AVERAGE,
            # Shortcut aliases >
            "motion"            : self.FILTER_MOTIONBLUR,
            "zoom"              : self.FILTER_ZOOMBLUR,
            "bump"              : self.FILTER_BUMPDISTORTION,
            "stretch"           : self.FILTER_BUMPDISTORTIONLINEAR,
            "hole"              : self.FILTER_HOLEDISTORTION,
            "splash"            : self.FILTER_CIRCLESPLASHDISTORTION,
            "wrap"              : self.FILTER_CIRCULARWRAP,
            "triangle"          : self.FILTER_TRIANGLETILE,
            "parallelogram"     : self.FILTER_PARALLELOGRAMTILE,
            "tile"              : self.FILTER_PERSPECTIVETILE,
            "star"              : self.FILTER_STARSHINEGENERATOR,
            "outline"           : self.FILTER_LINEOVERLAY,
            "sketch"            : self.FILTER_LINEOVERLAY,
            "curl"              : self.FILTER_PAGECURLTRANSITION,
            "halftone"          : self.FILTER_DOTSCREEN
        }
        
        # Either uses a 32-bit pixel format or a 128-bit pixel format.
        # The 128-bit format produces better gradients and crisper output
        # in fast mode but takes longer to render.
        self.quality = kCIFormatARGB8
        if quality == QUALITY_LOW: 
            self.quality = kCIFormatARGB8
        if quality == QUALITY_HIGH:
            self.quality = kCIFormatRGBAf
        
        # A queue of renders to draw in NodeBox.
        # Usually contains only one render (the rendered canvas),
        # unless you did multiple canvas.draw() in your script.
        # The difference only propagates when layers and the canvas
        # are accumulated so dynamics are possible.
        self._queue = []
        self._i = 0

    def filter(self, name, input=None, parameters={}):
        """ Generates a CIFilter from the given input CIImage.
        The specific parameters for this filter are passed as a dictionary.
        The return value is a filtered CIImage.
        """
        filter = CIFilter.filterWithName_(name)
        filter.setDefaults()
        if input != None:
            filter.setValue_forKey_(input, "inputImage")
        for key in parameters.keys():
            value = parameters[key]
            filter.setValue_forKey_(value, key)
        return filter.valueForKey_("outputImage") 
    
    def is_render(self, object):
        return isinstance(object, CIImage)
        
    def imagesize(self, path):
        url = NSURL.fileURLWithPath_(str(path))
        img = CIImage.imageWithContentsOfURL_(url)
        w, h = img.extent()[1]
        return w, h
    
    def image(self, type, data, w, h, layer=None, x=0, y=0):
    
        """ Returns a CIImage based on the given layer properties.
        
        Images can be created from files, colors,
        or a canvas of layers based on the layer's type.
        
        An PNG image with alpha information may contain a
        subtle white edges near the transparency,
        instead supply a TIFF with layers and transparency. 
        This is noticable in straight masks 
        (straight horizontal/vertical holes).
        
        """

        # The layer's source is an image file.
        # ------------------------------------------------------------------------
        if type == LAYER_FILE:
            url = NSURL.fileURLWithPath_(data)
            img = CIImage.imageWithContentsOfURL_(url)
        
        # The layer's source is a single color
        # for which we create a fill rectangle using a CIImageAccumulator.
        # ------------------------------------------------------------------------
        elif type == LAYER_FILL:
            r = NSRect((x,y), (w,h))
            a = CIImageAccumulator.imageAccumulatorWithExtent_format_(r, self.quality)
            c = data
            c = CIColor.colorWithRed_green_blue_alpha_(c.r, c.g, c.b, c.a)        
            img = self.filter("CIConstantColorGenerator", parameters={"inputColor": c})
            a.setImage_(img)
            img = a.image()

            #img = NSImage.alloc().initWithSize_((w,h))
            #img.lockFocus()
            #NSColor.colorWithDeviceRed_green_blue_alpha_(c.r, c.g, c.b, c.a).set()
            #NSRectFill(((x,y), (w,h)))
            #img.unlockFocus()
            #img = img.TIFFRepresentation()
            #img = CIImage.imageWithData_(img)

        # The layer's source are two colors
        # from which we create a vertical linear gradient
        # spread equally across the layer's height.
        # ------------------------------------------------------------------------    
        elif type == LAYER_LINEAR_GRADIENT:
            r = NSRect((x,y), (w,h))
            a = CIImageAccumulator.imageAccumulatorWithExtent_format_(r, self.quality)
            c0, c1 = data
            c0 = CIColor.colorWithRed_green_blue_alpha_(c0.r, c0.g, c0.b, c0.a)
            c1 = CIColor.colorWithRed_green_blue_alpha_(c1.r, c1.g, c1.b, c1.a)
            img = self.filter("CILinearGradient", 
                   parameters={"inputColor0": c0, 
                               "inputColor1": c1,
                               "inputPoint0": CIVector.vectorWithX_Y_(0, 0),
                               "inputPoint1": CIVector.vectorWithX_Y_(0, h)})
            a.setImage_(img)
            img = a.image()

        # The layer's source are two colors
        # from which we create a radial gradient
        # spread across either the layer's width or the layer's height, whichever is smaller.
        # ------------------------------------------------------------------------
        elif type == LAYER_RADIAL_GRADIENT:
            r = NSRect((x,y), (w,h))
            a = CIImageAccumulator.imageAccumulatorWithExtent_format_(r, self.quality)
            c0, c1, spread = data
            c0 = CIColor.colorWithRed_green_blue_alpha_(c0.r, c0.g, c0.b, c0.a)
            c1 = CIColor.colorWithRed_green_blue_alpha_(c1.r, c1.g, c1.b, c1.a)
            spread = max(0.0, min(spread, 0.99))
            radius = min(w/2, h/2)
            img = self.filter("CIRadialGradient", 
                   parameters={"inputColor0" : c0, 
                               "inputColor1" : c1,
                               "inputCenter" : CIVector.vectorWithX_Y_(w/2, h/2),
                               "inputRadius0": radius*spread,
                               "inputRadius1": radius})
            a.setImage_(img)
            img = a.image()

        # The layer's source consists of vector curves
        # which we need to transform to bitmap information.
        # ------------------------------------------------------------------------        
        elif type == LAYER_PATH:
            path, bg, fg, s, sw = data
            sw = float(sw)
            (px, py), (pw, ph) = path.bounds()
            img = NSImage.alloc().initWithSize_((w,h))
            img.lockFocus()
            NSColor.colorWithDeviceRed_green_blue_alpha_(bg.r, bg.g, bg.b, bg.a).set()
            NSRectFill(((x,y), (w,h)))
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(w/2, h/2)
            t.scaleXBy_yBy_(1, -1)
            t.translateXBy_yBy_(-px+sw/2+PATH_PADDING, -py+sw/2+PATH_PADDING)
            t.translateXBy_yBy_(-w/2, -h/2)
            t.set()
            NSColor.colorWithDeviceRed_green_blue_alpha_(fg.r, fg.g, fg.b, fg.a).set()
            path.fill()
            if sw != None and sw > 0:
                NSColor.colorWithDeviceRed_green_blue_alpha_(s.r, s.g, s.b, s.a).set()
                path.setLineWidth_(sw)
                path.stroke()            
            img.unlockFocus()
            img = img.TIFFRepresentation()
            img = CIImage.imageWithData_(img)

        # The layer's source is a list of pixel colors.
        # Duane Bailey, http://nodebox.net/code/index.php/shared_2007-12-28-23-34-57
        # If there is more width*height than there are pixels,
        # the bitmap will be completed with transparent pixels.
        # ------------------------------------------------------------------------      
        elif type == LAYER_PIXELS:
            p, w, h = data
            import numpy
            raw = numpy.array([0] * w*h*4, typecode='c')
            for i in range(len(p)):
                raw[i*4+0] = p[i].r * 255
                raw[i*4+1] = p[i].g * 255
                raw[i*4+2] = p[i].b * 255
                raw[i*4+3] = p[i].a * 255
            raw = (raw, None, None, None, None)
            img = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
                raw, w, h, 8, 4, True, False, NSDeviceRGBColorSpace, w * 4, 32
            )
            img = img.TIFFRepresentation()
            img = CIImage.alloc().initWithData_(img)

        # The layer is in fact a canvas of layers,
        # flatten it and use the resulting CIImage.
        # ------------------------------------------------------------------------    
        elif type == LAYER_LAYERS:
            img = self.merge(data)
        
        # The layer's source is a CIImage object.
        # ------------------------------------------------------------------------
        elif type == LAYER_CIIMAGEOBJECT:
            img = data
            # The CIImage's extent can have x and y different from zero.
            # To ensure this rendered layer appears 
            # at the center of the canvas by default we translate it to (0,0).
            (x0, y0), (w0, h0) = img.extent()
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(-x0, -y0)
            img = self.filter("CIAffineTransform", img, {"inputTransform": t})
            # Crop to the canvas size for speed.
            #v = CIVector.vectorWithX_Y_Z_W_(0, 0, layer.canvas.w, layer.canvas.h)
            #img = self.filter("CICrop", img, {"inputRectangle" : v})

        # The layer's source is NSImage.TIFFRepresentation data.
        # ------------------------------------------------------------------------
        elif type == LAYER_NSIMAGEDATA:
            img = CIImage.imageWithData_(data)        
        
        return img

    def pixels(self, layer, crop=False):
        """ Returns a Pixels object based on the layer.
        """
        img = self.render(layer, crop=crop)
        return CoreImagePixels(self, layer, img)
    
    def render_adjustments(self, layer, img):
        """ Render layer adjustments.
        Applies the layer's adjustments to the given image:
        brightness, contrast, saturation and invert.
        """
        if layer._brightness != 0.0 \
        or layer._contrast != 1.0 \
        or layer._saturation != 1.0:
            p = {
                "inputBrightness" : max(-1.0, min(layer._brightness, 1.0)), 
                "inputContrast"   : max(0.25, min(layer._contrast, 4.0)), 
                "inputSaturation" : max(0.0, min(layer._saturation, 2.0))
            }
            img = self.filter("CIColorControls", img, p)
        if layer.inverted == True:
            img = self.filter("CIColorInvert", img)
        return img
    
    def render_filters(self, layer, img):
        """ Render layer filters.
        Applies the layer's filters to the given image: blur and sharpen.
        This renderer has other specific filters that are also processed here.
        """
        if layer.blur > 0.0:
            p = {"inputRadius": max(0.0, min(layer.blur, 100.0))}
            img = self.filter("CIGaussianBlur", img, p)
        if layer.sharpness > 0.0:
            p = {
                "inputRadius"    : max(0.0, min(layer.sharpness, 100.0)), 
                "inputIntensity" : 0.5
            }
            img = self.filter("CIUnsharpMask", img, p)
        # Apply all other filters, in order of entry.
        for filter, options in layer.filters:
            if filter in self.filters:
                f = getattr(self, "render_filter_" + filter[2:].lower())
                # Filter options can be supplied by NodeBox sliders
                if self.helper != None \
                and "interface" in options \
                and options["interface"] == True:
                    # The filter options are not in a command call,
                    # but in the NodeBox var panel.
                    # The panel also has a "render" check to enable/disable the filter.
                    options = self.helper.interface(filter)
                    if options["render"] == True: 
                        img = f(layer, img, options)
                else:
                    img = f(layer, img, options) 
        return img
    
    # COLOR MATRIX
    # ------------------------------------------------------------------------
    def render_filter_colormatrix(self, layer, img, options):
        # Apply the Core Image Color Matrix filter.
        # This powerful filter has functionalities
        # comparable to PhotoShop levels or curves.
        # For each RGBA channel you can specify
        # a multiplication factor, increasing or decreasing
        # the channel's prominence.
        # Instead of a single value a four-tuple can
        # be supplied as well (for instance, to increase
        # the blue in the R channel.
        # Setting r=0, g=0, b=0 and a=1
        # removes all color information while
        # keeping the alpha information.
        # This results in the image's alpha mask,
        # useful as a shadow for example.
        # I.e. setting a channel to zero removes it.
        v = []
        for channel in "rgba":
            v.append(options[channel])
        for i in range(len(v)):
            if  not isinstance(v[i], (list, tuple)):
                x = v[i]
                v[i] = [0, 0, 0, 0]
                v[i][i] = x
            else:
                v[i] = list(v[i])
            if i == 3: 
                v[i][3] -= 0.000001
            v[i] = CIVector.vectorWithX_Y_Z_W_(v[i][0], v[i][1], v[i][2], v[i][3])
        p = {
            "inputRVector" : v[0], 
            "inputGVector" : v[1], 
            "inputBVector" : v[2], 
            "inputAVector" : v[3],
            "inputBiasVector" : CIVector.vectorWithX_Y_Z_W_(0,0,0,0)
        }        
        img = self.filter(self.FILTER_COLORMATRIX, img, p)
        return img 

    # EDGES
    # ------------------------------------------------------------------------
    def render_filter_edges(self, layer, img, options):
        # Apply the Core Image Edges filter effect,
        # it finds all the edges in an image and displays them in a color.
        p = {"inputIntensity": max(0.0, min(options["intensity"], 10.0))}
        img = self.filter(self.FILTER_EDGES, img,  p)
        return img  
    
    # MOTION BLUR
    # ------------------------------------------------------------------------
    def render_filter_motionblur(self, layer, img, options):
        # Apply the Core Image Motion Blur filter effect,
        # generating a swooshy directional blur.
        # This filter is shaky in certain situations,
        # e.g. crashes when combined with tiling.
        for filter, params in layer.filters:
            if filter == self.FILTER_PERSPECTIVETILE:
                return img
        (x,y), (w,h) = img.extent() 
        # If the image is opaque at the edges it will will stretch out beyond its bounds.
        # To solve this, we add a transparent 1-pixel border/gutter around the layer.    
        if w < layer.canvas.w*10 and h < layer.canvas.h*10:
            base = self.image(LAYER_FILL, Transparent(), w+2, h+2)
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(-1, -1)
            base = self.filter("CIAffineTransform", base, {"inputTransform": t})
            img = self.filter("CISourceOverCompositing", img, {"inputBackgroundImage": base}) 
        p = {
            "inputRadius" : max(0.0, min(options["radius"], 100.0)), 
            "inputAngle"  : radians(options["angle"])
        }
        img = self.filter(self.FILTER_MOTIONBLUR, img, p)
        # After applying the filter w and h will be near infinity.
        # To solve this we crop to something workable.
        d = 20 + 4 * p["inputAngle"]
        v = CIVector.vectorWithX_Y_Z_W_(x-d, y-d, w+d*2, h+d*2)
        img = self.filter("CICrop", img, {"inputRectangle" : v})
        return img   

    # ZOOM BLUR
    # ------------------------------------------------------------------------
    def render_filter_zoomblur(self, layer, img, options):
        # Apply the Core Image Zoom Blur filter effect,
        # simulating the effect of zooming the camera while capturing the image.
        dx = options["dx"]
        dy = options["dy"]
        p = {
            "inputCenter" : CIVector.vectorWithX_Y_(layer._w*0.5+dx, layer._h*0.5-dy),
            "inputAmount" : max(0.0, min(options["amount"], 200.0))
        }
        img = self.filter(self.FILTER_ZOOMBLUR, img, p)
        return img  

    # NOISE REDUCTION
    # ------------------------------------------------------------------------
    def render_filter_noisereduction(self, layer, img, options):
        # Apply the Core Image Noise Reduction filter effect,
        # blurring edges below the threshold and sharpening above.
        p = {
            "inputNoiseLevel" : max(0.0, min(options["noise"], 0.1)), 
            "inputSharpness"  : max(0.0, min(options["sharpness"], 2.0))
        }
        img = self.filter(self.FILTER_NOISEREDUCTION, img, p)
        return img
    
    # BUMP DISTORTION
    # ------------------------------------------------------------------------
    def render_filter_bumpdistortion(self, layer, img, options):
        # Apply the Core Image Bump Distortion filter effect,
        # generating a pinch or bump in the layer.
        dx = options["dx"]
        dy = options["dy"]
        p = {
            "inputCenter" : CIVector.vectorWithX_Y_(layer._w*0.5+dx, layer._h*0.5-dy), 
            "inputRadius" : max(0.0, min(options["radius"], 600.0)), 
            "inputScale"  : max(-1.0, min(options["scale"], 1.0))
        }
        img = self.filter(self.FILTER_BUMPDISTORTION, img, p)
        return img

    # BUMP DISTORTION LINEAR
    # ------------------------------------------------------------------------
    def render_filter_bumpdistortionlinear(self, layer, img, options):
        # Apply the Core Image Bump Distortion Linear filter effect,
        # generating a pinch or bump from an entire line in the layer.
        # Left and top edge sometimes get chopped off if we don't accumulate it first.
        a = CIImageAccumulator.imageAccumulatorWithExtent_format_(img.extent(), self.quality)
        a.setImage_(img)
        img = a.image()
        dx = options["dx"]
        dy = options["dy"]
        p = {
            "inputCenter" : CIVector.vectorWithX_Y_(layer._w*0.5+dx, layer._h*0.5-dy), 
            "inputRadius" : max(0.0, min(options["radius"], 600.0)), 
            "inputScale"  : max(-1.0, min(options["scale"], 1.0)), 
            "inputAngle"  : radians(options["angle"])
        }
        img = self.filter(self.FILTER_BUMPDISTORTIONLINEAR, img, p)
        return img
    
    # HOLE DISTORTION
    # ------------------------------------------------------------------------
    def render_filter_holedistortion(self, layer, img, options):
        # Apply the Core Image Hole Distortion filter effect,
        # pushing the layer's pixels outwards.    
        if options["radius"] > 0:
            dx = options["dx"]
            dy = options["dy"]
            p = {
                "inputCenter": CIVector.vectorWithX_Y_(layer._w*0.5+dx, layer._h*0.5-dy), 
                "inputRadius": max(0.0, min(options["radius"], 1000.0))
            }
            img = self.filter(self.FILTER_HOLEDISTORTION, img, p)
        return img

    # CIRCLE SPLASH DISTORTION
    # ------------------------------------------------------------------------
    def render_filter_circlesplashdistortion(self, layer, img, options):
        # Apply the Core Image Circle Splash Distortion filter effect,
        # pushing the layer's pixels on a circle circumference outwards.    
        if options["radius"] > 0:
            dx = options["dx"]
            dy = options["dy"]
            p = {
                "inputCenter" : CIVector.vectorWithX_Y_(dx, dy), 
                "inputRadius" : max(0.0, min(options["radius"], 1000.0))
            }
            img = self.filter(self.FILTER_CIRCLESPLASHDISTORTION, img, p)
        return img
    
    # TWIRL DISTORTION
    # ------------------------------------------------------------------------
    def render_filter_twirldistortion(self, layer, img, options):
        # Apply the Core Image Twirl Distortion filter effect,
        # generating wave motion in the layer.         
        dx = options["dx"]
        dy = options["dy"]
        p = {
            "inputCenter" : CIVector.vectorWithX_Y_(layer._w*0.5+dx, layer._h*0.5-dy), 
            "inputRadius" : max(0.0, min(options["radius"], 500.0)), 
            "inputAngle"  : radians(options["angle"])
        }
        img = self.filter(self.FILTER_TWIRLDISTORTION, img, p)
        return img
    
    # CIRCULAR WRAP
    # ------------------------------------------------------------------------
    def render_filter_circularwrap(self, layer, img, options):
        # Apply the Core Image Circular Wrap filter effect,
        # wrapping the layer around a transparent circle.          
        p = {
            "inputCenter": CIVector.vectorWithX_Y_(layer._w*0.5, layer._h*0.5), 
            "inputRadius": max(0.0, min(options["radius"], 600.0)), 
            "inputAngle": radians(options["angle"])
        }
        img = self.filter(self.FILTER_CIRCULARWRAP, img, p)
        return img

    # KALEIDOSCOPE
    # ------------------------------------------------------------------------    
    def render_filter_kaleidoscope(self, layer, img, options):
        # Apply the Core Image Kaleidoscope filter effect,
        # generating a fractal-like output.
        if options["count"] > 0:
            dx = options["dx"]
            dy = options["dy"]
            p = {
                "inputCenter" : CIVector.vectorWithX_Y_(layer._w*0.5+dx, layer._h*0.5+dy),
                "inputCount"  : max(0, min(options["count"], 100))
            }
            img = self.filter(self.FILTER_KALEIDOSCOPE, img, p) 
        return img

    # TRIANGLE TILE
    # ------------------------------------------------------------------------
    def render_filter_triangletile(self, layer, img, options):
        # Apply the Core Image Triangle Tile filter effect,
        # generating a fractal-like output.
        (x,y), (w,h) = img.extent()
        dx = options["dx"]
        dy = options["dy"]        
        p = {
            "inputCenter" : CIVector.vectorWithX_Y_(layer._w*0.5+dx, layer._h*0.5+dy),
            "inputWidth"  : options["width"], 
            "inputAngle"  : radians(options["angle"]) 
            }
        img = self.filter(self.FILTER_TRIANGLETILE, img, p)
        img = self.filter("CICrop", img, {"inputRectangle": CIVector.vectorWithX_Y_Z_W_(x, y, w, h)})  
        return img

    # PARALLELOGRAM TILE
    # ------------------------------------------------------------------------
    def render_filter_parallelogramtile(self, layer, img, options):
        # Apply the Core Image Parallelogram Tile filter effect,
        # generating a fractal-like output.
        (x,y), (w,h) = img.extent()
        dx = options["dx"]
        dy = options["dy"]              
        p = {
            "inputCenter"     : CIVector.vectorWithX_Y_(layer._w*0.5+dx, layer._h*0.5+dy),
            "inputWidth"      : options["width"], 
            "inputAngle"      : radians(options["angle"]), 
            "inputAcuteAngle" : radians(options["tilt"]) 
        }
        img = self.filter(self.FILTER_PARALLELOGRAMTILE, img, p)
        img = self.filter("CICrop", img, {"inputRectangle": CIVector.vectorWithX_Y_Z_W_(x, y, w, h)})
        return img
    
    # PERSPECTIVE TILE
    # ------------------------------------------------------------------------
    def render_filter_perspectivetile(self, layer, img, options):
        # Apply the Core Image Perspective Tile filter effect.
        # This filter distorts the layer by translating its
        # corner points, and then tiling that on a plane.
        (x,y), (w,h) = img.extent()
        dx0 = options["dx0"]
        dy0 = options["dy0"] + h
        dx1 = options["dx1"] + w
        dy1 = options["dy1"] + h
        dx2 = options["dx2"] + w
        dy2 = options["dy2"]
        dx3 = options["dx3"]
        dy3 = options["dy3"]
        p = {
            "inputTopLeft"     : CIVector.vectorWithX_Y_(dx0, dy0),
            "inputTopRight"    : CIVector.vectorWithX_Y_(dx1, dy1),
            "inputBottomRight" : CIVector.vectorWithX_Y_(dx2, dy2),
            "inputBottomLeft"  : CIVector.vectorWithX_Y_(dx3, dy3)
        }
        img = self.filter(self.FILTER_PERSPECTIVETILE, img, p)
        return img

    # STARSHINE GENERATOR
    # ------------------------------------------------------------------------
    def render_filter_starshinegenerator(self, layer, img, options):
        # Apply the Core Image Starshine Generator filter effect.
        # This filter maps stars and sun bursts on the layer,
        # which is usually a new transparent layer.
        (x, y), (w, h) = img.extent()    
        dx = options["dx"]
        dy = options["dy"]
        p = {
            "inputCenter"     : CIVector.vectorWithX_Y_(layer._w*0.5+dx, layer._h*0.5-dy), 
            "inputRadius"     : max(0.0, min(options["radius"], 300.0)), 
            "inputCrossScale" : max(0.0, min(options["x_scale"], 100.0)), 
            "inputCrossAngle" : radians(options["x_angle"]),
            "inputCrossWidth" : options["x_width"],
            "inputEpsilon"    : max(-8.0, min(options["epsilon"], 8.0))
        }
        starshine = self.filter(self.FILTER_STARSHINEGENERATOR, None, p)
        #starshine = self.render_opacity(layer, starshine, x, y, w, h)
        img = self.filter("CISourceOverCompositing", starshine, {"inputBackgroundImage": img})       
        img = self.filter("CICrop", img, {"inputRectangle" : CIVector.vectorWithX_Y_Z_W_(x, y, w, h)})
        return img 

    # CHECKERBOARD GENERATOR
    # ------------------------------------------------------------------------
    def render_filter_checkerboardgenerator(self, layer, img, options):
        # Apply the Core Image Checkerboard Generator filter effect.
        (x, y), (w, h) = img.extent()
        clr1 = options["clr1"]
        clr2 = options["clr2"]
        if clr1 == None: clr1 = Color(0.0)
        if clr2 == None: clr2 = Color(1.0)
        p = {
            "inputCenter"    : CIVector.vectorWithX_Y_(-1, layer._h), 
            "inputColor0"    : CIColor.colorWithRed_green_blue_alpha_(clr1.r, clr1.g, clr1.b, clr1.a), 
            "inputColor1"    : CIColor.colorWithRed_green_blue_alpha_(clr2.r, clr2.g, clr2.b, clr2.a), 
            "inputWidth"     : max(0.0, min(options["width"], 800.0)),
            "inputSharpness" : max(0.0, min(options["sharpness"], 1.0))
        }
        checkerboard = self.filter(self.FILTER_CHECKERBOARDGENERATOR, None, p)
        #checkerboard = self.render_opacity(layer, checkerboard, x, y, w, h)
        img = self.filter("CISourceOverCompositing", checkerboard, {"inputBackgroundImage": img})
        img = self.filter("CICrop", img, {"inputRectangle" : CIVector.vectorWithX_Y_Z_W_(x, y, w, h)})  
        return img

    # BLOOM
    # ------------------------------------------------------------------------
    def render_filter_bloom(self, layer, img, options):
        # Apply the Core Image Bloom filter effect
        # which adds a hazy glow to the layer by softening edges.
        p = {
            "inputRadius"    : max(0, min(options["radius"], 100)), 
            "inputIntensity" : max(0.0, min(options["intensity"], 1.0))
        }
        img = self.filter(self.FILTER_BLOOM, img, p)
        return img        

    # PIXELATE
    # ------------------------------------------------------------------------
    def render_filter_pixellate(self, layer, img, options):
        # Apply the Core Image Pixellate filter effect.
        # You will notice the layer's bounding box varying slightly
        # as the pixel scale increases.
        (x,y), (w,h) = img.extent()
        p = {
            "inputScale"  : max(1, min(options["scale"], 100)), 
            "inputCenter" : CIVector.vectorWithX_Y_(w/2, h/2)
        }
        img = self.filter(self.FILTER_PIXELATE, img, p)
        img = self.filter("CICrop", img, {"inputRectangle" : CIVector.vectorWithX_Y_Z_W_(x, y, w, h)})  
        return img 

    # CRYSTALLIZE
    # ------------------------------------------------------------------------
    def render_filter_crystallize(self, layer, img, options):
        # Apply the Core Image Crystallize effect
        # which creates polygon blocks of groups of pixels.
        # Looks useful for Voronoi-like spatial analysis.   
        (x,y), (w,h) = img.extent()
        if options["radius"] > 0:
            r = max(0, min(options["radius"], 100))
            p = {"inputCenter" : CIVector.vectorWithX_Y_(r, r), "inputRadius" : r}
            img = self.filter(self.FILTER_CRYSTALLIZE, img, p) 
        return img 

    # DOTSCREEN
    # ------------------------------------------------------------------------
    def render_filter_dotscreen(self, layer, img, options):
        # Apply the Core Image Dotscreen effect
        # which simulates the dot patterns of a halftone screen..  
        if options["width"] > 0:
            dx = options["dx"]
            dy = options["dy"]
            p = {
                "inputCenter"    : CIVector.vectorWithX_Y_(dx,dy),
                "inputAngle"     : max(0, min(options["angle"], 360)),
                "inputWidth"     : max(0, min(options["width"], 50)),
                "inputSharpness" : max(0, min(options["sharpness"], 1))
            }
            img = self.filter(self.FILTER_DOTSCREEN, img, p) 
        return img 

    # SPOTLIGHT
    # ------------------------------------------------------------------------
    def render_filter_spotlight(self, layer, img, options):
        # Apply the Core Image Bloom Spotlight effect
        # which adds lighting to the layer.
        # This complex filter has a helper to provide visual feedback.
        # The light source is positioned at dx0, dy0, dz0 measured
        # from the layer's center.
        # The light shines in the direction of dx1, dy1.
        (x,y), (w,h) = img.extent()
        dx0 = options["dx0"] + w/2
        dx1 = options["dx1"] + w/2
        dy0 = h/2 - options["dy0"]
        dy1 = h/2 - options["dy1"]
        dz0 = max(100, min(options["dz0"], 10000))        
        dz1 = 0
        b = max(0.0, min(options["brightness"], 10.0))
        c = max(0.0, min(options["concentration"], 1.0)) * 0.1
        p = {
            "inputLightPosition" : CIVector.vectorWithX_Y_Z_(dx0, dy0, dz0),
            "inputLightPointsAt" : CIVector.vectorWithX_Y_Z_(dx1, dy1, dz1),
            "inputBrightness"    : b,
            "inputConcentration" : c,
        }
        clr = options["color"]
        if clr != None: 
            p["inputColor"] = CIColor.colorWithRed_green_blue_alpha_(clr.r, clr.g, clr.b, clr.a)
        img = self.filter(self.FILTER_SPOTLIGHT, img, p)
        # Pass the unmodified parameters so the helper
        # can decide its relative position for itself.
        if options["helper"] == True and self.helper != None:
            self.helper.spotlight(layer, w, h, dx0-w/2, h/2+dy0, dz0, dx1-w/2,h/2+dy1, dz1, b, c)
        return img

    # SHADED MATERIAL
    # ------------------------------------------------------------------------
    def render_filter_shadedmaterial(self, layer, img, options):
        # Apply the Core Image Shaded Material effect
        # which adds texturing to the layer.
        # Without the texture parameter,
        # transforms the layer to a height field mask:
        # the white area becomes a gradient with black at the edges.
        # When the texture parameter is a Canvas,
        # shades that canvas on the height field.
        (x,y), (w,h) = img.extent()
        p = {"inputRadius": max(0, min(options["radius"], 300))}
        img = self.filter("CIHeightFieldFromMask", img, p)
        canvas = options["texture"]
        if isinstance(canvas, Canvas):
            dx = max(-canvas.w/2, min(options["dx"], canvas.w/2))
            dy = max(-canvas.h/2, min(options["dy"], canvas.h/2))
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(dx, dy)
            canvas = self.merge(canvas)  
            canvas = self.filter("CIAffineTransform", canvas, {"inputTransform": t})
            p = {
                "inputShadingImage" : canvas, 
                "inputScale"        : 1.0
            }
            img = self.filter("CIShadedMaterial", img, p)
        img = self.filter("CICrop", img, {"inputRectangle" : CIVector.vectorWithX_Y_Z_W_(x, y, w, h)})  
        return img

    # LINE OVERLAY
    # ------------------------------------------------------------------------
    def render_filter_lineoverlay(self, layer, img, options):
        # Apply the Core Image Line Overlay effect
        # which simulates a sketch by outlining the edges in black,
        # after performing Noise Reduction.
        p = {
            "inputNRNoiseLevel"  : max(0, min(options["noise"], 0.1)),
            "inputNRSharpness"   : max(0, min(options["sharpness"], 2.0)),
            "inputEdgeIntensity" : max(0, min(options["intensity"], 200)),
            "inputThreshold"     : max(0, min(options["threshold"], 1.0)),
            "inputContrast"      : max(0.25, min(options["contrast"],  200))
        }
        img = self.filter(self.FILTER_LINEOVERLAY, img, p) 
        return img 

    # PAGE CURL TRANSITION
    # ------------------------------------------------------------------------
    def render_filter_pagecurltransition(self, layer, img, options):
        
        # Apply the Core Image Page Curl effect,
        # which curls the edges of the layer to reveal the layer's recto backside.
        (x,y), (w,h) = img.extent()
    
        # By default the backside of the layer is the layer itself,
        # filtered up to the page curl. Works great for transparent layers.
        # The back parameter can also be "pattern",
        # then the backside is a triangle-tiled pattern of the layer.
        if options["back"] in (None, "pattern"):
            back = layer.copy()
            back._scale = Point(1.0, 1.0)
            back.rotation = 0
            filters = []
            # Avoid recursion by removing Page Curl from the duplicate backside.
            for name, params in back.filters:
                if name != self.FILTER_PAGECURLTRANSITION:
                    filters.append((name, params))
                else: 
                    break
            back.filters = filters
            if options["back"] == "pattern":
                back.filter("triangletile", angle=40, width=75)
                back.saturation = 0.75          
            back = back.render()
            (bx, by), (bw, bh) = back.extent()
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(-bx, -by)
            back = self.filter("CIAffineTransform", back, {"inputTransform": t})

        # A custom Canvas can be supplied as backside.
        # It will be strechted to fit.
        elif isinstance(options["back"], Canvas) \
        and options["back"] != layer.canvas:
            back = options["back"]
            back = back.render()
            (bx, by), (bw, bh) = back.extent()
            t = NSAffineTransform.transform()
            t.scaleXBy_yBy_((w-x)/bw, (h-y)/bh) 
            back = self.filter("CIAffineTransform", back, {"inputTransform": t})
        
        # Finally, a color can be supplied as backside.
        else:
            try:
                clr = options["back"]
                r, g, b, a = clr.r, clr.g, clr.b, clr.a
                back = self.image(LAYER_FILL, clr, w, h)
            except:
                pass

        # Gradient shade on background. Works only for top corners apparently.
        transparent = self.image(LAYER_FILL, Transparent(), w, h)
        shade = self.image(LAYER_RADIAL_GRADIENT, (Transparent(), color(0,0,0,0.5), 0), w, h)
        p = {
            "inputTargetImage"   : transparent, 
            "inputBacksideImage" : back, 
            "inputShadingImage"  : shade,
            "inputExtent"        : CIVector.vectorWithX_Y_Z_W_(0, 0, 300, 300), 
            "inputTime"          : max(0, min(options["time"], 3.0)), 
            "inputAngle"         : radians(-options["angle"]), 
            "inputRadius"        : max(1, min(options["radius"], 200))
        }
        img = self.filter("CIPageCurlTransition", img, p)
        return img

    # HISTOGRAM
    # ------------------------------------------------------------------------
    def render_filter_areahistogram(self, layer, img, options):
        (x,y), (w,h) = img.extent()
        p = {
            "inputExtent" : CIVector.vectorWithX_Y_Z_W_(x, y, w, h), 
            "inputCount"  : 255,
            "inputScale"  : 1.0,
        }
        img = self.filter(self.FILTER_HISTOGRAM, img, p) 
        return img 
    
    # AVERAGE
    # ------------------------------------------------------------------------
    def render_filter_areaaverage(self, layer, img, options):
        (x,y), (w,h) = img.extent()
        p = {
            "inputExtent" : CIVector.vectorWithX_Y_Z_W_(x, y, w, h), 
        }
        img = self.filter(self.FILTER_AVERAGE, img, p)
        return img     
    
    def render_transforms(self, layer, img):
        """ Render layer transformations.
        By default a top-left coordinate system is emulated.
        Scaling is handled first to avoid distortion when rotating.
        The layer scales and rotates from its origin point.
        """
        img = self.render_transform_flip(layer, img)    
        img = self.render_transform_distort(layer, img)
        img = self.render_transform_scale(layer, img)
        img = self.render_transform_rotate(layer, img)
        img = self.render_transform_translate(layer, img)
        return img 
    
    def render_transform_flip(self, layer, img):
        flip_h, flip_v = layer._flip
        if flip_h == True \
        or flip_v == True:
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(layer._w*0.5, layer._h*0.5)
            if flip_h == True: t.scaleXBy_yBy_(-1, 1)
            if flip_v == True: t.scaleXBy_yBy_(1, -1)
            t.translateXBy_yBy_(-layer._w*0.5, -layer._h*0.5)
            img = self.filter("CIAffineTransform", img, {"inputTransform": t})
        return img
        
    def render_transform_distort(self, layer, img):
        # Distort doesn't work very well with filters.
        # Example: when applying a blur, the blur overflows at the edges
        # will not originate from the center, causing the image to displace.
        (x,y), (w,h) = img.extent()
        l, t, r, b = layer.bounds()
        ox = ((w-x) - layer._w) / 2
        oy = ((h-y) - layer._h) / 2
        # Check first if a distort transform is defined.
        distorted = False
        for pt in layer._distort:
            if pt.x != 0.0 or pt.y != 0.0:
                distorted = True
                break
        # If so, render it.
        if distorted == True:
            p = {
                "inputTopLeft"     : 0, 
                "inputTopRight"    : 1, 
                "inputBottomLeft"  : 3, 
                "inputBottomRight" : 2
            }
            for k in p.keys():
                i = p[k]
                dx =  layer._distort[i].x * w
                dy = -layer._distort[i].y * h
                if i == 1 or i == 2: dx += w
                if i == 0 or i == 1: dy += h
                p[k] = CIVector.vectorWithX_Y_(dx-ox/0.8, dy-oy/2)
            img = self.filter("CIPerspectiveTransform", img, p)
        return img

    def render_transform_scale(self, layer, img):
        if layer._scale.x != 1.0 \
        or layer._scale.y != 1.0:
            dx = layer._w*0.5 * layer._origin.x
            dy = layer._h*0.5 * (1-layer._origin.y)
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(dx * layer._scale.x, dy * layer._scale.y)
            t.scaleXBy_yBy_(layer._scale.x, layer._scale.y)        
            t.translateXBy_yBy_(-dx, -dy)
            img = self.filter("CIAffineTransform", img, {"inputTransform": t})
        return img

    def render_transform_rotate(self, layer, img):
        if layer.rotation % 360 != 0:
            dx = layer._w * layer._scale.x * layer._origin.x
            dy = layer._h * layer._scale.y * (1-layer._origin.y)
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(dx, dy)
            t.rotateByDegrees_(-layer.rotation)
            t.translateXBy_yBy_(-dx, -dy)
            img = self.filter("CIAffineTransform", img, {"inputTransform": t})
        return img
        
    def render_transform_translate(self, layer, img):
        dx = layer._w * layer._scale.x * layer._origin.x
        dy = layer._h * layer._scale.y * (1-layer._origin.y)
        t = NSAffineTransform.transform()
        t.translateXBy_yBy_(layer.x, layer.canvas.h-layer.y)
        t.translateXBy_yBy_(-dx, -dy)
        img = self.filter("CIAffineTransform", img, {"inputTransform": t})
        return img

    def render_crop(self, layer, img):
        if layer._crop != None:
            x, y, w, h = layer._crop
            v = CIVector.vectorWithX_Y_Z_W_(x, layer._h-y-h, w, h)
            img = self.filter("CICrop", img, {"inputRectangle" : v})
            # XXX - we shouldn't adjust width and height here.
            # Also, when the transform queue order changes crop will not behave right
            # (e.g. when first rotating and scaling and then cropping).
            # Also, since we adjust width and height, Canvas.draw() followed by Canvas.export()
            # generates a problem.
            (x,y), (w,h) = img.extent()
            layer._w = w
            layer._h = h
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(-x, -y)
            img = self.filter("CIAffineTransform", img, {"inputTransform": t}) 
        return img   
    
    def render_mask(self, layer, img):
        """ Render the layer mask.
        Returns the layer with its alpha mask applied.
        A mask makes the layer shine through where it is darker.
        """
        mask = None
        if isinstance(layer.mask, Canvas) \
        and len(layer.mask.layers) > 0:
            mask = self.merge(layer.mask)
        if mask != None:
            (x, y), (w, h) = img.extent()
            p = {
                "inputBackgroundImage" : self.image(LAYER_FILL, Transparent(), w, h), 
                "inputMaskImage"       : mask    
            }
            img = self.filter("CIBlendWithMask", img, p)
        return img      

    def render_opacity(self, layer, img, x=None, y=None, w=None, h=None):
        """ Render layer blending.
        Apply its global transparency by blending with a grey mask layer.
        """
        if x == y == w == h == None:
            (x, y), (w, h) = img.extent()
        p = {
            "inputBackgroundImage" : self.image(LAYER_FILL, Transparent(), w, h, x=x, y=y), 
            "inputMaskImage"       : self.image(LAYER_FILL, Color(layer._opacity), w, h, x=x, y=y)
        }
        img = self.filter("CIBlendWithMask", img, p)
        return img
    
    def render_shadow(self, layer, img):
        """ Render the layer's dropshadow.
        Returns a blurred black copy of the layer.
        This method is faster than Canvas._render_shadows() 
        because it does not create a Layer object copy, 
        instead it first renders the layer and copies that CIImage.
        """
        if layer._shadow != None:
            dx, dy, alpha, blur = layer._shadow
            alpha = max(0.0, min(alpha, 1.0))
            blur = max(0.0, min(blur, 100.0))
            p = {
                "inputBrightness" : -1, 
                "inputContrast"   : 0, 
                "inputSaturation" : 0
            }
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(dx, -dy)
            shadow = self.filter("CIColorControls", img, p)
            shadow = self.filter("CIAffineTransform", shadow, {"inputTransform": t})
            (x, y), (w, h) = shadow.extent()
            p = {
                "inputBackgroundImage" : self.image(LAYER_FILL, Transparent(), w, h, x=x, y=y), 
                "inputMaskImage"       : self.image(LAYER_FILL, Color(alpha), w, h, x=x, y=y)
            }
            # Using about half of the actual blur 
            # gives an output identical to Canvas._render_shadows().
            shadow = self.filter("CIBlendWithMask", shadow, p)
            shadow = self.filter("CIGaussianBlur", shadow, {"inputRadius": blur/2})
            return shadow
    
    def render(self, layer, fast=False, crop=True):
        """ Renders a single layer.
        Apply filters, transforms, mask and opacity.
        The actual layer compositing (blending) is done in merge().
        """
        img = self.image(layer.type, layer.data, layer._w, layer._h, layer)
        for action in self.render_queue:
            if action == RENDER_CROP:
                img = self.render_crop(layer, img)
            elif action == RENDER_FILTERS and layer.filters_first():
                img = self.render_filters(layer, img)
            elif action == RENDER_OPACITY:
                img = self.render_opacity(layer, img)
            elif action == RENDER_ADJUSTMENTS:
                img = self.render_adjustments(layer, img)
            elif action == RENDER_MASK:
                img = self.render_mask(layer, img)   
            elif action == RENDER_TRANSFORMS:
                img = self.render_transforms(layer, img)
        if not layer.filters_first():
            img = self.render_filters(layer, img)
        # Put this through an ImageAccumulator.
        # This makes interactive editing with objects returned
        # from Layer.render() significantly faster.
        # You'll notice that the CoreImageRenderer.merge()
        # method accumulates merged layers as well.
        if fast:
            a = CIImageAccumulator.imageAccumulatorWithExtent_format_(img.extent(), self.quality)
            a.setImage_(img)
            img = a.image()
        # Crop to the canvas size.
        # This is important for dynamics, where layers shouldn't grow larger and larger
        # on each iteration, but might be undesirable in other situations.
        if crop:
            v = CIVector.vectorWithX_Y_Z_W_(0, 0, layer.canvas.w, layer.canvas.h)
            img = self.filter("CICrop", img, {"inputRectangle" : v})
        return img
    
    def merge(self, canvas, layers=[], fast=False):
        
        """ Flattens the canvas into a single CIImage.
        
        Composites the layers in the given canvas
        by rendering them individually and then blending them.
        The optional layers list specifies which layers
        from the canvas to render (all by default).
        
        """
        
        if len(layers) == 0:
            layers = canvas.layers
        
        # All of the layers are rendered
        # against a transparent canvas background.
        w = canvas.w
        h = canvas.h
        base = self.image(LAYER_FILL, Transparent(), w, h)

        # Determine which layers to render:
        # hidden layers don't need to be processed.
        # If the layers list is not empty,
        # render only layers that are in it.
        layers_to_render = [layer for layer in layers if not layer.hidden]
        for layer in layers_to_render:
            img = self.render(layer, fast, crop=False) # we'll crop later, after shadow.

            # Render a dropshadow.
            if self.can_render_shadows and layer._shadow != None:
                shadow = self.render_shadow(layer, img)
                base = self.filter("CIMultiplyBlendMode", shadow, {"inputBackgroundImage": base})

            # Always crop the layer to the bounds of the canvas.
            v = CIVector.vectorWithX_Y_Z_W_(0, 0, w, h)
            img = self.filter("CICrop", img, {"inputRectangle" : v})
            
            if layer.blendmode == BLEND_NORMAL:                
                base = self.filter("CISourceOverCompositing", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_LIGHTEN:  
                base = self.filter("CILightenBlendMode", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_DARKEN:  
                base = self.filter("CIDarkenBlendMode", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_MULTIPLY:  
                base = self.filter("CIMultiplyBlendMode", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_SCREEN:  
                base = self.filter("CIScreenBlendMode", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_OVERLAY:  
                base = self.filter("CIOverlayBlendMode", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_SOFTLIGHT:  
                base = self.filter("CISoftLightBlendMode", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_HARDLIGHT:
                base = self.filter("CIHardLightBlendMode", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_DIFFERENCE:
                base = self.filter("CIDifferenceBlendMode", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_HUE:  
                base = self.filter("CIHueBlendMode", img, 
                       parameters={"inputBackgroundImage": base})
            if layer.blendmode == BLEND_COLOR:  
                base = self.filter("CIColorBlendMode", img, 
                       parameters={"inputBackgroundImage": base})

        # The result is one CIImage
        # which contains a flattened image of the layers.
        # Put this through an ImageAccumulator.
        # This is important for performance in interactive scripts
        # that use Core Image (i.e. where you can alter the content
        # of a canvas with the mouse).
        if fast:
            a = CIImageAccumulator.imageAccumulatorWithExtent_format_(base.extent(), self.quality)
            a.setImage_(base)
            base = a.image()

        return base
    
    def draw(self, canvas, x, y, layers=[], fast=False, helper=False):

        """ Draws the flattened image of the canvas to NodeBox.
        
        The output of the canvas is drawn at x and y.
        If the renderer was unable to produce output in NodeBox,
        raises a CanvasToNodeBoxError.
        
        It's very easy to modify this code to have Core Image
        draw somewhere else than in NodeBox: don't append _draw()
        to the NodeBox scenegraph but use update_graphicscontext()
        directly with a flattened canvas to update 
        the NSGraphicsContext.
        
        The resulting image in NodeBox has pixel errors when
        you export it to PDF, likely because it is in RGB and
        contains transparency. When exporting PDf you should
        export a CMYK TIFF and draw that with the NodeBox image() command.
        
        """

        w = canvas.w
        h = canvas.h
        flattened = self.merge(canvas, layers, fast)

        try:
            state = _ctx._transform.copy()
            self._queue.append( (x, y, w, h, flattened, state) )
            _ctx.canvas.append(self)
        except:
            raise CanvasToNodeBoxError

        if helper == True:
            self.helper.rulers(x, y, w, h)
            if layers == []: layers = canvas.layers
            self.helper.guides(x, y, w, h, layers)

    def _draw(self):
        
        # Before drawing into the current graphics context,
        # different transformations need to be applied
        # according to whether transform(CORNER) or
        # transform(CENTER) is used in NodeBox. 
        
        # Grab the canvas render associated with this _draw() call.
        x, y, w, h, flattened, state = self._queue[self._i]
        self._i += 1
        if self._i == len(self._queue): 
            self._i = 0
        
        NSGraphicsContext.currentContext().saveGraphicsState()

        centered = False
        from nodebox.graphics import CENTER
        if _ctx._transformmode == CENTER: 
            centered = True
        if centered:
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(x+w/2, y+h/2)
            t.concat()
        
        # Apply the current NodeBox transform state.
        state.concat()   
        # Flip the image!
        t = NSAffineTransform.transform()
        t.scaleXBy_yBy_(1, -1)
        t.concat()
        if centered:
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(-w/2, -h/2)
            t.concat()
        else:
            t = NSAffineTransform.transform()
            t.translateXBy_yBy_(x, -y-h)
            t.concat()
        
        self.update_graphicscontext(flattened, 0, 0, w, h)
        NSGraphicsContext.currentContext().restoreGraphicsState()

        if self.helper != None:
            self.helper.draw()
    
    def update_graphicscontext(self, img, x, y, w, h):
        # Very sweet: draw the flattened CIImage in a CIContext
        # from the current context to take full advantage of Core Image.
        ctx = NSGraphicsContext.currentContext().CIContext()
        ctx.drawImage_atPoint_fromRect_(img, (x,y), ((0,0),(w,h)))
    
    def export(self, canvas, name, type=FILE_PNG, compression=None, cmyk=False, layers=[]):
        
        """ Exports a flattened composition as a file.
        
        Merges all of the layers and export that image to file.
        You can choose between a FILE_GIF,
        a FILE_PNG with transparent background,
        a FILE_JPEG with white background and (optional) compression,
        a FILE_TIFF with transparent background and(optional) LZW-compression.
        
        When exporting to TIFF you can choose to convert it to CMYK.
        Currently LZW is not supported for CMYK TIFF.
        
        """
        
        w = canvas.w
        h = canvas.h
        flattened = self.merge(canvas, layers)

        # Draw the CIImage in a bitmap context
        # from which we can then extract file data.
        # This is where the memory leak occurs.
        alpha, colorspace = True, NSDeviceRGBColorSpace
        if cmyk == True:
            alpha, colorspace = False, NSDeviceCMYKColorSpace
        img = NSBitmapImageRep.alloc()
        img.initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
            None, w, h, 8, 4, alpha, False, colorspace, 0, 0
        )
        ctx = NSGraphicsContext.graphicsContextWithBitmapImageRep_(img)
        ctx = ctx.CIContext()
        ctx.drawImage_atPoint_fromRect_(flattened, (0,0), ((0,0),(w,h)))
                
        options = None
        if type == FILE_GIF:
            type = NSGIFFileType
        if type == FILE_PNG:
            type = NSPNGFileType
        if type == FILE_JPEG:
            type = NSJPEGFileType
            if isinstance(compression, float):
                options = {NSImageCompressionFactor: max(0.0, min(compression, 1.0))}
        if type == FILE_TIFF:
            type = NSTIFFFileType
            if compression == True:
                options = {NSImageCompressionMethod:NSTIFFCompressionLZW}
        
        data = img.representationUsingType_properties_(type, options)
        f = open(name, "w")
        f.write(data.bytes())
        f.close()

### COREIMAGEPIXELS ##################################################################################

import numpy
class CoreImagePixels:
    
    def __init__(self, renderer, layer, img):
        """ The Pixels class provides pixel-based information for CIImage objects.
        Creates a pixel array for a CIImage object, using NumPy for faster array processing.
        The pixels values are assumed to be RGB and range between 0 and 255.
        Acquiring pixel information may take some time to process.
        """
        self.renderer = renderer
        self.layer = layer
        (self.x, self.y), (self.w, self.h) = img.extent()
        self.width = self.w = int(self.w)
        self.height = self.h = int(self.h)
        # Set y to the top of the bounding box and not the bottom.
        self.y = layer.canvas.h - self.y - self.h
        # Render the CIImage.
        self._img = NSImage.alloc().initWithSize_((self.w, self.h))
        self._img.addRepresentation_(NSCIImageRep.imageRepWithCIImage_(img))
        self._img = self._img.TIFFRepresentation()
        self._img = NSBitmapImageRep.imageRepWithData_(self._img)
        self.channels = self._img.samplesPerPixel()

    def is_rgb(self):
        return self._img.colorSpaceName().find("RGB") >= 0
    
    def has_alpha(self):
        return (self._img.hasAlpha() == 1)
        
    def get_pixel(self, x, y):
        """ Returns color for the pixel at x, y.
        """
        if 0 <= x < self.w and \
           0 <= y < self.h:
            return _ctx.color(self._img.colorAtX_y_(x, y))
            
    def get_range(self, x, y, w, h):
        """ Returns a list of pixels colors inside the given box.
        """
        r = []
        for j in range(h):
            for i in range(w):
                clr = self.get_pixel(x+i, y+j)
                if clr != None:
                    r.append(clr)        
        return r
        
    def set_pixel(self, x, y, clr):
        """ Sets the pixel at x, y with the given color.
        """
        if 0 <= x < self.w and \
           0 <= y < self.h:        
            self._img.setColor_atX_y_(clr._rgb, x, y)

    def update(self):
        """ Updates the layer with the changes from set_pixel().
        """
        self.layer.data = self._img.TIFFRepresentation()
        self.layer.type = LAYER_NSIMAGEDATA

    def __len__(self):
        return self.w * self.h
    def __getitem__(self, i):
        if i<0: i = len(self) + i
        return self.get_pixel(i%self.w, i/self.w)
    def __setitem__(self, i, clr): 
        if i<0: i = len(self) + i
        self.set_pixel(i%self.w, i/self.w, clr)
    def __getslice__(self, i, j):
        return [self[k] for k in range(i,j)]
    def __call__(self, i, j):
        return self.get_pixel(i, j)

    def _array(self, int=8):
        """ All the pixel color values as a lists of integers.
        """
        bytes = self._img.bitmapData()
        a = numpy.fromstring(bytes, numpy.uint8)
        a = numpy.reshape(a, (self.w*self.h, self.channels))
        if int == 32:
            a = a.astype(numpy.uint32)
        # r = a[:,0]
        # g = a[:,1]
        # b = a[:,2]
        # a = a[:,3]
        return a
    
    def min(self, transparency=False, threshold=0):
        """ Returns the lowest color values in the image.
        By default, transparent pixels (alpha=0) are not searched. 
        The threshold defines the cutoff, for example threshold=0.1 
        means that all pixels with alpha less than 10% are not taken into account.
        """
        if isinstance(threshold, float): 
            threshold *= 255
        a = self._array(int=32)
        if transparency == False and self.has_alpha():
            # Find the indices of all pixels whose alpha is greater than given threshold.
            # Take only the pixels at those indices.
            i = numpy.greater(a[:,3], threshold).astype(numpy.int).nonzero()[0]
            a = numpy.take(a, i, axis=0)            
        i = numpy.argmin(a, 0)
        v = []
        for j in range(self.channels):
            v.append(a[i[j]][j])
        # Return a color object:
        clr = _ctx.color(0)
        clr.r, clr.g, clr.b = v[0]/255.0, v[1]/255.0, v[2]/255.0
        if self.has_alpha(): 
            clr.a = v[3]/255.0
        return clr
    
    def max(self, transparency=False, threshold=0):
        """ Returns the highest color values in the image.
        """
        if isinstance(threshold, int): 
            threshold /= 255.0
        a = self._array(int=32)
        if transparency == False and self.has_alpha():
            i = numpy.greater(a[:,3], threshold).astype(numpy.int).nonzero()[0]
            a = numpy.take(a, i, axis=0)
        i = numpy.argmax(a, 0)
        v = []
        for j in range(self.channels):
            v.append(a[i[j]][j])
        # Return a color object:
        clr = _ctx.color(0)
        clr.r, clr.g, clr.b = v[0]/255.0, v[1]/255.0, v[2]/255.0
        if self.has_alpha(): 
            clr.a = v[3]/255.0
        return clr
        
    def average(self, transparency=False, threshold=0):
        """ Returns the average color values in the image.
        """
        a = self._array(int=32)
        n = len(a)
        if isinstance(threshold, int): 
            threshold /= 255.0
        if transparency == False and self.has_alpha():
            i = numpy.greater(a[:,3], threshold).astype(numpy.int).nonzero()[0]
            a = numpy.take(a, i, axis=0)
            n = len(i)
        a = sum(a) / float(n)
        v = []
        for i in range(self.channels):
            v.append(int(a[i]))
        # Return a color object:
        clr = _ctx.color(0)
        clr.r, clr.g, clr.b = v[0]/255.0, v[1]/255.0, v[2]/255.0
        if self.has_alpha(): 
            clr.a = v[3]/255.0
        return clr
        
    def histogram(self, channel=None, helper=False):
        """ Computes a histogram for the image.
        A histogram is a list for each color channel.
        Each color list has indices from 0 to 255,
        and lists the occurence of each of those color values
        as a percentage between 0.0 and 1.0
        """
        a = self._array()
        bins = numpy.arange(1, 255, 1)
        v = []
        for i in range(self.channels):
            p = a[:,i]
            # From the NumPy searchsorted() documentation.
            n = numpy.searchsorted(numpy.sort(p), bins)
            n = numpy.concatenate([n, [len(p)]])
            n = n[1:]-n[:-1]
            # Make the values in the histogram percentual
            # by dividing each by the highest.
            n = n.astype(numpy.float)
            n = n / n[numpy.argmax(n)]
            v.append(n)
        if helper == True and self.renderer.helper != None:
            self.renderer.helper.histogram(v, self.layer.x, self.layer.y)
        return v

### COREIMAGEHELPER ##################################################################################

class CoreImageHelper:
    
    """ Provides visual feedback in NodeBox on certain filters.
    
    Usually the helper is only useful when the layer is
    transformed by that single filter. If you furthermore
    transform and filter the layer the helper will not
    display at the correct position.
    
    Invoking a helper is usually as simple as setting
    the helper=True in the filter parameters.
    
    """
    
    def __init__(self, renderer):
    
        self.renderer = renderer
        self.background = (0.0, 0.0, 0.0, 0.6)
        self.foreground = (1.0, 1.0, 1.0, 0.6)
        self.roundness = 0.1
        self.font = "Arial"
        self.fontsize = 8.5
        
        self._stack = {}
        self._i = 1
    
    def interface(self, filter):
        
        """ Interfaces parameters for the filter to NodeBox sliders.
        """
        
        from nodebox.graphics import BOOLEAN, NUMBER
        
        vars = {}
 
        # Use the short alias as display name
        # and provide a render yes/no checkbox.
        name = filter
        for alias in self.renderer.aliases:
            if self.renderer.aliases[alias] == filter:
                name = alias     
                break
        name = str(self._i) + "_" +  name
        _ctx.var(name, BOOLEAN, True)
        try: vars["render"] = _ctx.findvar(name).value
        except: vars["render"] = True
        
        # For each parameter,
        # find the defaults in the corresponding CIFilter.
        f = CIFilter.filterWithName_(filter)
        a = f.attributes().items()
        for param in self.renderer.filters[filter]:
            
            n = param + "_" + str(self._i)
            value = self.renderer.filters[filter][param]
            vars[param] = value
 
            if param == "helper":
                _ctx.var(n, BOOLEAN, False)
                try: vars[param] = _ctx.findvar(n).value
                except: vars[param] = False
            
            if isinstance(value, (int, float)) \
            and param != "interface" \
            and param != "helper":
                min = -600.0
                max =  600.0
                if param == "dx" or param == "dy":
                    min = -1000
                    max =  1000
                elif param in "rgba":
                    min = 0.0
                    max = 1.0
                else:  
                    for key, attr in a:
                        if key.lower().find(param) >= 0:
                            min = attr['CIAttributeSliderMin']
                            max = attr['CIAttributeSliderMax']
                            if  param == "angle" \
                            or (param == "tilt" and name == "CIParallelogramTile"):
                                min = min / 3.14 * 360
                                max = max / 3.14 * 360
                            break
                
                _ctx.var(n, NUMBER, value, min, max)
                try: vars[param] = _ctx.findvar(n).value
                except: vars[param] = value
        
        self._i += 1 
        return vars

    def draw(self):
        """ Draws all the defined helpers.
        This command is called from the renderer
        once the merged canvas has been drawn in NodeBox.
        """
        if isinstance(self.background, tuple):
            r,g,b,a = self.background
            self.background = _ctx.color(r,g,b,a)
            r,g,b,a = self.foreground
            self.foreground = _ctx.color(r,g,b,a)
        for f in self._stack:
            args = self._stack[f]
            f = getattr(self, "_"+f)
            f(args)    
        self._stack = {}
    
    def rulers(self, x, y, w, h):
        """ Helper that draws canvas rulers.
        """
        self._stack["rulers"] = (x, y, w, h)
    
    def _rulers(self, args):
        x, y, w, h = args
        rw = 3 * 10
        _ctx.nostroke()
        _ctx.fill(self.background)
        _ctx.rect(x, y, rw, h)
        _ctx.rect(x+rw, y, w-rw, rw)
        _ctx.fill(self.foreground)
        _ctx.stroke(self.foreground)
        _ctx.strokewidth(0.5)
        _ctx.font(self.font, self.fontsize)
        d = 10
        n = (h-rw)/d
        for i in range(n):
            if (i+3) % 5 == 0:
                _ctx.text(str((i+3)*d), x+2, rw+i*d-2)
                _ctx.stroke(1.0)
            _ctx.line(x, rw+i*d, x+rw, rw+i*d)
            _ctx.stroke(self.foreground)
        n = (w-rw)/d
        for i in range(n):
            if (i+3) % 5 == 0:
                _ctx.stroke(1.0)
            _ctx.line(rw+i*d, y, rw+i*d, y+rw)
            _ctx.stroke(self.foreground)
    
    def guides(self, x, y, w, h, layers):
        """ Helper that draws layer bounds and origin.
        """
        self._stack["guides"] = (x, y, w, h, layers)
            
    def _guides(self, args):
        x, y, w, h, layers = args
        for layer in layers:
            if layer.hidden: 
                continue
            l, t, r, b = layer.bounds()
            _ctx.nofill()
            _ctx.stroke(self.foreground)
            _ctx.strokewidth(0.5)
            _ctx.rect(l, t, r-l, b-t)
            r = 10
            _ctx.fill(self.background)
            _ctx.oval(layer.x-r/2, layer.y-r/2, r, r)
            _ctx.line(layer.x, y, layer.x, h)
            _ctx.line(x, layer.y, w, layer.y)
    
    def histogram(self, h, x, y):
        """ Helper for the Layer.pixels().histogram command.
        """
        self._stack["histogram"] = (h, x, y)
        
    def _histogram(self, args):
        h, x, y = args
        x += 5
        y += 5
        dh = 30
        dw = 0.5
        _ctx.nostroke()
        _ctx.fill(self.background)
        _ctx.rect(x, y, 30+255*dw, 20+len(h)*(dh+10), roundness=self.roundness)
        x += 15
        y += 15
        for channel in h:
            _ctx.stroke(self.foreground)
            _ctx.strokewidth(0.75)
            _ctx.line(x, y+dh, x+255*dw, y+dh)
            for i in range(len(channel)):
                _ctx.line(x+i*dw, y+dh, x+i*dw, y+dh-channel[i]*dh)
            y += dh+10
            
    def spotlight(self, layer, w, h, dx0, dy0, dz0, dx1, dy1, dz1, brightness, concentration):
        """ Helper for the Layer.filter(name="lighting") command.
        """
        self._stack["spotlight"] = (layer, w, h, dx0, dy0, dz0, dx1, dy1, dz1, brightness, concentration) 

    def _spotlight(self, args):
        
        layer, w, h, dx0, dy0, dz0, dx1, dy1, dz1, brightness, concentration = args
        l, t, r, b = layer.bounds()
        
        from nodebox.graphics import CORNER, CENTER
        
        # Draw the helper relative to
        # the layer's position.
        # Layer scaling, rotation, etc. are not processed.
        dx0 += l+(r-l)/2
        dy0 -= t+(b-t)/2
        dx1 += l+(r-l)/2
        dy1 -= t+(b-t)/2
        _ctx.stroke(self.foreground)
        _ctx.strokewidth(0.5)
        _ctx.fill(self.background)
        
        # Spotlight position
        r = 20
        vx0 = dx0
        vy0 = h - dy0
        _ctx.oval(vx0-r/2, vy0-r/2, r, r)
        _ctx.fill(self.background)
        f = _ctx.fill()
        f.a /= 2
        _ctx.fill(f)
        r = 10
        vx1 = dx1
        vy1 = h - dy1
 
        # Light concentration radius
        dr = concentration*8000 * (1+0.025/concentration)
        _ctx.oval(vx1-dr/2, vy1-dr/2, dr, dr)
        
        # Light direction
        _ctx.oval(vx1-r/2, vy1-r/2, r, r)
        _ctx.line(vx0, vy0, vx1, vy1)    

        # Light spread based on source height.
        spread = 10 + dz0/10
        a = self._angle(vx0, vy0, vx1, vy1)
        n = self._distance(vx0, vy0, vx1, vy1) + dz0
        _ctx.transform(CORNER)
        _ctx.push()
        _ctx.translate(vx0, vy0)
        _ctx.rotate(a-spread)
        _ctx.line(0, 0, n, 0)
        _ctx.pop()
        _ctx.push()
        _ctx.translate(vx0, vy0)
        _ctx.rotate(a+spread)
        _ctx.line(0, 0, n, 0)
        _ctx.pop()  
        _ctx.transform(CENTER)

    def _distance(self, x0, y0, x1, y1):
        return sqrt(pow(x1-x0, 2) + pow(y1-y0, 2))
        
    def _angle(self, x0, y0, x1, y1):
        a = degrees( atan((y1-y0) / (x1-x0+0.00001)) ) + 360
        if x1-x0 < 0: a += 180
        return 360 - a
    
#### TESTS ##########################################################################################

def test_transformstate():

    from nodebox.graphics import CORNER, CENTER

    c = canvas(400, 400)
    c.layer_linear_gradient(color(1.0, 0, 0))
    c.draw(10, 10)

    _ctx.push()
    _ctx.transform(CENTER)
    _ctx.scale(0.5)
    _ctx.translate(100, 100)
    _ctx.rotate(45)

    x = 25
    y = 25

    c.draw(x,y)

    _ctx.fill(0, 0, 0.5, 0.5)
    _ctx.rect(x, y, 400, 400)
    _ctx.pop()
    _ctx.translate(50, 50)
    _ctx.oval(0, 0, 10, 10)
 
def test_multipledraws():
    
    c = canvas(100,100)
    l = c.layer(choice(files("images/*.jpg")))

    p = l.pixels()
    if p.has_alpha():
        r, g, b, a = p.average()
    else:
        r, g, b = p.average()

    _ctx.colormode(RGB, 255)
    _ctx.fill(r, g, b)
    _ctx.rect(0, 0, 400, 400)

    l.filter_twirl(angle=400)
    l.filter_holedistortion(radius=25)

    from nodebox.graphics import grid
    for x, y in grid(4, 4, 100, 100):
        l.filter_twirl(angle=x+y*5)
        c.draw(x, y)
        
def test_interface():
    c = canvas(400, 400)
    for i in range(2):
        l = c.layer(files("images/*.jpg")[0])
        l.x +=  i*200
        l.filter_kaleidoscope(interface=True)
        l.filter_twirl(interface=True)
    c.draw()

# 1.9.5
# Numeric calls have been replaced with numpy calls.
# Fixed float("inf").

# 1.9.4.7
# Improved optional color parameters for layer from path.

# 1.9.4.6
# Added histogram and average reduction filters (undocumented).
# layer.pixels() now has a crop=False (so pixels outside the canvas are processed as well).
# The spread parameter for gradients only works when type="radial"
# (previously a linear gradient with a spread would revert to radial).

# 1.9.4.5
# Added difference blend mode.

# 1.9.4.4
# Bug fixes for CoreImagePixels.

# 1.9.4.3
# crop=True parameter for Layer.render()
# Layer.origin() works with absolute values.
# Issues with layer transparency on Mac OS X 10.5 still need fixing.

# 1.9.4.2
# Added noise reduction filter.
# Added 10.5 filters: bump distortion linear, parallelogram tile, line overlay.
# Core Graphics is no longer imported (proprietary to MacPython 2.3 and NodeBox runs 2.5).
# CMYK export without using Core Graphics.
# Fixes for opacity in generator filters (checkerboard, starshine).
# Adjustments to Layer.bounds() for cropping.

# 1.9.4.1
# Fixed color bug when duplicating path layers.

# 1.9.4
# Added list slice method to Canvas.
# Added dotscreen filter.

# 1.9.3
# Added edges filter.

# 1.9.2.1
# Improved Canvas.layer() + it has a Canvas.append() alias.
# Added Canvas.append(layer) functionality.
# Various improvements and fixes for Layer.render().
# Canvas acts as a list reflecting the contents of Canvas.layers.
# Added crop to Layer.
# Added center() to Layer.
# Added dropshadow() to Layer.
# Layer.index is now a property instead of a method.
# Layer adjustments are accessible as properties.
# Layer.blend("darken") should be documented.
# Added get_range() to CoreImagePixels + it now behaves as a list.
# Improved page curl filter.
# Added pixelate, crystallize, circular, checkerboard, circlesplash wrap filters.
# Added Renderer.render_queue defining the order of layer rendering actions.

# 1.9.2
# Added layers_pixels() to Canvas.
# Added set_pixel() to CoreImagePixels.
# All of the CoreImagePixels methods, except histogram(),
# now use color() objects instead of lists of R,G,B values.

# 1.9.0
# Layers from bytes (e.g. download stream) can be created with Canvas.layer_bytes().

# 1.9.0
# Compliant with NodeBox 1.9.0 - we now use nodebox.graphics instead of DrawingPrimitives.
# Layers can be created from NSImage object.
# This way Core Image can handle frames from QTMovie.

# 1.8.5.3
# Added page curl filter.
# Layers from paths now ignore the BezierPath's x and y position.

# 1.8.5.2
# export() no longer uses TIFFRepresentation but draws in a CIContext().
# However, the problem remains: both leak memory.
# CoreGraphics is imported in try/except block.
    
# 1.8.5.1
# render_opacity() uses CIBlendWithMask instead of CIColorMatrix.
# Opacity is always rendered first, avoiding artefacts in output on Intel machines.

# 1.8.5
# Added filter_triangletile()
# Pixel map has x, y, w, h properties.
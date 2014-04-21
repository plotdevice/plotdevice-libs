# The Membrane example.
# This example uses Core Image Dynamics
# to stack layer manipulations in a real-time animation.

size(350,350)
speed(50)

try: 
    coreimage = ximport("coreimage")
except:
    coreimage = ximport("__init__")
    reload(coreimage)

def setup():
    
    global img, cache
    img = choice(files("images/*.jpg"))
    cache = img

def draw():
    
    global img, cache
    
    canvas = coreimage.canvas(WIDTH, HEIGHT)
    
    # The bottom layer is the unmodified image.
    l = canvas.append(img)
    l.mask.radial()
    
    # On top is the image again, but filtered.
    # Each frame we apply filters and then cache it.
    # So next frame the layer is made up of the filtered image,
    # then we add new filters to it, cache it, and so on.
    l = canvas.append(cache)
    l.rotate(1)
    l.blend(97)
    l.scale(1.01)
    
    # Bulge the layer outward randomly.
    x = random(WIDTH)/2-100
    y = random(HEIGHT)/2-100
    l.filter("bumpdistortion", dx=x, dy=y, radius=20, scale=2.0)
    
    # Punch random holes in it.
    x = random(WIDTH)/2-100
    y = random(HEIGHT)/2-100
    l.filter("holedistortion", dx=x, dy=y, radius=20+random(10))    
    
    # Store a screenshot of the canvas in cache.
    cache = canvas.flatten()   

    # When the mouse is pressed,
    # bulge the center.
    if mousedown:        
        dx = MOUSEX - l.x - 50
        dy = MOUSEY - l.y - 50       
        l.filter("bumpdistortion", radius=150, scale=1.0)
        cache = canvas.flatten()
    
    l = canvas.append(color(1,0.75,0.5))
    l.blend(50, "hue")

    canvas.draw()
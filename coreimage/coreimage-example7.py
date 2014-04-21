# Interactive eraser.

size(500, 400)

try: 
    coreimage = ximport("coreimage")
except:
    coreimage = ximport("__init__")
    reload(coreimage)

img = "images/France_414.jpg"

m = None # The image's alpha mask we'll be editing
r = 50   # Radius of the eraser.
a = 0.5  # Alpha transparency of the eraser.

speed(40)
def draw():
    
    background(None)
    global img, m, r
    
    canvas = coreimage.canvas(WIDTH, HEIGHT)
    l = canvas.append(img)
    
    if not m:
        # If we haven't yet created an image mask which we can update,
        # do so now. The mask is initially a white rectangle,
        # meaning that all underlying pixels from the image will show.
        m = l.mask.append(color(1))
    else:
        # If we have a mask from a previous frame, use that.
        m = l.mask.append(m)
    
    # The eraser oval.
    p = oval(0, 0, r, r)
    if mousedown:
        # If the mouse is pressed, add a new layer to the image mask.
        # This new layer contains the eraser oval in black,
        # so pixels at this location will be hidden.
        erase = l.mask.append(p, fill=color(0,0,0,a))
        # Get the relative position in the mask right.
        # The mask may be bigger than the canvas or the screen.
        w, h = erase.size()
        erase.x = (w-WIDTH)/2 + MOUSEX
        erase.y = (h-HEIGHT)/2 + MOUSEY
        erase.scale(0.8)
        # The blurriness of the eraser.
        erase.blur = 10
    
    # Each frame, all of the layers in the mask are "rendered".
    # This is the same as flattening a set of layers in Photoshop.
    # We'll use this flattened mask in the next frame.
    m = l.mask.render()
    canvas.draw()
    
    # Show the eraser.
    nofill()
    stroke(0,1,0)
    translate(MOUSEX-r/2, MOUSEY-r/2)
    drawpath(p)
    
    
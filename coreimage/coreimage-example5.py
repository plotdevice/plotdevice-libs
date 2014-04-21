# Coffee dynamics.

try: 
    coreimage = ximport("coreimage")
except:
    coreimage = ximport("__init__")
    reload(coreimage)

size(500, 500)
speed(30)
def setup():
    
    global copy, a, x, y
    copy = None
    a = 0
    x = 0
    y = 0

def draw():
    
    global copy, a, x, y
    
    # A canvas of layers with the same size as the NodeBox window.
    canvas = coreimage.canvas(WIDTH, HEIGHT)
    
    # The bottom layer is a brownish fill color.
    l = canvas.append(color(0.07,0.05,0))

    if not copy:
        # During the first frame,
        # construct a layer from an outlined text path.
        fontsize(100)
        p = textpath("COFFEE", 0, 50)
        copy = canvas.append(p, fill=color(1,1,0.95))
    else:
        # During the next frames of the animation,
        # take a screenshot of the text layer.
        copy = copy.render()
        copy = canvas.append(copy)

    # Each frame, apply some twirl filters to the text layer.
    # Give them a random radius.
    copy.filter("twirl", dx=x, dy=y, radius=random(50,100), angle=a)
    copy.filter("twirl", dx=-x, dy=-y, radius=random(50,100), angle=-a/2)
    
    # After applying the twirl effects,
    # apply hole distortions at random locations near the twirl.
    # The results is something resembling smoke rings.
    copy.filter("holedistortion", radius=random(5,10), dx=x+random(-10,10))
    copy.filter("holedistortion", radius=random(0,5), dx=x+random(-10,10))

    # This variable controls the angle of the twirl effects.
    # Each frame, increase or decrease it a  bit.
    a += random(-5.0, 5.0)
    a = max(-50, min(a, 50))
    
    x += random(-10.0, 10.0)
    y += random(-10.0, 10.0)

    canvas.draw()
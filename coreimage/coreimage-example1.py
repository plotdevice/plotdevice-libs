# The Twisted World example
# http://nodebox.net/code/index.php/Twisted_world

size(800, 500)

# Import the library
try: 
    # This is the statement you normally use.
    coreimage = ximport("coreimage")
except:
    # But since these examples are "inside" the library
    # we may need to try something different when
    # the library is not located in /Application Support
    coreimage = ximport("__init__")
    reload(coreimage)

# Draw a dark grey background
background(0.1)

# Create a 800x500 canvas to hold layers.
canvas = coreimage.canvas(WIDTH, HEIGHT)

# Create 20 random layers.
# Remember, it may take a few seconds to load
# all the images during the first run.
for i in range(20):
    img = choice(files("images/*.jpg"))
    l = canvas.append(img)
    
    # Give each layer a gradient mask.
    l.mask.gradient(type="radial")
    
    # Put it at a random location on the canvas.
    l.x = random(canvas.w)
    l.y = random(canvas.h)
    
    # Maybe flip it,
    # some random rotation and scaling.
    l.flip(horizontal=choice((True,False)))
    l.rotate(random(360))
    l.scale(random(1.0,2.0))
    
    # Randomly apply kaleidoscopic, twirl and bump effects.
    if random() > 0.75:
        l.filter("kaleidoscope")
    if random() > 0.25:
        l.filter("twirl")
    if random() > 0.25:
        l.filter("bumpdistortion")

# Put a central image on top of the mess.
#img = choice(files("images/*.jpg"))
#l = canvas.layer(img)
#l.mask.layer_radial_gradient()

# Add a orange fill color that hues
# all the layers below.
l = canvas.append(color(1.0,0.5,0))
l.blend(50, "hue")

# Put all the layers as a group in a second canvas, 
# then adjust the contrast of the group.
c2 = coreimage.canvas(800, 500)
l = c2.append(canvas)
l.contrast = 1.1

# Draw to NodeBox!
c2.draw()
# The Twisted World example,
# with random images from MorgueFile
# http://nodebox.net/code/index.php/Twisted_world

# What images are we looking for?
query = "insect"

# Import the Core Image library
try: 
    coreimage = ximport("coreimage")
except:
    coreimage = ximport("__init__")
    reload(coreimage)

# Import the MorgueFile library
try: 
    from coreimage import morguefile
except:
    morguefile = ximport("morguefile")

from random import shuffle

# Download some images from morguefile.com
# The script will create a folder and put
# the downloaded images in it.
# Next time we will take images from this folder
# instead of downloading them again.
if len(files("images/"+ query+"/*")) == 0:
    images = morguefile.query(query, max=30)
    shuffle(images)
    for img in images[:5]:
        img.download("images/"+query+"/")

# Draw a dark grey background
fill(0.1)
rect(0,0,WIDTH,HEIGHT)

# Create a 800x500 canvas to hold layers.
canvas = coreimage.canvas(800, 500)

# Create 20 random layers.
# Remember, it may take a few seconds to load
# all the images during the first run.
for i in range(20):
    img = choice(files("images/"+ query+"/*"))
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
#img = choice(files("images/"+ query+"/*"))
#l = canvas.layer(img)
#l.mask.layer_radial_gradient()

# Add a fill color that hues
# all the layers below.
l = canvas.append(color(random(), random(), random()))
l.blend(50)
l.blend_hue()

# Put all the layers as a group in a second canvas, 
# then adjust the contrast of the group.
c2 = coreimage.canvas(800, 500)
l = c2.append(canvas)
l.contrast = 1.1

# Draw to NodeBox!
c2.draw()
# The Geospheres example.

size(600, 800)

try: 
    coreimage = ximport("coreimage")
except:
    coreimage = ximport("__init__")
    reload(coreimage)
    
c = coreimage.canvas(WIDTH, HEIGHT)

# Create a black background.
l = c.append(color(0))

# Create an image layer with a radial mask.
# Use the first image in the image folder.
l = c.layer(files("images/*.jpg")[0])
l.mask.gradient(type="radial", spread=0.5)
l.y -= 120

# Scale to fit to the canvas.
l.scale(1.0)

# Change this number to vertically rotate our sphere.
d = 0

# Transform the layer to an interesting geometric pattern.
# Play around with the parameters for different effects.
l.filter("triangletile", dx=random(0,40), width=-140, dy=random(180), angle=57.2+random(0.4))
l.filter("kaleidoscope", dy=93-d, count=10)

# Bulge the top of the layer outward.
# This creates the illusion of a sphere.
l.filter("bumpdistortion", scale=0.66, radius=379, dy=-55+d/2, dx=1)

# Use some lighting at the top of the sphere to enhance the effect.
l.filter("lighting", dx1=-88, dy1=58, dx0=-53, dy0=544, dz0=565, helper=False)

c.draw()


# Some fun converting pixels to curves.
# Uncomment the code below to grow hair on a sphere.
'''
l.contrast = 1.1

p = l.pixels()

nofill()
strokewidth(0.25)
autoclosepath(False)

# This is the bounding box of the pixel region.
print p.x, p.y, p.w, p.h

# Traverse each pixel.
for i in range(p.w):
    for j in range(p.h):
        
        # Process about half of them,
        # more requires to much processing and clogs the image.
        if random() > 0.5:
            clr = p.get_pixel(i,j)
            
            # We don't draw curves on black pixels.
            if not (clr.r == clr.g == clr.b == 0):
                
                # The actual location of the curve
                # is at the pixel's index in the pixel map
                # plus the left top corner of the pixel map.
                x = i + p.x
                y = j + p.y
                
                # Curve away from the center.
                dx = x-l.x
                dy = y-l.y
                dh = 20

                stroke(clr)
                beginpath(x, y)
                curveto(x+random(dh),
                        y+random(dh),
                        x-random(dh),
                        y-random(dh),
                        x+random(dx/3), 
                        y+random(dy/3))
                path = endpath()
                
                # For pixels in the lower half of the image,
                # curve downwards in a stem.
                if (random() > 0.92 and y > l.y):
                    beginpath(x, y)
                    curveto(x+dx,
                            y+dy,
                            WIDTH/2-random(dx*2),
                            HEIGHT,
                            WIDTH/2,
                            HEIGHT)
                    path = endpath()                    
'''
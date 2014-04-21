# A drawing example for the WiiMote.
# This example doesn't use classes, to keep it simple to follow.

# INSTRUCTIONS:
# Keep the Wii Remote straight up (like a torch).
# You control the speed, not the position, of the cursor.
# Hold the A button to draw.

from math import sin, cos

# Import the library
try:
    # This is the statement you normally use.
    wiinode = ximport("wiinode")
except ImportError:
    # But since these examples are "inside" the library
    # we may need to try something different when
    # the library is not located in /Application Support
    wiinode = ximport("__init__")
    reload(wiinode)

size(600,400)
speed(30)

class Turtle:
    """Remembers the position of the cursor."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0

def setup():
    global wm, turtle, trails_list, current_trail
    wm = wiinode.WiiMote()
    # We represent the lines on screen as a list of a list of points.
    trails_list = []
    # The current trail is what we're drawing right now.
    current_trail = []
    # Put the turtle in the center.
    turtle = Turtle(WIDTH/2, HEIGHT/2)

def draw():
    global wm, turtle, trails_list, current_trail
    background(0)
    wm.update()

    # Displays debug text.
    #fontsize(12)    
    #text("x: %.2f y: %.2f, z: %.2f" % (wm.x, wm.y, wm.z), 5, HEIGHT-5)
    #text("p: %.2f r: %.2f, y: %.2f, a:%.2f" % (wm.pitch, wm.roll, wm.yaw, wm.accel), 5, HEIGHT-24)    
    
    # Update the turtle. You can play around with these values to get another "feel".
    turtle.vx = (wm.yaw-0.5) * 30.0
    turtle.x += turtle.vx
    # Keep the turtle on screen
    turtle.x = max(min(turtle.x, WIDTH), 0)
    turtle.vy = (0.5-wm.z) * 100.0
    if turtle.vy > 0.0: turtle.vy *= 2.0 # Backwards needs to be faster
    turtle.y += turtle.vy
    # Keep the turtle on screen
    turtle.y = max(min(turtle.y, HEIGHT), 0)    
    
    # If the A button is pressed, we append our new position to the current trail.
    if wm.a:
        current_trail.append((turtle.x, turtle.y))
    else:
        # If the button is not pressed, we append the current trail to the new list.
        # This should only happen once, so we check if we there is something in the
        # current trail.
        if len(current_trail) > 0:
            trails_list.append(current_trail)
        current_trail = []
    
    # Here, we play around with the current trails, to give them a bit of animation.
    new_trails = list(trails_list)
    new_trails.append(current_trail)
    for t in new_trails:
        t = list(t)
        # Do I *really* have to explain this?
        t = [(x+sin(FRAME/10.0+i/3.0)*15.0, y+cos(FRAME/10.0+i/3.0)*15.0) for i, (x, y) in enumerate(t)]
        drawpath(t, fill=None, stroke=1, strokewidth=10)

    # Draw the current trail as a small line to show what we're doing.
    drawpath(current_trail, fill=None, stroke=(1,0.5), strokewidth=1.0)
    
    # Change the size of the turtle based on the acceleration of the WiiMote.
    # Totally useless, but maybe a nice effect.
    sz = wm.accel * 40.0
    # Draw the turtle. The fill color uses the wm.a value to give a different color
    # when the button is pushed.
    oval(turtle.x-sz, turtle.y-sz, sz*2, sz*2, fill=(wm.a, wm.a, 1))

def stop():
    wm.stop()
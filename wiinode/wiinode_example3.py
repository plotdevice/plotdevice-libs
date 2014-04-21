# A WiiMote visualizer. This shows all the captured inputs;
# useful for developing your own scripts.

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

size(550, 320)
speed(30)

##################################################
# Controls
# Display functions for visualizing WiiMote values.
# WiiMote values fall between 0.0 and 1.0.
##################################################

def gauge(txt, x, y, v):
    text(txt, x, y)
    h = 30.0
    rect(x+50, y, 10, -h, fill=1)
    rect(x+50, y, 10, -h*v, fill=(1,0,0), stroke=0, strokewidth=0.2)
    rect(x+50, y, 10, -h, fill=None, stroke=0)
    text("%.3f" % v, x+50, y+10, fontsize=9)
    
def rotor(txt, x, y, v):
    text(txt, x, y)
    push()
    translate(55, -10)
    rotate((1.0-v)*180)
    scale(0.21)
    arrow(x+50, y)
    pop()
    text("%.3f" % v, x+50, y+10, fontsize=9)
    
def button(txt, x, y, sel):
    rect(x-4, y-40, 41, 45, fill=(sel, 0,0))
    text(txt, x, y)
    
def setup():
    pass
    global wm
    wm = wiinode.WiiMote()

def draw():
    global wm
    wm.update()

    font("Helvetica", 48)
    fill(1)

    rect(50, 50, WIDTH-100, HEIGHT-100, fill=0.2, roundness=0.1)
    gauge("X", 100, 100, wm.x)
    gauge("Y", 200, 100, wm.y)
    gauge("Z", 300, 100, wm.z)
    
    rotor("P", 100, 170, wm.pitch)
    rotor("R", 200, 170, wm.roll)
    rotor("Y", 300, 170, wm.yaw)
    gauge("A", 400, 170, wm.accel)
    
    button("A", 100, 240, wm.a)
    button("B", 200, 240, wm.b)

def stop():
    wm.stop()

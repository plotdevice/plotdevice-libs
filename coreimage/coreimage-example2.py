size(400,250)
speed(100)

try: 
    coreimage = ximport("coreimage")
except:
    coreimage = ximport("__init__")
    reload(coreimage)

def setup():
    
    global img
    img = choice(files("images/*.jpg"))

def draw():

    global img
    canvas = coreimage.canvas(400,250)
    canvas.append(color(0))
    l = canvas.append(img)
    
    d = FRAME
    l.filter("bumpdistortion", radius=350-d, scale=-4+d*0.01)
    l.filter("bumpdistortion", radius=250-d, scale=-4+d*0.01, dy=-d+100)
    l.scale(1.35+d*0.0015)
    
    canvas.draw()
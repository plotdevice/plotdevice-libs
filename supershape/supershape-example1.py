from math import sin, cos
try:
    supershape = ximport("supershape")
except:
    supershape = ximport("__init__")
    reload(supershape)

speed(100)
size(400, 400)

def setup():
    
    global x, y, w, h, m, n1, n2, n3, i
    
    x, y = 200, 200
    w, h = 100, 100
    m = 6.0
    n1 = 1.0
    n2 = 1.0
    n3 = 1.0
    i = 0.0

def draw():
    
    global x, y, w, h, m, n1, n2, n3, i

    m = 12
    n1 = 5.0 + sin(i)
    n2 = 10 + cos(i) * 10
    n3 = sin(i) * 10
    i += 0.05
    
    rotate(i*10)
    p = supershape.path(x, y, w, h, m, n1, n2, n3)
    drawpath(p)
    

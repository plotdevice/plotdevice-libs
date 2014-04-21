size(500, 250)

try: 
    lsystem = ximport("lsystem")
except:
    lsystem = ximport("__init__")
    reload(lsystem)

# Aperiodic Penrose tiling.
# http://en.wikipedia.org/wiki/Penrose_tiling
penrose = lsystem.create()
penrose.rules["6"] = "81++91----71[-81----61]++"
penrose.rules["7"] = "+81--91[---61--71]+"
penrose.rules["8"] = "-61++71[+++81++91]-"
penrose.rules["9"] = "--81++++61[+91++++71]--71"
penrose.rules["1"] = ""
penrose.rules["0"] = "[7]++[7]++[7]++[7]++[7]"
penrose.root = "0"

penrose.angle = 36
penrose.segmentlength = 100

def segment(length, generations, time, id):
    stroke(0)
    line(0, 0, 0, -length)
    
penrose.segment = segment
    
penrose.draw(250, 125, 5)
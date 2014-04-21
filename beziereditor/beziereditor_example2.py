try:
    beziereditor = ximport("beziereditor")
except:
    beziereditor = ximport("__init__")
    reload(beziereditor)

speed(100)
size(400, 400)

def setup():
    
    global editor

    # Initialize the editor with a path
    # constructed from a character.
    fontsize(300)
    p = textpath("a", 80, 300)
    editor = beziereditor.start(p, filename="path")

def draw():
    
    global editor
    editor.draw()
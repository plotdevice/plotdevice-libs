# TEXT SPLIT
# The text module in the Grid library is for cutting a text
# into blocks that fit inside a given area.
# Widow/orphan control ensures that none of these blocks
# start or end with stray lines (as this would not look very aesthetic).

var("txt", NUMBER, 0, 0, 100)
var("pt", NUMBER, 9, 1, 50)
var("width", NUMBER, 250, 0, 500)
var("height", NUMBER, 250, 0, 650)
var("widows", TEXT, 1)
var("orphans", TEXT, 1)
var("forward", BOOLEAN, 1)

try: 
    grid = ximport("grid")
except:
    grid = ximport("__init__")
    reload(grid)

from random import seed
seed(txt)

fontsize(pt)
txt = grid.text.placeholder(n=4)
block1, block2 = grid.text.split(
    txt, 
    width, 
    height,
    int(widows),
    int(orphans),
    forward)

rect(0, 0, width+10, height, fill=0.3)
text(block1, 5, fontsize(), width, fill=1)
text(block2, 5, height+fontsize(), width, fill=0)
# TEXT SPLIT
# The text module in the Grid library is for cutting a text
# into blocks that fit inside a given area.
# Widow/orphan control ensures that none of these blocks
# start or end with stray lines (as this would not look very aesthetic).

var("txt", NUMBER, 0, 0, 100)
var("width", NUMBER, 250, 0, 500)
var("height", NUMBER, 250, 0, 650)

try: 
    grid = ximport("grid")
except:
    grid = ximport("__init__")
    reload(grid)
    
from random import seed
seed(txt)

txt = grid.text.placeholder.sentence()
fontsize(grid.text.fit_fontsize(txt, width, height))
lineheight(grid.text.fit_lineheight(txt, width, height))

rect(0, 0, width+10, height, fill=0.3)
text(txt, 5, fontsize(), width, fill=1)
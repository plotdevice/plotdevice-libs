# ENGLISH PLACEHOLDER TEXT, FLIPPED CONTENT, CUSTOM BACKGROUND

try: 
    grid = ximport("grid")
except:
    grid = ximport("__init__")
    reload(grid)
    
size(*grid.format.A4)

# --- STRUCTURE ---------------------------------------------------------

g = grid.create(2, 1)
g.proportion = "fib"
g.bottom.split(1,3)          # below the header are three columns
g.bottom.left.split(2,1)     # the left column has two rows
g.bottom.left.top.split(1,2) # the top row has two columns
g.bottom.second.split(5,1)   # the middle column has five rows

# --- STYLE -------------------------------------------------------------

# Default styling:
g.styles.background = color(0.25, 0.25, 0.2)
g.styles.fill = color(0.6, 0.85, 1)
g.styles.font = "Georgia"
g.styles.fontsize = 9
g.styles.lineheight = 1.1
g.styles.align = LEFT
g.styles.margin = 1
g.styles.padding = 15

# A banner of slanted lines,
# which we'll be drawing in the header's background.
def under_construction(x, y, width, height, style=None):
    skew(45)
    fill(0, 0.1) 
    w = width/10
    for i in range(10):
        rect(x+i*w*2, y, w, height)

# Things to note:
# - A custom background.
# - We use phi (or golden_ratio) to create a harmonious, bigger fontsize.
# - We flip the header content upside-down by rotating it 180 degrees.
s = g.styles.create("top")
g.top.style = s.name
s.background.draw = under_construction
s.fontsize *= g.proportion.phi**3
s.fill = color(1, 0, 0.5)
s.rotation = 180

# --- CONTENT -----------------------------------------------------------

# English placeholder text.
# To top it off, we add a trendy arrow to the start of the text.
g.content = grid.text.arrow2 + " " + grid.text.placeholder.english()

# -----------------------------------------------------------------------

g.draw()

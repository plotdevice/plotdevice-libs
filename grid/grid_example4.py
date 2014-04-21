# CUSTOM CONTENT
# Drawing content in a cell from your own command is very easy.
# You can use it to put multiple variations of artwork in a grid, for example.
try: 
    grid = ximport("grid")
except:
    grid = ximport("__init__")
    reload(grid)

size(500, 500)
background(0.1, 0, 0.1)

# --- STRUCTURE ---------------------------------------------------------

g = grid.create(5, 5, WIDTH-10, HEIGHT-10)

# Play around with the numbers for nice different layouts:
#g.column(0).relative_width = 0.5
#g.row(0).relative_height = 0.5

# --- STYLE -------------------------------------------------------------

# Default styling:
g.styles.default.stroke = color(0.8)
g.styles.default.strokewidth = 0.5
g.styles.default.roundness = 10
g.styles.default.margin = 3

# --- CONTENT -----------------------------------------------------------

# Here's our custom content command.
# It outputs random colorful ovals.
def ovals(x, y, width, height, style=None):
    for i in range(random(4, 12)):
        r, g, b = random(0.3, 1.0), random(0.4), random(0.8)
        fill(r, g, b, random(0.5))
        stroke(r, g, b, random(0.5))
        strokewidth(random(20))
        r = random(20)
        oval(
            x - r + random(width),
            y - r + random(height),
            r*2,
            r*2
        )

g.content = ovals

# -----------------------------------------------------------------------

g.draw(5, 5)
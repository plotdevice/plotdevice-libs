try: 
    grid = ximport("grid")
except:
    grid = ximport("__init__")
    reload(grid)

w, h = grid.format.A4
size(w+0, h+0)

# A grid with a top and bottom cell.
# The top cell is smaller, 
# with a harmonious Fibonacci (golden mean) proportion between them.
g = grid.create(2, 1, WIDTH-20, HEIGHT-20)
g.arrange("fib")

# New styles which we'll be creating later on inherit from the default style.
# So here we can set some things that apply to all cells.
g.styles.default.fill = color(0.3)
g.styles.default.padding = 8

# --- HEADER ------------------------------------------------------------

# We name the top cell "header" so we can reference it more easily.
# The header contains two rows, one for the title and one for the baseline.
g.top.name = "header"
g.header.split(2, 1, proportion="fib")
g.header.top.content = "NodeBox"
g.header.bottom.content = "NodeBox is a Mac OS X application that lets you create 2D visuals (static, animated or interactive) using Python programming code and export them as a PDF or a QuickTime movie. NodeBox is free and well-documented."

g.header.style = "header"
g.header.top.style = "title"
g.header.bottom.style = "baseline"

# Header style.
# The style.delegate = False means that the background image
# spans both the title and baseline cell. If style.delegate where True,
# the title and baseline cells would each get their own copy
# of the background image.
s = g.styles.create("header")
s.background.image = "nodebox.jpg"
s.roundness = 0.1
s.fit = True
s.delegate = False

# Title style.
# The style.fit = True means that the text size will scale to fit
# the size of the title cell as best as possible.
s = g.styles.create("title")
s.fill = color(1)
s.font = "Helvetica-Bold"
s.fit = True

# Baseline style.
# Again, fit the text as large as possible.
# Change the size of the entire grid to see what happens.
s = g.styles.create("baseline")
s.fill = color(1)
s.font = "Georgia"
s.fit = True

# --- BODY --------------------------------------------------------------

# The bottom part of the grid consists of three columns 
# with flowing body text. We generate some lorem ipsum text
# and assign it to the body. The three columns will figure
# out for themselves which part of the text to display.
g.bottom.split(1, 3)
g.bottom.content = grid.text.placeholder()
g.bottom.style = "body"

s = g.styles.create("body")
s.font = "Georgia"
s.fontsize = 9
s.align = JUSTIFY
s.margin.top = 10

# We want the text to start with a subtitle.
# We can do this by splitting the left column in two rows.
# The top row will contain the subtitle.
# When you resize columns and rows in a grid, the other rows and columns
# will adjust their size to make room. In this case we don't want this to
# happen, so we give the subtitle cell a fixed height that never changes.
g.bottom.left.split(2, 1)
g.bottom.left.top.name = "subtitle"
g.subtitle.content = "Welcome to NodeBox " + grid.text.heart
g.subtitle.height = 40
g.subtitle.fixed = True
g.subtitle.style = "subtitle"

s = g.styles.create("subtitle", template="body")
s.background = color(0.3)
s.fill = color(1)
s.font = "Helvetica-Bold"
s.fit = True
s.margin = (4, 15, 4, 0)
s.padding = (5, 2, 0, 2)

# -----------------------------------------------------------------------

g.draw(10, 10)

#grid.highlight(g.bottom, recursive=True)
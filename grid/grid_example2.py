# IMAGE GRID

try: 
    grid = ximport("grid")
except:
    grid = ximport("__init__")
    reload(grid)

# Play around with the rows, columns, width and height.
# With the g.styles.fit = True defined below,
# the image will always try to fit a cell as best as possible.
g = grid.create(2, 1, 500, 500)

# Our own custom proportion.
p = grid.proportion(distribution="fib", reversed=True, mirrored=True)
g.top.split(2, 3, p)

# Images are centered in a cell, and scale as needed.
g.styles.align = (CENTER, CENTER)
g.styles.fit = True
g.styles.margin = 1

# Display all the images in the current folder.
g.content = files("*.jpg")
g.content.repeat = True

g.draw(10,10)
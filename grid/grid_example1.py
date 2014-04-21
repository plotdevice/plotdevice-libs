# Import the library
try: 
    # This is the statement you normally use.
    grid = ximport("grid")
except:
    # But since this example is "inside" the library
    # we may need to try something different when
    # the library is not located in /Application Support
    grid = ximport("__init__")
    reload(grid)

g = grid.create(3, 1, width=400, height=500)
g.bottom.split(1, 3)

g.styles.default.padding = 4
g.styles.default.margin = 1
g.styles.default.fill = color(0.9)
g.styles.default.background = (
    color(0.5, 0.55, 0.6), 
    color(0.4, 0.45, 0.5)
)

g.content = grid.text.placeholder()
g.top.content = "nodebox.jpg"

g.draw()
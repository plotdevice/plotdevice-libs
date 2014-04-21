# PROPORTION
# A proportion defines the way rows and columns in the grid are organised.
# Here's a handy script to try out different proportions:

try: 
    grid = ximport("grid")
except:
    grid = ximport("__init__")
    reload(grid)

p = grid.proportion(
    distribution="fib",
    mirrored=False,
    reversed=False,
    shuffled=False,
    sorted=False,
    repetition=1
)

p.generate(5)
p.draw(10, 10)
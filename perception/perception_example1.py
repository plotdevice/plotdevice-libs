# PERCEPTION BROWSER

try:
    perception = ximport("perception")
except ImportError:
    perception = ximport("__init__")
    reload(perception)

g = None
def load(node):
    
    global g
    # Load a new cluster of nodes surrounding the clicked node.
    # Note the "max" parameter - you won't find it documented.
    # We use it here to cap the number of rules returned.
    # A fast graph is more important right now than all of the data.
    g = perception.cluster(str(node), depth=2, max=30, labeled=False)
    g.distance = 1.4
    g.layout.n = 2000
    g.styles.apply()
    g.layout.force = 0.005 # lower if nodes are twitching
    g.events.click = load

load("cool")

size(600, 600)
speed(30)
def draw():
    g.update()
    g.draw(traffic=True, directed=True)
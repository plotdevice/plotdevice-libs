# Import the library
try: 
    # This is the statement you normally use.
    lsystem = ximport("lsystem")
except:
    # But since these examples are "inside" the library
    # we may need to try something different when
    # the library is not located in /Application Support
    lsystem = ximport("__init__")
reload(lsystem)

# Create a simple treelike pattern.
tree = lsystem.create()
tree.rules = {
    "1" : "[-FF-FF1][+FF+FF1]"            
}

# Each F command depletes a little bit of time.
# Calculate the total time we need to grow 6 generations.
done = tree.duration(5)

# Our custom segment is a pinkish oval.
# When we divide the current time at the segment by done,
# we get a number between 0.0 and 1.0 we can use for coloring.
def segment(length, generations, time, id):
    t = min(1.0, time/done)
    fill(1-t*0.75, 0, 0.5, 0.6)
    oval(-length/2, -length, length, length)

tree.segment = segment

# Animate the growth of the tree using the FRAME count.
size(500, 250)
speed(20)
def draw():
    background(0.2, 0, 0.2)
    time = min(FRAME*0.1, done)
    tree.draw(250, 250, 5, time, ease=8)
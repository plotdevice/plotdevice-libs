size(600, 450)
background(0)

# Import the library
try: 
    # This is the statement you normally use.
    isight = ximport("isight")
except:
    # But since this example is "inside" the library
    # we may need to try something different when
    # the library is not located in /Application Support
    isight = ximport("__init__")
    reload(isight)

# Create a grid of 3 x 3 with each image grabbed from the iSight.
# This will take some time.
for x, y in grid(3, 3, 200, 150):
    image(isight.grab(width=190, height=140), x + 5, y + 5)
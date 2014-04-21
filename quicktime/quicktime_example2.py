try:
    quicktime = ximport("quicktime")
except:
    quicktime = ximport("__init__")
    reload(quicktime)

size(575, 595)
movie = quicktime.movie("twisted_world.mp4")

# Grab 20 frames evenly distributed along the movie.
frames = movie.frames(20)

i = 0
for x, y in grid(4, 5, 145, 120):
    image(None, x, y, data=frames[i].data, width=140)
    i += 1

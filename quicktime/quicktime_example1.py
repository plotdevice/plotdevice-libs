try:
    quicktime = ximport("quicktime")
except:
    quicktime = ximport("__init__")
    reload(quicktime)

movie = quicktime.movie("twisted_world.mp4")

print movie.fps
print movie.duration

size(movie.width, movie.height)
speed(50)

def draw():
    # The frame() method grabs a frame from the movie 
    # at the given time in seconds.
    frame = movie.frame(FRAME*0.1)
    image(None, 0, 0, data=frame.data, width=frame.width)
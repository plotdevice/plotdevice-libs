# Quicktime + Core Image

try:
    quicktime = ximport("quicktime")
except:
    quicktime = ximport("__init__")
    reload(quicktime)

coreimage = ximport("coreimage")
    
movie = quicktime.movie("twisted_world.mp4")
# Set the size whenever we know the movie's size
size(movie.width, movie.height)

# Use a slider to determine at what time in the movie
# to grab a frame.
var("time", NUMBER, 10, 0, movie.duration*10)
frame = movie.frame(time*0.1)

# We can simply pass the frame as input
# to a Core Image layer.
canvas = coreimage.canvas(movie.width, movie.height)
l = canvas.layer(frame)
l.filter_zoomblur(dy=time, amount=time)

canvas.draw()
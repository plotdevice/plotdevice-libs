try:
    quicktime = ximport("quicktime")
except:
    quicktime = ximport("__init__")
    reload(quicktime)

size(500, 500)

reload(quicktime)

audio = quicktime.audio("modron_cube.mp3")

# We only need a snippet of the sound file.
# The numbers represent seconds.
audio = audio.selection(start=0, stop=7.2)
audio.play()

speed(100)
def draw():

    background(0.2)

    # The horizontal mouse position controls the playback rate.
    # The vertical mouse position controls the volume.
    h = MOUSEX/WIDTH * 2
    v = MOUSEY/HEIGHT * 2
    audio.rate = h
    audio.volume = v
    
    # Loop the audio fragment.
    # Note: when the animation stops, 
    # the sound fragment will finish out its remaining time.
    if not audio.is_playing:
        audio.play()
    
    # Draw a rotating star.
    # It rotates quicker when the playback rate is higher.
    # It's bigger when the volume is higher.
    fill(0.8)
    rotate(FRAME*h)
    star(MOUSEX, MOUSEY, 20, 10+v*15, 10+v*23)
    reset()
    
    # Playback rate and volume statistics.
    fill(0)
    fontsize(12)
    text("rate %#.2f" % audio.rate, MOUSEX+10, MOUSEY)
    text("volume %#.2f" % audio.volume, MOUSEX+10, MOUSEY+12)
    
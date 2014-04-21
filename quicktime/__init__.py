### CREDITS ##########################################################################################

# Copyright (c) 2007 Tom De Smedt.
# See LICENSE.txt for details.

__author__    = "Tom De Smedt"
__version__   = "1.9.0"
__copyright__ = "Copyright (c) 2007 Tom De Smedt"
__license__   = "MIT"

### NODEBOX QUICKTIME ################################################################################

# The NodeBox Quicktime library adds movie and audio support to NodeBox.
# You can use it to grab image frames from a movie or to control sound playback.
# Quicktime is a Mac OS X specific framework available from Mac OS X 1.4 (Tiger) and NodeBox 1.9.0.

from QTKit import *

### MEDIA ############################################################################################

class Media:
    
    def __init__(self, data, start=0, stop=None):
        
        """ Quicktime movie wrapper.
        
        Media is split into Movie and Audio, each with different functionality.
        The data parameter is either a pathname passed as a string,
        or a tuple containing a path string, aQTMovie and a QTTimeRange 
        (i.e. a selection).
        
        """
        
        if isinstance(data, str):
            self.path = data
            self._qtmovie = QTMovie.movieWithFile_(data)
        if isinstance(data, tuple) and isinstance(data[1], QTMovie):
            self.path = data[0]
            self._qtmovie = QTMovie.movie().initWithMovie_timeRange_error_(data[1], data[2], None)
            print "MOVIE", self._qtmovie
            self._qtmovie = self._qtmovie[0]
        
        self.duration = self._qtmovie.duration()
        print "DURATION",  self.duration
        self.duration = 1.0 * self.duration.timeValue / self.duration.timeScale
        self.timescale = self._qtmovie.attributeForKey_("QTMovieTimeScaleAttribute")

        self._qtmovie.stepForward()
        self.fps = int(1.0 / (1.0 * self._qtmovie.currentTime().timeValue / self.timescale))

        self.has_video = self._qtmovie.attributeForKey_("QTMovieHasVideoAttribute")
        self.has_audio = self._qtmovie.attributeForKey_("QTMovieHasAudioAttribute")
        
        if start > 0 or stop != None:
            s = self.selection(start, stop)
            self._qtmovie = s._qtmovie
            self.duration = s.duration
        
    def _abs_timerange(self, start=0, stop=None):
        
        """ Given a start and stop time in seconds, returns the absolute scaled time.
        
        The start time is always zero or more.
        The stop time is always less than Media.duration, 
        and more than the start time.
        
        """

        if stop == None: 
            stop = self.duration
        
        start = max(start, 0)
        stop = min(max(start, stop), self.duration)
            
        start = start * self.timescale
        stop = stop * self.timescale
        
        return start, stop
        
        
    def selection(self, start=0, stop=None):
        
        """ Creates a copy with the given start and end time.
        """
        
        start, stop = self._abs_timerange(start, stop)
        
        duration = stop - start
        duration = QTMakeTime(int(duration), self.timescale)
        start = QTMakeTime(int(start), self.timescale)
        r = QTMakeTimeRange(start, duration)
        s = self.__class__((self.path, self._qtmovie, r))
        
        return s
        
    def copy(self):
        
        return self.selection()

### MOVIE ############################################################################################

class Movie(Media, object):
 
    def __init__(self, data, start=0, stop=None):
        
        """ A movie from which you can grab image frames.
        """
        
        Media.__init__(self, data, start, stop)
        w, h = self._qtmovie.attributeForKey_("QTMovieNaturalSizeAttribute").sizeValue()
        self.width = w
        self.height = h
 
    def frame(self, t):
        
        """ Returns the frame at t seconds in the movie.
        """
        
        t = max(0, min(t, self.duration))
        t = int(t*self.timescale)
        t = max(0, t-1)
        
        time = QTMakeTime(t, self.timescale)
        frame = self._qtmovie.frameImageAtTime_(time)
        frame = MovieFrame(frame, src=self.path, time=t)
        
        return frame
        
    def frames(self, n=10, start=0, stop=None):
        
        """ Returns n frames between start and stop time in seconds.
        
        By default, the start and stop are the beginning and end of the movie.
        If n is 1, returns the first frame.
        If n is 2, returns the first and last frame.
        
        """
        
        if n <= 0:
            return []
        
        start, stop = self._abs_timerange(start, stop)
        
        images = []
        for i in range(n-1):
            time = int(start + (stop-start) * i / (n-1))
            time = QTMakeTime(time, self.timescale)
            frame = self._qtmovie.frameImageAtTime_(time)
            frame = MovieFrame(frame, src=self.path, time=time)
            images.append(frame)

        if n > 1:
            # Retrieving the very last frame returns None in QuickTime 7.2.0,
            # so we retrieve the one-before-last frame.
            time = int(stop - 1)
        else:
            time = int(start)
        time = QTMakeTime(time, self.timescale)
        frame = self._qtmovie.frameImageAtTime_(time)
        frame = MovieFrame(frame, src=self.path, time=time)    
        images.append(frame)
        
        return images

def movie(data, start=0, stop=None):
    return Movie(data, start, stop)

### MOVIE FRAME ######################################################################################

class MovieFrame:
    
    """ Movie frame with data attribute to pass to image()
    
    A MovieFrame can be passed to NodeBox by data:
    image(None, 0, 0, data=frame.data)
    To Core Image, MovieFrame will pose as an NSImage
    with size() and TIFFRepresentation() method,
    two things by which Core Image identifies an NSImage.
    
    """
    
    def __init__(self, img, src="", time=0.0):
        self._nsimage = img
        self.src = src
        self.time = time
        self.size = img.size
        self.width, self.height = img.size()
        self.TIFFRepresentation = img.TIFFRepresentation
        
    def _data(self):
        return self._nsimage.TIFFRepresentation()
        
    data = property(_data)

### AUDIO ############################################################################################

class Audio(Media, object):
    
    def __init__(self, data, start=0, stop=None):
        
        """ A sound which you can play, pause and stop.
        
        Audio has three properties which you can change:
        - Audio.volume: from 0 to 2.0
        - Audio.time: the playback time, from 0 to Audio.duration
        - Audio.rate: the playback rate, from 0 to 3.0
        
        Note that when audio stops playing,
        the time will be reset to zero.
        
        """
        
        Media.__init__(self, data, start, stop)
        self.paused = False
        
        self._volume = 1.0
        self._time = 0
        self._rate = 1.0
    
    def _get_volume(self): 
        return self._qtmovie.volume()
    def _set_volume(self, v):
        v = max(0.0, min(v, 2.0))
        self._qtmovie.setVolume_(v)
        self._volume = v

    def _get_time(self):
        t = self._qtmovie.currentTime()
        return 1.0 * t.timeValue / t.timeScale
    def _set_time(self, t): 
        t = max(0, min(t, self.duration))
        t = QTMakeTime(int(t*self.timescale), self.timescale)
        self._qtmovie.setCurrentTime_(t)
        self._time = t

    def _get_rate(self): 
        return self._rate
    def _set_rate(self, r): 
        r = max(0.25, min(r, 5.0))
        self._qtmovie.setRate_(r)
        self._rate = r
        
    volume = property(_get_volume, _set_volume)    
    time = property(_get_time, _set_time)  
    rate = property(_get_rate, _set_rate)

    def play(self):
        self.paused = False
        self._qtmovie.play()
        self._qtmovie.setRate_(self._rate)
        
    def stop(self):
        self.paused = False
        self._qtmovie.stop()
        self.time = 0
        
    def pause(self):
        self.paused = True
        self._qtmovie.stop()
        
    def _is_playing(self):
        if self.time == 0 or self.time == self.duration:
            self.stop()
            return False
        elif self.paused:
            return False
        else:
            self._qtmovie.setRate_(self._rate)
            return True
    
    is_playing = property(_is_playing)

    def reset(self):
        self.volume = 0.0
        self.time = 0.0
        self.rate = 1.0

    def __del__(self):
        self._qtmovie.stop()
        
    def selection(self, start=0, stop=None):
        s = Media.selection(self, start, stop)
        s.volume = self.volume
        s.time = self.time
        s.rate = self.rate
        return s

def audio(data, start=0, stop=None):
    return Audio(data, start, stop)        

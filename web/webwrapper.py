import sys
sys.path.append('/Users/fdb/Java/jython2.5b0/Lib')
from plotdevice.gfx import Image
from . import flickr

def flickrImage(query):
    images = flickr.search(query, start=1, count=1)
    if len(images) == 0: return None
    img = images[0]
    img.download(size="small")
    return Image(img.path, 0, 0)

import sys
sys.path.append('/Users/fdb/Java/jython2.5b0/Lib')
from net.nodebox import graphics
import flickr

def flickrImage(query):
    images = flickr.search(query, start=1, count=1)
    if len(images) == 0: return None
    img = images[0]
    img.download(size="small")
    return graphics.Image(img.path, 0, 0)

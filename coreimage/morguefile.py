# MORGUEFILE - last updated for NodeBox 1rc7
# Author: Tom De Smedt <tomdesmedt@trapdoor.be>
# Based on the MorgueFile API:
# http://box115.morguefile.com/wiki/index.php/Morguefile_api

from urllib import urlopen
from xml.dom.minidom import parseString
import os

class MorgueFileImage:
    
    def __init__(self):
        
        self.id        = 0
        self.category  = ""
        self.author    = ""
        self.name      = ""
        self.url       = ""
        self.date      = ""
        self.views     = 0
        self.downloads = 0
        
    def download(self, path="", thumbnail=False):

        """ Downloads the image to the given path folder.
    
        If the path does not exist, attempts to create the path.
        If thumbnail is True, downloads the image thumbnail.
        Returns the filename at the given path.
        The filename is composed of the author's name + image name.
    
        """
    
        if path != "" and not os.path.isdir(path):
            os.mkdir(path)
    
        url = self.url
        if thumbnail == False:
            url = self.url.replace("thumbnails", "lowrez")
        
        data = urlopen(url).read()
        path = os.path.join(path, self.author + "_" + self.name)
        f = open(path, "w")
        f.write(data)
        f.close()
    
        return path

def search(q, max=100, _author=False):
    
    """ Queries the MorgueFile API.
    
    Returns a list of MorgueFileImage objects.
    When _author is True, returns images that have q as author.
    
    """
    
    q = q.replace(" ", "+")
    
    arg = "terms"
    if _author == True: arg = "author"
    
    api = "http://morguefile.com/archive/archivexml.php"
    api += "?" + arg + "=" + q + "&archive_max_image=" + str(max)
    xml = urlopen(api).read()
    dom = parseString(xml)

    def _getdata(e, tag):
        return e. getElementsByTagName(tag)[0].childNodes[0].data

    images = []
    for e in dom.getElementsByTagName("image"):
        img = MorgueFileImage()
        img.id        = _getdata(e, "unique_id")
        img.category  = _getdata(e, "category")
        img.author    = _getdata(e, "author")
        img.name      = _getdata(e, "title")
        img.url       = _getdata(e, "photo_path")
        img.date      = _getdata(e, "date_added")
        img.views     = _getdata(e, "views")
        img.downloads = _getdata(e, "downloads")
        images.append(img)

    return images

query = search

def search_by_author(author, max=100):
    return search(author, max, _author=True)

query_by_author = search_by_author

def download(img, path="", thumbnail=False):
    if isinstance(img, MorgueFileImage):
        return img.download(path, thumbnail)
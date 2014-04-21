# Google - last updated for NodeBox 1.9.0
# Author: Tom De Smedt <tomdesmedt@organisms.be>
# Manual: http://nodebox.net/code/index.php/Google
# Copyright (c) 2007 by Tom De Smedt, Frederik De Bleser
# See LICENSE.txt for details.

from pygoogle import google as pygoogle
import sys

class Output:

    """Mutes the output from print operations.

    No print commands are dumped when mute() is called.
    Used to filter comments from PyGoogle we don't need.

    """

    def __init__(self): self.out = sys.stdout
    def mute(self): sys.stdout = self
    def on(self): sys.stdout = self.out
    def write(self, x): pass

class GoogleError(Exception): pass
class GoogleLicenseError(Exception): pass
class GoogleLimitError(Exception): pass

def license(id):
    
    """Sets the license key of your Google API account.
    
    A license key entitles you (by default) to 1000 queries
    on Google per day. Obtain a key at www.google.com/apis/
    
    """
    
    pygoogle.setLicense(id)

def limit_exceeded():
    
    """Checks whether the Google API query limit is exceeded.
    
    Returns true when the well is dry,
    ususally after a 1000 queries.
    
    """
    
    try: message = str(sys.exc_info()[1])
    except: message = ""
    if message.find("exceeded") > 0:
        return True
    else:
        return False
        
# Deprecated.
dry = limit_exceeded

def search(query, page=1):
    
    """Retrieves a list of links from Google.
    
    Searches Google for query using SOAP.
    Returns a list of links related to the query.

    """

    o = Output()
    o.mute()

    try:
        data = pygoogle.doGoogleSearch(query, start=(page-1)*10)
        data = [x.URL for x in data.results]
        o.on()
        return data
        
    except pygoogle.NoLicenseKey:
        o.on()
        raise GoogleLicenseError
        
    except Exception, e:
        o.on()
        if dry(): raise GoogleLimitError
        else: raise GoogleError
    
def results(query):
    
    """Returns the number of results for the given query.

    This is useful for statistical operations,
    for example querying google for the "grass green",
    "grass yellow", "grass blue" and determining what
    color is most likely associated with "grass".
    
    """

    o = Output()
    o.mute()
    
    try:
        data = pygoogle.doGoogleSearch(query)
        data = data.meta.estimatedTotalResultsCount
        o.on()
        return data
    
    except pygoogle.NoLicenseKey:
        o.on()
        raise GoogleLicenseError
    
    except Exception, e:
        o.on()
        if dry(): raise GoogleLimitError
        else: raise GoogleError
        
def sort(list, key=None, strict=True):
    
    """Performs a "Google-sort" on the given list.
    
    Sorts the items in the list according to 
    the result count Google yields on an item.
    As such, we assume that the entire internet
    is some sort of "emotive opinion" on the subject.
    
    Setting a key sorts the items according
    to their relation to this key;
    for example sorting [red, green, blue] by "love"
    yields red as the highest results,
    likely because red is the color commonly associated with love.

    Setting a key often yield strange, illogical and
    unpredictable results. Just like with people.
    
    This algorithm does not process a weight for each item.
    This apparently influenced the results in a bad way:
    like red bananas and green love.
    
    """
    
    q = []
    for item in list:
        query = item + " " + str(key)
        if strict: query = "\"" + query + "\""
        count = results(query)
        q.append((count, item))
        
    sum = 0.000000000000000001
    for count, item in q: sum += count
    q = [(count*1.0/sum, item) for count, item in q]
        
    q.sort()
    q.reverse()
    
    #Returns a list of (count,item) tuples,
    #sorted descending by count.
    #Count is a value between 0 and 1,
    #representing the item's percentual meaning in the list.
    return q
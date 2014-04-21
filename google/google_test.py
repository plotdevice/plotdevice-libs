from urllib import urlopen
import re

size(500, 500)
background(0.2,0.5,0)

# Import the Google library
try: 
    # This is the statement you normally use.
    google = ximport("google")
except:
    # From inside the library folder.
    google = ximport("__init__")
    reload(google)

# Set the license key
google.license("<your license key>")

# Search for "nodebox" and get the first result from the list
first_result = google.search("nodebox")[0]  # I'm feeling lucky!

# Read in the first result's page and search for the description
page = urlopen(first_result).read()
description=re.search("name=\"description\"\s+content=\"(.*?)\"", page).groups()[0]

# Draw the description
text(description, 10, 80, width=WIDTH-20, fontsize=30, fill=1, font="Helvetica-Bold")



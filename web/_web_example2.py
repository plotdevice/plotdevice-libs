# Parsing web pages.

try:
    web = ximport("web")
except:
    web = ximport("__init__")
    reload(web)

reload(web.html)

url = "http://nodebox.net"
print web.url.is_webpage(url)

# Retrieve the data from the web page and put it in an easy object.
html = web.page.parse(url)

# The actual URL you are redirected to.
# This will be None when the page is retrieved from cache.
print html.redirect

# Get the web page title.
print html.title

# Get all the links, including internal links in the same site.
print html.links(external=False)

# Browse through the HTML tree, find <div id="content">,
# strip tags from it and print out the contents.
content = html.find(id="content")
fontsize(10)
text( web.html.plain(content), 20, 20, width=300)
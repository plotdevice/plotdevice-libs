# Wikipedia articles.

try:
    web = ximport("web")
except:
    web = ximport("__init__")
    reload(web)

web.clear_cache()

q = "computer graphics"
article = web.wikipedia.search(q, language="en")

# Get the article title.
text(article.title, 20, 40)

# Get a list of all the links to other articles.
# We can supply these to a new search.
print article.links

# The title of each paragraph
for p in article.paragraphs: 
    print p.title
    #print "-"*40
    #print p

fontsize(10)
text(article.paragraphs[0], 20, 60, width=300)

print
print choice(article.references)
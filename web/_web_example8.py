import importlib
# Definitions from the Urban Dictionary.

try:
    web = ximport("web")
except:
    web = ximport("__init__")
    importlib.reload(web)

definitions = web.urbandictionary.search("human")
text( choice(definitions), 50, 50, width=300)
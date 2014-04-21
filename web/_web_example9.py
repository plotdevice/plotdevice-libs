# Clearing the cache.

try:
    web = ximport("web")
except:
    web = ximport("__init__")
    reload(web)

# Queries and images are cached locally for speed,
# so it's a good idea to empty the cache now and then.
# Also, when a query fails (internet is down etc.),
# this "bad" query is also cached.
# Then you may want to clear the cache of the specific
# portion of the library you're working with,
# for example: web.morguefile.clear_cache()

web.clear_cache()
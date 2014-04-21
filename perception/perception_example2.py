# COMPARATIVES

try:
    perception = ximport("perception")
except ImportError:
    perception = ximport("__init__")
    reload(perception)

size(1000, 1000)

p = "is-more-important-than"
cmp = perception.compare_concepts(p)

# The return value is a list:
#for concept1, concept2 in cmp:
#   print concept1, p, concept2

# Creating a graph from the results is easy enough.
# Typically, the graph will contain different clusters
# that are disconnected from each other.
# We take the biggest cluster.
g = cmp.graph()
g = g.split()[0] # increase 0 for more clusters
g.solve()
g.styles.apply()
g.draw(weighted=True, directed=True, traffic=3)

# Print out the results,
# with the most relevant first.
for concept1, comparisons in cmp.rank(g):
    for concept2 in comparisons:
        print concept1, cmp.relation, concept2
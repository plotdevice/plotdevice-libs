# SIMILE

try:
    perception = ximport("perception")
except ImportError:
    perception = ximport("__init__")
    reload(perception)

# Use Google search engine to look for properties:
q = "princess"
results = perception.suggest_properties(q)

for property in results:
    count = "(" + str(results[property]) + ")"
    print property, "is-property-of", q, count
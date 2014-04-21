# coding: utf-8

### PERCEPTION #######################################################################################
# Analysis tools for working with data from http://nodebox.net/perception in NodeBox.
# The library is roughly organised in 5 parts that add up to the final solver object:
# 1) query()   : returns lists of rules form the online database, using a caching mechanism.
# 2) cluster() : returns a graph objects based on a cluster of rules around a central concept.
# 3) range()   : find sibling concepts (e.g. fonts, movies, colors, trees) using a taxonomy graph.
# 4) index     : object for building and searching cached indices of shortest paths.
# 5) cost      : object that simplifies the creation of path search heuristics.
# => solver    : object for inferring knowledge from the database, using clusters, indices and ranges.

### CREDITS ##########################################################################################

# Copyright (c) 2008 Tom De Smedt.
# See LICENSE.txt for details.

__author__    = "Tom De Smedt"
__version__   = "beta+"
__copyright__ = "Copyright (c) 2008 Tom De Smedt"
__license__   = "GPL"

######################################################################################################

import os
import md5
import glob
from re import sub
from socket import setdefaulttimeout
from urllib2 import urlopen
import cPickle as pickle
from random import random

import graph
from graph.cluster import sorted, unique

# "_range" is the name of a singleton class in the library.
# "range" is the name of the class instance.
def range_(start, stop=None, step=1):
    if stop is None: 
    	stop, start = start, 0
    cur = start
    while cur < stop:
        yield cur
        cur += step

#### BASIC PROPERTIES ################################################################################
# Those we think can easily be translated visually.

basic_properties = [
	"angular",  "round",      "large",    "small",
	"long",     "short",      "bright",   "dark",
	"calm",     "wild",       "chaotic",  "structured",
	"clean",    "dirty",      "cold",     "hot",
	"cool",     "warm",       "sharp",    "soft",
	"complex",  "simple",     "deep",     "shallow",
	"dynamic",  "static",     "fast",     "slow",
	"fluid",    "solid",      "hard",     "soft",
	"heavy",    "light",      "loud",     "quiet",
	"natural",  "artificial", "old",      "new",
	"elegant",  "raw",        "strong",   "weak",
	"tangible", "abstract",   "thick",    "thin", "repetitive"
]

#### CACHE ###########################################################################################
# Caches the results returned from the NodeBox Perception API so queries run faster.

CACHE = os.path.join(os.path.dirname(__file__), "cache")

def _path(key):
    return os.path.join(CACHE, md5.new(key).hexdigest()+".txt")
    
def cache(key, value):
    open(_path(key), "w").write(value)
    
def cached(key):
    return open(_path(key)).read()
    
def in_cache(key):
    return os.path.exists(_path(key))

def clear_cache():
    for f in glob.glob(os.path.join(CACHE, "*")):
        os.unlink(f)

#### API #############################################################################################
# The query() command returns a list of rules from the online Perception database.
# Locally cached results are used whenever available.

AUTHOR = ""
def is_robot(author):
	return author == "robots@nodebox.net"

def normalize(str):
    """ Returns lowercase version of string with accents removed.
    Used in Rules.disambiguate() to get the correct cluster root.
    """
    accents = [
        ("á|ä|â|å|à", "a"), 
        ("é|ë|ê|è", "e"), 
        ("í|ï|î|ì", "i"), 
        ("ó|ö|ô|ø|ò", "o"), 
        ("ú|ü|û|ù", "u"), 
        ("ÿ|ý", "y"), 
        ("š", "s"), 
        ("ç", "c"), 
        ("ñ", "n")
    ]
    str = str.lower()
    for a, b in accents: str = sub(a, b, str)
    return str

class InternetError: pass

class Rule:
    
    def __init__(self, concept1, relation, concept2, context=None, weight=1, author=None, date=None):
        """ A rule from the NodeBox Perception database,
        e.g. 'cat' is-a 'predator' in the 'nature' context.
        """
        self.concept1 = concept1
        self.relation = relation
        self.concept2 = concept2
        self.context  = context
        self.weight   = weight
        self.author   = author
        self.date     = date
    
    def __repr__(self):
        str = self.concept1 + " " + self.relation + " " +self.concept2
        if self.context != None: str += " (" + self.context + ")"
        return str

class Rules(list):
	
	def _concepts(self):
		""" Returns a dictionary of concepts to number of occurences in the ruleset.
		"""
		rank = {}
		for rule in self:
			if not rule.concept1 in rank: rank[rule.concept1] = 0
			if not rule.concept2 in rank: rank[rule.concept2] = 0
			rank[rule.concept1] += 1
			rank[rule.concept2] += 1
		return rank
		
	concepts = property(_concepts)
	
	def disambiguate(self, root=None):
		""" Disambiguate case-sensitive concepts (e.g. "god" or "God").
		Opt for what occurs most in the ruleset, this avoids unconnected graphs.
		The selected case for the given root concept is returned.
		""" 
		if root == None: return root
		self._root = root
		def _vote(concept, rank):
			lower = concept.lower()
			if lower in rank and rank[lower] >= rank[concept]:
				return lower
			if lower == self._root:
				self._root = concept
			return concept
		rank = self.concepts
		for rule in self:
			rule.concept1 = _vote(rule.concept1, rank)
			rule.concept2 = _vote(rule.concept2, rank)
		# A search for "schrodinger" yields a cluster with "Schrödinger" as root.
		if self._root not in rank:
			for concept in rank.keys():
				if normalize(concept) == self._root.lower():
					self._root = concept
					break
		return self._root

def query(concept, relation=None, context=None, author=None, depth=1, max=None, wait=10):
    
    """ Returns search results from the NodeBox Perception database.
    Retrieves a list of rules involving the given concept, relation, context and author.
    If depth is > 1, returns a cluster of rules:
    - concepts connected to the given concept = depth 1
    - concepts connected to the depth 1 set = depth 2, etc.
    """
    
    if concept == None: concept = ""
    if author  == None: author  = AUTHOR
    robots = author==None
    robots = True
    
    api  = "http://nodebox.net/perception/?q="
    #api  = "http://127.0.0.1/~tom/perception/?q="
    api += concept.replace(" ", "_")
    api += "&format=txt"

    if relation != None: api += "&relation=" + relation
    if context  != None: api += "&context="  + context
    if author   != None: api += "&author="   + author
    if depth    >  1   : api += "&depth="    + str(depth)
    if max      != None: api += "&max="      + str(max)
    if robots   == True: api += "&robots=1"

    if in_cache(api): 
        response = cached(api)
    else:
        try:
            setdefaulttimeout(wait)
            response = urlopen(api).read()
            cache(api, response)
        except Exception, e:
            raise InternetError
    
    rules = Rules()
    if response == "": 
        return rules
    def _parse(str):
        str = str.strip(" '")
        str = str.replace("\\'", "'")
        return str
    for rule in response.split("\n"):
        rule = rule.split(",")
        concept1 = _parse(rule[0])
        relation = _parse(rule[1])
        concept2 = _parse(rule[2])
        context  = _parse(rule[3])
        weight   = float(_parse(rule[4]))
        author   = _parse(rule[5])
        date     = _parse(rule[6])
        rules.append(Rule(concept1, relation, concept2, context, weight, author, date))
    return rules

#### CONCEPT CLUSTER ################################################################################# 
# Extends the Graph and Node objects for handling a semantic network of rules.

#--- NODE RULE ASSERTION -----------------------------------------------------------------------------

graph.edge.relation = None
graph.edge.context = None
graph.edge.author = None

def has_rule(node1, relation, node2=None, direct=True, reversed=False):
    """ Returns True if the edge between node1 and node2 is the given relation type.
    If node2 is not given, searches all linked nodes for the relation type.
    If direct is False, does a node1.con_reach(node2) search.
    """
    if node2 == None:
        # Check all connected nodes.
        for node2 in node1.links:
            if node1.has_rule(relation, node2, direct, reversed): 
                return True
        return False
    if isinstance(node2, str):
        node2 = node1.graph[node2]
    if reversed:
        node1, node2 = node2, node1
    if not direct:
        # If both nodes are the same, they can reach each other.
        # However, the given relation still needs to exist before we return True.
        # This is a special case but not impossible: recusion is-part-of recursion.
        if node1 == node2 \
        and ((not node2 in node1.links) \
        or (not node1.links.edge(node2).relation == relation)):
            return False
        # Check nodes connected to nodes with the given relation.
        return node1.can_reach(node2, 
            traversable=lambda n, e: n == e.node1 and e.relation == relation)
    # Assert that given relation goes from n1 directly to n2.
    if  node1 in node2.links \
    and node2.links.edge(node1).node1 == node1 \
    and node2.links.edge(node1).relation == relation:
        return True
    else:
        return False
    
graph.node.has_rule = has_rule

def is_a(node1, node2, direct=True)           : return node1.has_rule("is-a",           node2, direct)
def is_part_of(node1, node2, direct=True)     : return node1.has_rule("is-part-of",     node2, direct)
def is_opposite_of(node1, node2, direct=True) : return node1.has_rule("is-opposite-of", node2, direct)
def is_property_of(node1, node2, direct=True) : return node1.has_rule("is-property-of", node2, direct)
def is_related_to(node1, node2, direct=True)  : return node1.has_rule("is-related-to",  node2, direct)
def is_same_as(node1, node2, direct=True)     : return node1.has_rule("is-same-as",     node2, direct)
def is_effect_of(node1, node2, direct=True)   : return node1.has_rule("is-effect-of",   node2, direct)

def has_specific(node1, node2, direct=True)   : return node2.has_rule("is-a",           node1, direct)
def has_part(node1, node2, direct=True)       : return node2.has_rule("is-part-of",     node1, direct)
def has_property(node1, node2, direct=True)   : return node2.has_rule("is-property-of", node1, direct)
def has_effect(node1, node2, direct=True)     : return node2.has_rule("is-effect_of",   node1, direct)

graph.node.is_a           = is_a
graph.node.is_part_of     = is_part_of
graph.node.is_opposite_of = is_opposite_of
graph.node.is_property_of = is_property_of
graph.node.is_related_to  = is_related_to
graph.node.is_same_as     = is_same_as
graph.node.is_effect_of   = is_effect_of

graph.node.has_specific   = has_specific
graph.node.has_part       = has_part
graph.node.has_property   = has_property
graph.node.has_effect     = has_effect 

def is_property(node) : return node.has_rule("is-property-of")
def is_related(node)  : return node.has_rule("is-related-to")
def is_effect(node)   : return node.has_rule("is-effect-of")

graph.node.is_property = property(is_property)
graph.node.is_related  = property(is_related)
graph.node.is_effect   = property(is_effect)

#--- NODE RULE RETRIEVAL -----------------------------------------------------------------------------

def enumerate_rules(node, relation, depth=1, reversed=False):
    """ Lists all nodes involving edges of the given relation.
    With reversed=False, returns relations FROM the node: tree -> tree is-a organism -> organism
    With reversed=True, returns relations TO the node: tree -> evergreen is-a tree -> evergreen
    """
    if reversed:
        f = lambda a, b: b.has_rule(relation, a)
    else:
        f = lambda a, b: a.has_rule(relation, b)
    nodes = [n for n in node.links if f(node, n)]
    if depth > 1:
        for n in nodes:
            nodes.extend(n.enumerate_rules(relation, depth-1, reversed))
    return unique(nodes)

graph.node.enumerate_rules = enumerate_rules

def specific(node, depth=1)     : return enumerate_rules(node, "is-a" ,          depth, True)
def parts(node, depth=1)        : return enumerate_rules(node, "is-part-of" ,    depth, True)
def opposites(node, depth=1)    : return enumerate_rules(node, "is-opposite-of", depth)
def properties(node, depth=1)   : return enumerate_rules(node, "is-property-of", depth, True)
def associations(node, depth=1) : return enumerate_rules(node, "is-related-to",  depth)
def aliases(node, depth=1)      : return enumerate_rules(node, "is-same-as",     depth)
def effects(node, depth=1)      : return enumerate_rules(node, "is-effect-of",   depth, True)

def type(node, depth=1)         : return enumerate_rules(node, "is-a",           depth)
def whole(node, depth=1)        : return enumerate_rules(node, "is-part-of",     depth)
def objects(node, depth=1)      : return enumerate_rules(node, "is-property-of", depth)
def causes(node, depth=1)       : return enumerate_rules(node, "is-effect-of",   depth)

graph.node.hypernyms    = graph.node.type         = type
graph.node.hyponyms     = graph.node.specific     = specific
graph.node.holonyms     = graph.node.whole        = whole
graph.node.meronyms     = graph.node.parts        = parts
graph.node.antonyms     = graph.node.opposites    = opposites
graph.node.objects                                = objects
graph.node.perceptonyms = graph.node.properties   = properties
graph.node.relations    = graph.node.associations = associations
graph.node.synonyms     = graph.node.aliases      = aliases
graph.node.effects                                = effects
graph.node.causes                                 = causes

#--- CLUSTER -----------------------------------------------------------------------------------------

def style(graph, relation=True):
    """ Apply styling to match the online Perception module.
    """
    try: __ctx = _ctx
    except:
    	return
    graph.styles.background     = _ctx.color(0.36, 0.36, 0.34)
    graph.styles.root.text      = _ctx.color(1)
    graph.styles.dark.fill      = _ctx.color(0, 0.2)
    graph.styles.important.fill = _ctx.color(0, 0.2)
    if relation:
	    # Associative nodes are green.
	    s = graph.styles.create("related")
	    s.fill = _ctx.color(0.5, 0.7, 0.1, 0.6)
	    graph.styles.guide.append("related", lambda g, n: n.is_related)
	    # Properties are blue.
	    s = graph.styles.create("property")
	    s.fill = _ctx.color(0.25, 0.5, 0.7, 0.7)
	    graph.styles.guide.append("property", lambda g, n: n.is_property)
	    # Ensure that the root node is styled last.
	    graph.styles.guide.order.remove("root")
	    graph.styles.guide.order += ["related", "property", "root"]

# Edge weight increases as more users describe the same rule.
VOTE = 0.05
      
def add_rule(graph, concept1, relation, concept2, context="", author="", 
             weight=0.5, length=1.0, label=""):
    """ Creates an edge between node1 and node2 of the given relation type and context.
    Multiple definitions of the same rule (e.g. by different users) increases the edge's weight.
    Multiple definitions differing in relation or context are currently ignored
    (e.g. a cookie can't be food and be part of food at the same time).
    """
    if relation == "is-opposite-of":
        # is-opposite-of edges are not interesting when looking for a shortest path,
        # because they represent a reversal in logic.
        weight = 0.25
    if author == "":
        # Discourage rules from anonymous authors.
        weight -= 0.25
    if is_robot(author):
        # Robots score less than people.
        weight -= 0.25
    e = graph.edge(concept1, concept2)
    if e and e.relation == relation:# and e.context == context:
    	v = VOTE
    	if is_robot(author): v *= 0.5
        e.weight += v
    else:
        e = graph.add_edge(concept1, concept2, weight, length, label)
        if e:
            e.relation = relation
            e.context  = context
            e.author   = author
    return e
    
graph.graph.add_rule = add_rule

def cluster(concept, relation=None, context=None, author=None, depth=2, max=None, labeled=False, 
            wait=15):
    """ Returns the given Perception query as a graph of connected concept nodes.
    """
    try: graph._ctx = _ctx
    except:
    	pass
    rules = query(concept, relation, context, author, depth, max, wait)
    concept = rules.disambiguate(concept)
    g = graph.create()
    style(g)
    if concept != None:
        g.add_node(concept, root=True)
    for rule in rules:
        e = g.add_rule(
            rule.concept1, 
            rule.relation, 
            rule.concept2,
            rule.context,
            rule.author,
            weight = 0.5 + VOTE*(rule.weight-1)
        )
        if e and labeled:
        	e.label = rule.relation
    return g

#--- CLUSTER HEURISTICS ------------------------------------------------------------------------------

def proper_nouns(graph):
    return [n for n in graph.nodes if n.id != n.id.lower()]

def proper_leaves(graph):
    proper_nouns = graph.proper_nouns
    return [n for n in graph.leaves if n in proper_nouns]
    
graph.graph.proper_nouns = proper_nouns
graph.graph.proper_leaves = proper_leaves

def neighbors(node, nodes=None, distance=2, heuristic=None):
    """ Returns a selection of nearby nodes from the given list.
    A node must be reachable by a shortest path of the maximum given distance.
    A heuristic can furthermore encourage or discourage specific waypoints.
    """
    def _is_nearby(n):
    	path = node.graph.shortest_path(node.id, n.id, heuristic)
    	return path != None and len(path) <= 1+distance
    if nodes == None:
        nodes = node.graph.nodes
    return filter(lambda n: _is_nearby(n), nodes)

graph.node.neighbors = graph.node.neighbours = neighbors

class cost(dict):
    """ A cost matrix for edge relations, used as graph.enumerate_rules() heuristic.
    """
    def __init__(self, costs={}, graph=None):
        self.graph = graph
        for k, v in costs.iteritems():
            self[k] = v
    def tax(self, relation, cost):
        self[relation] = cost
    def __call__(self, id1, id2):
        e = self.graph.edge(id1, id2)
        if self.has_key(e.relation):
            return self[e.relation]
        else:
            return 0
            
heuristic = cost

def graph_enumerate_rules(graph, relation, distance=2, heuristic=None, reversed=False):
    """ Returns nodes in the graph that have given outgoing relation.
    Nodes directly connected to the root are at the beginning of the list,
    followed by nodes sorted by weight (eigenvalue).
    The distance of the shortest path between the root and the node is limited,
    and a heuristic for finding shortest paths can be passed.
    """
    nodes = []
    if graph.root:
        nodes = graph.root.enumerate_rules(relation, 1, not reversed)
    nodes  = sorted(nodes, lambda a, b: (a.betweenness < b.betweenness)*2-1) # XXX - use betweenness or eigenvalue?
    nodes += graph.nodes_by_eigenvalue(-1)
    nodes  = unique(nodes)
    nodes  = filter(lambda n: n.has_rule(relation, reversed=reversed), nodes)
    if graph.root and distance != None:
        if isinstance(heuristic, cost):
            heuristic.graph = graph
        nodes = graph.root.neighbors(nodes, distance, heuristic)
    return nodes
    
graph.graph.enumerate_rules = graph_enumerate_rules

# "Describe what the sun is like" -> red, hot, bright, ...
def graph_properties(graph, distance=2, heuristic=None):
    """ Returns a list of important nodes that are property-of other nodes.
    By default, dislikes is-opposite-of paths.
    A "sun" node might have these direct properties: red, hot, bright, round.
    The algorithm will also find: slow, healthy, dangerous, blue, mysterious, 
    white, exotic, organic, passionate, chaotic, intense, fast, dry.
    """
    if not heuristic:
        heuristic=cost({"is-opposite-of": 10})
    return graph.enumerate_rules("is-property-of", distance, heuristic)

# "Specify concrete examples of a tree" -> oak, linden, ...
def graph_specific(graph, proper=False, fringe=1):
    """ Returns a list of hyponym nodes in the fringe (all if None).
    """
    if fringe:
        nodes = graph.fringe(fringe)
    else:
        nodes = graph.nodes
    if graph.root:
        nodes = filter(lambda n: n.is_a(graph.root, direct=False), nodes)
    else:
        nodes = filter(lambda n: n.has_rule("is-a", direct=True), nodes)
    if proper:
        nodes = filter(lambda n: n in graph.proper_nouns(), nodes)
    return nodes  

# "Illustrate what wild is like" -> landscape, anger, sea, rodeo, ...
def graph_objects(graph, distance=2, heuristic=None):
    """ Returns a list of tangible concepts.
    When the root is an object, returns a list of hyponym leaves. 
    For example, for a "tree" cluster: beech, birch, crapabble, dogwood, linden, ...
    When the root is a property, returns a list of objects.
    For example, for a "wild" cluster: landscape, forest, anger, sea, rodeo, ...
    """
    if not heuristic:
        heuristic=cost({"is-opposite-of": 10})
    if graph.root.is_property:
        nodes = graph.enumerate_rules("is-property-of", distance, heuristic, reversed=True)
        nodes = filter(lambda n: not n.is_property, nodes)
    else:
        nodes = graph.specific(proper=False)
    return nodes

graph.graph.perceptonyms = graph.graph.properties = graph_properties
graph.graph.hyponyms     = graph.graph.specific   = graph_specific
graph.graph.objects      = graph_objects

#### TAXONOMY ######################################################################################## 
# Taxonomies are used to find specific/concrete interpretations of a concept.

def taxonomy(concept, context, author=None, depth=4):
    """ Returns a graph containing only is-a edges.
    """
    return cluster(concept, "is-a", context, author, depth, wait=30)
    
hierarchy = taxonomy

class _range(dict):
    
    def __init__(self):
        """ Creates a taxonomy from a given concept and filters hyponyms from it.
        For example: range.typeface -> Times, Helvetica, Arial, Georgio, Verdana, ...
        For example: range.movie -> Star Wars, Conan The Barbarian, ...
        The dictionary itself contains settings for how graph.specific() is called.
        """
        self.rules = {
            "animal"   : ("animal",   "nature",    3, False),
            "tree"     : ("tree",     "nature",    2, False),
            "flower"   : ("flower",   "nature",    2, False),
            "emotion"  : ("emotion",  "emotion",   2, False),
            "facial_expression" : ("facial expression", "emotion", 1, False),
            "movie"    : ("movie",    "media",     1, True),
            "font"     : ("typeface", "graphics",  2, True),
            "color"    : ("color",    "graphics",  4, False),
            "shape"    : ("shape",    "graphics",  4, False),
            "person"   : ("person",   "people",    4, True),
            "vehicle"  : ("vehicle",  "culture",   4, False),
            "building" : ("building", "culture",   2, False),
            "city"     : ("city",     "geography", 1, True),
            "country"  : ("country",  "geography", 1, True),
            "state"    : ("state",    "geography", 1, True),
        }
    
    def append(self, name, concept, context, fringe=2, proper=False):
        self.rules[name] = (concept, context, fringe, proper)
    
    def _hyponyms(self, concept, context=None, fringe=2, proper=False):
        g = taxonomy(concept, context)
        return sorted([n.id for n in g.hyponyms(proper, fringe=fringe)])
    
    def __getattr__(self, a):
        """ Each attribute behaves as a list of hyponym nodes.
        Attributes are expected to be singular nouns.
        Some of these are fine-tuned in the range, others are generic.
        """
        if a in self.rules:
            concept, context, fringe, proper = self.rules[a]
            return self._hyponyms(concept, context, fringe, proper)
        elif a == "properties":
            g = cluster(None, context="properties", depth=None, wait=30)
            return sorted(g.keys())
        elif a == "basic properties" \
          or a == "basic_properties":
          	return basic_properties
        else:
            a = a.replace("_", " ")
            return self._hyponyms(a, None, 2, False)
    
    def __call__(self, a):
        return self.__getattr__(a)

range = _range()

#### INDEX ########################################################################################### 
# A cached index of shortest paths between concepts.
# You give it a list of concepts and it looks up all the paths between them,
# based on the rules in the Perception database.
# This is essential: we can't create a NodeBox visualization script for each and every concept. 
# We will later need to "solve" how to get from something undefined to something defined.

INDEX = os.path.join(os.path.dirname(__file__), "index")

class _index(dict):
    
    def __init__(self, name="properties"):
        self.name = name
    
    def _get_name(self):
        return self._name
    def _set_name(self, v):
        self._name = v
        self._file = os.path.join(INDEX, v)
        if os.path.exists(self._file):
        	dict.__init__(self, pickle.load(open(self._file)))
        else:
            dict.__init__(self, {})
    name = property(_get_name, _set_name)
    
    def build(self, name, concepts=[], heuristic=None):
        """ Caches the shortest paths between nodes in the given set.
        Retrieves the entire online Perception database as a graph.
        Creates a pickled index file.
        By supplying different sets of concepts, different index names
        and a different heuristic we can build custom indices.
        This proces can take some time (e.g. 30 minutes for 200 concepts on a MacBook Pro).
        """
        self._name = name
        g = cluster(None, depth=None, wait=600)
        if isinstance(heuristic, cost):
            heuristic.graph = g
        index = {}
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                path = g.shortest_path(concept1, concept2, heuristic)
                if concept1 not in index: index[concept1] = {}
                if concept2 not in index: index[concept2] = {}
                if path:
                	index[concept1][concept2] = path[1:-1]
                	index[concept2][concept1] = list(reversed(path[1:-1]))
        f = open(os.path.join(INDEX, self.name), "w")
        pickle.dump(index, f)
        f.close()

    def shortest_path(self, concept1, concept2):
        """ Returns the shortest path between the given concepts (or None).
        """
        if concept1 == concept2: 
        	return [concept2]
        if concept1 in self and \
           concept2 in self[concept1]:
            return [concept1] + self[concept1][concept2] + [concept2]

    def nearest(self, root, concepts):
        """ Returns the concept from the list of concepts that is nearest to the root.
        """
        candidate, distance = None, 1000
        for concept in concepts:
            path = self.shortest_path(root, concept)
            if path and len(path) < distance:
                candidate, distance = concept, len(path)
        return candidate
        
    def sort_by_distance(self, root, concepts):
        """ Returns the list of concepts sorted by distance from root.
        """
        def _cmp(a, b):
            p1 = self.shortest_path(root, a)
            p2 = self.shortest_path(root, b)
            if p1 == None: return  1
            if p2 == None: return -1
            return len(p1) - len(p2)
        return sorted(concepts, _cmp)
        
index = _index()

def _build_properties_index(): 
    index.build(
        "properties",
        range.properties,
        cost({"is-property-of" : -0.25,
              "is-same-as"     : -0.5,
              "is-opposite-of" : 10})
    )

#### SOLVER ########################################################################################## 
# The solver finds the best match between a property and a range of concepts (e.g. creepy <=> flowers).
# To retrieve the creepiest flower, it analyzes the properties of each specific flower.
# For each of these properties, we calculate the shortest path to "creepy".
# Less important properties (further down the list) have less impact on the total score (factor m).
# XXX - how many paths does the human brain take into account (high m, low m?)	
def add_method(name, method):
    setattr(graph.graph, name, method)
graph.add_method = add_method

def score(list, m=0.5):
	""" Returns the sum of the list, where each item is increasingly dampened.
	"""
	n = 0
	for x in list:
		n += x*m
		m = m**2
	return n

# Cache the results from concept cluster graphs.
_SOLVER_CACHE = {}

class IndexError(Exception): pass
class MethodError(Exception): pass

class analysis(dict): pass

class _solver:

    def __init__(self, index="properties", method="properties"):
        self.index = index
        self.method = method
        self.analysis = analysis()
        self.m = 0.5 # score dampener
        
    def _prepare(self):
        if index.name != self.index:
            index.name = self.index
            _SOLVER_CACHE.clear()
        if len(index) == 0:
            raise IndexError, "index '"+index.name+\
                "' to use with solver is empty or non-existent"
        if not hasattr(graph.graph, self.method):
            raise MethodError, "'"+self.method+\
                "' is not an existing cluster method the solver can call"
        self.analysis = analysis()
	
    def _retrieve(self, concept, depth=3, cached=True):
		
		""" Creates a concept cluster graph and returns the results from self.method.
		For example => cluster("sun").properties()
		The results are cached for faster retrieval.
		"""
		
		if not (cached and concept in _SOLVER_CACHE):
			g = cluster(concept, depth=depth)
			_SOLVER_CACHE[concept] = [n.id for n in getattr(g, self.method)()]
		return _SOLVER_CACHE[concept]
	
    def sort_by_relevance(self, root, concepts, threshold=0, weighted=False):
        
        """ Returns the list of concepts sorted by relevance to the root [property].
        
        1) For each of the concepts, a Perception cluster is created.
        2) The cluster is analyzed for [properties] that best describe the concept (eigenvalue).
        3) A cached index of distances between all [properties] is used 
           to decide which [properties] of which concept are closest to the given query (Dijkstra).
        4) A list of winning concepts is returned (closest first).
        
        For example: painful <-> range.emotion = shame, envy, pride, anger, jealousy, sadness, fear, anxiety, ...
        
        The word [properties] can be replaced with another type of concept,
        as long as it is a graph method the solver can call,
        e.g. graph.properties(), graph.specific(), ...
        
        The threshold defines the minimum amount of [properties] a concept must have.
        
        To get absurd results, the returned list can be reversed.
        
        """

        self._prepare()
        candidates = []
        for concept in concepts:
			# Create a cluster of related concepts.
			# Find the [properties] that best describe the concept.
			# Find paths to the root for each [property]. 
			# The length of the paths at the start of the list is important.
			if concept == root:
				S = [[] for i in range_(100)]
			else:
				S = self._retrieve(concept, depth=3, cached=True)
				S = [index.shortest_path(n, root) for n in S]
				S = [path for path in S if path != None]
			if len(S) > threshold: # We can filter out poorly described concepts here.
				self.analysis[concept] = S # Cache the paths for later analysis.
				S = [len(path) for path in S]
				candidates.append((concept, S))
        
        if len(candidates) == 0: 
        	return []
		
		# Find the concept with the least [properties]:
		# this is the maximum amount of paths we can compare to find the best candidate.
        n = min([len(paths) for concept, paths in candidates])
        candidates = [(score(paths[:n], self.m), concept)  for concept, paths in candidates]
        # Best candidates will be at the front of the list.
        candidates.sort()
        if not weighted:
	        candidates = [concept for x, concept in candidates]
        
        # The analysis dictionary contains an overview of the thought process.
        # How each concept travels to the given root.
        for key in self.analysis:
        	self.analysis[key] = self.analysis[key][:n]
        
        return candidates
    
    find = sort_by_relevance

solver = _solver()

#--- ANALOGY -----------------------------------------------------------------------------------------
# Uses the solver to analyze multiple properties of a given object.
# This way we can map objects to a different context: 
# music styles to colors, people to animals, cars to geometric shapes, ...
# e.g. what kind of animal is George W. Bush?

class _analogy:
    
    def __init__(self):
        self.analysis = analysis()
        self.depth = 20 # how many object properties to analyze?
        self.m = 0.9 # score dampener
    
    def _best_first(self, list, candidates=[]):
    	""" Returns a list copy with items that appear in candidates at the head.
    	We use this to implement common sense. 
    	Example: assume we want a color analogy for "water".
    	- Properties for water: cool, clean, wet, transparent, slow, ..., blue, ...
    	- Color concepts: black, blue, green, red, yellow, ...
    	- Obviously, "blue" makes an excellent candidate. 
    	- However, the "blue" property is too far down the list to score highly.
    	- Therefore, we sort the water properties to available colors, putting blue at the front.
    	"""
    	list = [item for item in list]
    	candidates = [item for item in list if item in candidates]
    	for item in reversed(candidates):
    		if item in list:
    			list.remove(item)
    			list.insert(0, item)
    	return list
    
    def __call__(self, object, concepts, properties=[], threshold=0, weighted=False):
        
        """ For each [property] of the given object, sort concepts by relevance.
        An object is a concept that has properties: sea, Darwin, church, sword, cat, ...
        Returns the list of concepts sorted by the relevance score sum.
        
        For example: sword <=> range.animal = hedgehog, scorpion, bee, cat, cheetah, cougar, ...
        
        """
        
        S = analysis([(concept, {}) for concept in concepts])
        p = properties + solver._retrieve(object)
        p = self._best_first(p, candidates=concepts)

        for i, property in enumerate(p[:self.depth]):
        	
            # The score for each concept is the sum of the length of the paths 
            # from the given property to each of the concept's properties, dampened by order.
            A = solver.find(str(property), concepts, threshold)
            A = solver.analysis
            for concept in A:
                A[concept] = [len(path) for path in A[concept]]
                A[concept] = score(A[concept], self.m)
			# Keep track of the scores of all the properties of the given object.
            for concept in A:
                S[concept][property] = A[concept] * self.m**i
        
            # The solver may not be able to find a path to each concept.
            # We then give it the worst possible score.
            if len(A) > 0:
                m = max(A.values()) + 0.00001
                for concept in S:
                    if concept not in A:
                        S[concept][property] = m
        
        self.analysis = S
        
        results = [(sum(S[concept].values()), concept) for concept in S]
        results.sort()
        if not weighted:
            results = [concept for n, concept in results]
        return results

    map_object = __call__

analogy = _analogy()

#### SEARCH-MATCH-PARSE ############################################################################## 

def search_match_parse(query, pattern, parse=lambda x: x, service="google", cached=True, n=10,):
	""" Parses words from search engine queries that match a given syntactic pattern.
	query   : a Google/Yahoo query. Google queries can include * wildcards. 
	pattern : an en.sentence.find() pattern, e.g. as big as * NN
	parse   : a function that filters data from a tagged sentence.
	"""
	import web
	import en
	matches = []
	if service == "google": n = min(n, 4)
	if service == "yahoo" : n = min(n, 10)
	for i in range_(n):
		if service == "google": 
			search = web.google.search(query, start=i*4, cached=cached)
		if service == "yahoo": 
			search = web.yahoo.search(query, cached=cached, start=i*100, count=100)
		for result in search:
			if result.description:
				result.description = result.description.replace(",",", ").replace("  "," ")
				match = en.sentence.find(result.description.lower(), pattern)
				if len(match) > 0 and len(match[0]) > 0:
					x = parse(match[0])
					matches.append(x)
	return matches

def count(list):
	""" Returns a dictionary with the list items as keys and their count as values.
	"""
	d = {}
	for v in list: d[v]  = 0
	for v in list: d[v] += 1
	return d

def clean(word):
	word = word.strip(",;:.?!'`\"-[()]")
	word = word.strip(u"‘“")
	if word.endswith( "'s"): word = word[:-2]
	if word.endswith(u"’s"): word = word[:-2]
	return word.strip()

#--- SIMILE ------------------------------------------------------------------------------------------

def suggest_properties(noun, cached=True):
	""" Learning to Understand Figurative Language: 
		From Similes to Metaphors to Irony,
		Tony Veale, Yanfen Hao
		http://afflatus.ucd.ie/Papers/LearningFigurative_CogSci07.pdf
    
	Uses simile to retrieve properties of nouns.
	For example: troll -> "as ugly as a troll" -> ugly is-property-of troll.
	Requires the Web and Linguistics libraries.
	Returns a dictionary of properties linked to count.
	"""
	import en
	noun = en.noun.article(noun)
	matches = search_match_parse(
		"\"as * as " + noun + "\"",
		"as * as " + noun,
		lambda chunk_: clean(chunk_[1][0]), # as A as a house -> A
		service="google", 
		cached=cached
	)
	matches = filter(lambda word: word not in ("well", "much"), matches)
	return count(matches)

def suggest_objects(adjective, cached=True):
	""" With the reverse logic we can find objects.
	For example: blue -> as blue as the sky -> sky has-property blue.
	"""
	import en
	def _parse(chunk_):
		# as deep as the oceans -> ocean
		noun = clean(chunk_[-1][0])
		if chunk_[-2][0] == "the" and en.is_noun(en.noun.singular(noun)):
			return en.noun.singular(noun)
		return noun
	matches = []
	for adverb in ("a", "an", "the"):
		matches += search_match_parse(
			"\"as " + adjective + " as " + adverb + " *\"",
			"as " + adjective + " as * NN",
			_parse,
			service="google", 
			cached=cached
		)
	matches = filter(lambda word: len(word) > 1 and word not in ("****"), matches)
	return count(matches)

#--- COMPARATIVE -------------------------------------------------------------------------------------

class compare_concepts(list):
	
	def __init__(self, relation, cached=True, n=10):
		""" Comparative search heuristic in the form of: concept1 is-more-important-than concept2.
		Returns a list of (concept1, concept2)-tuples.
		Suggested patterns: "is-more-important-than", "is-bigger-than", "is-the-new", ...
		Requires the Web, Linguistics and Graph libraries.
		T. De Smedt, F. De Bleser
		"""
		matches = search_match_parse(
			"\"" + relation.replace("-"," ") + "\"",
			"NN " + relation.replace("-"," ") + " (a) (an) (JJ) NN",
			lambda chunk_: (clean(chunk_[0][0]), clean(chunk_[-1][0])), # A is bigger than B --> (A, B)
			service="yahoo", 
			cached=cached, 
			n=n
		)
		self.relation = relation.replace(" ","-")
		list.__init__(self, matches)
						
	def graph(self):
		""" Returns a graph with edges connecting concepts.
		Different unconnected clusters will be present in the graph.
		"""
		try: graph._ctx = _ctx
		except:
			pass
		g = graph.create()
		for a, b in self:
			e = g.edge(b, a)
			if not e:
				e = g.add_edge(b, a)
			else:
				e.weight += 1
			if e: e.relation = self.relation.replace(" ", "-")
		style(g, relation=False)
		return g
	
	def rank(self, graph=None):
		""" Returns a list of (concept1, [concept2, ...])-tuples sorted by weight.
		The weight is calculated according to nodes' eigenvalue in a graph.
		Be aware that tuples with the same weight may shuffle.
		For example:
		cmp = perception.compare_objects("is more important than")
		for concept1, comparisons in cmp.rank():
			for concept2 in comparisons:
				print concept1, cmp.comparison, concept2
		>>> life is more important than money
		>>> life is more important than kindness
		>>> ...
		"""
		# Nodes with the highest weight are at the front of the list.
		eigensort = lambda graph, id1, id2: (graph.node(id1).weight < graph.node(id2).weight)*2-1
		if graph == None:
			graph = self.graph()
		r = []
		for node in graph.nodes:
			# Get the id's of all the nodes that point to this node.
			# Sort them according to weight.
		    links = [n.id for n in node.links if node.links.edge(n).node1 == n]
		    links.sort(cmp=lambda a, b: eigensort(graph, a, b))
		    r.append((node.id, links))
		r.sort(cmp=lambda a, b: eigensort(graph, a[0], b[0]))
		return r

def suggest_comparisons(concept1, concept2, cached=True):
	""" With the reverse logic we can find relations between concepts.
	"""
	matches = search_match_parse(
		"\""+concept1+" is * than "+concept2+"\"",
		"is (*) * than",
		lambda chunk_: " ".join(x[0] for x in chunk_[1:-1]), # A is bigger than B --> bigger
		service="google", 
		cached=cached
	)
	return count(matches)

###################################################################################################### 

#solver.index = "properties"
#solver.method = "properties"
#print solver.sort_by_relevance("dark", range("emotion"))
#print solver.sort_by_relevance("bright", range("emotion"))

# BETA+
# - Implemented is-effect-of and has-effect rules.
# - Perception module has a right-click preferences menu for columns.
# - The solver's analysis is deeper (multiple properties per concept examined).
# - The solver uses caching for graph properties.
# - New analogy component.
# - graph.enumerate_rules() sorts according to betweenness instead of eigenvalue.

# BETA
# - query() and cluster() have a wait parameter.
# - Rules now have a weight.
# - search-match-parse, similes and comparatives.
# - Optimized index builder speed by removing reverse paths.
# - Rebuilt properties index.
# - Tested if numerical index paths instead of string index paths 
#   would shrink file size: no difference (due to pickle format?)

# This example plays "the association game": based on a word in WordNet,
# we traverse the network to find a wrong defintion, occasionally giving
# humorous results.
# It's what wordnet.noun_absurd_gloss() does.

background(0.2)
size(500, 500)

try:
    wordnet = ximport("wordnet")
except ImportError:
    wordnet = ximport("__init__")
    reload(wordnet)
    
# Start with any noun that's in WordNet.
the_word = "dictator"
# Traverse up the tree to a more general meaning
# (e.g. hamburger -> sandwich -> food)
word_hypernym = wordnet.noun_hypernym(the_word)
word_hypernym = wordnet.noun_hypernym(word_hypernym[0][0])
word_hypernym = wordnet.noun_hypernym(word_hypernym[0][0])
# Now that we have a more general meaning, go down
# the tree to find a more specific meaning
# (e.g. animal -> dog -> poodle)
word_hyponym = choice(wordnet.noun_hyponym(word_hypernym[0][0]))
# Now, take the glossary of this word
the_definition = wordnet.noun_gloss(word_hyponym[0])

# Display it on screen by concatenating the strings.
text("%s: %s." % (the_word, the_definition), 10, 48, width=WIDTH-20,
     fontsize=38, font="Helvetica-Bold", fill=1)
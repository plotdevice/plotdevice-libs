# Keywords - last updated for NodeBox 1.8.5
# Author: Tom De Smedt <tom@organisms.be>
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

connectives = [
    "I", "the", "of", "and", "to", "a", "in", "that", 
    "is", "was", "he", "for", "it", "with", "as", "his", 
    "on", "be", "at", "by", "i", "this", "had", "not", 
    "are", "but", "from", "or", "have", "an", "they", 
    "which", "one", "you", "were", "her", "all", "she", 
    "there", "would", "their", "we", "him", "been", "has", 
    "when", "who", "will", "more", "no", "if", "out", 
    "so", "said", "what", "u", "its", "about", "into", 
    "than", "them", "can", "only", "other", "new", "some", 
    "could", "time", "these", "two", "may", "then", "do", 
    "first", "any", "my", "now", "such", "like", "our", 
    "over", "man", "me", "even", "most", "made", "after", 
    "also", "did", "many", "before", "must", "through", 
    "back", "years", "where", "much", "your", "way", 
    "well", "down", "should", "because", "each", "just", 
    "those", "eople", "mr", "how", "too", "little",
     "state", "good", "very", "make", "world", "still", 
     "own", "see", "men", "work", "long", "get", "here", 
     "between", "both", "life", "being", "under", "never", 
     "day", "same", "another", "know", "while", "last", 
     "might", "us", "great", "old", "year", "off", 
     "come", "since", "against", "go", "came", "right", 
     "used", "take", "three",
     "whoever", "nonetheless", "therefore", "although",
     "consequently", "furthermore", "whereas",
     "nevertheless", "whatever", "however", "besides",
     "henceforward", "yet", "until", "alternatively",
     "meanwhile", "notwithstanding", "whenever",
     "moreover", "despite", "similarly", "firstly",
     "secondly", "lastly", "eventually", "gradually",
     "finally", "thus", "hence", "accordingly",
     "otherwise", "indeed", "though", "unless"
]

def is_connective(word):
    
    """ Guesses whether the word is a connective.
    
    Connectives are conjunctions such as "and", "or", "but",
    transition signals such as "moreover", "finally",
    and words like "I", "she".
    
    It's useful to filter out connectives
    when guessing the concept of a piece of text.
    ... you don't want "whatever" to be the most important word
    parsed from a text.
    
    """
    
    if word.lower() in connectives:
        return True
    else:
        return False

import sgmllib
class TagStripper(sgmllib.SGMLParser):
    
	def __init__(self):
		sgmllib.SGMLParser.__init__(self)
		
	def strip(self, html):
		self.data = ""
		self.feed(html)
		self.close()
		return self.data
		
	def handle_data(self, data):
	    self.data += data + " "

import re
def strip_tags(str, clean=True):
    
    s = TagStripper()
    str = s.strip(str)
    str = re.sub("[ ]+", " ", str)
    
    if clean:
        lines = str.split("\n")
        str = ""
        for l in lines:
            if len(l.strip()) > 0:
                str += l.strip() + "\n"
        str.strip().strip()
        
    return str.strip()

def keywords(str, top=10, nouns=True, singularize=True, filters=[]):
    
    """ Guesses keywords in a piece of text.
    
    Strips delimiters from the text and counts words occurences.
    By default, uses WordNet to filter out words,
    and furthermore ignores connectives and tags.
    By default, attempts to singularize nouns.
    
    The return value is a list (length defined by top)
    of (count, word) tuples.
    
    For example:
    from urllib import urlopen
    html = urlopen("http://news.bbc.co.uk/").read()
    meta = ["news", "health", "uk", "version", "weather", "video", "sport", "return", "read", "help"]
    print sentence_keywords(html, filters=meta)
    >>> [(6, 'funeral'), (5, 'beirut'), (3, 'war'), (3, 'service'), (3, 'radio'), (3, 'mull'), (3, 'lebanon'), (3, 'islamist'), (3, 'function'), (3, 'female')]
    
    """
    
    if nouns:
        # Attempt to load the WordNet library.
        # When this fails, don't filter for nouns.
        try:
            import wordnet
        except:
            nouns = False
    
    str = strip_tags(str)
    str = str.replace("\n", " ")
    str = str.split(" ")

    count = {}
    for word in str:
        
        word = word.lower()
        
        # Remove special characters.
        # Do this a number of times to counter typos like:: this.
        for i in range(10):
            word = word.strip("(){}[]'\"\r\n\t,.?!;:-*/ ")
        
        # Determine nouns using WordNet.
        # Attempt a lame singularization:
        # if a word is not a noun
        # and it is longer than three characters,
        # and it ends in an s,
        # and the same word without the s IS a noun,
        # then this word is probably a plural.
        noun = False
        if nouns == True:
            if wordnet.is_noun(word):
                noun = True
            elif singularize \
            and len(word) > 3 \
            and word.endswith("s") \
            and wordnet.is_noun(word[:-1]):
                noun = True
                word = word[:-1]
            else:
                noun = False
        
        # Filter for connectives
        # and (by default) keep only nouns.
        if len(word) > 1 \
        and not word in filters \
        and not is_connective(word) \
        and (not nouns or noun):
            if word in count.keys():
                count[word] += 1
            else:
                count[word] = 1
    
    sorted = []
    for word in count.keys():
        sorted.append((count[word], word))
    sorted.sort()
    sorted.reverse()
    
    return sorted[:top]

# Alias for keywords(), so we can do keywords.top()
# instead of keywords.keywords()
def top(str, n=10, nouns=True, singularize=True, filters=[]):
    return keywords(str, n, nouns, singularize, filters)
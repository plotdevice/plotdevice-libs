# Copyright (c) 2008 Tom De Smedt.
# See LICENSE.txt for details.

from random import random, choice, randrange

#### SYMBOLS #########################################################################################

toxic      = u"\u2620"
radiation  = u"\u2622"
biohazard  = u"\u2623"
recycling  = u"\u2672"
arrow1     = u"\u27A1"
arrow2     = u"\u27B2"
heart      = u"\u2764"
bullet     = u"\u2022"
check      = u"\u2714"
cross      = u"\u2715"
telephone  = u"\u260F"
mail       = u"\u2709"
warning    = u"\u26A0"
sad        = u"\u2639"
happy      = u"\u263A"
euro       = u"\u20AC"
pound      = u"\u00A3"
yen        = u"\u00A5"
trademark  = u"\u2122"
copyright  = u"\u00A9"
registered = u"\u00AE"

def superscript(i):
    s = str(i)
    digits = [u"\u2070", u"\u00B9", u"\u00B2", u"\u00B3", u"\u2074", 
              u"\u2075", u"\u2076", u"\u2077", u"\u2078", u"\u2079"]
    for i, digit in enumerate(digits):
        s = s.replace(str(i), digits[i])
    return s

#### PLACEHOLDER TEXT ################################################################################

class _placeholder:

    def __init__(self):
        
        self.str = """
            lorem ipsum dolor sit amet consectetur adipisicing elit sed do 
            eiusmod tempor incididunt ut labore et dolore magna aliqua ut 
            enim ad minim veniam quis nostrud exercitation ullamco laboris 
            nisi ut aliquip ex ea commodo consequat duis aute irure dolor in 
            reprehenderit in voluptate velit esse cillum dolore eu fugiat 
            nulla pariatur excepteur sint occaecat cupidatat non proident 
            sunt in culpa qui officia deserunt mollit anim id est laborum
        """
        self.str = self.str.replace("\n", "")
        self.str = self.str.replace("   ", "")
        self.words = self.str.split(" ")
       
    def sentence(self, n=6):
        """ Generates a placeholder sentence with n words.
        The first character is uppercase and the sentence ends with a point.
        """
        s = ""
        comma = False
        for i in range(n):
            # We don't want the same word twice in a sentence.
            w = choice(self.words)
            while w in s: w = choice(self.words)
            s += w
            # If it's not the first or the last word,
            # there's a 10% chance we add a comma for realistic purposes.
            if not comma and 0 < i < n-2 and random() > 0.9: 
                comma = True
                s += ","
            s += " "
        return s.capitalize().strip() + "."
    
    def paragraph(self, n=10, first=False):
        """ Generates a placeholder paragraph with n sentences.
        """
        # Calling x() returns a random number between 2 and 12.
        x = lambda: randrange(2, 12)
        s = ""
        # The first paragraph in a text starts with the typical "Lorem ipsum dolor...".
        if first:
            s = " ".join(self.words[:x()]).capitalize()+". "
        for i in range(n):
            s += self.sentence(x())
            s += " "
        return s

    def text(self, n=10):
        """ Generates multiple paragraphs of placeholder text.
        """
        short  = lambda: randrange(2, 8)
        middle = lambda: randrange(3, 20)
        long   = lambda: randrange(6, 40)
        s = ""
        first = True
        for i in range(n):
            s += self.paragraph(choice((short, middle, long))(), first)
            s += "\n\n"
            first = False
        return s
        
    __call__ = text

    def kant(self):
        """ Kant Generator, readable placeholder text.
        """
        from nodebox.util import autotext
        from os.path import dirname, join
        s = autotext(join(dirname(__file__), "kant.xml"))
        s = s.replace("    ", "\n").strip()
        s = s.replace("  ", " ")
        return s

    english = kant

placeholder = _placeholder()
#fontsize(10)
#text(placeholder.text(3), 20, 20, width=500)

#### ORPHAN/WIDOW CONTROL ############################################################################

def keep_together(str1, str2, width, widows=1, orphans=1, forward=False):

    """ If text(str1) ends with a widow line, move it to str2.
    If text(str2) starts with an orphan line, move it to str1.
    If forward is True the orphan is not moved to str1, but the end of str1 is moved to str2.
    """

    # An orphan is a string whose height is less than that of n lines.
    keep = lambda str, n: _ctx.textheight(str, width) <= _ctx.textheight(" ") * n

    # Check the end of str1.
    n = str1.split("\n")
    if len(n) > 0 and keep(n[-1], widows) and not str2.startswith("\n"):
        str1 = "\n".join(n[:-1])
        str2 = n[-1]+" "+str2
    # Check the start of str2.
    n = str2.split("\n")
    if not forward and len(n) > 0 and keep(n[0], orphans):
        str1 = str1+" "+n[0]
        str2 = "\n".join(n[1:])

    if forward:
        while len(str1) > 0 and len(n) > 0 and keep(n[0], orphans):
            # Find the last sentence in str1. Push it on str2.
            i = str1.strip()[:-1].rfind(".")
            str2 = str1[i+1:]+str2
            str1 = str1[:i+1]
            n = str2.split("\n")

    return (str1.lstrip(), str2.lstrip())

#### TEXT SPLIT ######################################################################################

def split(txt, width, height, widows=1, orphans=1, forward=True):

    """Splits a text with the first half fitting width and height, given the current font.
    Returns a 2-tuple of (block, remainder).
    """
    
    if width == 0 or height < _ctx.textheight(" "):
        return ("", txt)
    if height > _ctx.textheight(txt, width): 
        return (txt.rstrip("\n"), "")

    i, j, m = len(txt), 0, 2
    txt = txt.replace("\n", " \n")

    # Splitter parameters.
    d = 1.6
    if _ctx.fontsize > 20: d = 1.15

    # Approximate by cutting in large chunks a few times.
    # When it gets down to chunks increasing or decreasing by 10 characters,
    # proceed from word to word.
    h = _ctx.textheight(txt[:i], width)
    while abs(h - height) > _ctx.fontsize():
        if abs(i/m) < 10: break # Increase or decrease becomes too small.
        if h >  height: i -= i/m; m *= d
        if h <= height: i += i/m
        i = int(i)
        h = _ctx.textheight(txt[:i], width)
    i = max(0, min(i, len(txt)))
    # Expand word per word.
    while i < len(txt) and _ctx.textheight(txt[:i], width) <= height:
        i += 1
        while i < len(txt) and txt[i] != " ": 
            i += 1
    # Decrease word per word.
    while i > 1 and _ctx.textheight(txt[:i], width) > height:
        i -= 1
        while i > 1 and txt[i] != " ": 
            i -= 1

    block = txt[:i].lstrip()
    remainder = txt[i:].lstrip()

    # Widow/orphan control.
    if widows > 0 or orphans > 0:
        block, remainder = keep_together(
            block, 
            remainder, 
            width, 
            widows, 
            orphans, 
            forward
        )

    return block.rstrip("\n"), remainder.rstrip("\n")

#### TEXT DIVIDE #####################################################################################

def divide(txt, width, height, widows=1, orphans=1, forward=True):
    """ Splits a text into blocks of equal width and height.
    """
    blocks = []
    block, remainder = split(txt, width, height, widows, orphans, forward)
    while remainder != "":
        blocks.append(block)
        block, remainder = split(remainder, width, height, widows, orphans, forward)
    blocks.append(block)
    return blocks

#### LEGIBLE WIDTH ###################################################################################

def legible_width(txt, chars=70):
    """ Calculates a legible width for the text set in the current font.
    Assumes an optimal of 70 characters per line at fontsize 10pt.
    Smaller lineheight furthermore decreases the width.
    """
    fs = _ctx.fontsize()
    _ctx.fontsize(10)
    str = ""
    for i in range(chars): 
        str += choice("abcdefghijklmnopqrstuvwxyz ")
    w = _ctx.textwidth(str)
    w *= 1.0 * fs / 10
    w *= _ctx.lineheight() / 1.2
    if txt == txt.upper(): 
        w *= 1.5
    _ctx.fontsize(fs)
    return w

#### FIT FONTSIZE ####################################################################################

def fit_fontsize(str, width, height):
    """ Returns the fontsize at which str fits inside a block of width and height.
    """
    # Should add better support for ascenders and descenders here.
    # E.g. if a word contains no descenders (Goo vs. goo) there is more room at the bottom to scale.
    def increase(str, width, height, factor):
        while _ctx.textheight(str, width) < height:
            _ctx.fontsize(_ctx.fontsize()+factor) 
    def decrease(str, width, height, factor):
        while _ctx.textheight(str, width) > height and _ctx.fontsize() > 0:
            _ctx.fontsize(_ctx.fontsize()-factor)
    if str == "" or width < 1 or height < 1:
        return 0.0001
    fs = _ctx.fontsize()
    increase(str, width, height, 10)
    decrease(str, width, height, 3)
    increase(str, width, height, 1)
    decrease(str, width, height, 1)
    x = _ctx.fontsize()
    _ctx.fontsize(fs)
    return max(x, 0.0001)
    
def fit_lineheight(str, width, height):
    """ Increases or decrease the line spacing to fit the text vertically in the box.
    """
    def increase(str, width, height, factor):
        while _ctx.textheight(str, width) < height:
            _ctx.lineheight(_ctx.lineheight()+factor) 
    def decrease(str, width, height, factor):
        while _ctx.textheight(str, width) > height and _ctx.lineheight() > 0.01:
            _ctx.lineheight(_ctx.lineheight()-factor)
    if _ctx.textheight(str, width) <= _ctx.textheight(" ") \
    or _ctx.textheight(str, width) <= 1 \
    or _ctx.fontsize() < 1:
        return _ctx.lineheight()
    if str == "" or width < 1 or height < 1:
        return 0.0001
    lh = _ctx.lineheight()
    increase(str, width, height, 0.1)
    decrease(str, width, height, 0.05)
    increase(str, width, height, 0.01)
    decrease(str, width, height, 0.01)
    x = _ctx.lineheight()
    _ctx.lineheight(lh)
    return max(x, 0.0001)

######################################################################################################

#w = 300
#h = 244
#align(LEFT)
#from time import time
#t = time()
#for i in range(1):
#    fontsize(9)
#    s = placeholder.text(n=4)
#    #s = "blah\nblah\nblah\nblah\nblah\nblah\nblah" # orphan/widow bugs.
#    b, r = split(s, w, h)
#    rect(0, 0, w, h, fill=None, stroke=0, strokewidth=1)
#text(b, 0, fontsize(), width=w, fill=0)
#print time()-t
#text(r, 0, h+fontsize(), w, fill=(1,0,0))    

#fontsize(9)
#lineheight(1.2)
#align(JUSTIFY)
#str = placeholder.text()
#w = legible_width(str)
#blocks = blocks(str, w, 300)
#x = 20
#for block in blocks:
#    text(block, x, 20, w)
#    x += w + 20
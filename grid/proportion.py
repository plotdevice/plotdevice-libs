# Copyright (c) 2008 Tom De Smedt.
# See LICENSE.txt for details.

from math import sqrt
from random import random, shuffle

#### PROPORTION ######################################################################################

PROPORTION_RANDOM      = "random"
PROPORTION_EVEN        = "even"
PROPORTION_FIBONACCI   = "fibonacci"
PROPORTION_FIB         = "fib"
PROPORTION_CONTRAST    = "contrast"

class proportion(list):

    """ A list of values distributed according to an aesthetical principle.
    """

    def __init__(self, n=None, distribution=PROPORTION_EVEN, 
                 sorted=False, reversed=False, shuffled=False, mirrored=False, 
                 repetition=1):
        
        self.golden_ratio = self.phi = 1.61803398875
        
        self.distribution = distribution
        self.sorted       = sorted
        self.reversed     = reversed
        self.shuffled     = shuffled
        self.mirrored     = mirrored
        self.repetition   = repetition
        self._ctx         = None # needed for drawing
        
        if isinstance(n, (list, tuple)):
            # Creates a custom proportion from a list.
            list.__init__(self, n)
            self.generate = lambda n: None
        if n != None:
            self.generate(n)

    def __getitem__(self, i):
        if i >= len(self):
            return 0
        else:
            return list.__getitem__(self, i)

    def copy(self):
        p = proportion(
            None,
            self.distribution, 
            self.sorted, 
            self.reversed,
            self.shuffled,
            self.mirrored,
            self.repetition
        )
        for x in self: p.append(x)
        return p

    def generate(self, n):
        
        """ Generates a range of values according to a proportional distribution.
        
        By default, the distribution is even: all values are equal.
        Other possibilities are:
        random, 
        contrast (a few very large values and many small values),
        golden ratio (using the Fibonacci sequence).
        
        Values are relativized so their sum is 1.0.
        If n is a list, relativize that.
        
        """
        
        r = max(1, self.repetition)
        
        if isinstance(n, list):
            list.__init__(self, n)
        elif n <= 0:
            list.__init__(self, [])
        elif n == 1:
            list.__init__(self, [1.0])
        elif self.distribution == PROPORTION_RANDOM:
            list.__init__(self, [random() for i in range(n/r)])
        elif self.distribution in (PROPORTION_EVEN):
            list.__init__(self, [1.0/n for i in range(n/r)])
        elif self.distribution in (PROPORTION_FIBONACCI, PROPORTION_FIB):
            # Values distributed according to the golden ratio.
            list.__init__(self, [self.fib(i) for i in range(2,(n/r)+2)])  
        elif self.distribution == PROPORTION_CONTRAST:
            # Split the range: 80% are 0.05-0.15 value and 20% are 0.85-1.0 values.
            i = max(1, int(round((n/r) * 0.2)))
            j = (n/r) - i
            if self.reversed: i, j = j, i
            list.__init__(self, [random()*0.15+0.85 for k in range(i)])
            for k in range(j): 
                self.append(random()*0.1+0.05)
        
        # Repeat the range and assert that the list has n elements.
        self *= r
        for i in range(n-len(self)):
            self.append(self[i])
        
        self.relativize()
        
        if self.sorted   : self.sort()
        if self.reversed : self.reverse()
        if self.shuffled : shuffle(self)
        if self.mirrored : self.mirror(self.reversed)

    def relativize(self):
        """ Relativizes the values so they fall between 0.0 and 1.0.
        """
        s = float(sum(self))
        if s > 0:
            list.__init__(self, [x/s for x in self])

    def mirror(self, reversed=False):
        """ Puts the smallest values in the middle of the list,
        then alternates between pushing and appending larger values on the list.
        """
        self.sort()
        if reversed: self.reverse()
        rng = []
        b = True
        for v in self:
            b = not b
            if b: 
                rng.append(v)
            else:
                rng.insert(0, v)
        list.__init__(self, rng)

    def fib(self, n):
        """ The Fibonnaci sequence relates to the golden ratio.
        """
        if n == 0: return 0
        if n == 1: return 1
        a, b = 0, 1
        for i in range(n-1): 
            a, b = b, a+b
        return b
        
    def draw(self, x, y, width=100, height=300):
        for v in self:
            self._ctx.fill(random(), random(), random())
            self._ctx.rect(x, y, width, v*height)
            y += v * height        

#p = proportion(
#    8, "fib", 
#    sorted=False, reversed=True, shuffled=False, mirrored=True,
#    repetition=1)
#
#p.draw(50, 50)
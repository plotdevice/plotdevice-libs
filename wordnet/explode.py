# Author: Tom De Smedt <tom@organisms.be>
# Manual: http://nodebox.net/code/index.php/Explode
# Copyright (c) 2007 by Tom De Smedt.

from nodebox.graphics import CORNER, CENTER

def node(leaves, x, y, angle, vpad=1.0):
    
    """Draws a node in the network
    
    A node is a central oval with branching leaves.
    Each leaf in the list is a string with its description.
    
    """
    
    try: from wordnet import _ctx
    except: pass

    size = _ctx.fontsize()
    _ctx.fontsize(size)
    
    _ctx.oval(x-size*0.25, y-size*0.25, size*0.5, size*0.5)
    
    #Defines a number of degrees to rotate
    #each leaf branch. Leaves branch in relation
    #to the node's branch, defined by the given angle.
    ri = 300.0 / len(leaves)
    ri = min(20, ri)
    r0 = 0 - ri * (len(leaves)-1) * 0.5

    w = size * 5

    for leaf in leaves:

        _ctx.push()
        _ctx.transform(CORNER)
        _ctx.translate(x,y)
        _ctx.rotate(r0)
        _ctx.line(0,0,w,0)
        _ctx.oval(w-1,-1,2,2)
        _ctx.translate(w+_ctx.textwidth(" "), size/3)
        _ctx.rotate(float(-r0*0.5))
        s = _ctx.stroke()
        _ctx.nostroke()
        #Depending on which font is used,
        #the leaf text may (will) not align nicely
        #to the middle of the leaf branch.
        #vpad (vertical padding) can be used to
        #correct this.
        _ctx.text(" "+leaf, 0, 0, outline=True)
        _ctx.stroke(s)
        _ctx.rotate(r0*0.5)
        _ctx.pop()
        
        r0 += ri
        
def explode(name, nodes, x, y, max=40, vpad=1.0):
    
    """Draws a central point named with given name,
    and branching nodes from that point.
    
    """

    try: from wordnet import _ctx
    except: pass
    
    size = _ctx.fontsize()
    _ctx.lineheight(1.2)
    
    if _ctx.stroke() == None: _ctx.stroke(_ctx.fill())
    _ctx.strokewidth(0.5)
    
    #To avoid a clutter of node leaves,
    #limit the number of nodes and shuffle them,
    #so there is a random chance of nodes with
    #a different amount of leaves appearing next
    #to each other.
    #This makes for a harmonious tree.
    nodes = nodes[:max]
    from random import shuffle
    shuffle(nodes)
    
    #Define a minimum number of degrees
    #to rotate each branching node, based
    #on the number of nodes.
    ri = 360.0 / len(nodes)
    ri = min(60, ri)
    r0 = 0
        
    for leaves in nodes:
        
        #Node branches are longer if there are more nodes.
        #This is the inner radius.
        #Nodes that have many leaves branches even further.
        #This is the outer radius.
        inside = size * len(nodes) * 0.1
        outside = size * min(4, len(leaves)) * 7
        w = inside + outside
        
        _ctx.push()
        _ctx.transform(CORNER)
        _ctx.translate(x,y)
        _ctx.rotate(r0)
        _ctx.line(size*1.5,0,w,0)
        node(leaves, w, 0, 0, vpad)
        _ctx.pop()
        
        r0 += ri
    
    f = _ctx.fill()
    _ctx.nofill()
    _ctx.oval(x-size*1.5, y-size*1.5, size*3, size*3)
    _ctx.fill(f)
    
    _ctx.fontsize(size*2)
    _ctx.align(CENTER)
    _ctx.text(name, x-size*10, y+size/2, size*20)
    _ctx.fontsize(size)

draw = explode
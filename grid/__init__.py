### CREDITS ##########################################################################################

# Copyright (c) 2008 Tom De Smedt.
# See LICENSE.txt for details.

__author__    = "Tom De Smedt"
__version__   = "1.9.4.2"
__copyright__ = "Copyright (c) 2008 Tom De Smedt"
__license__   = "GPL"

### NODEBOX GRID #####################################################################################

# The NodeBox Grid library offers a number of tools to work with rows and columns in a page layout. 
# It's like having a combination of InDesign and Excel available in NodeBox. 
# You can use the library to generate flowing columns of text and image grids, 
# automatically apply aesthetic proportions between cells in the grid, create spreadsheet tables with 
# (simple) statistics, define reusable visual styles in a CSS-like way. 
# Numerous of text commands help you for example determine good, legible column widths, 
# apply widow/orphan control to paragraphs, generate lorem ipsum placeholder text.
#
# Central concepts in this library are:
#
# * Grid: rows and columns containing cells. Each cell can be a new grid.
# * Content: a text or a list of images that is divided among the rows and columns in a grid.
# * Proportion: aesthetic relations between the cells in a grid.
# * Style: a description of colors, typography, whitespace that can be attached to cells.
#
# The library has a caching mechanism that allows you to create multi-page documents (e.g. a book), 
# keeping track of the text and images that have already been drawn along the way.

######################################################################################################

import proportion as _proportion
import content as _content
import style
import text

from random import random, shuffle
from types import MethodType, FunctionType
from math import sqrt

### UNIQUE ID ########################################################################################

__unique_id = 0
def _unique_id():
    """ Never returns the same integer.
    """
    global __unique_id
    __unique_id += 1
    return __unique_id

### FORMAT ###########################################################################################
# Useful paper formats.

class format:
    
    def __init__(self):
        self.A4 = (595.2765,     841.89105)
        self.A3 = (self.A4[0]*2, self.A4[1])
        self.A2 = (self.A3[0],   self.A3[1]*2)
        self.A1 = (self.A2[0]*2, self.A2[1])
        self.A0 = (self.A1[0],   self.A1[1]*2)
        self.A5 = (self.A4[0],   self.A4[1]/2)
        self.A6 = (self.A5[0]/2, self.A5[1])
        self.A7 = (self.A6[0],   self.A6[1]/2)
        self.A8 = (self.A7[0]/2, self.A7[1])
        self.C5 = (self.A6[1],   self.A6[0])
        self.page     = self.A4
        self.poster   = self.A2
        self.envelope = self.C5
        self.letter   = (612.2736, 790.8534)
        self.legal    = (612.2736, 1009.1176)
        
    def __call__(self, format):
        if hasattr(self, format):
            return getattr(self, format)

format = format()

### TEXT #############################################################################################
# Rewire the functions in the text module that need a drawing context.

reload(text)
text._keep_together = text.keep_together
text._split = text.split
text._divide = text.divide
text._legible_width = text.legible_width
text._fit_fontsize = text.fit_fontsize

def _update_text_ctx():
    text._ctx = _ctx

def keep_together(str1, str2, width, widows=1, orphans=1, forward=False):
    _update_text_ctx()
    return text._keep_together(str1, str2, width, widows, orphans, forward)

def split(txt, width, height, widows=1, orphans=1, forward=True):
    _update_text_ctx()
    return text._split(txt, width, height, widows, orphans, forward)

def divide(txt, width, height, keep=1):
    _update_text_ctx()
    return text._divide(txt, width, height, keep)

def legible_width(txt, chars=70):
    _update_text_ctx()
    return text._legible_width(txt, width, height, keep)

def fit_fontsize(str, width, height):
    _update_text_ctx()
    return text._fit_fontsize(str, width, height)

text.keep_together = keep_together
text.split = split
text.divide = divide
text.legible_width = legible_width
text.fit_fontsize = fit_fontsize

### CONTENT ##########################################################################################
# This content() wrapper makes more sense than calling content.content(_ctx, data) directly.

def content(data):
    if isinstance(data, _content.content): 
        return data
    return _content.content(_ctx, data)

### PROPORTION #######################################################################################

def proportion(distribution=_proportion.PROPORTION_EVEN, 
               sorted=False, reversed=False, shuffled=False, mirrored=False, 
               repetition=1, n=None):
    p = _proportion.proportion(n, distribution, sorted, reversed, shuffled, mirrored, repetition)
    p._ctx = _ctx
    return p

#### SPLITTER MIXIN ##################################################################################
# Offers a verbose way of retrieving nested grids.

class splitter:
    
    def _jump(self, list):
        # If the row or column has only one cell, reference this cell directly.
        if len(list) == 1: return list[0]
        return list
    
    def _first(self)  : return self._jump(self[0])
    def _second(self) : return self._jump(self[1])
    def _third(self)  : return self._jump(self[2])
    def _fourth(self) : return self._jump(self[3])
    def _fifth(self)  : return self._jump(self[4])
    def _sixth(self)  : return self._jump(self[5])
    
    def _top(self)    : return self._jump(self.row(0))
    def _left(self)   : return self._jump(self.col(0))
    def _bottom(self) : return self._jump(self.row(-1))    
    def _right(self)  : return self._jump(self.col(-1))
    
    first  = property(_first)
    second = property(_second)
    third  = property(_third)
    fourth = property(_fourth)
    fifth  = property(_fifth)
    sixth  = property(_sixth)
    
    top    = property(_top)
    left   = property(_left)
    bottom = property(_bottom)
    right  = property(_right)

#### STATISTICS MIXIN ################################################################################
# Offers simple math statistics on rows and columns.

class statistics(object):
    
    def _count(self):
        """ Counts the number of cells.
        """
        return len(self)
    count = property(_count)
    
    def _used(self):
        """ Counts the cells that have content.
        """
        return len(filter(lambda cell: cell.has_content(), self))
    used = property(_used)
    
    def _empty(self):
        return len(self) - self.used
    empty = property(_empty)
    
    def _numeric(self):
        """ Counts the cells that have numeric content.
        """
        return filter(lambda cell: cell.has_content() and cell.content.is_numeric(), self)
    numeric = property(_numeric)
    
    def _numbers(self):
        """ Returns a list of numerical content found in the cells.
        """
        return [float(cell.content) for cell in self.numeric]
    numbers = property(_numbers)
    
    def _sum(self):
        return sum(self.numbers)
    sum = property(_sum)
    
    def _avg(self):
        return self.sum / len(self.numeric)
    mean = average = avg = property(_avg)
    
    def _min(self):
        return min(self.numbers)
    min = property(_min)

    def _max(self):
        return max(self.numbers)
    max = property(_max)
    
    def _variance(self):
        avg = self.avg
        return sum([(x-avg)**2 for x in self.numbers]) / (len(self.numeric)-1)
    variance = property(_variance)
    
    def _stdev(self):
        return sqrt(self.variance)
    stdev = property(_stdev)

#### ROWS AND COLUMNS ################################################################################

class rows(list, splitter):
    def row(self, i): 
        return self[i]

class columns(list, splitter):
    def column(self, i): 
        return self[i]
    col = column
cols = columns

#--- CELLS -------------------------------------------------------------------------------------------
# Parent class for row and column.

class cells(list, splitter, statistics):
    
    def __init__(self, data=[], parent=None):
        list.__init__(self, data)
        self._id = _unique_id()
        self.parent = parent
        self.name = ""
        
    def __eq__(self, other):
        return self._id == other._id

    def __add__(self, other):
        return cells(list.__add__(self, other))

    def __getslice__(self, i, j):
        """ A slice is a cells object too: you can do statistics and splitting on it.
        """
        slice = list(self)[i:j]
        return cells(slice)

    def _get_property(self, k):
        """ Returns the property of this row 
        if all the cells have the same property, None otherwise.
        """
        p = getattr(self[0], k)
        for cell in self:
            if getattr(cell, k) != p: return None
        return p
        
    def _set_property(self, k, v):
        for cell in self: setattr(cell, k, v)
    
    def _get_root(self): return self._get_property("root")
    root = property(_get_root)

    def _get_styles(self): return self._get_property("styles")
    style = property(_get_styles)
    
    def _get_style(self)    : return self._get_property("style")
    def _set_style(self, v) : self._set_property("style", v)
    style = property(_get_style, _set_style)

    def _get_content(self)    : return self._get_property("content")
    def _set_content(self, v) : self._set_property("content", content(v))
    content = value = property(_get_content, _set_content)

    def _get_content_width(self)  : return self._get_property("content_width")
    def _get_content_height(self) : return self._get_property("content_height")
    content_width  = property(_get_content_width)
    content_height = property(_get_content_height)
    
    def _get_width(self)    : return self._get_property("width")
    def _set_width(self, v) : self._set_property("width", v)
    width = property(_get_width, _set_width)    

    def _get_height(self)    : return self._get_property("height")
    def _set_height(self, v) : self._set_property("height", v)
    height = property(_get_height, _set_height)

    def _get_fixed(self)    : return self._get_property("fixed")
    def _set_fixed(self, v) : self._set_property("fixed", v)
    fixed = property(_get_fixed, _set_fixed)

    def _get_x(self): return 0
    def _get_y(self): return self._get_property("y")
    x = property(_get_x)
    y = property(_get_y)

    def flow_horizontal(self, recursive=True):
        for cell in self:
            cell.flow_horizontal(recursive)

    def flow_vertical(self, recursive=True):
        for cell in self:
            cell.flow_vertical(recursive)
    
#--- ROW ---------------------------------------------------------------------------------------------

class row(cells):

    def column(self, i):
        if i < 0: i = len(self) + i
        return self[i]

    cell = col = column

    def _get_relative_width(self)    : return self.parent.relative_width 
    def _set_relative_width(self, v) : self.parent.relative_width = v
    relative_width = property(_get_relative_width, _set_relative_width)    

    def _get_relative_height(self): 
        return self._get_property("_height")
    
    def _set_relative_height(self, v):
        """ Adjusts the height (0.0-1.0) of the cells in the row.
        The height of other rows is evenly adjusted,
        except that rows containing fixed cells are left untouched.
        """
        p = self[0].parent
        fluid = [row for row in p.rows if not row.fixed and row != self]
        if len(fluid) > 0: 
            d = (v-self._height) / len(fluid)
        for row in fluid:
            for cell in row:
                cell._height -= d 
        for cell in self:
            cell._height = v
            
    relative_height = _height = property(_get_relative_height, _set_relative_height)
    
#--- COLUMN ------------------------------------------------------------------------------------------

class column(cells):

    def row(self, i):
        if i < 0: i = len(self) + i
        return self[i]
        
    cell = row

    def _get_relative_height(self)    : return self.parent.relative_height 
    def _set_relative_height(self, v) : self.parent.relative_height = v
    relative_height = property(_get_relative_height, _set_relative_height)   
    
    def _get_relative_width(self): 
        return self._get_property("_width")
     
    def _set_relative_width(self, v):
        """ Adjusts the width (0.0-1.0) of the cells in the column.
        The width of other columns is evenly adjusted,
        except that columns containing fixed cells are left untouched.
        """
        p = self[0].parent
        fluid = [col for col in p.cols if not col.fixed and col != self]
        if len(fluid) > 0: 
            d = (v-self._width) / len(fluid)
        for col in fluid:
            for cell in col:
                cell._width -= d 
        for cell in self:
            cell._width = v
    
    relative_width = _width = property(_get_relative_width, _set_relative_width)

#### GRID ############################################################################################

class grid(list, splitter, statistics):
    
    def __init__(self, rows=1, columns=1, width=None, height=None, parent=None, name=""):
        
        """ A grid of rows and columns of cells, which are grids themselves.
        """
        
        self._id = _unique_id()
        self.parent = parent
        self.name = name
        
        # By default, a grid has the width and height of its parent,
        # or the canvas width and height if there is no parent.
        if width == None: 
            if self.parent == None:
                width = _ctx.WIDTH
            else:
                width = 1.0
        if height == None: 
            if self.parent == None:
                height = _ctx.HEIGHT
            else:
                height = 1.0   
        self._width = width
        self._height = height
        self.fixed = False

        # Styling and content.
        if parent == None:
            self._styles = style.styles(_ctx, self)
            self._style = "default"
        else:
            self._styles = None
            self._style = None
        self._content = None
        
        # The proportion between the cells in the grid.
        self._proportion = proportion()
        self.clear()
        self.split(rows, columns)
        
        # The order in which cells are drawn.
        self.flow = []
        self._done = False
    
    def _get_proportion(self):
        return self._proportion
    def _set_proportion(self, v):
        """ Sets the proportions of row height and column width in the grid.
        You can supply a single proportion object or a tuple (one for rows and one for columns).
        """
        if isinstance(v, str): v = proportion(distribution=v)
        if isinstance(v, tuple):
            h, v = v
            if isinstance(h, str): h = proportion(distribution=h)
            if isinstance(v, str): v = proportion(distribution=v)
            v = (h, v)
        self._proportion = v
        self.split(len(self.rows), len(self.columns))

    proportion = property(_get_proportion, _set_proportion)

    def arrange(self, horizontal, vertical=None):
        h, v = horizontal, vertical
        if v == None: v = h
        self.proportion = (h, v)
            
    def clear(self):
        """ Clear cell data whilst retaining style and proportion.
        """
        list.__init__(self, [])
        self.rows = rows()
        self.columns = columns()
        self.flow = []
    
    def split(self, y, x, proportion=None, style=None):
        
        """ Splits the grid into different cells, each of which is a new grid.
        Existing rows and columns of cells are retained if possible.
        """
        
        # y => the number of rows
        # x => the number of columns
      
        if proportion != None:
            self.proportion = proportion
        
        y, x = max(1, y), max(1, x)
        if y * x <= 1: 
            self.clear()
            return

        # Append new rows of cells to the bottom of the grid.
        # Append new columns of cells to the right of the grid.        
        n, m = len(self.rows), len(self.columns)
        if m == 0: 
            m = x
        for i in range(y-n):
            for j in range(m):
                g = grid(parent=self, name="cell_"+str(n+i)+str(j))
                list.append(self, g)
        for j in range(x-m):
            for i in range(y):
                g = grid(parent=self, name="cell_"+str(y-i-1)+str(m+j))
                list.insert(self, (y-i)*(m+j), g)

        # Delete excess rows of cells from the bottom of the grid.
        # Delete excess columns of cells from the right of the grid.        
        n, m = len(self.rows), len(self.columns)
        for i in range(n-y):
            for j in range(m): 
                del self[-1]
        for i in range(y):
            for j in range(m-x):
                del self[(y-i)*m-j-1]
        
        # Organize the cells into row and column objects.
        self.rows, self.columns = rows(), columns()
        for i in range(y):
            self.rows.append(
                row([self[i*x+j] for j in range(x)], parent=self))
        for i in range(x):
            self.columns.append(
                column([self[i+j*x] for j in range(y)], parent=self))
    
        # Based on the grid's proportion object, 
        # which is for example a list of logarithmic numbers whose sum is 1.0,
        # assign a width to each column, and a height to each row.
        # Three columns would be sized 17%, 33% and 50% of the parent's width.
        if isinstance(self._proportion, tuple):
            h, v = self._proportion
        else:
            h = self._proportion
            v = self._proportion.copy()
        h.repetition = min(x, h.repetition)
        v.repetition = min(y, v.repetition)
        h.generate(x)
        v.generate(y)
        for i in range(y):
            for j in range(x):
                self[i*x+j]._width = h[j]
                self[i*x+j]._height = v[i]
        
        # Set the style of all the cells in the grid,
        # but not that of this parent grid.
        if style != None:
            for cell in self:
                cell.style = style

        # The flow is always reset.
        self.flow = []
        return self
    
    def update(self):
        self.split(len(self.rows), len(self.columns))    
    
    def _get_root(self):
        if self.parent == None:
            return self
        return self.parent.root
        
    root = property(_get_root)
    
    def flatten(self, containers=False):
        """ Returns a flat list of all cells in the grid.
        If containers is False, grids with further child cells are not included themselves.
        """
        if containers or len(self) <= 1:
            all = [self]
        else:
            all = []
        for cell in self:
            all += cell.flatten(containers)
        return all
    
    all = flatten

    def copy(self, parent=None):
        
        """ Returns a deep copy of the grid.
        """
        
        # Copy content, proportion, styles, current style.
        g = grid(1, 1, self._width, self._height, parent, self.name)
        if self._content:
            g._content = self._content.copy(parent=g)
        if self._proportion:
            g._proportion = self._proportion.copy()
        if self._styles:
            g._styles = self._styles.copy(g)
        g.style = self.style
        
        # A map of cell/column/row id's linking to their copy.
        # This is used to easily copy a grid's flow.
        map = {}
        
        # Copy rows and columns.
        for x in self.rows:
            g.rows.append(row(parent=g))
            map[x._id] = g.rows[-1]
        for x in self.cols:
            g.cols.append(column(parent=g))
            map[x._id] = g.cols[-1]
        
        # Copy all the cells in this grid.
        # Put each of the cells in the right row/column.
        for cell1 in self:
            cell2 = cell1.copy(parent=g)
            g.append(cell2)
            map[cell1._id] = cell2
            for i in range(len(self.rows)):
                if cell1 in self.rows[i]:
                    g.rows[i].append(cell2)
            for i in range(len(self.cols)):
                if cell1 in self.cols[i]:
                    g.cols[i].append(cell2)

        for x in self.flow:
            g.flow.append(map[x._id])

        return g

    def __repr__(self):
        """ Represent as a list when it has rows and columns, with its name otherwise.
        """
        if len(self) > 1:
            return list.__repr__(self)
        else:
            return self.name

    def __eq__(self, other):
        """ Compares two grids based on their unique id's.
        This happens when retrieving a cell's index in a parent grid for example.
        """
        if not isinstance(other, grid): return False
        return self._id == other._id
        
    def __ne__(self, other):
        return not self.__eq__(other)

    def find(self, name):
        """ Returns a cell, row or column by name.
        """
        for cell in self.flatten(containers=True):
            if cell.name == name:
                return cell
        for row in self.rows:
            if row.name == name:
                return row
        for col in self.cols:
            if col.name == name:
                return col
                
    def __getattr__(self, name):
        x = self.find(name)
        if x != None: return x
        raise AttributeError, "grid instance has no attribute '"+name+"'"

    def cell(self, i, j):
        """ Returns the cell in row i, column j.
        """
        return self.rows[i][j]
    
    def __call__(self, i, j):
        return self.cell(i, j)

    def row(self, i):
        """ Returns row i in the grid.
        If a grid is supplied, returns the row in which that grid is a cell.
        """
        if isinstance(i, grid):
            for row in self.rows:
                if i in row: return row
        return self.rows[i]
    
    def column(self, i): 
        if isinstance(i, grid):
            for column in self.columns:
                if i in column: return column   
        return self.columns[i]
        
    col = column
    
    def _get_cols(self)    : return self.columns
    def _set_cols(self, v) : self.columns = v
    cols = property(_get_cols, _set_cols)

    def _get_relative_width(self): 
        if self.parent == None:
            return 1.0
        else:
            return self._width
    def _get_relative_height(self): 
        if self.parent == None:
            return 1.0
        else:
            return self._height
    
    def _set_relative_width(self, v): 
        if self.parent == None: 
            self._width *= v
        else:
            self.parent.column(self).relative_width = v
    
    def _set_relative_height(self, v): 
        if self.parent == None: 
            self._height *= v
        else:
            self.parent.row(self).relative_height = v
            
    relative_width = property(_get_relative_width, _set_relative_width)
    relative_height = property(_get_relative_height, _set_relative_height)

    def _get_width(self):
        """ The absolute width of a cell nested in a grid.
        Multiply the relative widths of all parent grids up to the root container.
        """
        if self.parent == None:
            return self._width
        else:
            return self._width * self.parent.width

    def _get_height(self):
        if self.parent == None:
            return self._height
        else:
            return self._height * self.parent.height
    
    def _set_width(self, v):
        """ The top-level grid's width can be adjusted directly.
        Otherwise, adjust the width of the entire column this grid cell is in.
        """  
        if self.parent == None: 
            self._width = v
        else:
            if self._width == 0:
                v = float(v) / self.parent.width
            else:
                v *= self._width / self.width
            self.parent.column(self).relative_width = v

    def _set_height(self, v): 
        if self.parent == None: 
            self._height = v
        else:
            if self._width == 0:
                v = float(v) / self.parent.width
            else:
                v *= self._height / self.height
            self.parent.row(self).relative_height = v
    
    width  = property(_get_width, _set_width)        
    height = property(_get_height, _set_height) 

    def size(self, w, h, fixed=False, relative=False):
        """ Sets the width and height of the cell, 
        adjusting the width and height of the other cells in the grid.
        Fixed cells are not adjusted (i.e. they always retain the size you gave them).
        """
        self.fixed = fixed
        if relative:
            self.relative_width = w
            self.relative_height = h
        else:
            self.width = w
            self.height = h

    def _get_x(self):
        """ Returns the absolute horizontal position of the column a cell is in.
        """
        x = 0
        if self.parent != None: 
            x += self.parent.x
            for cell in self.parent.row(self):
                if cell == self: break
                x += cell.width
        return x

    def _get_y(self):
        """ Returns the absolute vertical position of the row a cell is in.
        """
        y = 0
        if self.parent != None: 
            y += self.parent.y
            for cell in self.parent.column(self):
                if cell == self: break
                y += cell.height
        return y
        
    x = property(_get_x)
    y = property(_get_y)

    def _get_styles(self):
        """ All grid cells refer to the styles object in the root grid.
        """
        if self.parent != None:
            return self.parent.styles
        else:
            return self._styles

    def _set_styles(self, v): 
        if self.parent != None:
            self.parent.styles = v
        else:
            self._styles = v
            
    styles = property(_get_styles, _set_styles)

    def  has_style(self) : return (self._style != None)
    def _set_style(self, v): self._style = v    
    def _get_style(self):
        """ Grid cells with no style defined inherit the style of the parent grid.
        When the parent's style is not delegated to child cells, assume the "default" style.
        """
        if self._style == None and self.parent != None:
            if not self.styles[self.parent.style].delegate:
                return "default"
            return self.parent.style
        else:
            return self._style
            
    style = property(_get_style, _set_style)

    def  has_content(self)    : return isinstance(self._content, _content.content)
    def _set_content(self, v) : 
        self._content = content(v)
        self._content.parent = self
    def _get_content(self):
        """ Grid cells with no content defined inherit the content of the parent grid.
        """
        if not self.has_content() and self.parent != None:
            return self.parent.content
        else:
            return self._content
            
    content = value = property(_get_content, _set_content)

    # The size of the content is the size of the grid,
    # minus margin and padding.
    
    def _content_width(self):
        s  = self.styles[self.style]
        w  = self.width
        w -= s.margin.left
        w -= s.margin.right
        w -= s.padding.left
        w -= s.padding.right
        return w
    content_width = property(_content_width)
    
    def _content_height(self):
        s  = self.styles[self.style]
        h  = self.height
        h -= s.margin.top
        h -= s.margin.bottom
        h -= s.padding.top
        h -= s.padding.bottom
        return h
    content_height = property(_content_height)
    
    def flow_vertical(self, recursive=True):
        """ Sets the flow so that the grid is filled with content columns-first.
        """
        for column in self.columns:
            for cell in column:
                self.flow.append(cell)
                if recursive: 
                    cell.flow_vertical(recursive)

    def flow_horizontal(self, recursive=True):
        """ Sets the flow so that the grid is filled with content rows-first.
        """
        for row in self.rows:
            for cell in row:
                self.flow.append(cell)
                if recursive: 
                    cell.flow_horizontal(recursive)

    def _reset(self):
        """ Resets the visited flag on this grid.
        """
        self._visited = False
        for cell in self:
            cell._reset()

    def _traverse(self, visit, leave):
        """ Visits cell, traverses the contained cells, leaves and sets visited flag.
        """
        visit(self)
        # If a flow has been defined, visit those cells first.
        # (i.e. they are filled with content before the others).
        for cell in self.flow:
            if isinstance(cell, grid) and not cell._visited:
                cell._traverse(visit, leave)
            if isinstance(cell, (row, column)):
                for cell in cell:
                    if not cell._visited:
                        cell._traverse(visit, leave)
        # By default, visit cells columns-first.
        for column_ in self.columns:
            for cell in column_:
                if not cell._visited:
                    cell._traverse(visit, leave)
        leave(self)
        self._visited = True

    def traverse(self, visit=lambda cell: None, leave=lambda cell: None):
        """ Resets visited flags and recurses cells.
        """
        self._reset()
        self._traverse(visit, leave)
    
    def draw(self, x=0, y=0):
        """ Traverses the grid and draws each cell in the right style.
        """
        def visit(self):
            # Use this cell's style to draw it.
            # Some things get drawn when we leave the cell (clipping mask, border).
            # We store "the things" in self._state so we can reuse them in leave().
            try: s = self.styles[self.style]
            except KeyError:
                raise KeyError, "no style with name '"+self.style+"'"
            self._state = style.begin_grob(s, self, 0, 0)
        def leave(self):
            s = self.styles[self.style]
            style.end_grob(s, self, *self._state)
        _ctx.push()
        _ctx.translate(x, y)
        self._drawn = (x, y) # used in grid.highlight()
        self.traverse(visit, leave)
        _ctx.pop()                

    # Content gets distributed to child cells when the grid is drawn.
    # This should happen at the moment when content is added.
    def distribute(self, explicit=True):
        """ Distributes content to cells than can be drawn (i.e. have no child cells).
        In explicit mode, container grids will no longer contain content.
        """
        def visit(self):
            # Am I a cell which inherits its content from a parent grid?
            if len(self) == 0 and not self.has_content() and self.content != None:
                try: s = self.styles[self.style]
                except KeyError:
                    raise KeyError, "no style with name '"+self.style+"'"
                _ctx.font(s.font, s.fontsize)
                _ctx.lineheight(s.lineheight)
                _ctx.align(style.alignment(s.horizontal))
                c = self.content.next(self.content_width, self.content_height)
                self.content = content(c)
                self.content._distributed = True
        self.traverse(leave=visit)
        # All content has now been distributed to drawable cells.
        # In explicit mode, container grids may no longer contain content.
        def commit(self):
            if len(self) > 0: 
                self._content = content(None)
        def rebuild(self):
            if self.content.is_text() and self.parent:
                if self.parent.content == None:
                    self.parent.content = self.content.copy()
                else:
                    self.parent.content += " "
                    self.parent.content += self.content
                        
        if explicit:
            self.traverse(commit, rebuild)

#-----------------------------------------------------------------------------------------------------

def create(rows=1, columns=1, width=None, height=None, parent=None, name=""):
    return grid(rows, columns, width, height, parent, name)

#### CACHE ###########################################################################################
# A hack to facilitate exporting multiple pages of grids.
# A grid can temporarily be saved, as long as the grid library is not reloaded.
# You can then reload it for the next export, with the next content being drawn.
# This only works in the same NodeBox window:
# you cannot juggle grids between different drawing contexts.
    
def save(grid):
    _content._saved_grid = grid

def load():
    try: g = _content._saved_grid
    except:
        return None
    if g.styles._ctx != _ctx:
        return None
    return g

#### HIGHLIGHT #######################################################################################

def highlight(grid, clr=None, recursive=False, _label="", _group=False):
    
    """ Highlights nested cells in the given grid, row or column.
    Displays the index to append to the given grid to get that cell.
    """
    
    def _draw_label(label, x, y):
        _ctx.font("Verdana", 9)
        w = _ctx.textwidth(label)
        _ctx.nostroke()
        _ctx.fill(0, 0.3)
        _ctx.rect(x+2, y+2, w+10, _ctx.fontsize()+10) #dropshadow
        _ctx.fill(clr)
        _ctx.rect(x, y, w+10, _ctx.fontsize()+10)
        _ctx.fill(0)
        _ctx.text(label, x+5, y+_ctx.fontsize()+5)        

    # When a column or row is supplied,
    # traverse all the grid objects in it and highlight them.
    if isinstance(grid, (column, row)):
        for i in range(len(grid)):
            highlight(grid[i], clr, recursive, _label="["+str(i)+"]", _group=True)
        return

    if clr == None:
        clr = _ctx.color(1, 0, 0)

    _ctx.push()
    try:
        # The grid.draw() has parameters x and y,
        # which define an offset for the grid.
        # Retrieve it so the highlight appears neatly on top.
        dx, dy = grid.root._drawn
    except:
        dx, dy = 0, 0
    
    # 1) The root grid is highlighted with a thick edge.
    # 2) Each root grid in a column or row is highlighted with a thick edge.
    # 3) Recursively nested grids get a thin edge.
    if _label == "":
        _ctx.translate(dx, dy)
        _ctx.strokewidth(5)
    elif _group:
        _ctx.translate(dx, dy)
        _ctx.strokewidth(5)
        _draw_label(_label, grid.x, grid.y)
    else:
        _ctx.strokewidth(1)
        _draw_label(_label, grid.x, grid.y)
    _ctx.stroke(clr)
    _ctx.nofill()
    _ctx.rect(grid.x, grid.y, grid.width, grid.height)
    
    # Label each nested cell.
    # When recursive, call highlight() on each cell.
    for i in range(len(grid.rows)):
        for j in reversed(range(len(grid.rows[i]))):
            cell = grid.rows[i][j]
            label = _label+"("+str(i)+","+str(j)+")"
            if not recursive:
                _draw_label(label, cell.x, cell.y)
            _ctx.strokewidth(1)
            _ctx.stroke(clr)
            _ctx.nofill()
            _ctx.rect(cell.x, cell.y, cell.width, cell.height)
            if recursive:
                highlight(cell, clr, recursive, label)

    _ctx.pop()

# 1.9.4.2
# Bug fix for grid._traverse()

# 1.9.4.1
# Added text.fit_lineheight() companion for text.fit_fontsize().
# Content: txt = txt.rstrip(\n") in default_draw instead of in __init__().
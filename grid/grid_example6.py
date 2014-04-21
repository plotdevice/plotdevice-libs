# SPREADSHEET
# When working with tables and schedules,
# do we go for automation and formulas (e.g. Excel)
# or do we go for visual style (e.g. InDesign)?
# Part of our efforts in the Grid library are trying to combine both.

try: 
    grid = ximport("grid")
except:
    grid = ximport("__init__")
    reload(grid)

# --- DATA --------------------------------------------------------------

# This is our data:
# to-do tasks linking to the months in which they should be realised.
timescale = "months"
schedule = {
    "NodeBox website": [1, 2, 3, 4],
    "Grid library": [5, 6, 7, 8],
    "NodeBox website forum": [1, 3, 5, 7],
    "Perception library": [2, 3, 7, 8, 9, 10],
    "Perception application": [2, 3, 7, 8, 9, 10],
}

# The number of tasks and the number of months (or weeks, years etc.)
# The number of months equals the highest number in the timing lists.
tasks  = len(schedule)
units = max([max(timing) for task, timing in schedule.iteritems()])

# --- STRUCTURE ---------------------------------------------------------

# The grid has a row for each task, plus a header and a footer for totals.
# The grid has a column for each time unit.
g = grid.create(tasks+2, units+2, width=571, height=150)

# To get the layout right, one thing we could do is define a fixed width
# for all the columns. But I want the grid to be able to scale fluidly,
# so I'll use the default relative widths with some tweaks: 
# the first column is 25% of the total width, 
# the last column 15%, the other columns are divided evenly.
g.proportion = "even"
g.left.relative_width = 0.25
g.right.relative_width = 0.15

# --- STYLE -------------------------------------------------------------

# Default styling:
g.styles.fill = color(0.2)
g.styles.stroke = color(0.2)
g.styles.strokewidth = 0.25
g.styles.font = "Helvetica"
g.styles.fontsize = 9
g.styles.padding.top = 3
g.styles.padding.left = 10

# The grid's outer border, with smooth round corners:
s = g.styles.create("fat-border")
s.strokewidth = 2
s.stroke = color(0.2)
s.roundness = 0.1
s.delegate = False
g.style = s.name

# The header row displaying the months has a purple background:
s = g.styles.create("header")
s.background = color(0.4, 0.4, 0.5)
s.fill = color(1)
s.stroke = color(1)
s.font = "Helvetica-Bold"
s.fontsize = 12
g.top.style = s.name

# The leftmost field in the header has a pink background.
# This looks kinda nice.
s = g.styles.create("task", template="header")
s.background = color(1.0, 0.0, 0.5)
g.top.left.style = s.name

# The bottom row displays totals and gets a grey background:
s = g.styles.create("total")
s.background = color(0.9, 0.9, 0.85, 0.7)
s.stroke = color(0.3)
s.strokewidth = 0.25
s.strokewidth.top = 1
s.font = "Helvetica-Bold"
g.bottom.style = s.name

# Months in which work has to be done have a lightblue background:
s = g.styles.create("work")
s.background = color(0, 0.5, 1, 0.1)
s.align = CENTER
s.padding.left = 0

# --- CONTENT -----------------------------------------------------------

# Set the content for the table header.
# On the left is a cell labeled "task", followed by a column for each month.
g.top.left.content = "task"
g.top.right.content = timescale
i = 1
for cell in g.top[1:-1]:
    cell.content = i
    i += 1

# Each task is a new row.
# The leftmost field in each row displays the task description.
# Each month in which a task is worked on gets marked by an "x".
i = 1
for task, timing in schedule.iteritems():
    g.row(i).left.content = task
    for t in timing:
        g.row(i)[t].content = "x"
        g.row(i)[t].style = "work"
    g.row(i).right.content = str(len(timing))
    i += 1

# Calculate the sum of each column:
# that means each cell in the column that has content, except the header.
g.bottom.name = "total"
g.total.left.content = "total"
total = 0
for i in range(1, len(g.total)-1):
    g.total[i].content = g.column(i)[1:].used
g.total.right.content = int(g.total.sum)

g.total[1:-1].style = "total-units"
s = g.styles.create("total-units", template="total")
s.padding.left = 0
s.align = CENTER

# -----------------------------------------------------------------------

g.draw(10, 10)

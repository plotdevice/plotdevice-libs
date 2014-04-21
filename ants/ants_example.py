try:
    ants = ximport("ants")
except:
    ants = ximport("__init__")
    reload(ants)


size(500,500)
speed(200)

def setup():    
    
    # Starts a colony with 30 ants in it.
    global colony
    colony = ants.colony(30, WIDTH/2, HEIGHT/2, 100)
    
    # Add some food in the vicinity of the colony.
    for i in range(8):
        x = 50 + random(WIDTH-100)
        y = 50 + random(HEIGHT-100)
        s = random(20,40)
        colony.foodsources.append(ants.food(x,y,s))
    
def draw():
    
    global colony
    
    fill(0.2)
    rect(0, 0, WIDTH, HEIGHT)
    
    # Draw the hoarded food in the colony.
    fill(0.3)
    s = colony.food
    oval(colony.x-s/2, colony.y-s/2, s, s)
    
    # Draw each foodsource in green.
    # Watch it shrink as the ants eat away its size parameter!
    fill(0.6,0.8,0)
    for f in colony.foodsources:
        oval(f.x-f.size/2, f.y-f.size/2, f.size, f.size)
    
    for ant in colony:
        
        stroke(0.8,0.8,0.8,0.5)
        strokewidth(0.5)
        nofill()
        autoclosepath(False)
        
        # Draw the pheromone trail for each ant.
        # Ants leave a trail of scent from the foodsource,
        # enabling other ants to find the food as well!
        if len(ant.trail) > 0:
            beginpath(ant.trail[0].x, ant.trail[0].y)
            for p in ant.trail: lineto(p.x, p.y)
            endpath()
        
        # Change ant color when carrying food.
        nostroke()
        fill(0.8,0.8,0.8,0.5)
        if ant.has_food: fill(0.6,0.8,0)
        
        # The main ant behaviour:
        # 1) follow an encountered trail,
        # 2) harvest nearby food source,
        # 3) bring food back to colony,
        # 4) wander aimlessly
        ant.forage()
        oval(ant.x, ant.y, 3, 3)
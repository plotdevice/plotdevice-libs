# A game that uses the WiiMote's rotation sensors.
# This is a pretty big example, but also shows nicely how you can construct
# a game in NodeBox. Everything is defined in classes, and the main draw() loop
# is kept as conscise as possible.

# INSTRUCTIONS:
# Point the WiiMote at the screen. Rotate to rotate the canon. Shoot with the A button.
# Try to shoot all the nasties before they reach the bottom of the screen.

from math import sin, cos, pow, sqrt

# Import the library
try:
    # This is the statement you normally use.
    wiinode = ximport("wiinode")
except ImportError:
    # But since these examples are "inside" the library
    # we may need to try something different when
    # the library is not located in /Application Support
    wiinode = ximport("__init__")
    reload(wiinode)

size(600, 400)
speed(30)

##################################################
# Utility methods
##################################################

def coordinates(x0, y0, distance, angle):
    """Calculates the location of a point based on angle and distance.
    See http://nodebox.net/code/index.php/Math"""
    from math import radians, sin, cos
    x1 = x0 + cos(radians(angle)) * distance
    y1 = y0 + sin(radians(angle)) * distance
    return x1, y1

def intersects(c1, c2):
    """Calculates whether two circle-like objects (with x, y and radius attributes) intersect."""
    dst = sqrt(pow(c2.x-c1.x, 2) + pow(c2.y-c1.y, 2))
    return dst < c1.radius + c2.radius
    
##################################################
# Game classes
##################################################

class Nasty(object):

    """The bad guys in the game. They come down with a certain speed; if they 
    reach the bottom before being shot, the game is over."""

    def __init__(self, speed=1.0):
        self.radius = 10.0
        self.y = 0
        self.x = random(self.radius, WIDTH-self.radius)
        self.vy = speed + random(-speed*0.2, speed*0.2)
        # Nasties remember if they are dead. Dead nasties are pruned from the list
        # on each update. (see GameState.update)
        self.dead = False
        self.reachedBottom = False
        
    def update(self):
        self.y += self.vy
        if self.y > HEIGHT:
            # This will be picked up by the GameState.
            self.reachedBottom = True
        
    def draw(self):
        sz = self.radius
        oval(self.x-sz, self.y-sz, sz*2, sz*2,
             fill=(abs(sin(FRAME/10.0*self.vy)), 0.0, 0.0), stroke=1, strokewidth=3)
        
class Bullet(object):
    
    """The hope for humanity. They destroy the nasty if they collide with them."""

    def __init__(self, angle):
        self.angle = angle
        self.dist = 0.0
        # Bullets are dead when they collide with nasties, or fall off-screen
        self.dead = False
        self.radius = 5.0
        self.update()
        
    def update(self):
        # Bullets are shot from the position of the canon
        self.x, self.y = coordinates(WIDTH/2, HEIGHT-20, self.dist, 270-self.angle)
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.dead = True
        self.dist += 8.0
        
    def draw(self):
        sz = self.radius
        oval(self.x-sz, self.y-sz, sz*2, sz*2, fill=(0.2, 0.2, 0.8))
        
class Canon(object):
    
    """The thing that the user controls with the WiiMote."""

    def __init__(self):
        self.angle = 0.0
    
    def update(self):
        global wm
        self.angle = (0.5-wm.roll) * 180

    def draw(self):
        push()        
        arrow_size = 50
        translate(WIDTH/2, HEIGHT)
        rotate(90)
        rotate(self.angle)
        translate(arrow_size/1.2,0)
        arrow(0, 0, arrow_size, fill=1)
        pop()        

class GameState(object):
    
    """This keeps all state in the game."""

    def __init__(self, score=0, level=1, nastySpeed=1.0):
        # A list of all active bullets.
        self.bullets = []
        # After each shot, the canon needs to cool down.
        self.cooldown = 0
        # General speed of the nasties
        self.nastySpeed = nastySpeed
        self.makeNasties()
        self.canon = Canon()
        self.score = score
        self.level = level
        self.gameOver = False
        
    def makeNasties(self):
        self.nasties = []
        for i in range(10):
            self.nasties.append(Nasty(self.nastySpeed))
                
    def update(self):        
        global wm
        
        # Each frame, the canon cools down a bit.
        self.cooldown = max(0, self.cooldown-1)
        self.canon.update()
        
        # The update can only happen if the game is not over.
        if not self.gameOver:
            # If the a button is pushed down, and the canon is cooled down,
            # fire a shot.
            if wm.a and self.cooldown == 0:
                # Firing a shot means adding a bullet. The bullet only
                # needs the angle of the canon; it already knows its position.
                self.bullets.append(Bullet(self.canon.angle))
                # Make the canon "hot", so you have to wait a little to fire
                # a new shot.
                self.cooldown = 3

            # Check intersections between bullets and nasties
            for bullet in self.bullets:
                for nasty in self.nasties:
                    if intersects(bullet, nasty):
                        # If a bullet/nasty collide, both are dead,
                        # and the score is increased.
                        nasty.dead = True
                        bullet.dead = True
                        self.score += 10
                        
            # Some list comprehensions that update the game state:
            # Update all nasties
            [nasty.update() for nasty in self.nasties]
            # Prune the dead nasties
            self.nasties = [nasty for nasty in self.nasties if not nasty.dead]
            # Check if the game is over (if a nasty has reached the bottom)
            self.gameOver = len([nasty for nasty in self.nasties if nasty.reachedBottom]) > 0
            # Update all bullets
            [bullet.update() for bullet in self.bullets]
            # Prune the dead bullets
            self.bullets = [bullet for bullet in self.bullets if not bullet.dead]
            # Check if the level is done (if there are no more nasties left)
            if self.levelDone:
                self.newLevel()

    def _get_levelDone(self):
        """The level is done if there are no more nasties left."""
        return len([nasty for nasty in self.nasties]) == 0
    levelDone = property(_get_levelDone)
    
    def newLevel(self):
        gameState.level += 1
        # Each level, the nasties become faster.
        gameState.nastySpeed += 0.3
        gameState.makeNasties()

    def draw(self):
        # Draw all on-screen elements.
        [nasty.draw() for nasty in self.nasties]
        [bullet.draw() for bullet in self.bullets]
        self.canon.draw()

        # Draw the header
        rect(0, 0, WIDTH, 20, fill=0.3)
        text("LEVEL: %i SCORE: %i" % (self.level, self.score), 10, 13, fill=1, fontsize=10)
        
        # If the game is over, draw the text
        if self.gameOver:
            text("GAME OVER", 0, 160, width=WIDTH, align=CENTER, fill=1, fontsize=60)
            
##################################################
# Main game loop
##################################################

def setup():
    global wm, gameState
    wm = wiinode.WiiMote()
    gameState = GameState()

def draw():
    global wm, gameState
    background(0)
    transform(CORNER)
    wm.update()
    gameState.update()
    gameState.draw()

    # Debug information
    #text("r: %.3f p: %.3f y: %.3f" % (wm.roll, wm.pitch, wm.yaw), 200, 13, fill=1, fontsize=10)
    
def stop():
    global wm
    wm.stop()
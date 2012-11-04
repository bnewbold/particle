
# The dimensions of the particle grid
# (determines how many particles there are)
GRID_SIZE = 25

# Gravity
# (controls how fast particles move toward the mouse)
GRAVITY = .075

# Friction (controls how quickly particles slows down)
FRICTION = .15

ANTIGRAVITY = False


#--------------------------------
# MISC parameters
#--------------------------------

TITLE = "particle game!"
S_WIDTH = 725
S_HEIGHT = 725
FRAMERATE = 40
ROWS, COLUMNS = GRID_SIZE, GRID_SIZE
# Particle size
P_SIZE = 0
# Number of pixels between each particle
MARGIN = int(S_WIDTH/ROWS)
# Offset in pixels from the top left of screen to position grid
OFFSET = MARGIN/2
# Minimum distance (prevents zero-division errors)
MIN_DIST = 0.001

DEBUG_MODE = False

def debug(stuff):
    if DEBUG_MODE:
        print "DEBUG: " + str(stuff)

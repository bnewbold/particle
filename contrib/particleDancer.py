"""
Particle Dancer - a particle/gravity simulator. 
By Jon Lemmon, 5 July 2010

How to use:
    - Just click and hold down your mouse anywhere on the screen and have fun!
    - To put the particles back to their original position, press the RESET
    button on the bottom of the screen.
    - To change the way the particles behave, adjust the parameter values 
    at the beginning of the script.

Requirements:
    The script uses vec2d.py, which can be found at:
    http://pygame.org/wiki/2DVectorClass

    Make sure vec2d.py is in the same folder as this script (or in your
    python path) before running particleDancer.py.

    If the simulation is running slow, try decreasing the GRID_SIZE 
    parameter (located at the beginning of the script).

Additional notes:
    The code for Particle Dancer is actually a heavily modified version of 
    Eric Pavey's vertletCloth simulation script. Eric's original code can 
    be found at: 
    http://www.akeric.com/blog/?page_id=1123

    Particle Dancer was inpsired by the iPhone/iPad app Gravilux:
    http://snibbe.com/projects/interactive/gravilux
"""

import sys
from math import sqrt

from vec2d import Vec2d
import pygame
from pygame.locals import *

#--------------------------------
# MAIN parameters
#--------------------------------

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

TITLE = "particle dance!"
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

class GravityForce(object):
    def __init__(self, position):
        """A force of gravity.

        currentPos can be of type tuple or Vec2d."""
        self.position = None
        self.set_pos(position)

    def get_pos(self):
        return self.position

    def set_pos(self, position):
        """Set the position of the gravity force."""
        if type(position) != type(Vec2d):
            position = Vec2d(position)
        self.position = position


class Particle(object):
    """
    Stores position and velocity.
    """
    def __init__(self, screen, currentPos):
        # Current Position
        self.currentPos = Vec2d(currentPos)
        self.velocity = Vec2d(0, 0)
        # Should the particle be locked at its current position?
        self.color = Color('white')
        self.screen = screen

    def __str__(self):
        return "Particle <%s, %s>"%(self.currentPos[0], self.currentPos[1])

    def draw(self):
        # Draw a circle at the given Particle.
        screenPos = (self.currentPos[0], self.currentPos[1])
        pygame.draw.circle(self.screen, self.color, (int(screenPos[0]),
                                                     int(screenPos[1])), 
                                                     P_SIZE, 0)

    def get_pos(self):
        # TODO: this should return a COPY, not the object itself
        return self.currentPos

    def get_velocity(self):
        # TODO: this should return a COPY, not the object itself
        return self.velocity

    def set_pos(self, position):
        """Set the position of the gravity force."""
        if type(position) != type(Vec2d):
            position = Vec2d(position)
        self.currentPos = position

    def set_velocity(self, velocity):
        """Set the velocity of the particle."""
        if type(velocity) != type(Vec2d):
            velocity = Vec2d(velocity)
        self.velocity = velocity

    def step(self, delta_t, g_force=None):
        """Recalculate the velocity and position for the particle.
        
        Takes the change in time (delta_t) and optionally a gravitational
        force (g_force)."""
        # Calculate gravity
        if g_force != None:
            distance_vector = self.get_pos() - g_force.get_pos()
            distance = (distance_vector).get_length()
            # bypass any zero-division errors
            distance = max(distance, MIN_DIST)
            if not ANTIGRAVITY:
                #self.velocity += -((GRAVITY * delta_t) / (distance ** 2)) * \
                #                 distance_vector.normalized()
                self.velocity += -((GRAVITY * delta_t) / (distance)) * \
                                distance_vector.normalized()
            else:
                self.velocity += ((GRAVITY * delta_t) / (distance)) * \
                                distance_vector.normalized()

        # Calculate friction
        self.velocity -= self.velocity * FRICTION

        # Calculate position
        self.currentPos += (self.velocity * delta_t)
        # make particles wrap around the screen
        self.currentPos[0] = self.currentPos[0] % S_WIDTH
        self.currentPos[1] = self.currentPos[1] % S_HEIGHT


class ParticleSystem(list):
    def __init__(self, screen, rows=16, columns=16, margin=MARGIN, offset=OFFSET):
        super(ParticleSystem, self).__init__()

        self.screen = screen
        self.rows = rows
        self.columns = columns
        self.margin = margin
        self.offset = offset

        # initialize particles
        for x in range(columns):
            for y in range(rows):
                currentPos = (x*self.margin+self.offset, y*self.margin+self.offset)
                self.append(Particle(self.screen, currentPos))

    def draw(self):
        """Draw the particle system onto the screen."""
        for particle in self:
            particle.draw()

    def reset(self):
        """Reset particles to default position."""
        i = 0
        for x in range(self.columns):
            for y in range(self.rows):
                currentPos = (x*self.margin+self.offset, 
                              y*self.margin+self.offset)
                self[i].set_pos(currentPos)
                self[i].set_velocity(Vec2d(0,0))
                i += 1

    def step(self, delta_t, g_force=None):
        """Move all the particles based on change in time (delta_t) and
        gravitational force (g_force)."""
        for particle in self:
            particle.step(delta_t, g_force)

def main():
    # Initial setup
    global ANTIGRAVITY # TODO: get rid of this global variable
    pygame.init()
    screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT + 20))
    clock = pygame.time.Clock()

    # Create a grid of particles
    particleSystem = ParticleSystem(screen, rows=ROWS, columns=COLUMNS)
    backgroundCol = Color('black')

    # Initialize variables
    g_force = None
    reset_flag = False

    # Main loop
    looping = True
    while looping:
        # Keep frames running under FRAMERATE
        clock.tick(FRAMERATE)
        delta_t = clock.get_time()

        # Fill title bar and screen background
        pygame.display.set_caption("%s  FPS: %.2f"%(TITLE, clock.get_fps()) )
        screen.fill(backgroundCol)

        # Draw bottom toolbar
        font = pygame.font.Font(pygame.font.get_default_font(), 10)
        reset_text = font.render("RESET", True, Color('white'), Color('black'))
        reset_rect = reset_text.get_rect().move(5, S_HEIGHT + 5)
        antigravity_text = font.render("ANTI-GRAVITY", True, Color('white'), 
                            Color('black'))
        antigravity_rect = antigravity_text.get_rect().move(S_WIDTH/2 - 20, 
                                                            S_HEIGHT + 5)
        quit_text = font.render("QUIT", True, Color('white'), Color('black'))
        quit_rect = reset_text.get_rect().move(S_WIDTH - 40, S_HEIGHT + 5)
        screen.blit(antigravity_text, antigravity_rect)
        screen.blit(reset_text, reset_rect)
        screen.blit(quit_text, quit_rect)
        toolbar_line = pygame.draw.line(screen, Color('white'), 
                      (0, S_HEIGHT), (S_WIDTH, S_HEIGHT))
        pygame.draw.rect(screen, Color('white'), toolbar_line, 1)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                looping = False

            # Handle mouse-events (create/move/destroy GravityForces,
            # or use toolbar)
            elif event.type == MOUSEBUTTONDOWN:
                mousePos = pygame.mouse.get_pos()
                # Check toolbar buttons
                if reset_rect.collidepoint(mousePos):
                    reset_flag = True
                if antigravity_rect.collidepoint(mousePos):
                    ANTIGRAVITY = not ANTIGRAVITY
                if quit_rect.collidepoint(mousePos):
                    looping = False
                else:
                    if mousePos[1] < S_HEIGHT:
                        g_force = GravityForce(mousePos)
            elif event.type == MOUSEMOTION:
                if g_force != None:
                    mousePos = pygame.mouse.get_pos()
                    g_force.set_pos(mousePos)
                    debug(g_force.get_pos())
            elif event.type == MOUSEBUTTONUP:
                g_force = None

        # Simulate particles
        if reset_flag == True:
            particleSystem.reset()
            reset_flag = False
        particleSystem.step(delta_t, g_force)
        particleSystem.draw()

        # Update the display
        pygame.display.update()

def debug(stuff):
    if DEBUG_MODE:
        print "DEBUG: " + str(stuff)

# Execution from shell/icon:
if __name__ == "__main__":
    print "Running Python version:", sys.version
    print "Running PyGame version:", pygame.ver
    print "Running %s.py"%TITLE
    sys.exit(main())


#!/usr/bin/env python
"""
Particle Game
November 2012

Acknowledgements:
    The script uses vec2d.py, which came from:
        http://pygame.org/wiki/2DVectorClass
    Code based on Particle Dancer by Jon Lemmon

This file has main() and loop(); the former calls the later
"""

import sys
import pygame
from pygame.locals import *

from settings import *
import physics

def main():
    # Initial setup
    global ANTIGRAVITY # TODO: get rid of this global variable
    pygame.init()
    screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT + 20))
    clock = pygame.time.Clock()

    # Create a grid of particles
    particleSystem = physics.ParticleSystem(screen, rows=ROWS, columns=COLUMNS)
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
                        g_force = physics.GravityForce(mousePos)
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

###############################################################################
if __name__ == "__main__":
    print "Running Python version:", sys.version
    print "Running PyGame version:", pygame.ver
    print "Running %s.py"%TITLE
    sys.exit(main())

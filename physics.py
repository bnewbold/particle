
import random

from math import sqrt
from vec2d import Vec2d
from pygame.locals import Color

from settings import *


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


class ParticleSource(object):
    def __init__(self, position, vector, rate, count):
        self.position = position
        self.vector = vector
        self.rate = float(rate)
        self.count = int(count)
        self.delta_t = 0    # time since last fire (milliseconds)

    def step(self, delta_t, particle_system):
        """Step delta_t seconds forward in time.
       
        If it's time to fire a shot and count hasn't been exceeded, fire a new
        particle
        """
        self.delta_t = self.delta_t + delta_t
        if self.delta_t > (1000. / self.rate):
            if self.count > 0:
                self.fire(particle_system)
            self.delta_t = 0.0

    def fuzz(self):
        return Vec2d(random.random(),
                     random.random())

    def fire(self, particle_system):
        self.count -= 1
        p = Particle(self.position)
        # TODO: plus randomness
        p.set_velocity(self.vector + self.fuzz())
        particle_system.append(p)
        debug("squirt: %s" % p)
        

class ParticleSink(object):
    def __init__(self, position, radius):
        self.count = 0
        self.position = position
        self.radius = float(radius)

    def gobble(self, particle_system):
        kill_list = []
        for i in range(len(particle_system)):
            p = particle_system[i]
            if self.radius > abs((self.position - p.get_pos()).get_length()):
                kill_list.append(i)
        kill_list.sort(reverse=True)
        for i in kill_list:
            debug("killing: %s" % i)
            # actually kill
            particle_system.pop(i)
            self.count += 1

class Particle(object):
    """
    Stores position and velocity.
    """
    def __init__(self, currentPos):
        # Current Position
        self.currentPos = Vec2d(currentPos)
        self.velocity = Vec2d(0, 0)
        # Should the particle be locked at its current position?
        self.color = Color('white')

    def __str__(self):
        return "Particle <%s, %s>"%(self.currentPos[0], self.currentPos[1])

    def get_pos(self):
        return Vec2d(self.currentPos)

    def get_velocity(self):
        return Vec2d(self.velocity)

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
    def __init__(self, rows=16, columns=16, margin=MARGIN, offset=OFFSET):
        super(ParticleSystem, self).__init__()

        self.rows = rows
        self.columns = columns
        self.margin = margin
        self.offset = offset

        self.sources = []
        self.sinks = []

        # initialize particles
        for x in range(columns):
            for y in range(rows):
                currentPos = (x*self.margin+self.offset, y*self.margin+self.offset)
                self.append(Particle(currentPos))


    def add_source(self, source):
        self.sources.append(source)

    def add_sink(self, sink):
        self.sinks.append(sink)

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
        for source in self.sources:
            source.step(delta_t, self)
        for sink in self.sinks:
            sink.gobble(self)

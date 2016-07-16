import random
import maya.cmds as cmds
import maya.api._OpenMaya_py2 as om2

import mscreen
reload(mscreen)


class Particle(object):
    def __init__(self):
        super(Particle, self).__init__()
        self.gl = mscreen.drawPoint()
        self.id = 0
        self.mass = 1.0
        self.age = 0
        self.velocity = om2.MVector()

        self.color = mscreen.COLOR_DARKCYAN
        self.size = 5

    def destroy(self):
        mscreen.erase(self.gl)

    @property
    def position(self):
        return self.gl.transform.translation(om2.MSpace.kWorld)

    @position.setter
    def position(self, value):
        self.gl.transform.setTranslation(value, om2.MSpace.kWorld)

    @property
    def size(self):
        return self.gl.size

    @size.setter
    def size(self, value):
        self.gl.size = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self.gl.color = value


class Emitter(object):
    def __init__(self):
        super(Emitter, self).__init__()
        self.rate = 20
        self.position = om2.MVector()
        self._initialVelocity = om2.MVector(0, 1, 0)
        self._randomize = False

    @property
    def initialVelocity(self):
        if self._randomize:
            return self._randomizeVelocity()
        return self._initialVelocity

    @initialVelocity.setter
    def initialVelocity(self, value):
        self._initialVelocity = value

    def randomizeVelocity(self, minimum=None, maximum=None):
        self._randomMinimum = minimum or om2.MVector(-0.1, -0.1, -0.1)
        self._randomMaximum = maximum or om2.MVector(0.1, 0.1, 0.1)
        self._randomize = True

    def _randomizeVelocity(self):
        v = om2.MVector()
        for i in range(3):
            factor = random.random() * 2
            v[i] = self._randomMinimum[i] + (factor * self._randomMaximum[i])
        v += self._initialVelocity
        return v


class ParticleSystem(object):
    def __init__(self):
        super(ParticleSystem, self).__init__()
        self.forces = list()
        self.emitters = list()
        self.ageLimit = None
        self.time = 1
        self.clear()

    def clear(self):
        self.particles = list()
        mscreen.clear()

    def addPoint(self):
        p = Particle()
        p.id = len(self.particles)
        self.particles.append(p)
        return p

    def addEmitter(self, emitter):
        self.emitters.append(emitter)

    def addForce(self, force):
        self.forces.append(force)

    def simulate(self, time):
        if time == 1 and time != self.time:
            self.clear()
            self.time = 1
            return

        if time <= self.time:
            return

        for e in self.emitters:
            for _ in range(e.rate):
                p = self.addPoint()
                p.position = om2.MVector(e.position)
                p.velocity = om2.MVector(e.initialVelocity)

        for p in self.particles:
            if p is None:
                continue
            # update velocity
            for f in self.forces:
                p.velocity += f(p)
            # update position
            p.position += p.velocity
            p.age += 1
            # remove old particle
            if self.ageLimit and p.age > self.ageLimit:
                p.destroy()
                self.particles[p.id] = None

        self.time = time


def simulate(particleSystem):
    time = cmds.currentTime(q=True)
    particleSystem.simulate(int(time))


def bounce(p, groundLevel=0.0):
    f = om2.MVector()
    if p.position.y < groundLevel:
        f.y = -1.5 * p.velocity.y
        p.position = om2.MVector(p.position.x,
                                 groundLevel + 0.01,
                                 p.position.z)
    return f

ps = ParticleSystem()
ps.addForce(lambda p: om2.MVector(0.0, -0.098, 0.0) * p.mass)
ps.addForce(bounce)
ps.ageLimit = 50

e = Emitter()
e.rate = 20
e.position = om2.MVector(0.0, 0.01, 0.0)
e.initialVelocity = om2.MVector(0.0, 1.0, 0.0)
e.randomizeVelocity()
ps.addEmitter(e)

mscreen.registerCallback(lambda: simulate(ps))

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

        self._color = mscreen.COLOR_DARKCYAN
        self.size = 8

    def destroy(self):
        mscreen.erase(self.gl)

    @property
    def speed(self):
        return self.velocity.length()

    @speed.setter
    def speed(self, value):
        self.velocity.normalize()
        self.velocity *= value

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
        speed = self.speed * 0.1
        self.gl.color = [x + speed for x in self._color]


class ParticleSystem(object):
    def __init__(self):
        super(ParticleSystem, self).__init__()
        self.forces = list()
        self.fps = 24
        self._emit = False
        self.lifeSpan = None
        self.clear()

    def clear(self):
        self.particles = list()
        mscreen.clear()

    def addPoint(self):
        p = Particle()
        p.id = len(self.particles)
        self.particles.append(p)
        return p

    def addEmitter(self, source, rate, velocity=None):
        self.time = 0
        self.emitionSource = source
        self.emitionRate = rate
        self.emitionVelocity = om2.MVector(velocity)
        self._emit = True

    def addForce(self, force):
        self.forces.append(force)

    def simulate(self, time):
        if time == 0 and time != self.time:
            self.clear()
            self.time = 0
            return

        if time <= self.time:
            return

        if self._emit:
            for _ in range(self.emitionRate):
                p = self.addPoint()
                p.position = om2.MVector(
                    self.emitionSource.x + (2 * (0.5 - random.random())),
                    self.emitionSource.y,
                    self.emitionSource.z + (2 * (0.5 - random.random())))
                p.velocity = om2.MVector(
                    self.emitionVelocity.x * (2.0 * (0.5 - random.random())),
                    self.emitionVelocity.y,
                    # self.emitionVelocity.y * (2.0 * (0.5 - random.random())),
                    self.emitionVelocity.z * (2.0 * (0.5 - random.random())))

        for _ in range(time - self.time):
            for p in self.particles:
                if p is None:
                    continue
                # update velocity
                for f in self.forces:
                    p.velocity += f * p.mass
                # update position
                p.position += p.velocity
                p.age += 1

                speed = p.speed * 0.4
                p.gl.color = [x + speed for x in p._color]

                if self.lifeSpan and p.age > self.lifeSpan:
                    p.destroy()
                    self.particles[p.id] = None

        self.time = time


def simulate(particleSystem):
    time = cmds.currentTime(q=True)
    particleSystem.simulate(int(time))


ps = ParticleSystem()
ps.addEmitter(om2.MVector(0.0, 3.0, 0.0), 20,
              om2.MVector(0.3, 1.0, 0.3))
ps.addForce(om2.MVector(0.0, -0.098, 0.0))
ps.lifeSpan = 50
mscreen.registerCallback(lambda: simulate(ps))

import random
import maya.api._OpenMaya_py2 as om2
import mscreen
reload(mscreen)  # debug purposes
ZERO_VECTOR = om2.MVector()


class Particle(object):
    def __init__(self):
        super(Particle, self).__init__()
        self.id = 0
        self.age = 0
        self.state = 0
        self.mass = 1.0
        self.velocity = om2.MVector()

        self.gl = mscreen.drawPoint()
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
        return self.gl.color

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

    def randomizeVelocity(self, minimum=(-0.1, -0.1, -0.1),
                          maximum=(0.1, 0.1, 0.1)):
        self._randomMinimum = om2.MVector(minimum)
        self._randomMaximum = om2.MVector(maximum)
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
        self.time = -1
        self._states = list()
        self.addState()
        self.clear()

    def clear(self):
        self.particles = list()
        mscreen.clear()

    def addPoint(self, state=0):
        p = Particle()
        p.id = len(self.particles)
        p.state = state
        self.particles.append(p)
        return p

    def addState(self):
        index = len(self._states)
        forces = list()
        emitters = list()
        ageLimit = None
        self._states.append([forces, emitters, ageLimit])
        return index

    def addForce(self, force, state=0):
        self._states[state][0].append(force)

    def addEmitter(self, emitter, state=0):
        self._states[state][1].append(emitter)

    def setAgeLimit(self, value, state=0):
        self._states[state][2] = value

    def simulate(self, time):
        if time == 1 and time != self.time:
            self.clear()
            self.time = 1
            return
        if time <= self.time:
            return

        for state in self._states:
            emitters = state[1]
            for e in emitters:
                for _ in range(e.rate):
                    p = self.addPoint()
                    p.position = om2.MVector(e.position)
                    p.velocity = om2.MVector(e.initialVelocity)

        for p in self.particles:
            if p is None:
                continue
            # update velocity
            forces = self._states[p.state][0]
            for f in forces:
                p.velocity += f(p)
            # update position
            p.position += p.velocity
            p.age += 1
            # remove old particle
            ageLimit = self._states[p.state][2]
            if ageLimit and p.age > ageLimit:
                self.particles[p.id] = None
                p.destroy()

        self.time = time


def bounce(particleSystem, p, groundLevel=0.0):
    if p.position.y > groundLevel:
        return ZERO_VECTOR

    f = om2.MVector()
    f.y = -1.5 * p.velocity.y
    p.position = om2.MVector(
        p.position.x, groundLevel + 0.01, p.position.z)

    coll = particleSystem.addPoint(state=1)
    coll.position = om2.MVector(p.position)
    coll.color = mscreen.COLOR_GRAY
    coll.size = 2
    return f


def scaleUp(p):
    p.size += 1
    return ZERO_VECTOR


ps = ParticleSystem()

# main particles (state=0)
e = Emitter()
e.rate = 20
e.position = om2.MVector(0.0, 0.01, -10.0)
e.initialVelocity = om2.MVector(0.0, 1.5, 0.5)
e.randomizeVelocity()
ps.addEmitter(e)

ps.addForce(lambda p: om2.MVector(0.0, -0.098, 0.0) * p.mass)  # gravity
ps.addForce(lambda p: bounce(ps, p))
ps.setAgeLimit(50)

# particles on collision (state=1)
state = ps.addState()
ps.setAgeLimit(5, state)
ps.addForce(scaleUp, state)

# get current time
sel = om2.MSelectionList()
sel.add("time1")
fnTime = om2.MFnDependencyNode(sel.getDependNode(0))
time = fnTime.findPlug("outTime", False)

# mscreen "magic"
mscreen.registerCallback(lambda: ps.simulate(int(time.asMTime().value)))

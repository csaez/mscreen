import random
import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)

NUM_CVS = 6
NUM_POINTS = 40

# draw curve cage
CVS = []
for cv in xrange(NUM_CVS):
    p = (random.randint(-10, 10),
         random.randint(0, 20),
         random.randint(-10, 10))
    mscreen.drawPoint(p, mscreen.COLOR_GRAY, size=10)
    CVS.append(p)
mscreen.drawLine(CVS, color=mscreen.COLOR_LIGHTGRAY)

# draw bezier curve
POINTS = []
for i in range(NUM_POINTS):
    t = i/float(NUM_POINTS - 1)
    p = mscreen.bezierInterpolate(t, CVS)
    mscreen.drawPoint(p, mscreen.COLOR_DARKBLUE, 4)
    POINTS.append(p)
mscreen.drawLine(POINTS, color=mscreen.COLOR_LIGHTBLUE)

mscreen.refresh()

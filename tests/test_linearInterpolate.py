import random
import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)

POS_A = (random.randint(-10, 0), random.randint(0, 10), random.randint(-5, 5))
POS_B = (random.randint(0, 10), random.randint(0, 10), random.randint(-5, 5))
NUM_POINTS = 15

# let's linear interpolate stuff
mscreen.drawCurve((POS_A, POS_B), color=mscreen.COLOR_DARKBLUE)
for i in range(NUM_POINTS):
    t = i/float(NUM_POINTS - 1)
    mscreen.drawPoint(
        mscreen.linearInterpolate(t, POS_A, POS_B),
        mscreen.linearInterpolate(t, mscreen.COLOR_LIGHTBLUE,
                                  mscreen.COLOR_CYAN),
        size=4)

mscreen.refresh()

import random
import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)


NUM_CVS = 6
CVS = [(random.randint(-10, 10), random.randint(0, 20),
        random.randint(-10, 10)) for _ in range(NUM_CVS)]

# draw cage
for p in CVS:
    mscreen.drawPoint(p, mscreen.COLOR_DARKGRAY, size=10)
mscreen.drawCurve(CVS, color=mscreen.COLOR_LIGHTGRAY)

# draw bezier
bezier = mscreen.drawCurve(CVS, degree=mscreen.CURVE_BEZIER,
                           color=mscreen.COLOR_LIGHTBLUE)

mscreen.refresh()

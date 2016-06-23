import random

import mscreen
mscreen.clear()
reload(mscreen)


POINTS = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0),
          (-2.0, 0.0, 2.0), (2.0, 0.0, 2.0))

# let's draw a square
square = mscreen.drawCurve(POINTS, color=mscreen.COLOR_GRAY)

# we can move/rotate/scale around
square.move(random.randint(-10, 10), random.randint(0, 10), random.randint(-10, 10))
square.rotate(random.random()*180, random.random()*180, random.random()*180)

# let's draw points on each corner of the square
for p in square.points:
    mscreen.drawPoint(p, color=mscreen.COLOR_LIGHTGRAY, size=4)

# mscreen primitives have a full transform (om2)
xfo = mscreen.drawTransform(square.transform)

# refresh the viewport, this is done explicitly to not slow down batch drawing
mscreen.refresh()


# What about removing stuff?
mscreen.erase(xfo)  # it can be done selectively
mscreen.refresh()

mscreen.clear()  # or just clear the entire screen
mscreen.refresh()

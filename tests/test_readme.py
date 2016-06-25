import random
import mscreen

mscreen.clear()
reload(mscreen)

# let's draw a square
POINTS = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0),
          (-2.0, 0.0, 2.0), (2.0, 0.0, 2.0))
square = mscreen.drawCurve(POINTS, color=mscreen.COLOR_GRAY)

# we can move/rotate/scale it around
square.move(random.randint(-10, 10), random.randint(0, 10), random.randint(-10, 10))
square.rotate(random.random()*180, random.random()*180, random.random()*180)

# mscreen primitives have a full transform (om2)
# let's draw it too!
xfo = mscreen.drawTransform(square.transform)

# let's draw a point on each corner
for p in square.points:
    mscreen.drawPoint(p, color=mscreen.COLOR_LIGHTGRAY, size=4)

# refresh the viewport, this is done explicitly to not slow down batch drawing
mscreen.refresh()

# What about removing stuff?
mscreen.erase(xfo)  # it can be done selectively
mscreen.refresh()

mscreen.clear()  # or just clear the entire screen
mscreen.refresh()

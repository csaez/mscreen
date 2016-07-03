# Overview
`mscreen` is a convenient library allowing to easily draw openGL on Maya's
viewport.

The goal is to offer TDs/TAs an easy way to draw basic GL primitives as visual
feedback during debuging and/or in non-critical tools (the library is
implemented in python, do not expect _high performance_).

## Features
Here's a quick demo of the main features:

```python
import random
import mscreen

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
```

Please check the [tests](https://github.com/csaez/mscreen/tree/master/tests) for
more examples.

## License
`mscreen` is licensed under MIT, use at your own risk.


## Contribuiting
- [Check for open issues](https://github.com/csaez/mscreen/issues) or open a fresh issue to start a discussion around a feature idea or a bug.
- Fork the [mscreen repository on Github](https://github.com/csaez/mscreen) to start making your changes (make sure to isolate your changes in a local branch).
- Write a test which shows that the bug was fixed or that the feature works as expected.
- Send a pull request and bug me until it gets merged and published. :)

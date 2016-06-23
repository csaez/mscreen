# Overview
`mscreen` is a convenient library allowing to easily draw openGL on Maya's
viewport.

The goal is to offer TDs/TAs an easy way to draw basic GL primitives as visual
feedback during debuging and/or in non-critical tools (the library is
implemented in python, do not expect _high performance_).

## Features
The feature set is quite sketchy at the moment, but here's a quick demo:

```python
import random
import mscreen


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
```

Please check the [tests](https://github.com/csaez/mscreen/tree/master/tests) for
more examples.

## License
`mscreen` is licensed under MIT, use at your own risk.


## Contribuiting
Please start a thread at [github's
issues](https://github.com/csaez/mscreen/issues) to discuss features or changes
in the code, it's early days and all code is likely to evolve quite a bit.

Again, __please don't start any work before having a discussion__. I really
appretiate your contributions and would love to merge them back, but
pull requests are not likely to be accepted until reach
[v1.0.0](https://github.com/csaez/mscreen/milestones/v1.0.0).

# Overview
`mscreen` is a convenient library allowing to easily draw openGL on Maya's
viewport.

The goal is to offer TDs/TAs an easy way to draw basic GL primitives as visual
feedback during debuging and/or in non-critical tools (the library is
implemented in python, _do not expect high performance_).

## Features

The feature set is quite sketchy at the moment, but here's a quick demo:

```python
import mscreen


# Lets draw some squares...
POINTS = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0),
(-2.0, 0.0, 2.0), (2.0, 0.0, 2.0))

RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
BLUE = (0.0, 0.0, 1.0)

redSq = mscreen.drawLine(POINTS, RED)

greenSq = mscreen.drawLine(POINTS, GREEN)
greenSq.rotate(90, 0, 0)

blueSq = mscreen.drawLine(POINTS, BLUE)
blueSq.rotate(90, 90, 0)

# @note: lines fully support transformations, you can access it's
#        MTransformationMatrix (om2) by calling my_line.transform.
#        Or offset the current transform via move/rotate/scale methods.

# refresh the view, this is done explicitly to not slow down batch drawing
mscreen.refresh()
```

```python
# What about removing lines?
mscreen.erase(greenSq)  # it can be done selectively
mscreen.refresh()

mscreen.clear()  # or just wipeout the entire screen
mscreen.refresh()
```

## License

`mscreen` is licensed under MIT, use at your own risk.


## Contribuiting

It's early days, but please start a thread at [github's
issues](https://github.com/csaez/mscreen/issues) to discuss features or changes
on the code, the project is on very early alpha stages and all code is subject
to evolve quite a bit.

__Please don't start any work before having a discussion__. I really appretiate
your contributions and would love to merge your extensions back, but pull
requests are not likely to be accepted until we move to beta (let's iterate
quickly and try new things for now).

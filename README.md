`mscreen` is a convenient library allowing to easily draw openGL primitives on
Maya's viewport.

The goal is to offer TDs/TAs an easy way to draw basic GL primitives as visual
feedback during debuging or on non performance critical custom tools (the
library is implemented in python).

## Features

The feature set is quite limited at sketchy at the moment, but here's a quick
demo:

```python
import mscreen


# Lets draw some squares...
POINTS = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0,-2.0), (-2.0, 0.0, 2.0), (2.0, 0.0, 2.0))

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

It's still early days, but please start a thread on [the project's issues]() to
discuss features or changes on the structure of the code, the project is on
very early alpha stages and all code is subject to evolve quite a bit.

__Please don't start any work before having a discussion__, pull requests are
not likely to be accepted (this will change as soon as we move to beta, let's
iterate quickly and try new things for now).

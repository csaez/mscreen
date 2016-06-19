# Overview
`mscreen` is a convenient library allowing to easily draw openGL on Maya's
viewport.

The goal is to offer TDs/TAs an easy way to draw basic GL primitives as visual
feedback during debuging and/or in non-critical tools (the library is
implemented in python, do not expect _high performance_).

## Features
The feature set is quite sketchy at the moment, but here's a quick demo:

```python
import mscreen


# Lets draw some squares...
POINTS = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0),
          (-2.0, 0.0, 2.0), (2.0, 0.0, 2.0))

mscreen.drawLine(POINTS, mscreen.COLOR_RED)

sq1 = mscreen.drawLine(POINTS, mscreen.COLOR_GREEN)
sq1.rotate(90, 0, 0)

sq2 = mscreen.drawLine(POINTS, mscreen.COLOR_BLUE)
sq2.rotate(90, 90, 0)


# refresh the viewport, this is done explicitly to not slow down batch drawing
mscreen.refresh()
```

```python
# What about removing lines?
mscreen.erase(sq1)  # it can be done selectively
mscreen.refresh()

mscreen.clear()  # or just clear the entire screen
mscreen.refresh()
```

> `mscreen` primitives fully support transformations, you can access its
> `MTransformationMatrix` (OpenMaya 2.0) by calling `my_prim.transform`.
>
> In addition you can offset the current transform via `move`/`rotate`/`scale`
> convenience methods.

Please check [`tests`](https://github.com/csaez/mscreen/tree/master/tests) for
more examples.

## License
`mscreen` is licensed under MIT, use at your own risk.


## Contribuiting
Please start a thread at [github's
issues](https://github.com/csaez/mscreen/issues) to discuss features or changes
in the code, the project it's early days and all code is likely to evolve quite
a bit.

Again, __please don't start any work before having a discussion__. I really
appretiate your contributions and would love to merge them back, but
pull requests are not likely to be accepted until reach
[v1.0.0](https://github.com/csaez/mscreen/milestones/v1.0.0).

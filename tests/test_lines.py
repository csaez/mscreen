import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)


POINTS = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0),
          (-2.0, 0.0, 2.0), (2.0, 0.0, 2.0))

# Lets draw some squares...
mscreen.drawCurve(POINTS, color=mscreen.COLOR_RED)

sq1 = mscreen.drawCurve(POINTS, color=mscreen.COLOR_GREEN)
sq1.rotate(90, 0, 0)

sq2 = mscreen.drawCurve(POINTS, color=mscreen.COLOR_BLUE)
sq2.rotate(90, 90, 0)

mscreen.refresh()

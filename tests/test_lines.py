import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)


POINTS = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0),
          (-2.0, 0.0, 2.0), (2.0, 0.0, 2.0))

# Lets draw some squares...
mscreen.drawLine(POINTS, mscreen.COLOR_RED)

sq1 = mscreen.drawLine(POINTS, mscreen.COLOR_GREEN)
sq1.rotate(90, 0, 0)

sq2 = mscreen.drawLine(POINTS, mscreen.COLOR_BLUE)
sq2.rotate(90, 90, 0)

mscreen.refresh()

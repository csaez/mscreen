import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)


# Lets draw some squares...
RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
POINTS = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0),
          (-2.0, 0.0, 2.0), (2.0, 0.0, 2.0))


redSq = mscreen.drawLine(POINTS, RED)

greenSq = mscreen.drawLine(POINTS, GREEN)
greenSq.rotate(90, 0, 0)

blueSq = mscreen.drawLine(POINTS, BLUE)
blueSq.rotate(90, 90, 0)

mscreen.refresh()

import mscreen
reload(mscreen)  # debugging purposes


points = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0))
colors = (mscreen.COLOR_GRAY, mscreen.COLOR_RED, mscreen.COLOR_GREEN)
mscreen.drawTriangle(points, colors)

mscreen.refresh()

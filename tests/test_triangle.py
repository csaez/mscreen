import mscreen
reload(mscreen)  # debugging purposes


points = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0))
colors = (mscreen.COLOR_RED, mscreen.COLOR_GREEN, mscreen.COLOR_BLUE)
mscreen.drawTriangle(points, colors)

yellow = mscreen.drawTriangle(points, mscreen.COLOR_YELLOW)
yellow.rotate(y=180)

mscreen.refresh()

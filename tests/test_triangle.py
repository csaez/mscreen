import random
import mscreen
reload(mscreen)  # debugging purposes


NUM_POINTS = 50
COLORS = (
    mscreen.COLOR_BLACK,
    mscreen.COLOR_GRAY,
    mscreen.COLOR_RED,
    mscreen.COLOR_GREEN,
    mscreen.COLOR_BLUE,
    mscreen.COLOR_YELLOW,
    mscreen.COLOR_MAGENTA,
    mscreen.COLOR_CYAN,
    mscreen.COLOR_WHITE,
)

POINTS = ((2.0, 0.0, 2.0), (2.0, 0.0, -2.0), (-2.0, 0.0, -2.0))
tr = mscreen.drawTriangle(POINTS, colors=[mscreen.COLOR_GRAY, mscreen.COLOR_RED, mscreen.COLOR_GREEN])

mscreen.refresh()

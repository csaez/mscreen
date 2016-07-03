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

# Lets draw some points...
for i in range(NUM_POINTS):
    pos = ((random.randint(-5, 5),
            random.randint(0, 10),
            random.randint(-5, 5)))
    mscreen.drawPoint(pos, color=COLORS[i % 9], size=random.randint(1, 10))

mscreen.refresh()

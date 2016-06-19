import random
import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)

# Lets draw some points...
NUM_POINTS = 50
COLOURS = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
    (1.0, 1.0, 0.0),
    (1.0, 0.0, 1.0),
    (0.0, 1.0, 1.0),
)

for i in range(NUM_POINTS):
    pos = ((random.randint(-5, 5),
            random.randint(-5, 5),
            random.randint(-5, 5)))
    mscreen.drawPoint(pos, colour=COLOURS[i % 6], size=random.randint(1, 10))

mscreen.refresh()

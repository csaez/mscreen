import random
import mscreen
reload(mscreen)  # debugging purposes


# Lets draw a few matrices...
for _ in range(10):
    xfo = mscreen.drawTransform()
    xfo.size = max(0.4, random.random() * 4)
    xfo.move(random.randint(-5, 5),
             random.randint(0, 10),
             random.randint(-5, 5))

mscreen.refresh()

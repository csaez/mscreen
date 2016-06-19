import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)

POS_A = (-4.0, 1.0, 0.0)
POS_B = (4.0, 1.0, 0.0)
NUM_POINTS = 15

# let's linear interpolate stuff
mscreen.drawLine((POS_A, POS_B), mscreen.COLOR_DARKBLUE)
for i in range(NUM_POINTS):
    t = i/float(NUM_POINTS - 1)
    mscreen.drawPoint(
        mscreen.linearInterpolate(t, POS_A, POS_B),
        mscreen.linearInterpolate(t, mscreen.COLOR_LIGHTBLUE,
                                  mscreen.COLOR_CYAN),
        size=4)

mscreen.refresh()

import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)

# Lets draw a few matrices...
xfo1 = mscreen.drawTransform()

xfo2 = mscreen.drawTransform()
xfo2.size = 0.5
xfo2.move(x=2)

xfo3 = mscreen.drawTransform()
xfo3.size = 2
xfo3.move(x=5)

mscreen.refresh()

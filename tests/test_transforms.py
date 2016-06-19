import mscreen

mscreen.clear()
mscreen.refresh()

reload(mscreen)

# Lets draw a few matrices...
mscreen.drawTransform()

xfo1 = mscreen.drawTransform()
xfo1.size = 0.5
xfo1.move(x=2)

xfo2 = mscreen.drawTransform()
xfo2.size = 2
xfo2.move(x=5)

mscreen.refresh()

import maya.cmds as cmds
import mscreen

mscreen.clear()
reload(mscreen)


# create a locator to drive mscreen prim
loc = cmds.createNode('transform')

# create a curve
points = ((3, 2), (-3, 0), (3, -2), (-1, 3), (-1, -3), (3, 2))
star = mscreen.drawCurve(points, color=mscreen.COLOR_LIGHTYELLOW)

# parent the curve to the locator
star.parent(loc)

mscreen.refresh()

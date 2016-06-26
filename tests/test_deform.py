import random
import maya.api.OpenMaya as om2

import mscreen
mscreen.clear()
reload(mscreen)


def deformById(curve, mobjects):
    points = []
    for o in mobjects:
        if o.isNull() or not len(om2.MFnDagNode(o).fullPathName()):
            return False
        fn = om2.MFnTransform(o)
        points.append(fn.translation(om2.MSpace.kTransform))
    curve.points = points
    return True


NUM_POINTS = 4
POINTS = [om2.MVector([random.randint(-10, 10) for _ in range(3)])
          for _ in range(NUM_POINTS)]

# create a bezier curve with `NUM_POINTS` control points
cage = mscreen.drawCurve(POINTS, color=mscreen.COLOR_GRAY)
crv = mscreen.drawCurve(POINTS, degree=mscreen.CURVE_BEZIER,
                        color=mscreen.COLOR_GREEN)

# lets create a transform node per control point
objs = []
for i in range(NUM_POINTS):
    fn = om2.MFnTransform()
    mobject = fn.create()
    fn.setTranslation(POINTS[i], om2.MSpace.kTransform)
    objs.append(mobject)


# add callback moving control points according to mobjects
cage.registerCallback(lambda x: deformById(x, objs))
crv.registerCallback(lambda x: deformById(x, objs))

mscreen.refresh()

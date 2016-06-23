# Copyright (R) 2016 Cesar Saez
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import math
import logging
logger = logging.getLogger(__name__)

try:
    import maya.cmds as mc
    import maya.OpenMaya as om
    import maya.OpenMayaUI as omui
    import maya.OpenMayaRender as omr
    import maya.api.OpenMaya as om2
except ImportError:
    import mock
    logger.debug('Maya not found')
    mc = om = omui = omr = om2 = mock.MagicMock()


# color constants
COLOR_BLACK = (0.0, 0.0, 0.0)
COLOR_GRAY = (0.5, 0.5, 0.5)
COLOR_RED = (1.0, 0.0, 0.0)
COLOR_GREEN = (0.0, 1.0, 0.0)
COLOR_BLUE = (0.0, 0.0, 1.0)
COLOR_YELLOW = (1.0, 1.0, 0.0)
COLOR_MAGENTA = (1.0, 0.0, 1.0)
COLOR_CYAN = (0.0, 1.0, 1.0)
COLOR_WHITE = (1.0, 1.0, 1.0)
COLOR_DARKGRAY = (0.25, 0.25, 0.25)
COLOR_DARKRED = (0.75, 0.0, 0.0)
COLOR_DARKGREEN = (0.0, 0.75, 0.0)
COLOR_DARKBLUE = (0.0, 0.0, 0.75)
COLOR_DARKYELLOW = (0.75, 0.75, 0.0)
COLOR_DARKMAGENTA = (0.75, 0.0, 0.75)
COLOR_DARKCYAN = (0.0, 0.75, 0.75)
COLOR_LIGHTGRAY = (0.75, 0.75, 0.75)
COLOR_LIGHTRED = (1.0, 0.25, 0.25)
COLOR_LIGHTGREEN = (0.25, 1.0, 0.25)
COLOR_LIGHTBLUE = (0.25, 0.25, 1.0)
COLOR_LIGHTYELLOW = (1.0, 1.0, 0.25)
COLOR_LIGHTMAGENTA = (1.0, 0.25, 1.0)
COLOR_LIGHTCYAN = (0.25, 1.0, 1.0)

# curve constants
CURVE_LINEAR = 1
CURVE_BEZIER = 3


class Primitive(object):
    def __init__(self, transform=None):
        logger.debug('Initializing: {}'.format(self))
        self._transform = om2.MTransformationMatrix() if transform is None \
            else om2.MTransformationMatrix(transform)
        self.isDirty = False

    @property
    def transform(self):
        return self._transform

    @transform.setter
    def transform(self, value):
        value = om2.MTransformationMatrix(value)  # copy
        if self._transform != value:
            self._transform = value
            self.isDirty = True

    def move(self, x=0.0, y=0.0, z=0.0):
        x, y, z = [v for v in (x, y, z) if isinstance(v, int)]
        print x, y, z
        if x == y == z == 0.0:
            return
        offset = om2.MVector(x, y, z)
        self.transform.translateBy(offset, om2.MSpace.kWorld)
        self.isDirty = True

    def rotate(self, x=0.0, y=0.0, z=0.0, asDegrees=True):
        if x == y == z == 0.0:
            return
        if asDegrees:
            x = math.radians(x)
            y = math.radians(y)
            z = math.radians(z)
        euler = (x, y, z, om2.MTransformationMatrix.kXYZ)
        self.transform.rotateByComponents(euler, om2.MSpace.kWorld,
                                          asQuaternion=False)
        self.isDirty = True

    def scale(self, x=0.0, y=0.0, z=0.0):
        if x == y == z == 0.0:
            return
        offset = om2.MVector(x, y, z)
        self.transform.scaleBy(offset, om2.MSpace.kWorld)
        self.isDirty = True

    def update(self):
        '''To be extended by subclasses'''
        logger.debug('Updating: {}'.format(self))
        self.isDirty = False

    def draw(self, view, renderer):
        '''To be extended by subclasses'''
        if self.isDirty:
            self.update()
        logger.debug('Drawing: {}'.format(self))


class CurvePrim(Primitive):
    def __init__(self, points=None, degree=None, color=None, width=2):
        super(CurvePrim, self).__init__()

        self.width = width
        self.color = color or COLOR_BLACK
        self.degree = degree or CURVE_LINEAR

        self._points = list()  # control points
        self._drawPoints = list()  # drawable points
        self._prePoints = list()  # pre-transform points

        if points:
            self.points = points

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self._prePoints = list(value)
        self._drawPoints = list(value)
        self.isDirty = True

    def update(self):
        super(CurvePrim, self).update()
        self._points = []
        matrix = self.transform.asMatrix()
        for i in xrange(len(self._prePoints)):
            point = om2.MPoint(self._prePoints[i])
            point *= matrix
            self._points.append(point)

        if self.degree == CURVE_LINEAR:
            self._drawPoints = [x for x in self._points]

        elif self.degree == CURVE_BEZIER:
            num_points = len(self._points)
            segs = (num_points - 1) * 16
            self._drawPoints = list()
            for i in range(segs):
                t = i/float(segs - 1)
                p = bezierInterpolate(t, self._points)
                self._drawPoints.append(p)

    def draw(self, view, renderer):
        super(CurvePrim, self).draw(view, renderer)

        view.beginGL()
        glFT = renderer.glFunctionTable()
        glFT.glPushAttrib(omr.MGL_LINE_BIT)
        glFT.glLineWidth(self.width)
        glFT.glBegin(omr.MGL_LINE_STRIP)

        r, g, b = [float(x) for x in self.color]
        glFT.glColor3f(r, g, b)

        for point in self._drawPoints:
            glFT.glVertex3f(point.x, point.y, point.z)

        glFT.glEnd()
        glFT.glPopAttrib()
        view.endGL()


class VectorPrim(CurvePrim):
    def __init__(self, vector, size=1.0, color=None):
        self._size = size
        _points = ((0, 0, 0), [x * self.size for x in vector])
        super(VectorPrim, self).__init__(_points, CURVE_LINEAR, color)
        self._width = self.width

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self.width = max(int(self._width * self.size), 1.0)
        self.isDirty = True

    def update(self):
        super(VectorPrim, self).update()
        self._drawPoints[1] = linearInterpolate(
            self.size, self._drawPoints[0], self._drawPoints[1])


class TransformPrim(Primitive):
    X_COLOR = COLOR_RED
    Y_COLOR = COLOR_GREEN
    Z_COLOR = COLOR_BLUE

    def __init__(self, transform=None, size=1.0):
        super(TransformPrim, self).__init__(transform)
        self._xAxis = VectorPrim((1, 0, 0), color=TransformPrim.X_COLOR)
        self._yAxis = VectorPrim((0, 1, 0), color=TransformPrim.Y_COLOR)
        self._zAxis = VectorPrim((0, 0, 1), color=TransformPrim.Z_COLOR)
        self.size = size

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self.isDirty = True

    def update(self):
        super(TransformPrim, self).update()
        for each in (self._xAxis, self._yAxis, self._zAxis):
            if each.size != self.size:
                each.size = self.size
            if each.transform != self.transform:
                each.transform = self.transform

    def draw(self, view, renderer):
        super(TransformPrim, self).draw(view, renderer)
        for each in (self._xAxis, self._yAxis, self._zAxis):
            each.draw(view, renderer)


class PointPrim(Primitive):

    def __init__(self, position=None, color=None, size=2):
        super(PointPrim, self).__init__()

        position = om2.MVector() if position is None else om2.MVector(position)
        self.transform.setTranslation(position, om2.MSpace.kWorld)

        self.color = color or COLOR_BLACK
        self._size = size

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = max(int(value), 1)

    def draw(self, view, renderer):
        super(PointPrim, self).draw(view, renderer)

        view.beginGL()
        glFT = renderer.glFunctionTable()
        glFT.glPushAttrib(omr.MGL_POINT_BIT)
        glFT.glPointSize(self.size)
        glFT.glBegin(omr.MGL_POINTS)

        r, g, b = [float(x) for x in self.color]
        glFT.glColor3f(r, g, b)

        point = self.transform.translation(om2.MSpace.kWorld)
        glFT.glVertex3f(point.x, point.y, point.z)

        glFT.glEnd()
        glFT.glPopAttrib()
        view.endGL()


class SceneManager(object):
    view = omui.M3dView.active3dView()
    renderer = omr.MHardwareRenderer.theRenderer()

    def __init__(self):
        self.primitives = []
        self._callbacks = []

    def clear(self):
        for each in self._callbacks:
            try:
                omui.MUiMessage.removeCallback(each)
            except Exception as err:
                logger.debug(err)

        self.primitives = []
        self._callbacks = []

    def registerPrim(self, primitive):
        currentModelPanel = self.getCurrentModelPanel()
        self.primitives.append(primitive)
        callback = omui.MUiMessage.add3dViewPostRenderMsgCallback(
            currentModelPanel,
            lambda *args: primitive.draw(self.view, self.renderer))
        self._callbacks.append(callback)

    def unregisterPrim(self, primitive):
        if primitive not in self.primitives:
            return
        i = self.primitives.index(primitive)
        try:
            callback = self._callbacks[i]
            omui.MUiMessage.removeCallback(callback)
            self.primitives.remove(primitive)
            self._callbacks.remove(callback)
        except Exception as err:
            logger.debug(err)

    def refresh(self):
        self.view.refresh(True, True)

    def drawCurve(self, points, degree=None, color=None, width=2):
        curve = CurvePrim(points, degree, color, width)
        self.registerPrim(curve)
        return curve

    def drawTransform(self, transform=None):
        xfo = TransformPrim(transform)
        self.registerPrim(xfo)
        return xfo

    def drawPoint(self, position=None, color=None, size=2):
        point = PointPrim(position, color, size)
        self.registerPrim(point)
        return point

    @staticmethod
    def getCurrentModelPanel():
        currentModelPanel = mc.getPanel(wf=True)
        if "modelPanel" not in currentModelPanel:
            currentModelPanel = mc.getPanel(vis=True)
            for each in currentModelPanel:
                if "modelPanel" in each:
                    currentModelPanel = each
        return currentModelPanel


def _isIterable(obj):
    try:
        for _ in obj:
            break
        return True
    except TypeError:
        return False


def linearInterpolate(t, p0, p1):
    if _isIterable(p0):
        p0 = om2.MVector(p0)
        p1 = om2.MVector(p1)
    return p0 + ((p1 - p0) * t)


def bezierInterpolate(t, points):
    if not _isIterable(points):
        logger.error('Points is expected to be a secuence of points')
        return
    n = len(points) - 1
    n_factorial = math.factorial(n)
    for i, p in enumerate(points):
        if not isinstance(p, om2.MVector):
            p = om2.MVector(p)
        k = n_factorial / float(math.factorial(i) * math.factorial(n - i))
        b = (t**i) * (1 - t)**(n - i)
        v = p * b * k
        if i == 0:
            rval = v
        else:
            rval += v
    return rval

_scn = SceneManager()  # singleton
clear = _scn.clear
refresh = _scn.refresh
drawCurve = _scn.drawCurve
drawTransform = _scn.drawTransform
drawPoint = _scn.drawPoint
erase = _scn.unregisterPrim

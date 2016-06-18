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
    logger.debug('maya not found')
    mc = om = omui = omr = om2 = mock.MagicMock()


class TransformBase(object):
    def __init__(self):
        self._transform = om2.MTransformationMatrix()

    @property
    def transform(self):
        return self._transform

    @transform.setter
    def transform(self, value):
        self._transform = om2.MTransformationMatrix(value)  # copy
        self.update()

    def move(self, x=0.0, y=0.0, z=0.0, update=True):
        offset = om2.MVector(x, y, z)
        self.transform.translateBy(offset, om2.MSpace.kWorld)
        if update:
            self.update()

    def rotate(self, x=0.0, y=0.0, z=0.0, asDegrees=True, update=True):
        if asDegrees:
            x = math.radians(x)
            y = math.radians(y)
            z = math.radians(z)
        euler = (x, y, z, om2.MTransformationMatrix.kXYZ)
        self.transform.rotateByComponents(euler, om2.MSpace.kWorld,
                                          asQuaternion=False)
        if update:
            self.update()

    def scale(self, x=0.0, y=0.0, z=0.0, update=True):
        offset = om2.MVector(x, y, z)
        self.transform.scaleBy(offset, om2.MSpace.kWorld)
        if update:
            self.update()

    def update(self):
        raise Exception('To be implemented')

    def draw(self, view, renderer):
        raise Exception('To be implemented')


class LinePrim(TransformBase):
    def __init__(self, points=None, color=None, width=2.0):
        super(LinePrim, self).__init__()
        self._points = []  # drawable points
        self._prePoints = []  # pre-transform points

        self.width = width
        self.color = color or [0.0, 0.0, 0.0]  # normalized rgb
        if points:
            self.points = points

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self._prePoints = list(value)  # copy
        self.update()

    def update(self):
        self._points = []
        matrix = self.transform.asMatrix()
        for i in xrange(len(self._prePoints)):
            point = om2.MPoint(self._prePoints[i])
            point *= matrix
            self._points.append(point)

    def draw(self, view, renderer):
        view.beginGL()
        glFT = renderer.glFunctionTable()
        glFT.glPushAttrib(omr.MGL_LINE_BIT)
        glFT.glLineWidth(self.width)
        glFT.glBegin(omr.MGL_LINE_STRIP)

        # set color
        r, g, b = [float(x) for x in self.color]
        glFT.glColor3f(r, g, b)

        # set points
        for point in self.points:
            glFT.glVertex3f(point.x, point.y, point.z)

        glFT.glEnd()
        glFT.glPopAttrib()
        view.endGL()


class VectorPrim(LinePrim):
    def __init__(self, vector, size=1.0, color=None):
        self._size = size
        _points = ((0, 0, 0), [x * self.size for x in vector])
        super(VectorPrim, self).__init__(_points, color)
        self._width = self.width

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self.width = self._width * self.size
        self.update()

    def update(self):
        self._points = []
        xfo = om2.MTransformationMatrix(self.transform)
        size = om2.MVector(self.size, self.size, self.size)
        xfo.scaleBy(size, om2.MSpace.kWorld)
        matrix = xfo.asMatrix()
        for i in xrange(len(self._prePoints)):
            point = om2.MPoint(self._prePoints[i])
            point *= matrix
            self._points.append(point)


class TransformPrim(TransformBase):
    X_COLOUR = (1.0, 0.0, 0.0)
    Y_COLOUR = (0.0, 1.0, 0.0)
    Z_COLOUR = (0.0, 0.0, 1.0)

    def __init__(self, transform=None, size=1.0):
        self._xAxis = VectorPrim((1, 0, 0), color=TransformPrim.X_COLOUR)
        self._yAxis = VectorPrim((0, 1, 0), color=TransformPrim.Y_COLOUR)
        self._zAxis = VectorPrim((0, 0, 1), color=TransformPrim.Z_COLOUR)
        self._transform = transform or om2.MTransformationMatrix()
        self.size = size

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        for each in (self._xAxis, self._yAxis, self._zAxis):
            each.size = value

    def update(self):
        for each in (self._xAxis, self._yAxis, self._zAxis):
            each.update()

    def draw(self, view, renderer):
        for each in (self._xAxis, self._yAxis, self._zAxis):
            if each.transform != self.transform:
                each.transform = self.transform
            each.draw(view, renderer)


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

    def drawLine(self, points, color=None, width=2.0):
        line = LinePrim(points, color, width)
        self.registerPrim(line)
        return line

    def drawTransform(self, transform=None):
        transform = transform or om2.MTransformationMatrix()
        if not isinstance(transform, om2.MTransformationMatrix):
            if isinstance(transform, (tuple, list)) and len(transform) >= 16:
                matrix = om2.MMatrix(transform)
                transform = om2.MTransformationMatrix(matrix)
            else:
                logger.error(
                    'Invalid argument, transform is expected to be a sequence'
                    'of 16 float values, four tuples of four float values'
                    'each, a MMatrix or a MTransformationMatrix (om2), {}'
                    'found instead.'.format(transform))
                return
        xfo = TransformPrim(transform)
        self.registerPrim(xfo)
        return xfo

    @staticmethod
    def getCurrentModelPanel():
        currentModelPanel = mc.getPanel(wf=True)
        if "modelPanel" not in currentModelPanel:
            currentModelPanel = mc.getPanel(vis=True)
            for each in currentModelPanel:
                if "modelPanel" in each:
                    currentModelPanel = each
        return currentModelPanel


_scn = SceneManager()  # singleton
clear = _scn.clear
refresh = _scn.refresh
drawLine = _scn.drawLine
drawTransform = _scn.drawTransform
erase = _scn.unregisterPrim


__all__ = ['clear', 'refresh', 'drawLine', 'drawTransform', 'erase']

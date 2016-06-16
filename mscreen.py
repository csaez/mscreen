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


class Primitive(object):
    def __init__(self):
        self.transform = om2.MTransformationMatrix()
        self._points = []  # drawable points
        self.__points = []  # pre-transform points
        self.color = [0.0, 0.0, 0.0]  # normalized rgb

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self.__points = list(value)  # copy
        self.updatePoints()

    def updatePoints(self):
        self._points = []
        matrix = self.transform.asMatrix()
        for i in xrange(len(self.__points)):
            point = om2.MPoint(self.__points[i])
            point *= matrix
            self._points.append(point)

    def move(self, x=0.0, y=0.0, z=0.0, update=True):
        offset = om2.MVector(x, y, z)
        self.transform.translateBy(offset, om2.MSpace.kWorld)
        if update:
            self.updatePoints()

    def rotate(self, x=0.0, y=0.0, z=0.0, asDegrees=True, update=True):
        if asDegrees:
            x = math.radians(x)
            y = math.radians(y)
            z = math.radians(z)
        euler = (x, y, z, om2.MTransformationMatrix.kXYZ)
        self.transform.rotateByComponents(euler, om2.MSpace.kWorld,
                                          asQuaternion=False)
        if update:
            self.updatePoints()

    def scale(self, x=0.0, y=0.0, z=0.0, update=True):
        offset = om2.MVector(x, y, z)
        self.transform.scaleBy(offset, om2.MSpace.kWorld)
        if update:
            self.updatePoints()

    def draw(self, view, renderer):
        raise Exception('To be implemented')


class Line(Primitive):
    def __init__(self, points=None, color=None, width=2.0):
        super(Line, self).__init__()

        self.color = color or self.color
        self.width = width
        if points:
            self.points = points

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
        '''
        Draw a line given the following parameters
        @param points: ((x0, y0, z0), (x1, y1, z1)... (xn, yn, zn))
        @param color: (r, g, b)
        @param width: line width in pixels, default to 2 pixels
        '''
        line = Line(points, color, width)
        self.registerPrim(line)
        return line

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
erase = _scn.unregisterPrim


__all__ = ['clear', 'refresh', 'drawLine', 'erase']

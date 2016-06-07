# MScreen is a manager allowing to draw OpenGL on Maya's viewport
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

import logging
logger = logging.getLogger(__name__)

try:
    import maya.cmds as mc
    import maya.OpenMayaUI as omui
    import maya.OpenMayaRender as omr
except ImportError:
    import mock
    logger.debug('maya not found')
    mc = omui = omr = mock.MagicMock()


class Primitive(object):
    def __init__(self):
        self.points = []
        self.color = [0.0, 0.0, 0.0]

    def move(self, x=0.0, y=0.0, z=0.0):
        points = []
        offset = (x, y, z)
        for point in self.points:
            coord = [float(p + offset[i]) for i, p in enumerate(point)]
            points.append(coord)
        self.points = points

    def draw(self, view, renderer):
        raise Exception('To be implemented')


class Line(Primitive):
    def __init__(self, points=None, color=None, width=2.0):
        super(Line, self).__init__()

        self.points = points or self.points
        self.color = color or self.color
        self.width = width

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
            x, y, z = [float(x) for x in point]
            glFT.glVertex3f(x, y, z)

        glFT.glEnd()
        glFT.glPopAttrib()
        view.endGL()


class Manager(object):
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


_m = Manager()  # singleton
clear = _m.clear
refresh = _m.refresh
drawLine = _m.drawLine
erase = _m.unregisterPrim


__all__ = ['clear', 'refresh', 'drawLine', 'erase']

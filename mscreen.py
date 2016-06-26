"""
**mscreen** is a convenient python library allowing to easily draw OpenGL
primitives on Autodesk's Maya viewport.

The goal is to offer TDs/TAs an easy way to draw basic GL primitives as visual
feedback during debuging and/or enhacing non-critical tools.

The [source for mscreen](https://github.com/csaez/mscreen) is available on
GitHub, and released under the MIT license.

To install mscreen from source, simply

    git clone https://github.com/csaez/mscreen.git
    cd mscreen
    python setup.py install

Or drop [`mscreen.py`](https://github.com/csaez/mscreen/blob/master/mscreen.py)
into a folder in your `PYTHONPATH`.

For usage examples, take a look at the
[`README`](https://github.com/csaez/mscreen/blob/master/README.md) and/or the
[tests](https://github.com/csaez/mscreen/tree/master/tests) provided.
"""

# === Technical Documentation ===

import math
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try:
    import maya.cmds as mc
    import maya.OpenMayaUI as omui
    import maya.OpenMayaRender as omr
    import maya.api.OpenMaya as om2
except ImportError:
    logger.debug('Maya not found')


# == Constants ==

# Color constants are simple tuples containing 3 floats representing RGB
# components (normalized). There's absolutely nothing special about these
# constants, they are here just for convenience.
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

# Curve constants represent the type of interpolation/degree of curves.
CURVE_LINEAR = 1
CURVE_BEZIER = 3

# Callback constants defining the order in which callbacks are called.
CALLBACK_PREUPDATE = 0
CALLBACK_POSTUPDATE = 1


# == Primitive ==

class Primitive(object):
    """
    `mscreen` define several primitives representing different things it
    is possible to draw on the screen, these primitives are returned by the
    higher level `drawSomething` methods later on (you shouldn't need to
    subclass for simple use cases).

    `Primitive` is intended as the base class defining a common interface and
    some minimums in order to play nicely with the whole system.
    """
    def __init__(self, transform=None):
        logger.debug('Initializing: {}'.format(self))
        self._transform = om2.MTransformationMatrix() if transform is None \
            else om2.MTransformationMatrix(transform)
        self._preCallbacks = list()
        self._postCallbacks = list()
        self._parent = None
        # `isDirty` sets whether or not the primitive needs to be updated
        # before drawing.
        self.isDirty = False

    # `transform` holds an OpenMaya 2.0 `MTransformationMatrix` object
    # representing the transformation matrix of the primitive. Feel free to
    # modify or assing a new transform taking advantage of Maya API.
    @property
    def transform(self):
        return self._transform

    @transform.setter
    def transform(self, value):
        value = om2.MTransformationMatrix(value)  # copy
        if self._transform != value:
            self._transform = value
            self.isDirty = True

    # `parent` holds a reference to a `MObject` driving the `transform` of the
    # primitive (live connection). It's possible to unparent any given
    # primitive by setting its `parent` to `None`.
    @property
    def parent(self):
        if self._parent is not None and \
                (self._parent.isNull() or
                 not len(om2.MFnDagNode(self._parent).fullPathName())):
            self._parent = None
        return self._parent

    @parent.setter
    def parent(self, mobject):
        if isinstance(mobject, basestring):
            _sel = om2.MSelectionList()
            _sel.add(mobject)
            mobject = _sel.getDependNode(0)
        elif isinstance(mobject, om2.MDagPath):
            mobject = mobject.node()
        self._parent = mobject

    # === Transform methods ===

    # Methods offseting primitive's `transform` by a given
    # translation/rotation/scale (world space). These methods are here for
    # convenience and should be equivalent to the ones provided by the Maya
    # API.
    def move(self, x=0.0, y=0.0, z=0.0):
        x, y, z = [v for v in (x, y, z) if isinstance(v, int)]
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

    # === Primitive callbacks ===

    # `mscreen` main entry point for interactivity between maya nodes and
    # OpenGL primitives is through callbacks at draw time (every time the
    # viewport gets refreshed).

    # It's possible to register/unregister any function as a callback
    # pre/post update (defined by the callback constant), the only requirement
    # is that said `function` should accept a fist argument corresponding to
    # the primitive itself and should return `True` or `False` as a result of
    # it computation (the return value is especially important in
    # `CALLBACK_PREUPDATE` type of callbacks, as it triggers a cleanup
    # procedure after its execution).
    def registerCallback(self, function, type=CALLBACK_PREUPDATE):
        index = -1
        if type == CALLBACK_PREUPDATE:
            index = len(self._preCallbacks)
            self._preCallbacks.append(function)
        elif type == CALLBACK_POSTUPDATE:
            index = len(self._postCallbacks)
            self._postCallbacks.append(function)
        return index

    def unregisterCallback(self, item, type=CALLBACK_PREUPDATE):
        if type == CALLBACK_PREUPDATE:
            _callbacks = self._preCallbacks
        elif type == CALLBACK_POSTUPDATE:
            _callbacks = self._postCallbacks
        else:
            return False
        if isinstance(item, int):
            item = _callbacks[item]
        if item in _callbacks:
            _callbacks.remove(item)

    # === To be extended by subclasses ===

    def update(self):
        """
        `update` is in charge of updating the data used in OpenGL calls during
        drawing, there might be many use cases depending on the primitive, but
        a common one would be updating the drawable points according to
        primitive's `transform` (i.e. `CurvePrim`).

        Notice how this method sets `isDirty` flag to False at the end, this
        is VERY IMPORTANT, otherwise your primitive will be updated each time
        the viewport gets refreshed (even when the data doesn't change).
        """
        logger.debug('Updating: {}'.format(self))
        self.isDirty = False

    def draw(self, view, renderer):
        """
        `draw` is in charge of actually making the OpenGL calls to draw
        whetever the primitive represent on the viewport.

        The base class provides the minimum loop needed *before* doing any
        drawing in order to be compatible with the callback system. That means
        this method is intended to be *EXTENDED* (i.e. always call super
        on subclasses... unless you know what you're doing).
        """
        logger.debug('Drawing: {}'.format(self))

        # Update transform according to `parent`.
        if self.parent:
            fn = om2.MFnTransform(self.parent)
            self.transform = fn.transformation()
            self.isDirty = True

        # Run pre-update callbacks (i.e. registered as `CALLBACK_PREUPDATE`).
        toRemove = []
        for each in self._preCallbacks:
            if each(self):
                self.isDirty = True
            else:
                toRemove.append(each)
        for x in toRemove:
            self.unregisterCallback(x)

        # Run `update` method if it's needed.
        if self.isDirty:
            self.update()

        # Run post-update callbacks (i.e. registered as `CALLBACK_POSTUPDATE`).
        toRemove = []
        for each in self._postCallbacks:
            if not each(self):
                toRemove.append(each)
        for x in toRemove:
            self.unregisterCallback(x)


# === Curve Primitive ===
class CurvePrim(Primitive):
    """
    Primitive representing poly-curves (arbitrary number of points).
    """
    def __init__(self, points=None, degree=None, color=None, width=2):
        super(CurvePrim, self).__init__()

        # `width` of the curve, in pixels
        self.width = width
        # `color` of the curve (tuple of floats representing RGB components)
        self.color = color or COLOR_BLACK
        # `degree` represents the type of curve (i.e. linear or bezier)
        self.degree = degree or CURVE_LINEAR

        self._points = list()  # control points
        self._drawPoints = list()  # drawable points
        self._prePoints = list()  # pre-transform points

        if points:
            self.points = points

    # `points` are the control points of the curve.
    @property
    def points(self):
        if self.isDirty:
            self.update()
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


# === Vector Primitive ===
class VectorPrim(CurvePrim):
    """
    `CurvePrim` subclass representing a vector.
    """
    def __init__(self, vector, length=1.0, color=None):
        self._length = length
        _points = ((0, 0, 0), [x * self.length for x in vector])
        super(VectorPrim, self).__init__(_points, CURVE_LINEAR, color)
        self._width = self.width

    # `length` of the vector
    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value
        self.width = max(int(self._width * self.length), 1.0)
        self.isDirty = True

    def update(self):
        super(VectorPrim, self).update()
        self._drawPoints[1] = linearInterpolate(
            self.length, self._drawPoints[0], self._drawPoints[1])


# === Transformation Matrix Primitive ===
class TransformPrim(Primitive):
    X_COLOR = COLOR_RED
    Y_COLOR = COLOR_GREEN
    Z_COLOR = COLOR_BLUE

    def __init__(self, transform=None, size=1.0):
        super(TransformPrim, self).__init__(transform)
        # Notice how 3 vectors can be used to compose the matrix (depending on
        # your use case, composition can provide a more convenient/clean way to
        # extend classes than inheritance).
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
            if each.length != self.size:
                each.length = self.size
            if each.transform != self.transform:
                each.transform = self.transform

    def draw(self, view, renderer):
        super(TransformPrim, self).draw(view, renderer)
        for each in (self._xAxis, self._yAxis, self._zAxis):
            each.draw(view, renderer)


# === Point Primitive ===
class PointPrim(Primitive):

    def __init__(self, position=None, color=None, size=2):
        super(PointPrim, self).__init__()

        position = om2.MVector() if position is None else om2.MVector(position)
        self.transform.setTranslation(position, om2.MSpace.kWorld)
        # `color` as a tuple of floats representing RGB values (normalized).
        self.color = color or COLOR_BLACK
        self._size = size

    # `size` in pixels.
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


# === Scene Manager ===
class SceneManager(object):
    """
    `SceneManager` is the entity interacting with Maya renderer and managing
    `mscreen` primitives, this is the main entry point for most users of the
    library.
    """
    view = omui.M3dView.active3dView()
    renderer = omr.MHardwareRenderer.theRenderer()

    def __init__(self):
        # `mscreen` works by registering ONE callback in a Maya 3dview, said
        # callback calls to `__draw` where all the registered primitives are
        # proccessed.
        self.primitives = list()
        # `_callback` holds Maya's callback ID.
        self._callback = None

    def __registerCallback(self):
        if self._callback is not None:
            return
        self._callback = omui.MUiMessage.add3dViewPostRenderMsgCallback(
            self.getCurrentModelPanel(), lambda *args: self.__draw())

    def __unregisterCallback(self):
        if self._callback is not None and len(self.primitives) == 0:
            try:
                omui.MUiMessage.removeCallback(self._callback)
            except Exception as err:
                logger.debug(err)
            self._callback = None

    def __draw(self):
        for each in self.primitives:
            each.draw(self.view, self.renderer)
        self.__unregisterCallback()

    def refresh(self):
        """
        Force a refresh of the Maya viewport.
        """
        self.view.refresh(True, True)

    def clear(self):
        """
        Clear the screen by removing all registered primitives.
        """
        self.primitives = list()

    def registerPrimitive(self, primitive):
        self.primitives.append(primitive)
        self.__registerCallback()

    def unregisterPrimitive(self, primitive):
        if primitive in self.primitives:
            self.primitives.remove(primitive)

    def drawCurve(self, points, degree=None, color=None, width=2):
        """
        Convenience method creating and registering a `CurvePrim`.
        """
        curve = CurvePrim(points, degree, color, width)
        self.registerPrimitive(curve)
        return curve

    def drawTransform(self, transform=None):
        """
        Convenience method creating and registering a `TransformPrim`.
        """
        xfo = TransformPrim(transform)
        self.registerPrimitive(xfo)
        return xfo

    def drawPoint(self, position=None, color=None, size=2):
        """
        Convenience method creating and registering a `PointPrim`.
        """
        point = PointPrim(position, color, size)
        self.registerPrimitive(point)
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


# === Utility functions ===
def _isIterable(obj):
    try:
        for _ in obj:
            break
        return True
    except TypeError:
        return False


def linearInterpolate(t, p0, p1):
    """
    Performs a linear interpolation between p0 and p1.
    """
    if _isIterable(p0):
        p0 = om2.MVector(p0)
        p1 = om2.MVector(p1)
    return p0 + ((p1 - p0) * t)


def bezierInterpolate(t, points):
    """
    Performs a bezier interpolation (recursive).
    """
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

# === Accessors ===
_scn = SceneManager()  # singleton
clear = _scn.clear
refresh = _scn.refresh
drawCurve = _scn.drawCurve
drawTransform = _scn.drawTransform
drawPoint = _scn.drawPoint
erase = _scn.unregisterPrimitive

from PyQt5 import QtWidgets, uic, QtCore, QtGui

from pyqtgraph import ImageView, ViewBox, Point, debug
from pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject
from pyqtgraph import functions as fn
import pyqtgraph as pg
import numpy as np

## By Jie Feng


class CustomViewBox(pg.ViewBox):
    sigWheelChanged = QtCore.pyqtSignal(object)
    sigZoomed = QtCore.pyqtSignal(object, object)
    sigCrosshairChanged = QtCore.pyqtSignal(object)
    def __init__(self, *args, **kwds):
        kwds['enableMenu'] = False
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen={'color': (76, 76, 255), 'style': QtCore.Qt.DashLine})
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen={'color': (76, 76, 255), 'style': QtCore.Qt.DashLine})
        self.vLine.setZValue(10)
        self.hLine.setZValue(10)
        self.addItem(self.vLine, ignoreBounds=True)
        self.addItem(self.hLine, ignoreBounds=True)
        self.vs = np.array((1,1))
        self.bound = None

    def init(self):
        self.bound = np.array(self.childrenBounds(items=self.addedItems))#only for one item, 2*2
        self.bound[:, 1] = self.bound[:, 1] - 1
        init_pos =((self.bound[:,1]//2/self.vs).astype(np.int)+0.5)*self.vs
        self.vLine.setPos(init_pos[0])
        self.hLine.setPos(init_pos[1])

    def setZoom(self, x, y):
        self._resetTarget()
        self.scaleBy(x=x, y=y, center=Point(self.vLine.getXPos(), self.hLine.getYPos()))

    def mouseClickEvent(self, ev):
        pos = ev.pos()

        if ev.button() == QtCore.Qt.LeftButton & self.sceneBoundingRect().contains(pos):
            ev.accept()
            if self.bound is not None:
                mousePoint = np.array([self.mapSceneToView(pos).x(), self.mapSceneToView(pos).y()])
                mousePoint = np.maximum(mousePoint, self.bound[:,0])
                mousePoint = np.minimum(mousePoint, self.bound[:,1])

                self.setCrosshairPosition((mousePoint / self.vs).astype(np.int))

    def mouseDragEvent(self, ev, axis=None):
        ## rewrite the dragevent by fj

        ## if axis is specified, event will only affect that axis.
        ev.accept()  ## we accept all buttons

        pos = ev.pos()
        lastPos = ev.lastPos()
        dif = pos - lastPos
        dif = dif * -1

        ## Ignore axes if mouse is disabled
        mouseEnabled = np.array(self.state['mouseEnabled'], dtype=np.float)
        mask = mouseEnabled.copy()
        if axis is not None:
            mask[1 - axis] = 0.0

        ## Scale or translate based on mouse button
        if ev.button() & QtCore.Qt.MidButton:
            if self.bound is not None:
                tr = self.childGroup.transform()
                tr = fn.invertQTransform(tr)
                tr = tr.map(dif * mask) - tr.map(Point(0, 0))

                x = tr.x() if mask[0] == 1 else None
                y = tr.y() if mask[1] == 1 else None

                self._resetTarget()
                if x is not None or y is not None:
                    self.translateBy(x=x, y=y)
                self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
        elif ev.button() & QtCore.Qt.RightButton:
            # print "vb.rightDrag"
            if self.bound is not None:
                if self.state['aspectLocked'] is not False:
                    mask[0] = 0

                dif = ev.screenPos() - ev.lastScreenPos()
                dif = np.array([dif.x(), dif.y()])
                dif[0] *= -1
                s = ((mask * 0.02) + 1) ** dif

                tr = self.childGroup.transform()
                tr = fn.invertQTransform(tr)

                x = s[0] if mouseEnabled[0] == 1 else None
                y = s[1] if mouseEnabled[1] == 1 else None

                #center = Point(self.vLine.getXPos(), self.hLine.getYPos())
                #self._resetTarget()
                #self.scaleBy(x=x, y=y, center=center)
                self.sigZoomed.emit(x, y)
                self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
        elif ev.button() & QtCore.Qt.LeftButton:
            pos = ev.pos()
            if self.bound is not None:
                mousePoint = np.array([self.mapSceneToView(pos).x(), self.mapSceneToView(pos).y()])
                mousePoint = np.maximum(mousePoint, self.bound[:,0])
                mousePoint = np.minimum(mousePoint, self.bound[:,1])

                self.setCrosshairPosition((mousePoint / self.vs).astype(np.int))

    def wheelEvent(self, ev):
        ev.accept()
        self.sigWheelChanged.emit(ev.delta()//120)##one step for 120

    def setCrosshairPosition(self, pos):
        #pos is a 2 dim image coordinate
        pos = pos.astype(np.int)
        new_pos = (pos + 0.5) * self.vs
        self.vLine.setPos(new_pos[0])
        self.hLine.setPos(new_pos[1])
        self.sigCrosshairChanged.emit(pos)

    def getCrosshairPosition(self):
        pos = np.array((self.vLine.getXPos(), self.hLine.getYPos()))
        return (pos/self.vs-0.5).astype(np.int)


class crosshairView(pg.ImageView):
    sigTimeChanged = QtCore.pyqtSignal(object)
    sigCrosshairChanged = QtCore.pyqtSignal(object)
    def __init__(self, mode='axial'):
        super(crosshairView, self).__init__(view=CustomViewBox())
        self.mode = mode
        self.ui.histogram.item.axis.setStyle(showValues=False)
        self.ui.histogram.item.gradient.showTicks(False)#need further imporvement

    def init(self):
        ##for the first time image available
        self.view.init()
        self.view.sigCrosshairChanged.connect(self.CrosshairChanged)

    def setImage(self, img, autoRange=True, autoLevels=True, levels=None, axes=None, xvals=None, pos=None, scale=None,
                 transform=None, autoHistogramRange=True, levelMode=None):
        ## rewrite by fj
        """
        Set the image to be displayed in the widget.

        ================== ===========================================================================
        **Arguments:**
        img                (numpy array) the image to be displayed. See :func:`ImageItem.setImage` and
                           *notes* below.
        xvals              (numpy array) 1D array of z-axis values corresponding to the first axis
                           in a 3D image. For video, this array should contain the time of each
                           frame.
        autoRange          (bool) whether to scale/pan the view to fit the image.
        autoLevels         (bool) whether to update the white/black levels to fit the image.
        levels             (min, max); the white and black level values to use.
        axes               Dictionary indicating the interpretation for each axis.
                           This is only needed to override the default guess. Format is::

                               {'t':0, 'x':1, 'y':2, 'c':3};

        pos                Change the position of the displayed image
        scale              Change the scale of the displayed image
        transform          Set the transform of the displayed image. This option overrides *pos*
                           and *scale*.
        autoHistogramRange If True, the histogram y-range is automatically scaled to fit the
                           image data.
        levelMode          If specified, this sets the user interaction mode for setting image
                           levels. Options are 'mono', which provides a single level control for
                           all image channels, and 'rgb' or 'rgba', which provide individual
                           controls for each channel.
        ================== ===========================================================================

        **Notes:**

        For backward compatibility, image data is assumed to be in column-major order (column, row).
        However, most image data is stored in row-major order (row, column) and will need to be
        transposed before calling setImage()::

            imageview.setImage(imagedata.T)

        This requirement can be changed by the ``imageAxisOrder``
        :ref:`global configuration option <apiref_config>`.

        """
        try:
            self.view.sigWheelChanged.disconnect(self.wheelChangeEvent)
        except:
            pass
        profiler = debug.Profiler()

        if hasattr(img, 'implements') and img.implements('MetaArray'):
            img = img.asarray()

        if not isinstance(img, np.ndarray):
            required = ['dtype', 'max', 'min', 'ndim', 'shape', 'size']
            if not all([hasattr(img, attr) for attr in required]):
                raise TypeError("Image must be NumPy array or any object "
                                "that provides compatible attributes/methods:\n"
                                "  %s" % str(required))

        self.image = img
        self.imageDisp = None
        if levelMode is not None:
            self.ui.histogram.setLevelMode(levelMode)

        profiler()

        if axes is None:
            x, y = (0, 1) if self.imageItem.axisOrder == 'col-major' else (1, 0)

            if img.ndim == 2:
                self.axes = {'t': None, 'x': x, 'y': y, 'c': None}
            elif img.ndim == 3:
                # Ambiguous case; make a guess
                if img.shape[2] <= 4:
                    self.axes = {'t': None, 'x': x, 'y': y, 'c': 2}
                else:
                    self.axes = {'t': 0, 'x': x + 1, 'y': y + 1, 'c': None}
            elif img.ndim == 4:
                # Even more ambiguous; just assume the default
                self.axes = {'t': 0, 'x': x + 1, 'y': y + 1, 'c': 3}
            else:
                raise Exception("Can not interpret image with dimensions %s" % (str(img.shape)))
        elif isinstance(axes, dict):
            self.axes = axes.copy()
        elif isinstance(axes, list) or isinstance(axes, tuple):
            self.axes = {}
            for i in range(len(axes)):
                self.axes[axes[i]] = i
        else:
            raise Exception(
                "Can not interpret axis specification %s. Must be like {'t': 2, 'x': 0, 'y': 1} or ('t', 'x', 'y', 'c')" % (
                    str(axes)))

        for x in ['t', 'x', 'y', 'c']:
            self.axes[x] = self.axes.get(x, None)
        axes = self.axes

        if xvals is not None:
            self.tVals = xvals
        elif axes['t'] is not None:
            if hasattr(img, 'xvals'):
                try:
                    self.tVals = img.xvals(axes['t'])
                except:
                    self.tVals = np.arange(img.shape[axes['t']])
            else:
                self.tVals = np.arange(img.shape[axes['t']])

        profiler()

        self.currentIndex = 0
        self.updateImage(autoHistogramRange=autoHistogramRange)
        if levels is None and autoLevels:
            self.autoLevels()
        if levels is not None:  ## this does nothing since getProcessedImage sets these values again.
            self.setLevels(*levels)

        if self.ui.roiBtn.isChecked():
            self.roiChanged()

        profiler()

        if self.axes['t'] is not None:
            self.ui.roiPlot.setXRange(self.tVals.min(), self.tVals.max())
            self.frameTicks.setXVals(self.tVals)
            self.timeLine.setValue(0)
            if len(self.tVals) > 1:
                start = self.tVals.min()
                stop = self.tVals.max() + abs(self.tVals[-1] - self.tVals[0]) * 0.02
            elif len(self.tVals) == 1:
                start = self.tVals[0] - 0.5
                stop = self.tVals[0] + 0.5
            else:
                start = 0
                stop = 1
            for s in [self.timeLine, self.normRgn]:
                s.setBounds([start, stop])

        profiler()

        self.imageItem.resetTransform()
        if scale is not None:
            self.imageItem.scale(*scale)
            self.view.vs = np.array(scale)
        if pos is not None:
            self.imageItem.setPos(*pos)
        if transform is not None:
            self.imageItem.setTransform(transform)

        profiler()

        if autoRange:
            self.autoRange()
        self.roiClicked()

        profiler()
        self.view.sigWheelChanged.connect(self.wheelChangeEvent)

    def wheelChangeEvent(self, delta):
        self.setCurrentIndex(self.currentIndex+delta)

    def setCrosshairPosition(self, pos):
        #pos is a 3 dim coordinate
        pos = self.PostoView(pos)

        self.view.setCrosshairPosition(pos[:2])
        self.setCurrentIndex(pos[2])

    def PostoView(self, pos):
        if self.mode == 'sag':
            pos = pos[[1,2,0]]
        elif self.mode == 'coro':
            pos = pos[[0,2,1]]
        return pos

    def ViewtoPos(self, pos):
        if self.mode == 'sag':
            pos = pos[[2,0,1]]
        elif self.mode == 'coro':
            pos = pos[[0,2,1]]
        return pos

    def CrosshairChanged(self, pos):
        pos = pos.tolist()
        pos.append(self.currentIndex)
        self.sigCrosshairChanged.emit(self.ViewtoPos(np.array(pos)))

    def timeLineChanged(self):
        if not self.ignorePlaying:
            self.play(0)

        (ind, time) = self.timeIndex(self.timeLine)
        if ind != self.currentIndex:
            self.currentIndex = ind
            self.updateImage()
        pos = self.view.getCrosshairPosition().tolist()
        pos.append(ind)
        self.sigTimeChanged.emit(self.ViewtoPos(np.array(pos)))

    def setCurrentIndex(self, ind):
        """Set the currently displayed frame index."""
        index = np.clip(int(ind), 0, self.getProcessedImage().shape[self.axes['t']]-1)
        self.ignorePlaying = True
        # Implicitly call timeLineChanged
        self.timeLine.setValue(self.tVals[index])
        self.ignorePlaying = False


class colorcrosshairView(crosshairView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lut = None

    def updateImage(self, autoHistogramRange=True):
        super().updateImage(autoHistogramRange)
        self.getImageItem().setLookupTable(self.lut)

class locationcrosshairView(crosshairView):

    def __init__(self, mode='axial'):
        super(crosshairView, self).__init__(view=locationCustomViewBox())
        self.mode = mode
        self.view.mode = self.mode
        self.ui.histogram.item.axis.setStyle(showValues=False)
        self.ui.histogram.item.gradient.showTicks(False)  # need further imporvement
        self.AC_pos = None
        self.PC_pos = None
        self.Cen_pos = None
        self.points = None
        self.paths = None

    def points_update(self):
        self.view.points.clear()
        self.view.points.update()
        self.view.paths.clear()
        if self.AC_pos is not None:
            if self.currentIndex == int(self.PostoView(self.AC_pos)[2]):
                self.view.points.addPoints([{'pos':self.PostoView(self.AC_pos)[:2]*self.view.vs,
                                             'brush':(0,0,0,0),'symbol':'s'}])
            elif abs(self.currentIndex-int(self.PostoView(self.AC_pos)[2]))<2:
                self.view.points.addPoints([{'pos':self.PostoView(self.AC_pos)[:2]*self.view.vs,
                                             'pen':'r', 'brush':(0,0,0,0),'symbol':'s'}])
        if self.PC_pos is not None:
            if self.currentIndex == int(self.PostoView(self.PC_pos)[2]):
                self.view.points.addPoints([{'pos':self.PostoView(self.PC_pos)[:2]*self.view.vs,
                                             'brush':(0,0,0,0),'symbol':'s'}])
            elif abs(self.currentIndex-int(self.PostoView(self.PC_pos)[2]))<2:
                self.view.points.addPoints([{'pos':self.PostoView(self.PC_pos)[:2]*self.view.vs,
                                             'pen':'r', 'brush':(0,0,0,0),'symbol':'s'}])
        if self.Cen_pos is not None:
            if self.currentIndex == int(self.PostoView(self.Cen_pos)[2]):
                self.view.points.addPoints([{'pos':self.PostoView(self.Cen_pos)[:2]*self.view.vs,
                                             'brush':(0,0,0,0),'symbol':'s'}])
            elif abs(self.currentIndex-int(self.PostoView(self.Cen_pos)[2]))<2:
                self.view.points.addPoints([{'pos':self.PostoView(self.Cen_pos)[:2]*self.view.vs,
                                             'pen':'r', 'brush':(0,0,0,0),'symbol':'s'}])

        if (self.points is not None) and (self.paths is None):
            for name, (status, point, _, _) in self.points.items():
                if status:
                    if self.currentIndex == int(self.PostoView(point)[2]):
                        self.view.points.addPoints([{'pos': self.PostoView(point)[:2] * self.view.vs,
                                                     'pen':'g', 'brush':(0,0,0,0), 'symbol': 'o', 'size': 10}])
                    elif abs(self.currentIndex-int(self.PostoView(point)[2]))<2:
                        self.view.points.addPoints([{'pos': self.PostoView(point)[:2] * self.view.vs,
                                                     'pen':'r', 'brush':(0,0,0,0), 'symbol': 'o', 'size': 10}])
        elif self.paths is not None:
            line = []
            for (status, entry, _, target_name) in self.paths:
                if status and entry is not None:
                    entry = self.PostoView(entry)
                    target = self.PostoView(self.points[target_name][1])
                    maxx = np.maximum(target, entry)
                    minn = np.minimum(target, entry)
                    if self.currentIndex == int(entry[2]):
                        self.view.points.addPoints([{'pos': entry[:2] * self.view.vs,
                                                     'pen':'g', 'brush':(0,0,0,0), 'symbol': 'o', 'size': 10}])
                    if self.currentIndex == int(target[2]):
                        self.view.points.addPoints([{'pos': target[:2] * self.view.vs,
                                                     'pen':'g', 'brush':(0,0,0,0), 'symbol': 'o', 'size': 10}])
                    if self.currentIndex < int(maxx[2]) and self.currentIndex > int(minn[2]):
                        alpha = abs((entry[2] - (self.currentIndex+0.5)) / (entry[2] - target[2]))
                        point = target * alpha + entry * (1 - alpha)
                        self.view.points.addPoints([{'pos': point[:2] * self.view.vs,
                                                     'pen':'g', 'brush':(0,0,0,0), 'symbol': 'o', 'size': 10}])
                    if self.currentIndex <= int(maxx[2]) and self.currentIndex >= int(minn[2]):
                        line.append([entry[:2] * self.view.vs, target[:2] * self.view.vs])
                elif status and entry is None:
                    _, point, _, _ = self.points[target_name]
                    if self.currentIndex == int(self.PostoView(point)[2]):
                        self.view.points.addPoints([{'pos': self.PostoView(point)[:2] * self.view.vs,
                                                     'pen':'g', 'brush':(0,0,0,0), 'symbol': 'o', 'size': 10}])
                    elif abs(self.currentIndex-int(self.PostoView(point)[2]))<2:
                        self.view.points.addPoints([{'pos': self.PostoView(point)[:2] * self.view.vs,
                                                     'pen':'r', 'brush':(0,0,0,0), 'symbol': 'o', 'size': 10}])
            self.view.paths.setData(pos=np.array(line), pen=np.array([(255, 0, 0, 255, 2)],
                    dtype=[('red',np.ubyte),('green',np.ubyte),('blue',np.ubyte),('alpha',np.ubyte),('width',float)]))
                    


    def setCurrentIndex(self, ind):
        """Set the currently displayed frame index."""
        index = np.clip(int(ind), 0, self.getProcessedImage().shape[self.axes['t']]-1)
        self.ignorePlaying = True
        # Implicitly call timeLineChanged
        self.timeLine.setValue(self.tVals[index])
        self.points_update()
        self.ignorePlaying = False

    def switchImage(self, img):
        if hasattr(img, 'implements') and img.implements('MetaArray'):
            img = img.asarray()

        if not isinstance(img, np.ndarray):
            required = ['dtype', 'max', 'min', 'ndim', 'shape', 'size']
            if not all([hasattr(img, attr) for attr in required]):
                raise TypeError("Image must be NumPy array or any object "
                                "that provides compatible attributes/methods:\n"
                                "  %s" % str(required))

        self.image = img
        self.imageDisp = None

        self.updateImage(autoHistogramRange=True)
        self.autoLevels()


class locationCustomViewBox(CustomViewBox):
    sigLocation = QtCore.pyqtSignal(object, object)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = None
        self.points = pg.ScatterPlotItem(size=15, pen=pg.mkPen('g'), pxMode=True)
        self.points.setZValue(5)
        self.paths = LineItem(self.points)
        self.paths.setZValue(3)
        self.addItem(self.points, ignoreBounds=True)
        self.addItem(self.paths, ignoreBounds=True)

    def mouseClickEvent(self, ev):
        pos = ev.pos()
        if ev.button() == QtCore.Qt.LeftButton & self.sceneBoundingRect().contains(pos):
            ev.accept()
            if self.bound is not None:
                mousePoint = np.array([self.mapSceneToView(pos).x(), self.mapSceneToView(pos).y()])
                mousePoint = np.maximum(mousePoint, self.bound[:, 0])
                mousePoint = np.minimum(mousePoint, self.bound[:, 1])

                if ev.modifiers()==QtCore.Qt.ControlModifier:
                    #print(self.mode, mousePoint / self.vs)
                    self.sigLocation.emit(self.mode, mousePoint / self.vs)
                else:
                    self.setCrosshairPosition((mousePoint / self.vs).astype(np.int))

    def mouseDragEvent(self, ev, axis=None):
        ## rewrite the dragevent by fj

        ## if axis is specified, event will only affect that axis.
        ev.accept()  ## we accept all buttons

        pos = ev.pos()
        lastPos = ev.lastPos()
        dif = pos - lastPos
        dif = dif * -1

        ## Ignore axes if mouse is disabled
        mouseEnabled = np.array(self.state['mouseEnabled'], dtype=np.float)
        mask = mouseEnabled.copy()
        if axis is not None:
            mask[1 - axis] = 0.0

        ## Scale or translate based on mouse button
        if ev.button() & QtCore.Qt.MidButton:
            if self.bound is not None:
                tr = self.childGroup.transform()
                tr = fn.invertQTransform(tr)
                tr = tr.map(dif * mask) - tr.map(Point(0, 0))

                x = tr.x() if mask[0] == 1 else None
                y = tr.y() if mask[1] == 1 else None

                self._resetTarget()
                if x is not None or y is not None:
                    self.translateBy(x=x, y=y)
                self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
        elif ev.button() & QtCore.Qt.RightButton:
            # print "vb.rightDrag"
            if self.bound is not None:
                if self.state['aspectLocked'] is not False:
                    mask[0] = 0

                dif = ev.screenPos() - ev.lastScreenPos()
                dif = np.array([dif.x(), dif.y()])
                dif[0] *= -1
                s = ((mask * 0.02) + 1) ** dif

                tr = self.childGroup.transform()
                tr = fn.invertQTransform(tr)

                x = s[0] if mouseEnabled[0] == 1 else None
                y = s[1] if mouseEnabled[1] == 1 else None

                # center = Point(self.vLine.getXPos(), self.hLine.getYPos())
                # self._resetTarget()
                # self.scaleBy(x=x, y=y, center=center)
                self.sigZoomed.emit(x, y)
                self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
        elif ev.button() & QtCore.Qt.LeftButton:
            pos = ev.pos()
            if self.bound is not None:
                mousePoint = np.array([self.mapSceneToView(pos).x(), self.mapSceneToView(pos).y()])
                mousePoint = np.maximum(mousePoint, self.bound[:, 0])
                mousePoint = np.minimum(mousePoint, self.bound[:, 1])

                self.setCrosshairPosition((mousePoint / self.vs).astype(np.int))


class LineItem(GraphicsObject):

    def __init__(self, scatter, **kwds):
        GraphicsObject.__init__(self)
        self.pos = None
        self.picture = None
        self.pen = 'default'
        self.setData(**kwds)
        self.scatter = scatter

    def setData(self, **kwds):
        """
        Change the data displayed by the graph.

        ==============  =======================================================================
        **Arguments:**
        pos             (N,2,2) array of the positions of each node in the graph.
        pen             The pen to use when drawing lines between connected
                        nodes. May be one of:

                        * QPen
                        * a single argument to pass to pg.mkPen
                        * a record array of length M
                          with fields (red, green, blue, alpha, width). Note
                          that using this option may have a significant performance
                          cost.
                        * None (to disable connection drawing)
                        * 'default' to use the default foreground color.
        ==============  =======================================================================
        """
        if 'pos' in kwds:
            self.pos = kwds['pos']
            self._update()
        if 'pen' in kwds:
            self.setPen(kwds.pop('pen'))
            self._update()

        self.informViewBoundsChanged()

    def _update(self):
        self.picture = None
        self.prepareGeometryChange()
        self.update()

    def setPen(self, *args, **kwargs):
        """
        Set the pen used to draw graph lines.
        May be:

        * None to disable line drawing
        * Record array with fields (red, green, blue, alpha, width)
        * Any set of arguments and keyword arguments accepted by
          :func:`mkPen <pyqtgraph.mkPen>`.
        * 'default' to use the default foreground color.
        """
        if len(args) == 1 and len(kwargs) == 0:
            self.pen = args[0]
        else:
            self.pen = fn.mkPen(*args, **kwargs)
        self.picture = None
        self.update()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        if self.pen is None or self.pos is None:
            return

        p = QtGui.QPainter(self.picture)
        try:
            pts = self.pos
            pen = self.pen
            if isinstance(pen, np.ndarray):
                lastPen = None
                for i in range(pts.shape[0]):
                    pen = self.pen
                    if np.any(pen != lastPen):
                        lastPen = pen
                        if pen.dtype.fields is None:
                            p.setPen(fn.mkPen(color=(pen[0], pen[1], pen[2], pen[3]), width=1, style=QtCore.Qt.DashLine))
                        else:
                            p.setPen(fn.mkPen(color=(pen['red'], pen['green'], pen['blue'], pen['alpha']),
                                              width=pen['width'], style=QtCore.Qt.DashLine))
                    p.drawLine(QtCore.QPointF(*pts[i][0]), QtCore.QPointF(*pts[i][1]))
            else:
                if pen == 'default':
                    pen = fn.getConfigOption('foreground')
                p.setPen(fn.mkPen(pen))
                pts = pts.reshape((pts.shape[0] * pts.shape[1], pts.shape[2]))
                path = fn.arrayToQPath(x=pts[:, 0], y=pts[:, 1], connect='pairs')
                p.drawPath(path)
        finally:
            p.end()

    def paint(self, p, *args):
        if self.picture == None:
            self.generatePicture()
        if fn.getConfigOption('antialias') is True:
            p.setRenderHint(p.Antialiasing)
        self.picture.play(p)

    def boundingRect(self):
        return self.scatter.boundingRect()

    def dataBounds(self, *args, **kwds):
        return self.scatter.dataBounds(*args, **kwds)

    def pixelPadding(self):
        return self.scatter.pixelPadding()

    def clear(self):
        self.picture = None
        self.update()


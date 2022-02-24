from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFrame,QGridLayout,QSizePolicy
from ui.config import uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from ui.CustomInteractiveCrossBoxWidget import CustomInteractiveCrossBoxWidget
from ui.CustomDecoratedLayout import CustomDecoratedLayout
import vtkmodules.all as vtk
import numpy as np
from utils.BaseImageData import Location
from utils.cycleSyncThread import CycleSyncThread
from utils.status import Status
from utils.util import numpy2VTK

class m2DImageShownWidget(QFrame, ImageShownWidgetInterface):

    sigWheelChanged = pyqtSignal(object)
    update2DImageShownSignal = pyqtSignal()
    updateCrossViewSubSignal = pyqtSignal()

    def __init__(self):
        QFrame.__init__(self)
        #初始化GUI配置

        #初始化数据
        self.imageData = None
        #初始化逻辑
        self.imageShownData = None
        self.isInit = True

        self.qvtkWidget = CustomQVTKRenderWindowInteractor()
        self.qvtkWidget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.iren = self.qvtkWidget.GetRenderWindow().GetInteractor()
        self.qvtkWidget.GetRenderWindow().SetInteractor(self.iren)
        self.vtkStyle = vtk.vtkInteractorStyleImage()
        self.iren.SetInteractorStyle(self.vtkStyle)
        self.reader = vtk.vtkDICOMImageReader()
        self.imageViewer =  vtk.vtkImageViewer2()
        self.imageViewer.SetupInteractor(self.iren)
        self.renImage = vtk.vtkRenderer()
        self.renText = vtk.vtkRenderer()

        #extra文本信息，依次是左上、右上、左下、右下
        self.textActors = {
            Location.UL:vtk.vtkTextActor(),
            Location.UR:vtk.vtkTextActor(),
            Location.DL:vtk.vtkTextActor(),
            Location.DR:vtk.vtkTextActor()
        }
        #方位actor，依次是left,right,top,bottom
        self.orientationActors = [vtk.vtkTextActor() for i in range(4)]

        # crossView
        # self.crossBoxWidget = CustomCrossBoxWidget(self)
        # self.installEventFilter(self.crossBoxWidget)#防止CrossBox遮挡其他应用窗口
        # self.crossBoxWidget.show()

        # interactive crossView
        self.iCrossBoxWidget = CustomInteractiveCrossBoxWidget()
        self.iCrossBoxWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 用GridLayout收敛它们
        self.gridLayout = CustomDecoratedLayout(QGridLayout())
        self.gridLayout.initParamsForPlain()
        self.gridLayout.getLayout().setAlignment(Qt.AlignCenter)
        self.gridLayout.getLayout().addWidget(self.qvtkWidget, 0, 0, 1, 1)
        self.setLayout(self.gridLayout.getLayout())

        self.timerThread = None

        self.sigWheelChanged.connect(self.wheelChangeEvent)

    def initBaseData(self, imageData):
        self.imageData = imageData

    def showAllViews(self):
        self.show2DImageVtkView()
        if self.imageShownData.showExtraInfoFlag:
            self.showImageExtraInfoVtkView()
            self.renderVtkWindow()
        else:
            self.renderVtkWindow(1)
            # self.showCrossView()

    def show2DImageVtkView(self):
        dcmFile = self.imageData.getDcmDataByIndex(self.imageData.currentIndex)
        vtkImageData = numpy2VTK(np.uint16(dcmFile.pixel_array))

        flip = vtk.vtkImageFlip()
        flip.SetInputData(vtkImageData)
        flip.SetFilteredAxes(1)
        flip.Update()

        self.imageViewer.SetInputConnection(flip.GetOutputPort())
        level,width = self.imageData.getDicomWindowCenterAndLevel(self.imageData.currentIndex)
        print("当前帧的窗位，窗宽依次是：{0} {1}".format(level,width))
        self.imageViewer.SetColorLevel(level)
        self.imageViewer.SetColorWindow(width)
        self.imageViewer.SetRenderer(self.renImage)
        self.imageViewer.SetRenderWindow(self.qvtkWidget.GetRenderWindow())
        self.imageViewer.UpdateDisplayExtent()

        self.renImage.SetLayer(0)
        if self.isInit:
            self.renImage.ResetCamera()
            self.isInit = False

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renImage)

    def showImageExtraInfoVtkView(self):
        self.renText.SetInteractive(0)
        self.renText.SetLayer(1)

        truWidth,truHeight = self.parent().width(),self.parent().height()

        #添加orientation注释
        orientationInfo = self.imageData.getImageOrientationInfoFromDicom(self.imageData.currentIndex)
        if orientationInfo != Status.bad:
            for i in range(len(orientationInfo)):
                self.orientationActors[i].SetInput(orientationInfo[i])
                self.orientationActors[i].SetTextScaleModeToViewport()
                self.orientationActors[i].SetNonLinearFontScale(0.7,10)
                self.orientationActors[i].GetTextProperty().SetColor(1, 0, 0)

            self.orientationActors[0].SetDisplayPosition(20,truHeight//2)
            self.orientationActors[1].SetDisplayPosition(truWidth - 20,truHeight//2)
            self.orientationActors[2].SetDisplayPosition(truWidth//2,truHeight - 10)
            self.orientationActors[2].GetTextProperty().SetVerticalJustificationToTop()
            self.orientationActors[3].SetDisplayPosition(truWidth//2,10)

            self.orientationActors[0].GetTextProperty().SetJustificationToLeft()
            self.orientationActors[1].GetTextProperty().SetJustificationToRight()
            self.orientationActors[2].GetTextProperty().SetJustificationToLeft()
            self.orientationActors[3].GetTextProperty().SetJustificationToLeft()

            for actor in self.orientationActors:
                self.renText.AddActor(actor)

        #添加文本注释
        textDict = self.imageData.getImageExtraInfoFromDicom(self.imageData.currentIndex)
        for location,textActor in self.textActors.items():
            textActor.SetTextScaleModeToViewport()
            textActor.SetNonLinearFontScale(0.6,12)
            textActor.SetInput(textDict[location])

        #调整文本位置
        self.textActors[Location.UL].GetTextProperty().SetJustificationToLeft()
        self.textActors[Location.UL].GetTextProperty().SetVerticalJustificationToTop()
        self.textActors[Location.UR].GetTextProperty().SetJustificationToRight()
        self.textActors[Location.UR].GetTextProperty().SetVerticalJustificationToTop()
        self.textActors[Location.DL].GetTextProperty().SetJustificationToLeft()
        self.textActors[Location.DR].GetTextProperty().SetJustificationToRight()
        self.textActors[Location.UL].SetDisplayPosition(
                self.calcExtraInfoWidth(), truHeight - self.calcExtraInfoHeight())
        self.textActors[Location.UR].SetDisplayPosition(
                truWidth - self.calcExtraInfoWidth(), truHeight - self.calcExtraInfoHeight())
        self.textActors[Location.DL].SetDisplayPosition(
                self.calcExtraInfoWidth(), self.calcExtraInfoHeight())
        self.textActors[Location.DR].SetDisplayPosition(
                truWidth - self.calcExtraInfoWidth(), self.calcExtraInfoHeight())

        #调整文本字体颜色，并添加到render中
        for textActor in self.textActors.values():
            textActor.GetTextProperty().SetColor(1, 1, 1)
            textActor.GetTextProperty().BoldOn()
            textActor.GetTextProperty().ShadowOn()

            self.renText.AddActor(textActor)

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renText)
        # size = [0.0,0.0]
        # self.textActor[0].GetSize(self.renText,size)
        # print("textActor size ", size)

    def hideImageExtraInfoVtkView(self):
        if self.renText is not None:
            self.qvtkWidget.GetRenderWindow().RemoveRenderer(self.renText)
            self.renderVtkWindow(layerCount=1)

    def tryHideCrossBoxWidget(self):
        if self.imageShownData.showCrossFlag:
            # self.crossBoxWidget.hide()
            self.iCrossBoxWidget.hide()
            self.imageShownData.showCrossFlag = False
            # self.crossBoxWidget.isShowContent = False

    def updateCrossBoxWidget(self):
        pass
        # self.updateCrossBoxWidgetGeometry()
        # self.updateCrossBoxWidgetContent()
        self.updateInteractiveCrossBoxContent()
        self.updateInteractiveCrossBoxGeometry()
        self.iCrossBoxWidget.show()

    def updateInteractiveCrossBoxGeometry(self):
        pos = self.mapToGlobal(QPoint(0,0))
        x,y = pos.x(),pos.y()
        width,height = self.width(),self.height()
        print("update ic View Geometry ", x,y,width,height)
        self.iCrossBoxWidget.setGeometry(x,y,width,height)
        self.iCrossBoxWidget.update()
        print("update res ", self.iCrossBoxWidget.geometry())

    def updateInteractiveCrossBoxContent(self):
        pass

    def updateCrossBoxWidgetGeometry(self):
        pos = self.mapToGlobal(QPoint(0,0))
        x,y = pos.x(),pos.y()
        width,height = self.width(),self.height()
        print("update ic View Geometry ", x,y,width,height)
        self.crossBoxWidget.setGeometry(x,y,width,height)
        self.crossBoxWidget.update()
        print("update res ", self.crossBoxWidget.geometry())

    def updateCrossBoxWidgetContent(self):
        x1,y1 = self.imageShownData.crossViewRatios[0]
        x2,y2 = self.imageShownData.crossViewRatios[1]
        _pos1 = QPoint(x1*self.width(),y1*self.height())
        _pos2 = QPoint(x2*self.width(),y2*self.height())
        self.crossBoxWidget.setPos(_pos1,_pos2)
        self.crossBoxWidget.isShowContent = True
        self.crossBoxWidget.update()
        self.crossBoxWidget.show()

    def renderVtkWindow(self, layerCount = 2):
        try:
            self.qvtkWidget.GetRenderWindow().SetNumberOfLayers(layerCount)
            self.qvtkWidget.Initialize()
            self.qvtkWidget.Start()
            if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)
        except:
            print("render error")

    def calcExtraInfoWidth(self):
        return uiConfig.shownTextInfoX

    def calcExtraInfoHeight(self):
        return uiConfig.shownTextInfoY

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        print("resize parent: ", self.parent().geometry())
        print("resize m2D: ",self.geometry())
        print("resize qvtWidget: ", self.qvtkWidget.geometry())
        self.showImageExtraInfoVtkView()

    #滚轮调用sigWheelChanged
    def wheelEvent(self, ev):
        if len(self.imageData.filePaths) <= 0:
            return
        print("wheelEvent")
        self.sigWheelChanged.emit(ev.angleDelta())

    #滚轮改变事件
    def wheelChangeEvent(self, angleDelta):
        self.setCurrentIndex(self.imageData.currentIndex+(angleDelta.y()//120))

    #切换到第ind张图
    def setCurrentIndex(self, ind):
        """Set the currently displayed frame index."""
        #ind调节到可用范围
        ind %= len(self.imageData.filePaths)
        if ind < 0:
            ind += len(self.imageData.filePaths)
        self.imageData.currentIndex = ind
        self.imageData.curFilePath = self.imageData.filePaths[self.imageData.currentIndex]

        self.showAllViews()

        self.update2DImageShownSignal.emit()
        self.updateCrossViewSubSignal.emit()

    def canSlideShow(self):
        return len(self.imageData.filePaths) > 0

    def controlSlideShow(self, flag):
        if flag:
            self.timerThread = CycleSyncThread(uiConfig.shownSlideSpeedDefault)
            self.timerThread.signal.connect(lambda :self.setCurrentIndex(self.imageData.currentIndex + 1))
            self.timerThread.start()
        else:
            print("申请退出线程")
            self.timerThread.requestInterruption()
            self.timerThread.quit()
            # self.timerThread.wait()

    def controlSlideShowSpeed(self, delta):
        if self.timerThread is not None:
            newSpeed = self.timerThread.interval + delta
            newSpeed = max(min(newSpeed,uiConfig.shownSlideSpeedMin),uiConfig.shownSlideSpeedMax)
            self.timerThread.interval = newSpeed

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.qvtkWidget.Finalize()
        if self.timerThread is not None and not self.timerThread.isFinished():
            self.timerThread.requestInterruption()
            self.timerThread.quit()
            self.timerThread.wait()

    def clearViews(self):
        self.qvtkWidget.Finalize()

    def showEvent(self, *args, **kwargs):
        if self.imageShownData.showCrossFlag:
            self.updateCrossBoxWidget()

    def hideEvent(self, *args, **kwargs):
        if self.imageShownData.showCrossFlag:
            # self.crossBoxWidget.hide()
            # self.crossBoxWidget.isShowContent = True
            self.iCrossBoxWidget.hide()
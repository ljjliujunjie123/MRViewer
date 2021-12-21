from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFrame
from ui.config import uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
import vtkmodules.all as vtk
from utils.util import getDicomWindowCenterAndLevel,getImageExtraInfoFromDicom,getImageOrientationInfoFromDicom
from utils.cycleSyncThread import CycleSyncThread

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
        self.reader = None
        self.imageViewer = None
        self.qvtkWidget = None
        self.renImage = None
        self.renText = None
        self.textActor = None
        self.showExtraInfoFlag = None
        self.showCrossFlag = None

        self.qvtkWidget = CustomQVTKRenderWindowInteractor(self)
        self.iren = self.qvtkWidget.GetRenderWindow().GetInteractor()
        self.reader = vtk.vtkDICOMImageReader()
        self.imageViewer =  vtk.vtkImageViewer2()
        self.renImage = vtk.vtkRenderer()
        self.renText = vtk.vtkRenderer()
        self.textActor = vtk.vtkTextActor()
        #方位actor，依次是left,right,top,bottom
        self.orientationActors = [vtk.vtkTextActor() for i in range(4)]

        #crossView
        self.crossBoxWidget = CustomCrossBoxWidget(self)
        self.installEventFilter(self.crossBoxWidget)#防止CrossBox遮挡其他应用窗口
        # self.crossBoxWidget.show()

        self.timerThread = None

        self.sigWheelChanged.connect(self.wheelChangeEvent)



    def initBaseData(self, imageData):
        self.imageData = imageData

    def showAllViews(self):
        self.show2DImageVtkView()
        if self.showExtraInfoFlag:
            self.showImageExtraInfoVtkView()
            self.renderVtkWindow()
        else:
            self.show2DImageVtkView()
            self.renderVtkWindow(1)
            # self.showCrossView()

    def getSingleContainerParent(self):
        return self.parent().parent().parent()

    def show2DImageVtkView(self):
        self.reader.SetDataByteOrderToLittleEndian()
        self.reader.SetFileName(self.imageData.curFilePath)
        self.reader.Update()

        self.imageViewer.SetInputConnection(self.reader.GetOutputPort())
        level,width = getDicomWindowCenterAndLevel(self.imageData.curFilePath)
        self.imageViewer.SetColorLevel(level)
        self.imageViewer.SetColorWindow(width)
        self.imageViewer.SetRenderer(self.renImage)
        self.imageViewer.SetRenderWindow(self.qvtkWidget.GetRenderWindow())
        self.imageViewer.SetupInteractor(self.iren)
        self.imageViewer.UpdateDisplayExtent()

        self.renImage.SetLayer(0)
        self.renImage.ResetCamera()

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renImage)

    def showImageExtraInfoVtkView(self):
        #添加orientation注释
        orientationInfo = getImageOrientationInfoFromDicom(self.imageData.curFilePath)
        for i in range(len(orientationInfo)):
            self.orientationActors[i].SetInput(orientationInfo[i])
            self.orientationActors[i].GetTextProperty().SetFontSize(20)
            self.orientationActors[i].GetTextProperty().SetColor(1, 0, 0)

        truWidth,truHeight = self.parent().width(),self.parent().height()
        self.orientationActors[0].SetDisplayPosition(20,truHeight//2)
        self.orientationActors[1].SetDisplayPosition(truWidth - 20,truHeight//2)
        self.orientationActors[2].SetDisplayPosition(truWidth//2,truHeight - 40)
        self.orientationActors[3].SetDisplayPosition(truWidth//2,20)

        self.orientationActors[0].GetTextProperty().SetJustificationToLeft()
        self.orientationActors[1].GetTextProperty().SetJustificationToRight()
        self.orientationActors[2].GetTextProperty().SetJustificationToLeft()
        self.orientationActors[3].GetTextProperty().SetJustificationToLeft()

        #添加文本注释
        # self.textActor.SetTextScaleModeToProp()
        self.textActor.SetDisplayPosition(
                self.calcImageExtraInfoWidthPos(),
                self.calcImageExtraInfoHeightPos()
        )
        self.textActor.SetInput(getImageExtraInfoFromDicom(self.imageData.curFilePath))
        # self.textActor.GetActualPosition2Coordinate().SetCoordinateSystemToNormalizedViewport()
        # self.textActor.GetPosition2Coordinate().SetValue(0.6, 0.1)
        self.textActor.GetTextProperty().SetFontSize(20)
        # self.textActor.GetTextProperty().SetFontFamilyToArial()
        self.textActor.GetTextProperty().SetJustificationToLeft()
        self.textActor.GetTextProperty().BoldOn()
        # self.textActor.GetTextProperty().ItalicOn()
        self.textActor.GetTextProperty().ShadowOn()
        self.textActor.GetTextProperty().SetColor(1, 1, 1)

        self.renText.SetInteractive(0)
        self.renText.SetLayer(1)
        self.renText.AddViewProp(self.textActor)
        for actor in self.orientationActors:
            self.renText.AddViewProp(actor)

        self.qvtkWidget.GetRenderWindow().AddRenderer(self.renText)
        size = [0.0,0.0]
        self.textActor.GetSize(self.renText,size)
        print("textActor size ", size)

    def hideImageExtraInfoVtkView(self):
        if self.renText is not None:
            self.qvtkWidget.GetRenderWindow().RemoveRenderer(self.renText)
            self.renderVtkWindow(layerCount=1)

    def tryHideCrossBoxWidget(self):
        if self.showCrossFlag:
            self.crossBoxWidget.hide()
            self.crossBoxWidget.isShowContent = False

    def updateCrossBoxWidgetGeometry(self):
        pos = self.mapToGlobal(QPoint(0,0))
        x,y = pos.x(),pos.y()
        width,height = self.width(),self.height()
        self.crossBoxWidget.setGeometry(x,y,width,height)
        self.crossBoxWidget.update()

    def updateCrossBoxWidgetContent(self, pos1, pos2):
        _pos1 = QPoint(pos1[0]*self.width(),pos1[1]*self.height())
        _pos2 = QPoint(pos2[0]*self.width(),pos2[1]*self.height())
        self.crossBoxWidget.setPos(_pos1,_pos2)
        self.crossBoxWidget.isShowContent = True
        self.showCrossFlag = True
        self.crossBoxWidget.update()
        self.crossBoxWidget.show()

    def renderVtkWindow(self, layerCount = 2):
        self.qvtkWidget.GetRenderWindow().SetNumberOfLayers(layerCount)
        self.iren.Initialize()
        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)

    def calcImageExtraInfoWidthPos(self):
        return uiConfig.shownTextInfoMarginWidth

    def calcImageExtraInfoHeightPos(self):
        return uiConfig.shownTextInfoMarginHeight

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        print("resize: ",self.geometry())
        self.qvtkWidget.setFixedSize(self.size())

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
        print("set current index")
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

    def setCurrentIndexMore(self, val):
        self.setCurrentIndex(self.imageData.currentIndex + 1)

    def controlSlideShow(self, flag):
        if flag:
            self.timerThread = CycleSyncThread(uiConfig.shownSlideSpeedDefault)
            self.timerThread.signal.connect(lambda x:self.setCurrentIndex(self.imageData.currentIndex + 1))
            self.timerThread.start()
        else:
            self.timerThread.requestInterruption()
            self.timerThread.quit()
            self.timerThread.wait()

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
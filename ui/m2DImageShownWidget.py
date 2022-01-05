from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFrame
from ui.config import uiConfig
from ui.CustomQVTKRenderWindowInteractor import CustomQVTKRenderWindowInteractor
from ui.ImageShownWidgetInterface import ImageShownWidgetInterface
from ui.CustomCrossBoxWidget import CustomCrossBoxWidget
import vtkmodules.all as vtk
from utils.util import getDicomWindowCenterAndLevel,getImageExtraInfoFromDicom,getImageOrientationInfoFromDicom,Location
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
        self.imageShownData = None

        self.qvtkWidget = CustomQVTKRenderWindowInteractor(self)
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
        if self.imageShownData.showExtraInfoFlag:
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
        textDict = getImageExtraInfoFromDicom(self.imageData.curFilePath)
        for location,textActor in self.textActors.items():
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
            textActor.GetTextProperty().SetFontSize(20)
            textActor.GetTextProperty().SetColor(1, 1, 1)
            textActor.GetTextProperty().BoldOn()
            textActor.GetTextProperty().ShadowOn()

            self.renText.AddActor(textActor)

        self.renText.SetInteractive(0)
        self.renText.SetLayer(1)
    
        for actor in self.orientationActors:
            self.renText.AddActor(actor)

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
            self.crossBoxWidget.hide()
            self.imageShownData.showCrossFlag = False
            self.crossBoxWidget.isShowContent = False

    def updateCrossBoxWidget(self):
        self.updateCrossBoxWidgetGeometry()
        self.updateCrossBoxWidgetContent()

    def updateCrossBoxWidgetGeometry(self):
        pos = self.mapToGlobal(QPoint(0,0))
        x,y = pos.x(),pos.y()
        width,height = self.width(),self.height()
        self.crossBoxWidget.setGeometry(x,y,width,height)
        self.crossBoxWidget.update()

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
        self.qvtkWidget.GetRenderWindow().SetNumberOfLayers(layerCount)
        self.qvtkWidget.Initialize()
        self.qvtkWidget.Start()
        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)

    def calcExtraInfoWidth(self):
        return uiConfig.shownTextInfoX

    def calcExtraInfoHeight(self):
        return uiConfig.shownTextInfoY

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        print("resize: ",self.geometry())
        self.qvtkWidget.setFixedSize(self.size())
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
        
        self.reader.SetFileName(self.imageData.curFilePath)
        self.reader.Update()

        if self.imageShownData.showExtraInfoFlag:
            self.showImageExtraInfoVtkView()
            self.renderVtkWindow()
        else:
            self.renderVtkWindow(1)


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
            self.crossBoxWidget.hide()
            self.crossBoxWidget.isShowContent = True
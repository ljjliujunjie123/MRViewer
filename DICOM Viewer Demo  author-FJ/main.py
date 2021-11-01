import os, sys

from PyQt5 import QtCore, QtWidgets, uic

import SimpleITK as sitk
import pyqtgraph as pg
import numpy as np

from crosshairView import crosshairView


class MainWindow(QtWidgets.QMainWindow):
    # NewImageLoaded = QtCore.pyqtSignal(int, int)

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('./window.ui', self)

        # view 
        self.graphicsView = crosshairView(mode='axial')
        self.graphicsView_2 = crosshairView(mode='sag')
        self.graphicsView_3 = crosshairView(mode='coro')
        self.gridLayoutView.addWidget(self.graphicsView, 0, 0, 2, 1)
        self.gridLayoutView.addWidget(self.graphicsView_2, 0, 1)
        self.gridLayoutView.addWidget(self.graphicsView_3, 1, 1)
        self.gridLayoutView.setColumnStretch(0, 6)
        self.gridLayoutView.setColumnStretch(1, 4)
        self.graphicsView.getHistogramWidget().setVisible(False)
        self.graphicsView.ui.menuBtn.setVisible(False)
        self.graphicsView.ui.roiBtn.setVisible(False)
        self.graphicsView_2.getHistogramWidget().setVisible(False)
        self.graphicsView_2.ui.menuBtn.setVisible(False)
        self.graphicsView_2.ui.roiBtn.setVisible(False)
        self.graphicsView_3.getHistogramWidget().setVisible(False)
        self.graphicsView_3.ui.menuBtn.setVisible(False)
        self.graphicsView_3.ui.roiBtn.setVisible(False)
        self.comBox.currentIndexChanged.connect(self.SwitchImage)
        
        self.images = {}

        #Connect actions
        self.actionLoad.triggered.connect(self.LoadImage)
            
    def LoadImage(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Image Files", os.getcwd(),
                                                            "Image Files(*.dcm *.ima *.img *.nii *.nii.gz)")
        if 'dcm' in fileName.lower() or 'ima' in fileName.lower():
            try:
                cur_series_ids = sitk.ImageSeriesReader.GetGDCMSeriesIDs(
                    os.path.dirname(fileName))  # search for all the dcm in the dir
                with pg.ProgressDialog('Loading..', cancelText=None, wait=0, busyCursor=True,
                                       maximum=len(cur_series_ids)) as dlg:
                    dlg.setWindowTitle('Please Wait')
                    for idx in cur_series_ids:
                        series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(os.path.dirname(fileName),
                                                                                          idx)
                        series_reader = sitk.ImageSeriesReader()
                        series_reader.SetFileNames(series_file_names)
                        series_reader.SetMetaDataDictionaryArrayUpdate(True)
                        image3D = series_reader.Execute()
                        assert image3D.GetDimension() == 3
                        image3D = sitk.DICOMOrient(image3D, 'LPS')
                        description = series_reader.GetMetaData(0, '0008|103e').strip()
                        while (description in self.images):
                            description += '_'
                        self.images[description] = sitk.Cast(image3D, sitk.sitkFloat32)
                        dlg += 1
            except:
                QtWidgets.QMessageBox.warning(self, "IO Warning",
                                              'DICOM IO ERROR on {}'.format(os.path.dirname(fileName)))

        elif 'nii' in fileName.lower():
            try:
                with pg.ProgressDialog('Loading..', cancelText=None, wait=0, busyCursor=True) as dlg:
                    dlg.setWindowTitle('Please Wait')
                    description = os.path.basename(fileName)
                    image3D = sitk.ReadImage(fileName)
                    assert image3D.GetDimension() == 3
                    image3D = sitk.DICOMOrient(image3D, 'LPS')
                    while description in self.images:
                        description += '_'
                    self.images[description] = sitk.Cast(image3D, sitk.sitkFloat32)
            except:
                QtWidgets.QMessageBox.warning(self, "IO Warning", 'NIFTI IO ERROR on {}'.format(fileName))
        elif fileName == '':
            del (fileName)
        else:
            del (fileName)
            QtWidgets.QMessageBox.warning(self, "IO Warning", 'IO ERROR on {}'.format(fileName))
        self.refreshcomBox()

    def refreshcomBox(self):
        self.comBox.currentIndexChanged.disconnect(self.SwitchImage)
        self.comBox.clear()
        self.comBox.setEnabled(True)
        self.comBox.addItems(self.images.keys())
        if self.comBox.count() == 0:
            self.comBox.clear()
            self.comBox.setEnabled(False)
        else:
            c = self.comBox.count()
            self.comBox.setCurrentIndex(c - 1)
            self.SwitchImage(c - 1)
        self.comBox.currentIndexChanged.connect(self.SwitchImage)

    def SwitchImage(self, i=False):
        try:
            self.graphicsView.sigCrosshairChanged.disconnect(self.crosshairChanged)
            self.graphicsView_2.sigCrosshairChanged.disconnect(self.crosshairChanged)
            self.graphicsView_3.sigCrosshairChanged.disconnect(self.crosshairChanged)
            self.graphicsView.sigTimeChanged.disconnect(self.timeChanged)
            self.graphicsView_2.sigTimeChanged.disconnect(self.timeChanged)
            self.graphicsView_3.sigTimeChanged.disconnect(self.timeChanged)
            self.graphicsView.getHistogramWidget().item.sigLevelsChanged.disconnect(self.levelChanged)
            self.graphicsView.view.sigZoomed.disconnect(self.zoomed)
            self.graphicsView_2.view.sigZoomed.disconnect(self.zoomed)
            self.graphicsView_3.view.sigZoomed.disconnect(self.zoomed)
        except TypeError:
            pass
        if type(i) is bool:
            i = self.comBox.currentIndex()  # For reset
        image3D = self.images[self.comBox.itemText(i)]
        image_array = sitk.GetArrayFromImage(image3D)  # z:0,y:1,x:2
        spacing = np.array(image3D.GetSpacing())
        
        self.graphicsView.getHistogramWidget().setVisible(True)
        self.graphicsView.setImage(image_array, xvals=np.arange(0, image_array.shape[0]),
                                   axes={'t': 0, 'y': 1, 'x': 2},
                                   scale=(1, spacing[1] / spacing[0]))
        self.graphicsView.init()
        self.graphicsView_2.setImage(image_array, xvals=np.arange(0, image_array.shape[2]),
                                     axes={'t': 2, 'y': 0, 'x': 1},
                                     scale=(spacing[1] / spacing[0],
                                            -spacing[2] / spacing[0]))
        self.graphicsView_2.init()
        self.graphicsView_3.setImage(image_array, xvals=np.arange(0, image_array.shape[1]),
                                     axes={'t': 1, 'y': 0, 'x': 2},
                                     scale=(1, -spacing[2] / spacing[0]))
        self.graphicsView_3.init()

        self.graphicsView.sigCrosshairChanged.connect(self.crosshairChanged)
        self.graphicsView_2.sigCrosshairChanged.connect(self.crosshairChanged)
        self.graphicsView_3.sigCrosshairChanged.connect(self.crosshairChanged)
        self.graphicsView.sigTimeChanged.connect(self.timeChanged)
        self.graphicsView_2.sigTimeChanged.connect(self.timeChanged)
        self.graphicsView_3.sigTimeChanged.connect(self.timeChanged)
        self.graphicsView.getHistogramWidget().item.sigLevelsChanged.connect(self.levelChanged)
        self.graphicsView.view.sigZoomed.connect(self.zoomed)
        self.graphicsView_2.view.sigZoomed.connect(self.zoomed)
        self.graphicsView_3.view.sigZoomed.connect(self.zoomed)

        self.graphicsView.setCurrentIndex((image_array.shape[0] - 1) // 2)
        self.graphicsView_2.setCurrentIndex((image_array.shape[2] - 1) // 2)
        self.graphicsView_3.setCurrentIndex((image_array.shape[1] - 1) // 2)

    def timeChanged(self, pos):
        if (self.graphicsView.view.getCrosshairPosition() != pos[:2]).any():
            self.graphicsView.setCrosshairPosition(pos)
        if (self.graphicsView_2.view.getCrosshairPosition() != pos[[1, 2]]).any():
            self.graphicsView_2.setCrosshairPosition(pos)
        if (self.graphicsView_3.view.getCrosshairPosition() != pos[[0, 2]]).any():
            self.graphicsView_3.setCrosshairPosition(pos)

    def levelChanged(self):
        self.graphicsView_2.imageItem.setLevels(self.graphicsView.imageItem.getLevels())
        self.graphicsView_3.imageItem.setLevels(self.graphicsView.imageItem.getLevels())

    def zoomed(self, x, y):
        self.graphicsView.view.setZoom(x, y)
        self.graphicsView_2.view.setZoom(x, y)
        self.graphicsView_3.view.setZoom(x, y)

    def crosshairChanged(self, pos):
        if (self.graphicsView.currentIndex != pos[2]):
            self.graphicsView.setCurrentIndex(pos[2])
        if (self.graphicsView_2.currentIndex != pos[0]):
            self.graphicsView_2.setCurrentIndex(pos[0])
        if (self.graphicsView_3.currentIndex != pos[1]):
            self.graphicsView_3.setCurrentIndex(pos[1])

if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
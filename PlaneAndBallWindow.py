import vtkmodules.all as vtk
from PyQt5 import QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class PlaneAndBallWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.frame = QtWidgets.QFrame()

        self.vl = QtWidgets.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Create source
        ballSource = vtk.vtkSphereSource()
        ballSource.SetCenter(0,0,0)
        ballSource.SetRadius(0.6)

        planeSource = vtk.vtkPlaneSource()
        planeSource.SetCenter(0,0,0)
        planeSource.SetNormal(1,1,1)

        # Create a mapper
        ballMapper = vtk.vtkPolyDataMapper()
        ballMapper.SetInputConnection(ballSource.GetOutputPort())

        planeMapper = vtk.vtkPolyDataMapper()
        planeMapper.SetInputConnection(planeSource.GetOutputPort())

        # Create an actor
        ballActor = vtk.vtkActor()
        ballActor.GetProperty().SetOpacity(0.25)
        ballActor.SetMapper(ballMapper)

        planeActor = vtk.vtkActor()
        planeActor.SetMapper(planeMapper)


        self.ren.AddActor(ballActor)
        self.ren.AddActor(planeActor)

        self.ren.ResetCamera()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.show()
        self.iren.Initialize()

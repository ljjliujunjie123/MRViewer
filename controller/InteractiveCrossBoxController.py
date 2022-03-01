from PyQt5.QtCore import *
from ui.CustomDecoratedLayout import CustomDecoratedLayout
from ui.SingleImageShownContainer import SingleImageShownContainer

import numpy as np
import sympy as sp
from utils.util import checkSameSeries,checkSameStudy


class DicomCoordinateHelper():
    """
    用来在Dicom的三维世界坐标下，进行空间几何计算
    """
    def calcPointToPlaneProjection(self, point, A, B, C, D):
        """
        计算Point在面上的投影点
        A,B,C,D是三维面一般方程的四个参数
        """
        x,y,z = point[0],point[1],point[2]
        A2,B2,C2 = A*A,B*B,C*C
        sumSquare = A2 + B2 + C2
        xp,yp,zp = ((B2 + C2)*x - A * (B*y + C*z + D))//sumSquare,\
                   ((A2 + C2)*y - B * (A*x + C*z + D))//sumSquare,\
                   ((A2 + B2)*z - C * (A*x + B*y + D))//sumSquare
        return (xp,yp,zp)

    def calcPoint3DTo2D(self, point, pos, vectorX, vectorY, spaceX, spaceY):
        """
        计算三维坐标的Point在一个固定面上的二维坐标
        """
        vectorOtoP = np.array(point) - pos
        x = np.dot(vectorOtoP,vectorX) / spaceX
        y = np.dot(vectorOtoP,vectorY) / spaceY
        return (x,y)

    def calcLinePlaneCrossPoint(self, point, vectorLine, planePoint, nVectorPlane):
         """
         计算三维空间一条线与一个固定面的交点三维坐标
         """
         x, y, z = sp.symbols('x, y, z')
         #面方程
         expr = nVectorPlane[0] * (x - planePoint[0]) + nVectorPlane[1] * (y - planePoint[1]) + nVectorPlane[2] * (z - planePoint[2])

         #建立方程组
         eqs = [
             vectorLine[0] / (x - point[0])  - vectorLine[1] / (y - point[1]),
             vectorLine[2] / (z - point[2]) - vectorLine[1] / (y - point[1]),
             expr
         ]

         #求解交点坐标
         res = list(sp.linsolve(eqs, [x, y, z]))
         return res[0]

    def calcVectorFromPoint(self, startPoint, endPoint, unitization = False):
        """
        根据两个三维的点计算它们之间的向量，unitization = true则进行单位化，false反之
        """
        vector = endPoint - startPoint
        if unitization:
            vector /= np.linalg.norm(vector)
        return vector

class InteractiveCrossBoxController(QObject):
    """
    Interactive Cross Box 简写 ICrossBox
    """
    def __init__(self, imageShownContainerLayout: CustomDecoratedLayout):
        QObject.__init__(self)
        self.imageShownContainerLayout = imageShownContainerLayout
        self.RTContainer = None
        self.dicomCoordinateHelper = DicomCoordinateHelper()
        pass

    def updateICrossBoxSignalHandler(self, emitContainer):
        """
        当RT窗口更新时，该函数控制其他SC刷新ICrossBox的位置和形状
        """
        self.RTContainer = emitContainer
        self.imageShownContainerLayout.mapWidgetsFunc(self.updateICrossBoxSignalSCHandler)
        pass

    def updateICrossBoxSignalSCHandler(self, handleContainer: SingleImageShownContainer):
        if handleContainer is self.RTContainer\
            or handleContainer.curMode != SingleImageShownContainer.m2DMode\
            or len(handleContainer.imageData.curFilePath) < 1:return

        df1 = handleContainer.imageData.getDcmDataByIndex(handleContainer.imageData.currentIndex)
        df2 = self.RTContainer.imageData.getDcmDataByIndex(self.RTContainer.imageData.currentIndex)
        isSameStudy = checkSameStudy(df1,df2)
        isSameSeries = checkSameSeries(df1, df2)
        if (not isSameStudy) or isSameSeries:
            return

        #建立世界坐标系
        index1,index2 = handleContainer.imageData.currentIndex, self.RTContainer.imageData.currentIndex
        img_array1,normalvector1,ImagePosition1,PixelSpacing1,\
        ImageOrientationX1,ImageOrientationY1,Rows1,Cols1= handleContainer.imageData.getBasePosInfo(index1)
        img_array2,normalvector2,ImagePosition2,PixelSpacing2,\
        ImageOrientationX2,ImageOrientationY2,Rows2,Cols2 = self.RTContainer.imageData.getBasePosInfo(index2)

        #定义Base面的面方程, 求出 Ax + By + Cz + D = 0 中的A,B,C,D
        A,B,C = normalvector1[0],normalvector1[1],normalvector1[2]
        D = -1 * sum([normalvector1[i] * ImagePosition1[i] for i in range(len(normalvector1))])

        #定义Projection面的四个三维空间点
        point1 = ImagePosition2
        point2 = ImagePosition2 + ImageOrientationX2 * Rows2 * PixelSpacing2[0]
        point3 = ImagePosition2 + ImageOrientationY2 * Cols2 * PixelSpacing2[1]
        point4 = ImagePosition2 + ImageOrientationX2 * Rows2 * PixelSpacing2[0] + ImageOrientationY2 * Cols2 * PixelSpacing2[1]

        points = [point1, point2, point3, point4]

        #根据公式求这四个点在Base面上的投影点
        points_p = [self.dicomCoordinateHelper.calcPointToPlaneProjection(point, A, B, C, D) for point in points]

        #将投影点的三维坐标转到Base面上的二维坐标
        points_2d = [
            self.dicomCoordinateHelper.calcPoint3DTo2D(point, ImagePosition1, ImageOrientationX1, ImageOrientationY1, PixelSpacing1[0], PixelSpacing1[1])
            for point in points_p
        ]
        pass

    def updateICrossBoxModeSignalHandler(self):
        """
        当工具栏的ICrossBox状态选择按钮触发时
        该函数控制当前被选中的SC更新ICrossBox的状态
        """
        pass

    def translateSignalHandler(self, handleContainer: SingleImageShownContainer):
        """
        当SC中的ICrossBox被平移时
        该函数计算新的RT空间信息并发起request
        """
        #建立世界坐标系
        index1,index2 = handleContainer.imageData.currentIndex, self.RTContainer.imageData.currentIndex
        img_array1,normalvector1,ImagePosition1,PixelSpacing1,\
        ImageOrientationX1,ImageOrientationY1,Rows1,Cols1= handleContainer.imageData.getBasePosInfo(index1)
        img_array2,normalvector2,ImagePosition2,PixelSpacing2,\
        ImageOrientationX2,ImageOrientationY2,Rows2,Cols2 = self.RTContainer.imageData.getBasePosInfo(index2)

        #定义RT图像的Pos点为O点，其在Base面上的投影为Op
        #则经过平移后的Op定义为Op'
        #则下面要求取RT平面上新的O'点

        #Base面上的Op'坐标
        #to do
        baseOriginP = ImagePosition1

        #RT面上的O'坐标
        RTPos = self.dicomCoordinateHelper.calcLinePlaneCrossPoint(baseOriginP, normalvector1, ImagePosition2, normalvector2)
        pass

    def rotateSignalHandler(self, handleContainer: SingleImageShownContainer):
        """
        当SC中的ICrossBox被旋转时
        该函数计算新的RT空间信息并发起request
        """
        #建立世界坐标系
        index1,index2 = handleContainer.imageData.currentIndex, self.RTContainer.imageData.currentIndex
        img_array1,normalvector1,ImagePosition1,PixelSpacing1,\
        ImageOrientationX1,ImageOrientationY1,Rows1,Cols1= handleContainer.imageData.getBasePosInfo(index1)
        img_array2,normalvector2,ImagePosition2,PixelSpacing2,\
        ImageOrientationX2,ImageOrientationY2,Rows2,Cols2 = self.RTContainer.imageData.getBasePosInfo(index2)

        #获取Base面上四个新的投影点坐标
        #顺序为Pos, Rows方向，Cols方向，Pos对角
        #to do
        projectionPoints = [ImagePosition1 for i in range(4)]

        #求出其对应的新的RT面的四个角点坐标
        originPoints = [
            self.dicomCoordinateHelper.calcLinePlaneCrossPoint(pPoint, normalvector1, ImagePosition2, normalvector2)
            for pPoint in projectionPoints
        ]

        #计算新的OrientationX,OrientationY
        orientationX = self.dicomCoordinateHelper.calcVectorFromPoint(originPoints[0],originPoints[1])
        orientationY = self.dicomCoordinateHelper.calcVectorFromPoint(originPoints[0],originPoints[2])
        pass

    def zoomSignalHandler(self, handleContainer: SingleImageShownContainer):
        """
        当SC中的ICrossBox被缩放时
        该函数计算新的RT空间信息并发起request
        """
        #建立世界坐标系
        index1,index2 = handleContainer.imageData.currentIndex, self.RTContainer.imageData.currentIndex
        img_array1,normalvector1,ImagePosition1,PixelSpacing1,\
        ImageOrientationX1,ImageOrientationY1,Rows1,Cols1= handleContainer.imageData.getBasePosInfo(index1)
        img_array2,normalvector2,ImagePosition2,PixelSpacing2,\
        ImageOrientationX2,ImageOrientationY2,Rows2,Cols2 = self.RTContainer.imageData.getBasePosInfo(index2)

        #获取Base面上四个新的投影点坐标
        #顺序为Pos, Rows方向，Cols方向，Pos对角
        #to do
        projectionPoints = [ImagePosition1 for i in range(4)]

        #求出其对应的新的RT面的四个角点坐标
        originPoints = [
            self.dicomCoordinateHelper.calcLinePlaneCrossPoint(pPoint, normalvector1, ImagePosition2, normalvector2)
            for pPoint in projectionPoints
        ]

        #将三维坐标转为RT平面上的二维坐标
        originPoints2D = [
            self.dicomCoordinateHelper.calcPoint3DTo2D(point, ImageOrientationX2, ImageOrientationY2, PixelSpacing2[0], PixelSpacing2[1])
            for point in originPoints
        ]

        #求出新的Rows和Cols
        rows,cols = (originPoints2D[1][0] - originPoints2D[0][0])//PixelSpacing2[0], (originPoints2D[1][1] - originPoints2D[0][1])//PixelSpacing2[1]
        pass

    def requestDicomSource(self):
        """
        根据计算出的新RT空间信息
        向MR机器发起请求
        """
        pass

    def reponseDicomSourceHandler(self):
        """
        从MR机器接收到新的DICOM数据后
        控制RT窗口刷新
        """
        pass
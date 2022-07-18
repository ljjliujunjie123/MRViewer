from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QColor,QFont,QPixmap
from PyQt5.QtCore import QRect,QSize
from PyQt5.Qt import Qt
from Config import uiConfig
class ImageScrollItemDelegate(QStyledItemDelegate):

    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)

    def paint(self, QPainter, QStyleOptionViewItem, QModelIndex):
        itemTextData = QModelIndex.data(0)
        itemIconData = QModelIndex.data(1)
        itemExtraData = QModelIndex.data(3)
        if itemExtraData is not None:
            #适配多级目录时的根节点
            try:
                if itemExtraData["isRootItem"]:
                    #绘制背景
                    rect = QStyleOptionViewItem.rect
                    print(rect)
                    QPainter.setRenderHint(QPainter.Antialiasing, True)
                    QPainter.setBrush(QColor(uiConfig.LightColor.Complementary))
                    QPainter.drawRect(rect)

                    #绘制study
                    QPainter.setPen(QColor(uiConfig.LightColor.Black))
                    font = QFont()
                    font.setFamily("Microsoft YaHei")
                    font.setPointSize(7)
                    QPainter.setFont(font)
                    QPainter.drawText(rect, Qt.AlignCenter, itemExtraData["studyName"])
            except:
                pass
        if itemTextData is None or itemIconData is None or itemExtraData is None:
            super().paint(QPainter, QStyleOptionViewItem, QModelIndex)
            return

        #绘制背景
        rect = QStyleOptionViewItem.rect
        QPainter.setRenderHint(QPainter.Antialiasing, True)
        QPainter.setBrush(QColor(uiConfig.LightColor.Analogous1))
        QPainter.drawRect(rect)

        #绘制缩略图
        iconRect = self.calcIconTargetRect(rect)
        QPainter.drawPixmap(iconRect, itemIconData.pixmap(
            uiConfig.iconSize, QIcon.Normal, QIcon.On
        ))

        #绘制series Name
        QPainter.setPen(QColor(uiConfig.LightColor.Black))
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(7)
        QPainter.setFont(font)
        QPainter.drawText(self.calcTextTargetRect(rect), Qt.AlignCenter, itemTextData)

        #绘制series Count
        annoRect = self.calcAnnotationTargetRect(iconRect)
        QPainter.setBrush(QColor("black"))
        QPainter.setPen(QColor(uiConfig.LightColor.White))
        QPainter.drawRect(annoRect)
        font.setPointSize(5)
        QPainter.setFont(font)
        QPainter.drawText(annoRect, Qt.AlignCenter, str(itemExtraData["seriesImageCount"]))

        #绘制特殊格式标志
        if itemExtraData["isMultiFrame"]:
            specialSymbolRect = self.calcSpecialSymbolTargetRect(iconRect)
            QPainter.drawPixmap(
                specialSymbolRect, self.createSpecialSymbolPixmap()
            )

    def calcTextTargetRect(self, itemRect):
        return QRect(
            itemRect.x(), itemRect.y(), itemRect.width(), uiConfig.textHeight
        )

    def calcIconTargetRect(self, itemRect):
        delta = uiConfig.textHeight + uiConfig.iconTextSpace
        iconLeftY = itemRect.y() + delta
        originIconSize = uiConfig.iconSize
        clipIconSize = QSize(originIconSize.width() - delta, originIconSize.height() - delta)
        centerX = itemRect.x() + itemRect.width() // 2
        iconLeftX = centerX - clipIconSize.width() // 2
        return QRect(
            iconLeftX, iconLeftY, clipIconSize.width(), clipIconSize.height()
        )

    def calcAnnotationTargetRect(self, iconRect):
        annoLeftX = iconRect.x() + iconRect.width() - uiConfig.annotationSize.width()
        annoLeftY = iconRect.y() + iconRect.height() - uiConfig.annotationSize.height()
        return QRect(
            annoLeftX, annoLeftY, uiConfig.annotationSize.width(), uiConfig.annotationSize.height()
        )

    def calcSpecialSymbolTargetRect(self, iconRect):
        symbolLeftX = iconRect.x()
        symbolLeftY = iconRect.y() + iconRect.height() - uiConfig.specialSymbolSize.height()
        return QRect(
            symbolLeftX, symbolLeftY, uiConfig.specialSymbolSize.width(), uiConfig.specialSymbolSize.height()
        )

    def createSpecialSymbolPixmap(self):
        pixmap = QPixmap("ui_source/video_pause_flag.png")
        pixmap = pixmap.scaled(uiConfig.specialSymbolSize,  Qt.KeepAspectRatio)
        return pixmap
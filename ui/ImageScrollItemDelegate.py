from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QColor,QFont
from PyQt5.QtCore import QRect,QSize
from PyQt5.Qt import Qt
from ui.config import uiConfig
class ImageScrollItemDelegate(QStyledItemDelegate):

    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)

    def paint(self, QPainter, QStyleOptionViewItem, QModelIndex):
        itemTextData = QModelIndex.data(0)
        itemIconData = QModelIndex.data(1)
        itemExtraData = QModelIndex.data(3)
        if itemTextData is None or itemIconData is None or itemExtraData is None:
            super().paint(QPainter, QStyleOptionViewItem, QModelIndex)
            return

        #绘制背景
        rect = QStyleOptionViewItem.rect
        # palette = QStyleOptionViewItem.palette
        # print("rect ", rect)
        QPainter.setRenderHint(QPainter.Antialiasing, True)
        QPainter.setBrush(QColor(80, 80, 80))
        QPainter.drawRect(rect)

        #绘制缩略图
        iconRect = self.calcIconTargetRect(rect)
        QPainter.drawPixmap(iconRect, itemIconData.pixmap(
            uiConfig.iconSize, QIcon.Normal, QIcon.On
        ))

        #绘制series Name
        QPainter.setPen(QColor(230, 230, 230))
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(7)
        QPainter.setFont(font)
        QPainter.drawText(self.calcTextTargetRect(rect), Qt.AlignCenter, itemTextData)

        #绘制series Count
        annoRect = self.calcAnnotationTargetRect(iconRect)
        QPainter.setBrush(QColor(0, 0, 0))
        QPainter.drawRect(annoRect)
        font.setPointSize(5)
        QPainter.setFont(font)
        QPainter.drawText(annoRect, Qt.AlignCenter, str(itemExtraData["seriesImageCount"]))

    def calcTextTargetRect(self, itemRect):
        textRect = QRect(
            itemRect.x(), itemRect.y(), itemRect.width(), uiConfig.textHeight
        )
        # print("textRect ", textRect)
        return textRect

    def calcIconTargetRect(self, itemRect):
        delta = uiConfig.textHeight + uiConfig.iconTextSpace
        iconLeftY = itemRect.y() + delta
        originIconSize = uiConfig.iconSize
        clipIconSize = QSize(originIconSize.width() - delta, originIconSize.height() - delta)
        centerX = itemRect.x() + itemRect.width() // 2
        iconLeftX = centerX - clipIconSize.width() // 2
        iconRect = QRect(
            iconLeftX, iconLeftY, clipIconSize.width(), clipIconSize.height()
        )
        # print("IconRect ", iconRect)
        return iconRect

    def calcAnnotationTargetRect(self, iconRect):
        annoLeftX = iconRect.x() + iconRect.width() - uiConfig.annotationSize.width()
        annoLeftY = iconRect.y() + iconRect.height() - uiConfig.annotationSize.height()
        annoRect = QRect(
            annoLeftX, annoLeftY, uiConfig.annotationSize.width(), uiConfig.annotationSize.height()
        )
        # print("annoRect ", annoRect)
        return annoRect
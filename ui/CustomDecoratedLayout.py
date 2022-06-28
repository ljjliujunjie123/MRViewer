from PyQt5.QtWidgets import QLayout,QWidget
from PyQt5.QtCore import QMargins
from functools import singledispatch

class CustomDecoratedLayout():

    def __init__(self, layout):
        self.layout = layout

    def initParamsForPlain(self):
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

    def setLayout(self, layout):
        self.layout = layout

    def getLayout(self):
        return self.layout

    def clearLayout(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            widget.setParent(None)

    def setSpacing(self, space):
        self.layout.setSpacing(space)

    def setAlignment(self, alignment):
        self.layout.setAlignment(alignment)

    def setLeftMargin(self, left):
        _left,_right,_top,_bottom = self.layout.getContentsMargins()
        self.layout.setContentsMargins(left,_right,_top,_bottom)

    def setRightMargin(self, right):
        _left,_right,_top,_bottom = self.layout.getContentsMargins()
        self.layout.setContentsMargins(_left,right,_top,_bottom)

    def setTopMargin(self, top):
        _left,_right,_top,_bottom = self.layout.getContentsMargins()
        self.layout.setContentsMargins(_left,_right,top,_bottom)

    def setBottomMargin(self, bottom):
        _left,_right,_top,_bottom = self.layout.getContentsMargins()
        self.layout.setContentsMargins(_left,_right,_top,bottom)

    def setMargins(self, obj):
        @singledispatch
        def handler(obj):
            return NotImplemented

        @handler.register(QMargins)
        def _(obj):
            self.layout.setContentsMargins(obj)

        @handler.register(int)
        def _(obj):
            self.layout.setContentsMargins(obj, obj, obj, obj)

        handler(obj)

    def addItems(self, itemList, location = None):
        for item in itemList:
            if isinstance(item,QLayout):
                if location is not None:
                    row,col,rowSpan,colSpan = location
                    self.layout.addLayout(item, row, col, rowSpan, colSpan)
                else:
                    self.layout.addLayout(item)
            elif isinstance(item, QWidget):
                self.layout.addWidget(item)
            elif isinstance(item, CustomDecoratedLayout):
                if location is not None:
                    row,col,rowSpan,colSpan = location
                    self.layout.addLayout(item.getLayout(), row, col, rowSpan, colSpan)
                else:
                    self.layout.addLayout(item.getLayout())

    def mapWidgetsFunc(self, func, *args):
        for i in range(self.layout.count()):
            if len(args) > 0:
                func(self.layout.itemAt(i).widget(),args)
            else:
                func(self.layout.itemAt(i).widget())
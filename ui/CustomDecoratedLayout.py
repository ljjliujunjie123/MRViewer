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

    def setMargins(self, margins):
        self.layout.setContentsMargins(margins)

    def addWidgets(self, widgetList):
        for widget in widgetList:
            self.layout.addWidget(widget)

    def mapWidgetsFunc(self, func, *args):
        for i in range(self.layout.count()):
            func(self.layout.itemAt(i).widget(),args)
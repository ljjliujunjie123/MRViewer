class CustomDecoratedLayout():

    def __init__(self, layout):
        self.layout = layout

    def initParamsForPlain(self):
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

    def getLayout(self):
        return self.layout

    def clearLayout(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            widget.setParent(None)

    def setSpacing(self, int):
        self.layout.setSpacing(int)

    def addWidgets(self, widgetList):
        for widget in widgetList:
            self.layout.addWidget(widget)

    def mapWidgetsFunc(self, func, *args):
        for i in range(self.layout.count()):
            func(self.layout.itemAt(i).widget(),args)
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
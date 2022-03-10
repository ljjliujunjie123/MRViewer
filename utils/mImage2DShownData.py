class mImage2DShownData():

    CROSS_VIEW_PROJECTION = 0
    CROSS_VIEW_INTERSECTION = 1

    def __init__(self):
        self.showExtraInfoFlag = True
        self.showCrossFlag = False
        self.crossViewRatios = ((0,0),(0,0))
        self.crossViewType = None

    def isCrossViewProjection(self):
        return self.crossViewType == self.CROSS_VIEW_PROJECTION

    def isCrossViewIntersection(self):
        return self.crossViewType == self.CROSS_VIEW_INTERSECTION
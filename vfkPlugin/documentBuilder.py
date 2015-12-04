# -*- coding: utf-8 -*-


class DocumentBuilder:
    def __init__(self):
        self.__mCurrentPageParIds = []
        self.__mCurrentPageBudIds = []
        self.__mCurrentDefinitionPoint = None

    def currentParIds(self):
        return self.mCurrentPageParIds

    def currentBudIds(self):
        return self.mCurrentPageBudIds

    def currentDefinitionPoint(self):
        return self.mCurrentDefinitionPoint

    def buildHtml(self, document, taskMap):
        pass

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_MainApp.ui'
#
# Created: Thu Feb 25 15:20:29 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainApp(object):

    def setupUi(self, MainApp):
        MainApp.setObjectName(_fromUtf8("MainApp"))
        MainApp.resize(890, 408)
        MainApp.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralWidget = QtGui.QWidget(MainApp)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.gridLayout_4 = QtGui.QGridLayout(self.centralWidget)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.splitter = QtGui.QSplitter(self.centralWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.stackedWidget = QtGui.QStackedWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.importPage = QtGui.QWidget()
        self.importPage.setObjectName(_fromUtf8("importPage"))
        self.gridLayout_10 = QtGui.QGridLayout(self.importPage)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.scrollArea_5 = QtGui.QScrollArea(self.importPage)
        self.scrollArea_5.setWidgetResizable(True)
        self.scrollArea_5.setObjectName(_fromUtf8("scrollArea_5"))
        self.scrollAreaWidgetContents_5 = QtGui.QWidget()
        self.scrollAreaWidgetContents_5.setGeometry(
            QtCore.QRect(0, 0, 371, 370))
        self.scrollAreaWidgetContents_5.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_5"))
        self.gridLayout_11 = QtGui.QGridLayout(self.scrollAreaWidgetContents_5)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.widget = QtGui.QWidget(self.scrollAreaWidgetContents_5)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout_12 = QtGui.QGridLayout()
        self.gridLayout_12.setObjectName(_fromUtf8("gridLayout_12"))
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_12.addWidget(self.label_2, 1, 0, 1, 1)
        self.parCheckBox = QtGui.QCheckBox(self.widget)
        self.parCheckBox.setChecked(True)
        self.parCheckBox.setObjectName(_fromUtf8("parCheckBox"))
        self.gridLayout_12.addWidget(self.parCheckBox, 1, 1, 1, 1)
        self.budCheckBox = QtGui.QCheckBox(self.widget)
        self.budCheckBox.setChecked(True)
        self.budCheckBox.setObjectName(_fromUtf8("budCheckBox"))
        self.gridLayout_12.addWidget(self.budCheckBox, 2, 1, 1, 1)
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_12.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.vfkFileLineEdit = QtGui.QLineEdit(self.widget)
        self.vfkFileLineEdit.setObjectName(_fromUtf8("vfkFileLineEdit"))
        self.horizontalLayout_3.addWidget(self.vfkFileLineEdit)
        self.browseButton = QtGui.QPushButton(self.widget)
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.horizontalLayout_3.addWidget(self.browseButton)
        self.gridLayout_12.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_12)
        spacerItem = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.labelLoading = QtGui.QLabel(self.widget)
        self.labelLoading.setText(_fromUtf8(""))
        self.labelLoading.setObjectName(_fromUtf8("labelLoading"))
        self.verticalLayout_2.addWidget(self.labelLoading)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.progressBar = QtGui.QProgressBar(self.widget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.horizontalLayout_2.addWidget(self.progressBar)
        self.loadVfkButton = QtGui.QPushButton(self.widget)
        self.loadVfkButton.setObjectName(_fromUtf8("loadVfkButton"))
        self.horizontalLayout_2.addWidget(self.loadVfkButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout_11.addWidget(self.widget, 0, 0, 1, 1)
        self.scrollArea_5.setWidget(self.scrollAreaWidgetContents_5)
        self.gridLayout_10.addWidget(self.scrollArea_5, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.importPage)
        self.searchPage = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.searchPage.sizePolicy().hasHeightForWidth())
        self.searchPage.setSizePolicy(sizePolicy)
        self.searchPage.setObjectName(_fromUtf8("searchPage"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.searchPage)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_3 = QtGui.QLabel(self.searchPage)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_4.addWidget(self.label_3)
        self.searchCombo = QtGui.QComboBox(self.searchPage)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.searchCombo.sizePolicy().hasHeightForWidth())
        self.searchCombo.setSizePolicy(sizePolicy)
        self.searchCombo.setObjectName(_fromUtf8("searchCombo"))
        self.horizontalLayout_4.addWidget(self.searchCombo)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.searchForms = QtGui.QStackedWidget(self.searchPage)
        self.searchForms.setObjectName(_fromUtf8("searchForms"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.gridLayout = QtGui.QGridLayout(self.page)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scrollArea = QtGui.QScrollArea(self.page)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 98, 28))
        self.scrollAreaWidgetContents.setObjectName(
            _fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_5 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.vlastniciSearchForm = VlastniciSearchForm(
            self.scrollAreaWidgetContents)
        self.vlastniciSearchForm.setObjectName(
            _fromUtf8("vlastniciSearchForm"))
        self.gridLayout_5.addWidget(self.vlastniciSearchForm, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.searchForms.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName(_fromUtf8("page_2"))
        self.gridLayout_6 = QtGui.QGridLayout(self.page_2)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.scrollArea_3 = QtGui.QScrollArea(self.page_2)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName(_fromUtf8("scrollArea_3"))
        self.scrollAreaWidgetContents_2 = QtGui.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 98, 28))
        self.scrollAreaWidgetContents_2.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_2"))
        self.gridLayout_7 = QtGui.QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.parcelySearchForm = ParcelySearchForm(
            self.scrollAreaWidgetContents_2)
        self.parcelySearchForm.setObjectName(_fromUtf8("parcelySearchForm"))
        self.gridLayout_7.addWidget(self.parcelySearchForm, 0, 0, 1, 1)
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout_6.addWidget(self.scrollArea_3, 0, 0, 1, 1)
        self.searchForms.addWidget(self.page_2)
        self.page_3 = QtGui.QWidget()
        self.page_3.setObjectName(_fromUtf8("page_3"))
        self.gridLayout_2 = QtGui.QGridLayout(self.page_3)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.scrollArea_2 = QtGui.QScrollArea(self.page_3)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName(_fromUtf8("scrollArea_2"))
        self.scrollAreaWidgetContents_3 = QtGui.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 98, 28))
        self.scrollAreaWidgetContents_3.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.budovySearchForm = BudovySearchForm(
            self.scrollAreaWidgetContents_3)
        self.budovySearchForm.setObjectName(_fromUtf8("budovySearchForm"))
        self.gridLayout_3.addWidget(self.budovySearchForm, 0, 0, 1, 1)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_3)
        self.gridLayout_2.addWidget(self.scrollArea_2, 0, 0, 1, 1)
        self.searchForms.addWidget(self.page_3)
        self.page_4 = QtGui.QWidget()
        self.page_4.setObjectName(_fromUtf8("page_4"))
        self.gridLayout_8 = QtGui.QGridLayout(self.page_4)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.scrollArea_4 = QtGui.QScrollArea(self.page_4)
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollArea_4.setObjectName(_fromUtf8("scrollArea_4"))
        self.scrollAreaWidgetContents_4 = QtGui.QWidget()
        self.scrollAreaWidgetContents_4.setGeometry(QtCore.QRect(0, 0, 98, 28))
        self.scrollAreaWidgetContents_4.setObjectName(
            _fromUtf8("scrollAreaWidgetContents_4"))
        self.gridLayout_9 = QtGui.QGridLayout(self.scrollAreaWidgetContents_4)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.jednotkySearchForm = JednotkySearchForm(
            self.scrollAreaWidgetContents_4)
        self.jednotkySearchForm.setObjectName(_fromUtf8("jednotkySearchForm"))
        self.gridLayout_9.addWidget(self.jednotkySearchForm, 0, 0, 1, 1)
        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_4)
        self.gridLayout_8.addWidget(self.scrollArea_4, 0, 0, 1, 1)
        self.searchForms.addWidget(self.page_4)
        self.verticalLayout_3.addWidget(self.searchForms)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.searchButton = QtGui.QPushButton(self.searchPage)
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.horizontalLayout.addWidget(self.searchButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.stackedWidget.addWidget(self.searchPage)
        self.widget_2 = QtGui.QWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.rightWidgetLayout = QtGui.QVBoxLayout(self.widget_2)
        self.rightWidgetLayout.setMargin(0)
        self.rightWidgetLayout.setObjectName(_fromUtf8("rightWidgetLayout"))
        self.vfkBrowser = VfkTextBrowser(self.widget_2)
        self.vfkBrowser.setObjectName(_fromUtf8("vfkBrowser"))
        self.rightWidgetLayout.addWidget(self.vfkBrowser)
        self.gridLayout_4.addWidget(self.splitter, 0, 0, 1, 1)
        MainApp.setWidget(self.centralWidget)
        self.actionVyhledavani = QtGui.QAction(MainApp)
        self.actionVyhledavani.setCheckable(True)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/search.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionVyhledavani.setIcon(icon)
        self.actionVyhledavani.setObjectName(_fromUtf8("actionVyhledavani"))
        self.actionImport = QtGui.QAction(MainApp)
        self.actionImport.setCheckable(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/db-add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionImport.setIcon(icon1)
        self.actionImport.setObjectName(_fromUtf8("actionImport"))
        self.actionBack = QtGui.QAction(MainApp)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/arrowBack.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionBack.setIcon(icon2)
        self.actionBack.setObjectName(_fromUtf8("actionBack"))
        self.actionForward = QtGui.QAction(MainApp)
        self.actionForward.setEnabled(True)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/arrowForward.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionForward.setIcon(icon3)
        self.actionForward.setObjectName(_fromUtf8("actionForward"))
        self.actionExportLatex = QtGui.QAction(MainApp)
        self.actionExportLatex.setObjectName(_fromUtf8("actionExportLatex"))
        self.actionExportHtml = QtGui.QAction(MainApp)
        self.actionExportHtml.setObjectName(_fromUtf8("actionExportHtml"))
        self.actionSelectParInMap = QtGui.QAction(MainApp)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/selectPar.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSelectParInMap.setIcon(icon4)
        self.actionSelectParInMap.setObjectName(
            _fromUtf8("actionSelectParInMap"))
        self.actionSelectBudInMap = QtGui.QAction(MainApp)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/selectBud.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSelectBudInMap.setIcon(icon5)
        self.actionSelectBudInMap.setObjectName(
            _fromUtf8("actionSelectBudInMap"))
        self.actionCuzkPage = QtGui.QAction(MainApp)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/cuzk.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCuzkPage.setIcon(icon6)
        self.actionCuzkPage.setObjectName(_fromUtf8("actionCuzkPage"))
        self.actionShowInfoaboutSelection = QtGui.QAction(MainApp)
        self.actionShowInfoaboutSelection.setCheckable(True)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/showInfo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowInfoaboutSelection.setIcon(icon7)
        self.actionShowInfoaboutSelection.setObjectName(
            _fromUtf8("actionShowInfoaboutSelection"))
        self.actionShowHelpPage = QtGui.QAction(MainApp)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/vfkPlugin.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowHelpPage.setIcon(icon8)
        self.actionShowHelpPage.setObjectName(_fromUtf8("actionShowHelpPage"))

        self.retranslateUi(MainApp)
        self.stackedWidget.setCurrentIndex(0)
        self.searchForms.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainApp)

    def retranslateUi(self, MainApp):
        MainApp.setWindowTitle(_translate("MainApp", "Prohlížeč VFK", None))
        self.label_2.setText(_translate("MainApp", "Vrstvy:", None))
        self.parCheckBox.setText(_translate("MainApp", "Parcely (PAR)", None))
        self.budCheckBox.setText(_translate("MainApp", "Budovy (BUD)", None))
        self.label.setText(_translate("MainApp", "VFK soubor:", None))
        self.browseButton.setText(_translate("MainApp", "Procházet", None))
        self.loadVfkButton.setText(_translate("MainApp", "Načíst", None))
        self.label_3.setText(_translate("MainApp", "Vyhledat:", None))
        self.searchButton.setText(_translate("MainApp", "Hledej", None))
        self.actionVyhledavani.setText(
            _translate("MainApp", "Vyhledávání", None))
        self.actionVyhledavani.setToolTip(
            _translate("MainApp", "Vyhledávání", None))
        self.actionVyhledavani.setShortcut(
            _translate("MainApp", "Ctrl+F", None))
        self.actionImport.setText(_translate("MainApp", "Import", None))
        self.actionImport.setToolTip(_translate("MainApp", "Import VFK", None))
        self.actionImport.setShortcut(_translate("MainApp", "Ctrl+I", None))
        self.actionBack.setText(_translate("MainApp", "back", None))
        self.actionBack.setToolTip(_translate("MainApp", "Zpět", None))
        self.actionBack.setShortcut(_translate("MainApp", "Ctrl+Z", None))
        self.actionForward.setText(_translate("MainApp", "forward", None))
        self.actionForward.setToolTip(_translate("MainApp", "Vpřed", None))
        self.actionForward.setShortcut(
            _translate("MainApp", "Ctrl+Shift+Z", None))
        self.actionExportLatex.setText(_translate("MainApp", "LaTeX", None))
        self.actionExportLatex.setToolTip(
            _translate("MainApp", "Export do LaTeXu", None))
        self.actionExportHtml.setText(_translate("MainApp", "HTML", None))
        self.actionExportHtml.setToolTip(
            _translate("MainApp", "Export do HTML", None))
        self.actionSelectParInMap.setText(
            _translate("MainApp", "selectParInMap", None))
        self.actionSelectParInMap.setToolTip(
            _translate("MainApp", "Označit aktuální parcely v mapě", None))
        self.actionSelectBudInMap.setText(
            _translate("MainApp", "selectBudInMap", None))
        self.actionSelectBudInMap.setToolTip(
            _translate("MainApp", "Označit aktuální budovy v mapě", None))
        self.actionCuzkPage.setText(_translate("MainApp", "cuzkPage", None))
        self.actionCuzkPage.setToolTip(
            _translate("MainApp", "Otevřít v prohlížeči aplikaci Nahlížení do KN pro aktuální nemovitost", None))
        self.actionShowInfoaboutSelection.setText(
            _translate("MainApp", "showInfoaboutSelection", None))
        self.actionShowInfoaboutSelection.setToolTip(
            _translate("MainApp", "Aktivovat/deaktivovat zobrazení informací o vybraných nemovitostech", None))
        self.actionShowHelpPage.setText(
            _translate("MainApp", "showHelpPage", None))
        self.actionShowHelpPage.setToolTip(
            _translate("MainApp", "Zobrazit nápovědu", None))

from vlastniciSearchForm import VlastniciSearchForm
from vfkTextBrowser import VfkTextBrowser
from jednotkySearchForm import JednotkySearchForm
from budovySearchForm import BudovySearchForm
from parcelySearchForm import ParcelySearchForm
import resources_rc

# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

from netwidget import Ui_netWidget
from advwidget import Ui_advWidget
from encrwidget import Ui_encrWidget

class netWidget(QtGui.QWidget):
  def __init__(self,parent):
    QtGui.QWidget.__init__(self)

    # Set up the UI from designer
    self.ui=Ui_netWidget()
    self.ui.setupUi(self)

class advWidget(QtGui.QWidget):
  def __init__(self,parent):
    QtGui.QWidget.__init__(self)

    # Set up the UI from designer
    self.ui=Ui_advWidget()
    self.ui.setupUi(self)

class encrWidget(QtGui.QWidget):
  def __init__(self,parent):
    QtGui.QWidget.__init__(self)

    # Set up the UI from designer
    self.ui=Ui_encrWidget()
    self.ui.setupUi(self)

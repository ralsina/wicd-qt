#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, traceback
from PyQt4 import QtCore, QtGui
from tray import WiTray

def main():
  
  # Create main window and display
  app=QtGui.QApplication(sys.argv)
  tray=WiTray()
  tray.show()
  r=app.exec_()
  sys.exit(r)
  
  # Show the wired interface as plugged or unplugged
  if wired.CheckPluggedIn():
    # Plugged
    pass
  else:
    # Unplugged
    pass
  
  # Get list of wireless networks

def my_excepthook(exc_type, exc_value, exc_traceback):
    app=QtCore.QCoreApplication.instance()
    msg = ' '.join(traceback.format_exception(exc_type,
                                                       exc_value,
                                                       exc_traceback,4))
    QtGui.QMessageBox.critical(None,
                         app.tr("Critical Error"),
                         app.tr("An unexpected Exception has occured!\n"
                                "%1").arg(msg),
                         QtGui.QMessageBox.Ok,
                         QtGui.QMessageBox.NoButton,
                         QtGui.QMessageBox.NoButton)

    # Call the default exception handler if you want
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def install_handler():
    sys.excepthook = my_excepthook

install_handler()
main()

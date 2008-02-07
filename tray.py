# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import time, os, dbus, dbus.service, sys, misc, mainwindow
from translations import language



class WiTray(QtGui.QSystemTrayIcon):
  def __init__(self):
    QtGui.QSystemTrayIcon.__init__ (self,QtGui.QIcon("network_connected_wlan.svg"))
    
    self.bus = dbus.SystemBus()
    print 'attempting to connect daemon...'
    proxy_obj = self.bus.get_object('org.wicd.daemon', '/org/wicd/daemon')
    print 'success'
    
    self.daemon = dbus.Interface(proxy_obj, 'org.wicd.daemon')
    self.wireless = dbus.Interface(proxy_obj, 'org.wicd.daemon.wireless')
    self.wired = dbus.Interface(proxy_obj, 'org.wicd.daemon.wired')
    self.config = dbus.Interface(proxy_obj, 'org.wicd.daemon.config')
    
    self.stTimer=QtCore.QTimer(self)
    self.updateToolTip()
    self.stTimer.setInterval(5000)
    QtCore.QObject.connect(self.stTimer,QtCore.SIGNAL("timeout()"),self.updateToolTip)
    self.stTimer.start()
    
    QtCore.QObject.connect(self,QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"),self.activate)
    
  def activate(self,button):
    # 1 is RMB, 3 is LMB
    if button==3:
      self.gui=mainwindow.Gui(tray=self)
      self.gui.show()
      self.gui.refresh()
    
    
  def updateToolTip(self):
    t=self.newTip()
    print "updating tooltip: ",t
    self.setToolTip(t)
    
  def newTip(self):
    wireless_ip = self.wireless.GetWirelessIP() #do this so that it doesn't lock up.
    wiredConnecting = self.wired.CheckIfWiredConnecting()
    wirelessConnecting = self.wireless.CheckIfWirelessConnecting()
    if wirelessConnecting == True or wiredConnecting == True:
      # Update faster, because things are happening
      self.stTimer.setInterval(500)
      print "connecting",str(self.wireless.CheckWirelessConnectingMessage()),wirelessConnecting
      if wirelessConnecting:
        return language[str(self.wireless.CheckWirelessConnectingMessage())]
      if wiredConnecting:
        return str(self.wired.CheckWiredConnectingMessage())
      return ""
      
    # Update slower
    self.stTimer.setInterval(5000)
      
    if wireless_ip:
      network = self.wireless.GetCurrentNetwork()
      if network:
        strength = self.wireless.GetCurrentSignalStrength()
        dbm_strength = self.wireless.GetCurrentDBMStrength()
        if strength is not None and dbm_strength is not None:
          # Change icons to connected on this one, to disconnected on all others
          network = str(network)
          if self.daemon.GetSignalDisplayType() == 0:
            strength = str(strength)
          else:
            strength = str(dbm_strength)
          ip = str(wireless_ip)
          return 'Connected to $A at $B (IP: $C)'.replace('$A',network).replace                                             ('$B',self.daemon.FormatSignalForPrinting(strength)).replace('$C',wireless_ip)

    wired_ip = self.wired.GetWiredIP()
    if wired_ip:
      if self.wired.CheckPluggedIn():
          if self.wiredItem: self.wiredItem.setIcon(QtGui.QIcon(":/network_connected_lan.svg"))
          return 'Connected to wired network (IP: $A)'.replace('$A',wired_ip)
    return 'Not connected'
    
  
# -*- coding: utf-8 -*-
from gui import Ui_MainWindow
import time, os, dbus, dbus.service, sys, misc

from PyQt4 import QtCore, QtGui

from translations import language

OPENDNS=['208.67.222.222','208.67.220.220']

def str2(s):
  if not s:
    return ""
  return str(s)

class Gui(QtGui.QMainWindow):
  def __init__(self,tray):
    QtGui.QMainWindow.__init__(self)

    # Set up the UI from designer
    self.ui=Ui_MainWindow()
    self.ui.setupUi(self)
    self.wiredItem=None
    self.wirelessItems={}
    self.ui.splitter.setSizes([1,0])
    
    self.bus = tray.bus
    self.daemon = tray.daemon
    self.wireless = tray.wireless
    self.wired = tray.wired
    self.config = tray.config
    
    self.stTimer=QtCore.QTimer(self)
    self.stTimer.setInterval(5000)
    QtCore.QObject.connect(self.stTimer,QtCore.SIGNAL("timeout()"),self.updateStatus)
    self.stTimer.start()
    
    
    self.encryptionTypes = misc.LoadEncryptionMethods()
    self.ui.encrWidget.ui.enctype.addItem('No encryption')
    for k in self.encryptionTypes:
      self.ui.encrWidget.ui.enctype.addItem(self.encryptionTypes[k][0])
        
    # All these things save configurations
    
    QtCore.QObject.connect(self.ui.netWidget.ui.auto,QtCore.SIGNAL("stateChanged(int)"),self.saveItem)
    
    QtCore.QObject.connect(self.ui.encrWidget.ui.enctype,QtCore.SIGNAL("currentIndexChanged(int)"),self.saveItem)
    QtCore.QObject.connect(self.ui.encrWidget.ui.enckey_1,QtCore.SIGNAL("textEdited(QString)"),self.saveItem)
    QtCore.QObject.connect(self.ui.encrWidget.ui.enckey_2,QtCore.SIGNAL("textEdited(QString)"),self.saveItem)
    QtCore.QObject.connect(self.ui.encrWidget.ui.enckey_3,QtCore.SIGNAL("textEdited(QString)"),self.saveItem)
    QtCore.QObject.connect(self.ui.encrWidget.ui.enckey_4,QtCore.SIGNAL("textEdited(QString)"),self.saveItem)
    
    QtCore.QObject.connect(self.ui.advWidget.ui.dnscombo,QtCore.SIGNAL("currentIndexChanged(int)"),self.saveItem)
    QtCore.QObject.connect(self.ui.advWidget.ui.dns1,QtCore.SIGNAL("textEdited(QString)"),self.saveItem)
    QtCore.QObject.connect(self.ui.advWidget.ui.dns2,QtCore.SIGNAL("textEdited(QString)"),self.saveItem)
    QtCore.QObject.connect(self.ui.advWidget.ui.dns3,QtCore.SIGNAL("textEdited(QString)"),self.saveItem)
    
  def on_dnscombo_currentIndexChanged(self,index):
    if not int==type(index): # Ignoring the wrong signals
      return
    networkID=int(self.ui.netlist.currentItem().props['networkID'])
    if index in (0,2,3):
      # Disable entries
      en=False
    else:
      en=True
    self.ui.advWidget.ui.dns1.setEnabled(en)
    self.ui.advWidget.ui.dns2.setEnabled(en)
    self.ui.advWidget.ui.dns3.setEnabled(en)
    
    if index in (0,2):
      self.ui.advWidget.ui.dns1.setText("")
      self.ui.advWidget.ui.dns2.setText("")
      self.ui.advWidget.ui.dns3.setText("")
    elif index == 3:
      self.ui.advWidget.ui.dns1.setText(OPENDNS[0])
      self.ui.advWidget.ui.dns2.setText(OPENDNS[1])
      self.ui.advWidget.ui.dns3.setText("")
    elif index == 1:
      self.ui.advWidget.ui.dns1.setText(str2(self.wireless.GetWirelessProperty(networkID,'dns1')))
      self.ui.advWidget.ui.dns2.setText(str2(self.wireless.GetWirelessProperty(networkID,'dns2')))
      self.ui.advWidget.ui.dns3.setText(str2(self.wireless.GetWirelessProperty(networkID,'dns3')))
    print "X1",str2(self.wireless.GetWirelessProperty(networkID,'dns1'))
    print "X2",str2(self.wireless.GetWirelessProperty(networkID,'dns2'))
    print "X3",str2(self.wireless.GetWirelessProperty(networkID,'dns3'))
    
  def on_enctype_currentIndexChanged(self,index):
    if not int==type(index): # Ignoring the wrong signals
      return
    self.ui.encrWidget.ui.enclab_1.hide()
    self.ui.encrWidget.ui.enclab_2.hide()
    self.ui.encrWidget.ui.enclab_3.hide()
    self.ui.encrWidget.ui.enclab_4.hide()
    self.ui.encrWidget.ui.enckey_1.hide()
    self.ui.encrWidget.ui.enckey_2.hide()
    self.ui.encrWidget.ui.enckey_3.hide()
    self.ui.encrWidget.ui.enckey_4.hide()
    if index==0: # No encryption
      return
    
    index-=1
    networkID=int(self.ui.netlist.currentItem().props['networkID'])
    self.encryptionInfo={}
    try:
      self.ui.encrWidget.ui.enclab_1.setText(self.encryptionTypes[index][2][0][0]+":")
      self.ui.encrWidget.ui.enclab_1.show()
      self.ui.encrWidget.ui.enckey_1.setText(str2(self.wireless.GetWirelessProperty(networkID,self.encryptionTypes[index][2][0][1])))
      self.ui.encrWidget.ui.enckey_1.show()
      self.encryptionInfo[self.encryptionTypes[index][2][0][1]]=self.ui.encrWidget.ui.enckey_1
    
      self.ui.encrWidget.ui.enclab_2.setText(self.encryptionTypes[index][2][1][0]+":")
      self.ui.encrWidget.ui.enclab_2.show()
      self.ui.encrWidget.ui.enckey_2.setText(str2(self.wireless.GetWirelessProperty(networkID,self.encryptionTypes[index][2][1][1])))
      self.ui.encrWidget.ui.enckey_2.show()
      self.encryptionInfo[self.encryptionTypes[index][2][1][1]]=self.ui.encrWidget.ui.enckey_2
    
      self.ui.encrWidget.ui.enclab_3.setText(self.encryptionTypes[index][2][2][0]+":")
      self.ui.encrWidget.ui.enclab_3.show()
      self.ui.encrWidget.ui.enckey_3.setText(str2(self.wireless.GetWirelessProperty(networkID,self.encryptionTypes[index][2][2][1])))
      self.ui.encrWidget.ui.enckey_3.show()
      self.encryptionInfo[self.encryptionTypes[index][2][2][1]]=self.ui.encrWidget.ui.enckey_3
    
      self.ui.encrWidget.ui.enclab_4.setText(self.encryptionTypes[index][2][3][0]+":")
      self.ui.encrWidget.ui.enclab_4.show()
      self.ui.encrWidget.ui.enckey_4.setText(str2(self.wireless.GetWirelessProperty(networkID,self.encryptionTypes[index][2][3][1])))
      self.ui.encrWidget.ui.enckey_4.show()
      self.encryptionInfo[self.encryptionTypes[index][2][3][1]]=self.ui.encrWidget.ui.enckey_4
    
    except KeyError:
      pass
 
  def on_netlist_currentItemChanged(self,item,old):
    if not item:
      self.ui.splitter.setSizes([1,0])
      return
    print "Activated item: ",str(item.text())
    if item==self.wiredItem:
      print "Config. of wired networks not implemented yet"
      self.ui.splitter.setSizes([1,0])
      return
    
    networkID=item.props['networkID']
    for key in ['essid','quality','strength','dbm_strength','bssid','mode','channel','encryption',
                'encryption_method','ip','netmask','gateway','use_global_dns',
                'automatic','enctype','dns1','dns2','dns3',
                ]:
      
      item.props[key]=self.wireless.GetWirelessProperty(networkID,key)
    
    
    print item.props
    
    # Set DNS info
    
    print "use_global_dns",self.wireless.GetWirelessProperty(networkID,'use_global_dns')
    if self.wireless.GetWirelessProperty(networkID,'use_global_dns'):
      self.ui.advWidget.ui.dnscombo.setCurrentIndex(2)
    elif self.wireless.GetWirelessProperty(networkID,'use_static_dns'):
      self.ui.advWidget.ui.dnscombo.setCurrentIndex(1)
    elif self.wireless.GetWirelessProperty(networkID,'use_open_dns'):
      self.ui.advWidget.ui.dnscombo.setCurrentIndex(3)
    else:
      self.ui.advWidget.ui.dnscombo.setCurrentIndex(0)
      
      
    # Set network info
    if not item.props['encryption_method']:
      enc='Unsecured'
    else:
      enc=item.props['encryption_method']
      
    self.ui.netWidget.ui.signal.setValue(int(item.props['quality']))
    self.ui.netWidget.ui.mac.setText("MAC: %s"%item.props['bssid'])
    self.ui.netWidget.ui.mode.setText("Mode: %s"%item.props['mode'])
    self.ui.netWidget.ui.encryption.setText("Encryption: %s"%enc)
    self.ui.netWidget.ui.channel.setText("Channel: %s"%item.props['channel'])
    self.ui.netWidget.ui.auto.setChecked(item.props['automatic'])
    
    # Set crypto info
    if item.props['encryption']:
      self.ui.encrWidget.ui.enctype.setCurrentIndex(0)
    else:
      activeID=-1
      for x in self.encryptionTypes:
        if self.encryptionTypes[x][1] == self.wireless.GetWirelessProperty(networkID,"enctype"):
          activeID = x
      self.ui.encrWidget.ui.enctype.setCurrentIndex(activeID+1)
      #self.on_enctype_currentIndexChanged(activeID+1)
    
    self.ui.splitter.setSizes([1,3])
    
    
    
  def saveItem(self,*args):
    print "saving",args
    
    item=self.ui.netlist.currentItem()
    nid=int(item.props['networkID'])
    print "for network",item.text(),nid
    
    if self.ui.netWidget.ui.auto.checkState():
      self.wireless.SetWirelessProperty(nid,'automatic',True)
    else:
      self.wireless.SetWirelessProperty(nid,'automatic',False)
    self.config.SaveWirelessNetworkProperty(nid,'automatic')    
  
    print "Setting encryption info..."
    encidx=self.ui.encrWidget.ui.enctype.currentIndex()-1
    if encidx == -1: # No encryption
      print "No encryption specified..."
      self.wireless.SetWirelessProperty(nid,"enctype","")
    else:
      #set the encryption type. without the encryption type, nothing is gonna happen
      self.wireless.SetWirelessProperty(nid,"enctype",self.encryptionTypes[encidx][1])
      for x in self.encryptionInfo:
        self.wireless.SetWirelessProperty(nid,x,str2(self.encryptionInfo[x].text()))
    
    print "Setting DNS info"
    dnsidx=self.ui.advWidget.ui.dnscombo.currentIndex()
    if dnsidx==0:
      self.wireless.SetWirelessProperty(nid,"use_static_dns",False)
      self.wireless.SetWirelessProperty(nid,"use_global_dns",False)
      self.wireless.SetWirelessProperty(nid,"use_open_dns",False)
      self.wireless.SetWirelessProperty(nid,"dns1","")
      self.wireless.SetWirelessProperty(nid,"dns2","")
      self.wireless.SetWirelessProperty(nid,"dns3","")
    if dnsidx==1:
      self.wireless.SetWirelessProperty(nid,"use_static_dns",True)
      self.wireless.SetWirelessProperty(nid,"use_global_dns",False)
      self.wireless.SetWirelessProperty(nid,"use_open_dns",False)
      self.wireless.SetWirelessProperty(nid,"dns1",str2(self.ui.advWidget.ui.dns1.text()))
      self.wireless.SetWirelessProperty(nid,"dns2",str2(self.ui.advWidget.ui.dns2.text()))
      self.wireless.SetWirelessProperty(nid,"dns3",str2(self.ui.advWidget.ui.dns3.text()))
    if dnsidx==2:
      self.wireless.SetWirelessProperty(nid,"use_static_dns",False)
      self.wireless.SetWirelessProperty(nid,"use_global_dns",True)
      self.wireless.SetWirelessProperty(nid,"use_open_dns",False)
    if dnsidx==3:
      self.wireless.SetWirelessProperty(nid,"use_static_dns",False)
      self.wireless.SetWirelessProperty(nid,"use_global_dns",False)
      self.wireless.SetWirelessProperty(nid,"use_open_dns",True)
      self.wireless.SetWirelessProperty(nid,"dns1",OPENDNS[0])
      self.wireless.SetWirelessProperty(nid,"dns2",OPENDNS[1])
      self.wireless.SetWirelessProperty(nid,"dns3","")
  
    self.config.SaveWirelessNetworkProfile(nid)
  
  def on_actionQuit_triggered(self):
    self.close()
    
  def on_actionDisconnect_triggered(self, *args):
    if args: #Ignore the signal with an argument. See http://lists.kde.org/?l=pykde&m=113829850106412&w=2
      return
    print "disconnect"
    self.wireless.DisconnectWireless()
    self.updateStatus()
    
  def on_actionRefresh_triggered(self, *args):
    if args: #Ignore the signal with an argument. See http://lists.kde.org/?l=pykde&m=113829850106412&w=2
      return
    self.refresh()

  def on_actionConnect_triggered(self, *args):
    if args: #Ignore the signal with an argument. See http://lists.kde.org/?l=pykde&m=113829850106412&w=2
      return
    print "connect"
    item=self.ui.netlist.currentItem()
    if not item:
      return
    nid=int(item.props['networkID'])
    # Mostrar boton de "conectando"
    self.showConnDisconn(2)
    
    #Guardamos la conexion (no deberia hacer falta)
    self.saveItem()
    
    
    self.wireless.ConnectWireless(nid)
    self.updateStatus()
    
  def updateStatus(self):
    
    print "updating status"
    self.config.DisableLogging()
    wireless_ip = self.wireless.GetWirelessIP() #do this so that it doesn't lock up.
    wiredConnecting = self.wired.CheckIfWiredConnecting()
    wirelessConnecting = self.wireless.CheckIfWirelessConnecting()
    if wirelessConnecting == True or wiredConnecting == True:
      # Update faster, because things are happening
      self.stTimer.setInterval(500)
      print "connecting",str(self.wireless.CheckWirelessConnectingMessage()),wirelessConnecting
      self.showConnDisconn(2)
      self.ui.netlist.setEnabled(False)
      if wirelessConnecting:
        self.statusBar().showMessage(language[str(self.wireless.CheckWirelessConnectingMessage())])
      if wiredConnecting:
        self.statusBar().showMessage(str(self.wired.CheckWiredConnectingMessage()))
      return 
    else:
      self.ui.netlist.setEnabled(True)
      
    # Update slower
    self.stTimer.setInterval(5000)
      
    if wireless_ip:
      print wireless_ip
      network = self.wireless.GetCurrentNetwork()
      if network:
        strength = self.wireless.GetCurrentSignalStrength()
        dbm_strength = self.wireless.GetCurrentDBMStrength()
        if strength is not None and dbm_strength is not None:
          # Change icons to connected on this one, to disconnected on all others
          if self.wiredItem: self.wiredItem.setIcon(QtGui.QIcon(":/network_disconnected_lan.svg"))
          for nID in self.wirelessItems:
            print nID,network
            if nID==network:
              self.wirelessItems[nID].setIcon(QtGui.QIcon(":/network_connected_wlan.svg"))
              print "icon set to connected"
            else:
              self.wirelessItems[nID].setIcon(QtGui.QIcon(":/network_disconnected_wlan.svg"))
          network = str(network)
          if self.daemon.GetSignalDisplayType() == 0:
            strength = str(strength)
          else:
            strength = str(dbm_strength)
          ip = str(wireless_ip)
          self.statusBar().showMessage('Connected to $A at $B (IP: $C)'.replace
                                                  ('$A',network).replace
                                                  ('$B',self.daemon.FormatSignalForPrinting(strength)).replace
                                                  ('$C',wireless_ip))
          self.showConnDisconn(1)
          return True

    wired_ip = self.wired.GetWiredIP()
    if wired_ip:
      if self.wired.CheckPluggedIn():
          if self.wiredItem: self.wiredItem.setIcon(QtGui.QIcon(":/network_connected_lan.svg"))
          self.statusBar().showMessage('Connected to wired network (IP: $A)'.replace('$A',wired_ip))
      self.showConnDisconn(1)
      return True
    self.statusBar().showMessage('Not connected')
    if self.wiredItem: self.wiredItem.setIcon(QtGui.QIcon(":/network_disconnected_lan.svg"))
    for nID in self.wirelessItems:
      self.wirelessItems[nID].setIcon(QtGui.QIcon(":/network_disconnected_wlan.svg"))
    self.showConnDisconn(0)
    
  def showConnDisconn(self,which=0):
    """Show either a connect or a disconnect action on the tooolbar, as needed"""
    if which==0: #Disconnected
      self.ui.actionConnect.setVisible(True)
      self.ui.actionDisconnect.setVisible(False)
      self.ui.actionConnecting.setVisible(False)
    elif which==1: #Connected
      self.ui.actionConnect.setVisible(False)
      self.ui.actionDisconnect.setVisible(True)
      self.ui.actionConnecting.setVisible(False)
    elif which==2: #Connecting
      self.ui.actionConnect.setVisible(False)
      self.ui.actionDisconnect.setVisible(False)
      self.ui.actionConnecting.setVisible(True)
    else:
      self.ui.actionConnect.setVisible(True)
      self.ui.actionDisconnect.setVisible(True)
      self.ui.actionConnecting.setVisible(True)
    
  def refresh(self):
    self.ui.netlist.clear()
    
    it=QtGui.QListWidgetItem("Wired Network")
    if self.wired.CheckPluggedIn():
      it.setIcon(QtGui.QIcon(":/network_connected_lan.svg"))
    else:
      it.setIcon(QtGui.QIcon(":/network_disconnected_lan.svg"))
    self.ui.netlist.addItem(it)
    
    self.wiredItem=it
    self.wirelessItems={}
    
    print 'Number of wireless networks detected:',self.wireless.GetNumberOfNetworks()
    for networkID in range(0,self.wireless.GetNumberOfNetworks()):
        # FIXME: Isn't this ripe for race conditions if a network disappears? Maybe it's guaranteed it won't?
        essid=self.wireless.GetWirelessProperty(networkID,'essid')
        it=QtGui.QListWidgetItem(essid)
        it.setIcon(QtGui.QIcon(":/network_disconnected_wlan.svg"))
        self.ui.netlist.addItem(it)
        self.wirelessItems[essid]=it
        it.props={}
        it.props['networkID']=networkID
        for key in ['essid','quality','strength','dbm_strength','bssid','mode','channel','encryption',
                    'encryption_method','ip','netmask','gateway','use_global_dns',
                    'automatic', 'enctype','dns1','dns2','dns3',
                   ]:
          
          it.props[key]=self.wireless.GetWirelessProperty(networkID,key)

    self.updateStatus()

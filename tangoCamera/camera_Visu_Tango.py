# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 13:33:11 2022
version : 2021.12


pip install git+https://github.com/julienGautier77/visu

"""

__author__='julien Gautier'
__version__='2022.03'

import tango
from tango import EventType
from PyQt6.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QWidget,QLayout

from PyQt6.QtWidgets import QComboBox,QSlider,QLabel,QSpinBox,QToolButton,QMenu,QInputDialog,QDockWidget
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6 import QtGui 
import sys,time
import pathlib,os
import qdarkstyle







class CAMERA(QWidget):
    
    signalData= QtCore.pyqtSignal(object)  #signal emited when a new image is ready for visualization
    
    
    
    def __init__(self, dp,confFile='confCamera.ini',**kwds):
        '''
        
        confFile : TYPE str, optional
            DESCRIPTION. 
                dep=Device Proxy 
                confFile= path to file.initr
                The default is 'confCamera.ini'.
        **kwds:
            affLight : TYPE boolean, optional
                DESCRIPTION.
                    affLight=False all the option are show for the visualisation
                    affLight= True only few option (save  open cross)
                    The default is True.
            multi add time sleep to access QApplication.processEvents() 
            + all kwds of VISU class
            
        '''
        
        
        super().__init__()
        
        self.version='Tango Viewer'
        self.ccdName=dp
        self.nbcam='camDefault'
        self.Cam = tango.DeviceProxy(dp)
        self._event_id = self.Cam.subscribe_event("img",EventType.CHANGE_EVENT,
                                                self.callback_receive)
        
        # self._event_id = self.Cam.subscribe_event('img',EventType.DATA_READY_EVENT,
        #                                      self.callback_receive)
        print('connected to',self.Cam)
        
        
        
        
        self.isConnected=True
        self.cameraType=self.Cam.model
        # except:
        #     self.isConnected=False
        # self._event_id = self._deviceProxy.subscribe_event("img",EventType.CHANGE_EVENT,
                                               # self)
       
        
        
        
        p = pathlib.Path(__file__)
        
        self.kwds=kwds
        
        
        if "affLight" in kwds:
            self.light=kwds["affLight"]
        else:
            self.light=True
        if "multi" in kwds:
            self.multi=kwds["multi"]
        else:
            self.multi=False 
        
        if "separate" in kwds:
            self.separate=kwds["separate"]
        else: 
            self.separate=True
            
        if "aff" in kwds: #  affi of Visu
            self.aff=kwds["aff"]
        else: 
            self.aff="right"    
        
        
        
        
        
        
        
        # self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5()) # qdarkstyle :  black windows style
        self.confPath=str(p.parent / confFile) # ini file path
        self.conf=QtCore.QSettings(self.confPath, QtCore.QSettings.Format.IniFormat) # ini file  # ini file 
        self.kwds["confpath"]=self.confPath
        sepa=os.sep
        print('conf',self.confPath)
        self.icon=str(p.parent) + sepa+'icons'+sepa
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.iconPlay=self.icon+'Play.png'
        self.iconSnap=self.icon+'Snap.png'
        self.iconStop=self.icon+'Stop.png'
        self.iconPlay=pathlib.Path(self.iconPlay)
        self.iconPlay=pathlib.PurePosixPath(self.iconPlay)
        self.iconStop=pathlib.Path(self.iconStop)
        self.iconStop=pathlib.PurePosixPath(self.iconStop)
        self.iconSnap=pathlib.Path(self.iconSnap)
        self.iconSnap=pathlib.PurePosixPath(self.iconSnap)
        self.nbShot=1
        
        self.version='Test'
        
        
        self.setup()
        self.setCamPara()
        #self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        
    def callback_receive(self,ev):
   
        # print ("Event -----push_event-----------------")
        # print ("Timestamp:      ", ev.reception_date)
        # print('dat       :   ' ,ev.attr_value.value) 
        # print(ev)
        if ev.attr_value.value is not None:
            self.data=ev.attr_value.value
            self.Display(ev.attr_value.value)
        
        
        
        
    def setCamPara(self):
        '''set min max gain and exp value of cam in the widget
        '''
        
        if self.isConnected==True: # if camera is connected we address min and max value  and value to the shutter and gain box
            # print('camshutter',self.CAM.camParameter["exposureTime"])
            # self.CAM.setTrigger("off")
            self.camParameter=dict()
            self.camParameter["expMax"]=self.Cam.expMax
            self.camParameter["expMin"]=self.Cam.expMin
            self.camParameter["gainMax"]=self.Cam.gainMax
            self.camParameter["gainMin"]=self.Cam.gainMin
            self.camParameter["exposureTime"]=self.Cam.exposure
            self.camParameter["gain"]=self.Cam.gainCam
            
            print('ici',self.camParameter)
            if self.camParameter["expMax"]>1500: # we limit exposure time at 1500ms
                self.hSliderShutter.setMaximum(1500)
                self.shutterBox.setMaximum(1500)
            else :
                self.hSliderShutter.setMaximum(int(self.camParameter["expMax"]))
                self.shutterBox.setMaximum(int(self.camParameter["expMax"]))
            
            self.hSliderShutter.setValue(int(self.camParameter["exposureTime"]))
            self.shutterBox.setValue(int(self.camParameter["exposureTime"]))
            self.hSliderShutter.setMinimum(int(self.camParameter["expMin"]+1))
            self.shutterBox.setMinimum(int(self.camParameter["expMin"]+1))
            
            
            
            self.hSliderGain.setMinimum(int(self.camParameter["gainMin"]))
            self.hSliderGain.setMaximum(int(self.camParameter["gainMax"]))
            self.hSliderGain.setValue(int(self.camParameter["gain"]))
            self.gainBox.setMinimum(int(self.camParameter["gainMin"]))
            self.gainBox.setMaximum(int(self.camParameter["gainMax"]))
            self.gainBox.setValue(int(self.camParameter["gain"]))
            
            self.actionButton()
            
        if  self.isConnected==False:
            self.setWindowTitle('Visualization         No camera connected      '   +  'v.  '+ self.version)
            self.runButton.setEnabled(False)
            self.snapButton.setEnabled(False)
            self.trigg.setEnabled(False)
            self.hSliderShutter.setEnabled(False)
            self.shutterBox.setEnabled(False)
            self.gainBox.setEnabled(False)
            self.hSliderGain.setEnabled(False)
            self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
            self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconSnap,self.iconSnap))
            
            
            
    def setup(self):  
        
            """ user interface definition 
            """
            self.setWindowTitle('Visualization    '+ self.cameraType+"   " + self.ccdName+'       v.'+ self.version)
            
    #         self.camNameLabel=QLabel('nomcam',self)
            
    #         self.camNameLabel.setText(self.ccdName)

    #         self.camNameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #         self.camNameLabel.setMaximumHeight(80)
    #         self.camNameLabel.setStyleSheet('font: bold 24px;color: purple')
    # #        self.camNameLabel.setStyleSheet('')
            
            vbox1=QVBoxLayout() # 
            # vbox1.addWidget(self.camNameLabel)
            
            hbox1=QHBoxLayout() # horizontal layout pour run snap stop
            self.sizebuttonMax=30
            self.sizebuttonMin=30

            self.runButton=QToolButton(self)
            self.runButton.setMaximumWidth(self.sizebuttonMax)
            self.runButton.setMinimumWidth(self.sizebuttonMax)
            self.runButton.setMaximumHeight(self.sizebuttonMax)
            self.runButton.setMinimumHeight(self.sizebuttonMax)
            self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: green;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"% (self.iconPlay,self.iconPlay) )
            
            self.snapButton=QToolButton(self)
            self.snapButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            menu=QMenu()
            menu.addAction('set nb of shot',self.nbShotAction)
            self.snapButton.setMenu(menu)
            self.snapButton.setMaximumWidth(self.sizebuttonMax)
            self.snapButton.setMinimumWidth(self.sizebuttonMax)
            self.snapButton.setMaximumHeight(self.sizebuttonMax)
            self.snapButton.setMinimumHeight(self.sizebuttonMax)
            self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: green;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"% (self.iconSnap,self.iconSnap) )
            
            self.stopButton=QToolButton(self)
            self.stopButton.setMaximumWidth(self.sizebuttonMax)
            self.stopButton.setMinimumWidth(self.sizebuttonMax)
            self.stopButton.setMaximumHeight(self.sizebuttonMax)
            self.stopButton.setMinimumHeight(self.sizebuttonMax)
            self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"% (self.iconStop,self.iconStop) )
            self.stopButton.setEnabled(False)
          
            
            hbox1.addWidget(self.runButton)
            hbox1.addWidget(self.snapButton)
            hbox1.addWidget(self.stopButton)
            # hbox1.addStretch(10)
            hbox1.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)#setFixedSize)#
            hbox1.setContentsMargins(0, 0, 0, 0)
            hbox1.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            vbox1.addLayout(hbox1)
            vbox1.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
            vbox1.setContentsMargins(0, 20, 10, 10)
            # vbox1.addSpacing(0)
            # vbox1.addStretch(1)
            self.widgetControl=QWidget(self)
            self.widgetControl.setLayout(vbox1)
            self.dockControl=QDockWidget(self)
            self.dockControl.setWidget(self.widgetControl)
            # self.dockControl.resize(80,80)
            self.trigg=QComboBox()
            self.trigg.setMaximumWidth(90)
            self.trigg.addItem('OFF')
            self.trigg.addItem('ON')
            self.trigg.setStyleSheet('font :bold 10pt;color: white')
            self.labelTrigger=QLabel('Trig')
            self.labelTrigger.setMaximumWidth(50)
            # self.labelTrigger.setMinimumHeight(50)
            self.labelTrigger.setStyleSheet('font :bold  10pt')
            self.itrig=self.trigg.currentIndex()
            hbox2=QHBoxLayout()
            hbox2.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
            hbox2.setContentsMargins(0, 20, 10, 10)
            hbox2.addWidget(self.labelTrigger)
            hbox2.addWidget(self.trigg)
            self.widgetTrig=QWidget(self)
            self.widgetTrig.setLayout(hbox2)
            self.dockTrig=QDockWidget(self)
            self.dockTrig.setWidget(self.widgetTrig)
            
            self.labelExp=QLabel('Exposure (ms)')
            self.labelExp.setStyleSheet('font :bold  10pt')
            self.labelExp.setMaximumWidth(140)
            self.labelExp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.hSliderShutter=QSlider(Qt.Orientation.Horizontal)
            self.hSliderShutter.setMaximumWidth(60)
            self.shutterBox=QSpinBox()
            self.shutterBox.setStyleSheet('font :bold  8pt')
            self.shutterBox.setMaximumWidth(120)
            
            hboxShutter=QHBoxLayout()
            hboxShutter.setContentsMargins(0, 0, 0, 5)
            hboxShutter.setSpacing(10)
            vboxShutter=QVBoxLayout()
            vboxShutter.setSpacing(0)
            vboxShutter.addWidget(self.labelExp)#,Qt.AlignLef)
            
            hboxShutter.addWidget(self.hSliderShutter)
            hboxShutter.addWidget(self.shutterBox)
            vboxShutter.addLayout(hboxShutter)
            vboxShutter.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
            vboxShutter.setContentsMargins(0, 0, 10, 0)
            vboxShutter.setSpacing(2)
            
            self.widgetShutter=QWidget(self)
            self.widgetShutter.setLayout(vboxShutter)
            self.dockShutter=QDockWidget(self)
            self.dockShutter.setWidget(self.widgetShutter)
            
            self.labelGain=QLabel('Gain')
            self.labelGain.setStyleSheet('font :bold  10pt')
            self.labelGain.setMaximumWidth(140)
            self.labelGain.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.hSliderGain=QSlider(Qt.Orientation.Horizontal)
            self.hSliderGain.setMaximumWidth(60)
            self.gainBox=QSpinBox()
            self.gainBox.setStyleSheet('font :bold  8pt')
            self.gainBox.setMaximumWidth(120)
            
            hboxGain=QHBoxLayout()
            hboxGain.setContentsMargins(0, 0, 0, 5)
            hboxGain.setSpacing(10)
            vboxGain=QVBoxLayout()
            vboxGain.setSpacing(0)
            vboxGain.addWidget(self.labelGain)
    
            hboxGain.addWidget(self.hSliderGain)
            hboxGain.addWidget(self.gainBox)
            vboxGain.addLayout(hboxGain)
            vboxGain.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
            
            vboxGain.setContentsMargins(0, 0, 10, 0)
            vboxGain.setSpacing(2)
            self.widgetGain=QWidget(self)
            self.widgetGain.setLayout(vboxGain)
            self.dockGain=QDockWidget(self)
            self.dockGain.setWidget(self.widgetGain)
            
            # self.TrigSoft=QPushButton('Trig Soft',self)
            # self.TrigSoft.setMaximumWidth(100)
            # self.vbox1.addWidget(self.TrigSoft)
        
            # self.vbox1.addStretch(1)
            # self.cameraWidget.setLayout(self.vbox1)
            # self.cameraWidget.setMinimumSize(150,200)
            # self.cameraWidget.setMaximumSize(200,900)
            
            hMainLayout=QHBoxLayout()
            
            if self.light==False: # light option : not all the option af visu 
                from visu import SEE
                self.visualisation=SEE(parent=self,name=self.nbcam,**self.kwds) ## Widget for visualisation and tools  self.confVisu permet d'avoir plusieurs camera et donc plusieurs fichier ini de visualisation
            else:
                from visu import SEELIGHT
                
                self.visualisation=SEELIGHT(parent=self,name=self.nbcam,**self.kwds)
                    
            self.visualisation.setWindowTitle(self.cameraType+"   " + self.ccdName+'       v.'+ self.version)
                
            self.dockTrig.setTitleBarWidget(QWidget())        
            self.dockControl.setTitleBarWidget(QWidget()) # to avoid tittle
            self.dockShutter.setTitleBarWidget(QWidget())
            self.dockGain.setTitleBarWidget(QWidget())
            
            if self.separate==True: # control camera button is not on the menu but in a widget at the left or right of the display screen
                self.dockTrig.setTitleBarWidget(QWidget())
                if self.aff=='left':
                    self.visualisation.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockControl)
                    self.visualisation.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockTrig)
                    self.visualisation.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockShutter)
                    self.visualisation.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dockGain)
                else:
                    self.visualisation.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.dockControl)
                    self.visualisation.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.dockTrig)
                    self.visualisation.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.dockShutter)
                    self.visualisation.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.dockGain)
            else:
            #self.dockControl.setFeatures(QDockWidget.DockWidgetMovable)
                self.visualisation.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea,self.dockControl)
                self.visualisation.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea,self.dockTrig)
                self.visualisation.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea,self.dockShutter)
                self.visualisation.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea,self.dockGain)
             
            hMainLayout.addWidget(self.visualisation)
            self.setLayout(hMainLayout)
            self.setContentsMargins(0, 0, 0, 0)
            #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # set window on the top 
            #self.activateWindow()
            #self.raise_()
            #self.showNormal()
            
    def actionButton(self): 
        '''action when button are pressed
        '''
        self.runButton.clicked.connect(self.acquireMultiImage)
        self.snapButton.clicked.connect(self.acquireOneImage)
        self.stopButton.clicked.connect(self.stopAcq)      
        self.shutterBox.editingFinished.connect(self.shutter)    
        self.hSliderShutter.sliderReleased.connect(self.mSliderShutter)
        
        self.gainBox.editingFinished.connect(self.gain)    
        self.hSliderGain.sliderReleased.connect(self.mSliderGain)
        self.trigg.currentIndexChanged.connect(self.trigger)
        
        
        # event subscription to receveive image from server
        self._event_id = self.Cam.subscribe_event("img",EventType.CHANGE_EVENT,
                                                self.callback_receive)
        
        
        
        # self.CAM.newData.connect(self.Display)
        # self.CAM.endAcq.connect(self.stopAcq)#,QtCore.Qt.DirectConnection)
        # self.TrigSoft.clicked.connect(self.softTrigger)
    
    
    def oneImage(self):
        #self.nbShot=1
        self.acquireOneImage()

    def nbShotAction(self):
        '''
        number of snapShot
        '''
        nbShot, ok=QInputDialog.getInt(self,'Number of SnapShot ','Enter the number of snapShot ')
        if ok:
            self.nbShot=int(nbShot)
            if self.nbShot<=0:
               self.nbShot=1
    
    
    def Display(self,data):
        '''Display data with visualisation module
        
        '''
        self.signalData.emit(data)
        # self.visualisation.newDataReceived(data)
        self.imageReceived=True
       
              
    def shutter (self):
        '''
        set exposure time 
        '''
        
        sh=self.shutterBox.value() # 
        self.hSliderShutter.setValue(sh) # set value of slider
        time.sleep(0.1)
        self.cam.exposure=sh # Set shutter CCD in ms
        self.conf.setValue(self.nbcam+"/shutter",float(sh))
        self.camParameter["exposureTime"]=sh
        self.conf.sync()
    
    
    
    def mSliderShutter(self): # for shutter slider 
        sh=self.hSliderShutter.value() 
        self.shutterBox.setValue(sh) # 
        self.Cam.exposure=sh # Set shutter CCD in ms
        self.conf.setValue(self.nbcam+"/shutter",float(sh))
        self.camParameter["exposureTime"]=sh
        # self.conf.sync()
        
        
    def gain (self):
        '''
        set gain
        '''
        g=self.gainBox.value() # 
        self.hSliderGain.setValue(g) # set slider value
        time.sleep(0.1)
        self.Cam.gainCam=g
        self.conf.setValue(self.nbcam+"/gain",float(g))
        self.conf.sync()
    
    def mSliderGain(self):
        '''
        set slider

        '''
        g=self.hSliderGain.value()
        self.gainBox.setValue(g) # set valeur de la box
        time.sleep(0.1)
        self.cam.gainCam=g
        self.conf.setValue(self.nbcam+"/gain",float(g))
        self.conf.sync()
        
    def trigger(self):
        
        ''' select trigger mode
         trigger on
         trigger off
        '''
        self.itrig=self.trigg.currentIndex()
        
        if self.itrig==1:
            self.Cam.trig=True
        else :
            self.Cam.trig=False
                
    def acquireOneImage(self):
        '''Start on acquisition
        '''
        self.imageReceived=False
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color:gray}"%(self.iconSnap,self.iconSnap))
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
        
        self.Cam.Grab()
        
    
    def acquireMultiImage(self):    
        ''' 
            start the acquisition thread
        '''
        
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconSnap,self.iconSnap))
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
        
        self.Cam.Play() # start mutli image acquisition thread 
        
        
    def stopAcq(self):
        
        '''Stop  acquisition
        '''
        
        if self.isConnected==True:
            self.Cam.Stop()
        
        self.runButton.setEnabled(True)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(True)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconSnap,self.iconSnap))
        
        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(True)  
    
    
    
    def close(self):
        if self.isConnected==True:
            pass#
            # self.Cam.closeCamera()
        
        
    def closeEvent(self,event):
        ''' closing window event (cross button)
        '''
        if self.isConnected==True:
             self.stopAcq()
             time.sleep(0.1)
             self.close()
            
            
            
if __name__ == "__main__":       
    
    appli = QApplication(sys.argv) 
    #appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    pathVisu='C:/Users/loa/Desktop/Python/camera/confCamera.ini'
    dp = 'Formation/camera/1'
    e = CAMERA(dp,fft='off',meas='on',affLight=False,aff='left',separate=False,multi=False,confpath=pathVisu) 
    
    e.show()
    
    appli.exec_()       
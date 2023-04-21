# -*- coding: utf-8 -*-
#
# This file is part of the AlliedCamera project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

"""

__all__ = ["AlliedCamera", "main"]

# PyTango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device, DeviceMeta
from tango.server import attribute, command
from tango.server import class_property, device_property
from tango import AttrQuality, AttrWriteType, DispLevel, DevState
# Additional import
# PROTECTED REGION ID(AlliedCamera.additionnal_import) ENABLED START #
# import alliedCam
from pyqtgraph.Qt import QtCore
import time

from threading import Thread
import vimba  ## pip install git+https://github.com/alliedvision/VimbaPython
import numpy as np

with vimba.Vimba.get_instance() as vmb:
    cameraIds=vmb.get_all_cameras()
    nbCamera=len(cameraIds)
    print( nbCamera,"Alliedvision Cameras available:")
    for i in range (0,nbCamera):
        print(cameraIds[i])


class AcquisitionThread(Thread):
    
    def __init__ (self, parent):
        super(AcquisitionThread,self).__init__()
        self.parent=parent
        
        
        self.stopRunAcq=False
        
    
    def run(self):
        self.stopRunAcq=False
        print('start')
        with vmb:
            with self.parent.cam0:
                            
                while self.stopRunAcq is not True :
                           
                    self.parent.set_state(tango.DevState.RUNNING)
                    try: 
                        frame=self.parent.cam0.get_frame(timeout_ms=3000)#00000000
                        data=(frame.as_numpy_ndarray())
                        data=data[:,:,0]
                        data=np.rot90(data,3)
                                   
                        if str(frame.get_status()) == "FrameStatus.Complete" : #np.max(data)>0 or 
                            self.parent.newImage(data)
                            print('acq)')

                    except:
                        self.parent.set_state(tango.DevState.FAULT)
                        pass
                
                
                
        
        self.parent.set_state(tango.DevState.STANDBY)
    
    def stopThread(self):
        self.stopRunAcq=True
        self.parent.set_state(tango.DevState.STANDBY)

   
class AcquisitionOneThread(Thread):

    def __init__ (self, parent):
        super(AcquisitionOneThread,self).__init__()
        self.parent=parent
        self.stopRunAcq=False
        
    
    def run(self):
       try: 
           self.parent.set_state(tango.DevState.RUNNING)
           
       except:
           self.parent.set_state(tango.DevState.FAULT)
    
    
    
    def stopThread(self):
        self.stopRunAcq=True
        self.parent.set_state(tango.DevState.STANDBY)

# PROTECTED REGION END #    //  AlliedCamera.additionnal_import


class AlliedCamera(Device):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(AlliedCamera.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  AlliedCamera.class_variable
    # ----------------
    # Class Properties
    # ----------------

    # -----------------
    # Device Properties
    # -----------------

    camID = device_property(
        dtype='str',
    )
    # ----------
    # Attributes
    # ----------

    exposure = attribute(
        dtype='int',
        access=AttrWriteType.READ_WRITE,
        unit="ms",
        max_value=1000,
    )
    gainCam = attribute(
        dtype='int',
        access=AttrWriteType.READ_WRITE,
    )
    trig = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )
    model = attribute(
        dtype='str',
    )
    expMax = attribute(
        dtype='double',
    )
    expMin = attribute(
        dtype='double',
    )
    gainMax = attribute(
        dtype='double',
    )
    gainMin = attribute(
        dtype='double',
    )
    img = attribute(
        dtype=(('uint',),),
        max_dim_x=1300, max_dim_y=1500,
    )
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # self.img.set_data_ready_event(True)
        self.set_change_event("img", True, False)
        # PROTECTED REGION ID(AlliedCamera.init_device) ENABLED START #
        
        print(self.camID)
        self.camParameter=dict()
        # self.camIsRunning=False
        self.nbShot=1
        
        
        with vmb:
            
            if self.camID is not None:
                try :
                    with vmb:
                        self.cam0=vmb.get_camera_by_id(self.camID)
                        
                        self.isConnected=True
                        
                        self.set_state(tango.DevState.STANDBY)
                except:
                    try:
                        print('Id not valid try to open the fisrt camera')
                        self.camID=cameraIds[0].get_id()
                        self.cam0=vmb.get_camera_by_id(self.camID) # we open the first one
                        self.set_state(tango.DevState.STANDBY)
                        self.isConnected=True
                    except:
                        self.set_state(tango.DevState.FAULT)
                        self.isConnected=False
            else: 
                try:
                    
                    self.camID=cameraIds[0].get_id()
                    self.cam0=vmb.get_camera_by_id(self.camID)# we open the first one
                    self.set_state(tango.DevState.STANDBY)
                    self.isConnected=True
                except:
                    self.set_state(tango.DevState.FAULT)
                    self.isConnected=False
                    
        if self.isConnected==True:
            self.setCamParameter()
        else:
            self.modelCam='no camera'
            
    def setCamParameter(self):
        """
        
        
        Set initial parameters
    
        """
        
        self.camLanguage=dict()
        

        with vmb:
            with self.cam0:
               # 
               # modelCam=self.cam0.get_model()
              self.modelCam=self.cam0.get_name()
              print( 'connected @:'  ,self.camID,'model : ',self.modelCam )
              
              self.cam0.TriggerMode.set('Off')
              self.cam0.TriggerSelector.set('AcquisitionStart')
              self.cam0.TriggerActivation.set('RisingEdge')
              self.cam0.AcquisitionMode.set('SingleFrame')#Continuous
                   
        ## init cam parameter## different command name depend on camera type 
        if self.modelCam=="GT1290":
            self.camLanguage['exposure']='ExposureTimeAbs'
            self.LineTrigger='Line1'
        if self.modelCam=="Manta":
            self.camLanguage['exposure']='ExposureTimeAbs'
            self.LineTrigger='Line1'
        if self.modelCam=='AVT Guppy PRO F031B': 
            self.camLanguage['exposure']='ExposureTime'
            self.LineTrigger='InputLines'
        if self.modelCam=='Allied Vision 1800 U-050m' :
            self.camLanguage['exposure']='ExposureTime'
            self.LineTrigger='Line1'
        if self.modelCam=='Allied Vision Mako U-029B' :
            self.camLanguage['exposure']='ExposureTime'
            self.LineTrigger='Line1'
        else:
            self.camLanguage['exposure']='ExposureTime'
            self.LineTrigger='Line1'
        
        with vmb:
            with self.cam0:
                
                self.camParameter["trigger"]=self.cam0.TriggerMode.get()
                
                if self.modelCam=='Allied Vision Mako U-029B':
                   pass
                else:
                   self.cam0.ExposureAuto.set('Off')
                   self.cam0.GainAuto.set('Off')
                   
                self.cam0.Height.set(self.cam0.HeightMax.get())
                self.cam0.Width.set(self.cam0.WidthMax.get())
                exp=self.cam0.get_feature_by_name(self.camLanguage['exposure'])
                self.camParameter["expMax"]=float(exp.get_range()[1]/1000)
                self.camParameter["expMin"]=float(exp.get_range()[0]/1000)+1
                self.camParameter["exposureTime"]=float(exp.get()/1000)
                self.camParameter["gainMax"]=self.cam0.Gain.get_range()[1]
                self.camParameter["gainMin"]=self.cam0.Gain.get_range()[0]
                self.camParameter["gain"]=self.cam0.Gain.get()
           
            print(self.camParameter)
            self.exposure.set_min_value(int(self.camParameter["expMin"]))
            self.exposure.set_max_value(int(self.camParameter["expMax"]))
            self.gainCam.set_min_value(int(self.camParameter["gainMin"]))
            self.gainCam.set_max_value(int(self.camParameter["gainMax"]))
        
        
       
        # PROTECTED REGION END #    //  AlliedCamera.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(AlliedCamera.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  AlliedCamera.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(AlliedCamera.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  AlliedCamera.delete_device

    # ------------------
    # Attributes methods
    # ------------------
    def newImage(self,data):
        self.imgData=data
        self.push_change_event("img",self.imgData)
        # self.push_data_ready_event("img",0)
        
    def read_exposure(self):
        # PROTECTED REGION ID(AlliedCamera.exposure_read) ENABLED START #
        with vmb:
                with self.cam0:
                        exp=self.cam0.get_feature_by_name(self.camLanguage['exposure'])
                        self.camParameter["exposureTime"]=int(exp.get())/1000
        
       
        return int(self.camParameter["exposureTime"])
        # PROTECTED REGION END #    //  AlliedCamera.exposure_read

    def write_exposure(self, value):
        # PROTECTED REGION ID(AlliedCamera.exposure_write) ENABLED START #
        with vmb:
                with self.cam0:
                        exp=self.cam0.get_feature_by_name(self.camLanguage['exposure'])
                        exp.set(float(value*1000))
                        self.camParameter["exposureTime"]=int(exp.get())/1000
                        print("exposure time is set to",self.camParameter["exposureTime"],' micro s')
        # PROTECTED REGION END #    //  AlliedCamera.exposure_write

    def read_gainCam(self):
        # PROTECTED REGION ID(AlliedCamera.gainCam_read) ENABLED START #
        with vmb:
                with self.cam0:
                    self.camParameter["gain"]=self.cam0.Gain.get()
        return  self.camParameter["gain"]
        # PROTECTED REGION END #    //  AlliedCamera.gainCam_read

    def write_gainCam(self, value):
        # PROTECTED REGION ID(AlliedCamera.gainCam_write) ENABLED START #
        with vmb:
                with self.cam0:
                    self.cam0.Gain.set(value) # 
                    self.camParameter["gain"]=self.cam0.Gain.get()
        print("Gain is set to",self.camParameter["gain"])   
        # PROTECTED REGION END #    //  AlliedCamera.gainCam_write

    def read_trig(self):
        # PROTECTED REGION ID(AlliedCamera.trig_read) ENABLED START #
        with vmb:
            with self.cam0:
               trig= self.cam0.TriggerMode.get()
        if trig=='on':
            trig=True
        else:
            trig=False
        return trig
        # PROTECTED REGION END #    //  AlliedCamera.trig_read

    def write_trig(self, value):
        # PROTECTED REGION ID(AlliedCamera.trig_write) ENABLED START #
        with vmb:
            with self.cam0:
                if value==True:
                    self.cam0.TriggerMode.set('On')
                    self.cam0.TriggerSource.set(self.LineTrigger)
                    self.itrig='on'
                    self.camParameter["trigger"]='On'
                else:
                    self.cam0.TriggerMode.set('Off')
                    self.camParameter["trigger"]='Off'
                    self.itrig='off'
                self.camParameter["trigger"]=self.cam0.TriggerMode.get()
        # PROTECTED REGION END #    //  AlliedCamera.trig_write

    def read_model(self):
        # PROTECTED REGION ID(AlliedCamera.model_read) ENABLED START #
        return self.modelCam
        # PROTECTED REGION END #    //  AlliedCamera.model_read

    def read_expMax(self):
        # PROTECTED REGION ID(AlliedCamera.expMax_read) ENABLED START #
        return int(self.camParameter["expMax"])
        # PROTECTED REGION END #    //  AlliedCamera.expMax_read

    def read_expMin(self):
        # PROTECTED REGION ID(AlliedCamera.expMin_read) ENABLED START #
        return int(self.camParameter["expMin"])
        # PROTECTED REGION END #    //  AlliedCamera.expMin_read

    def read_gainMax(self):
        # PROTECTED REGION ID(AlliedCamera.gainMax_read) ENABLED START #
        return int(self.camParameter["gainMax"])
        # PROTECTED REGION END #    //  AlliedCamera.gainMax_read

    def read_gainMin(self):
        # PROTECTED REGION ID(AlliedCamera.gainMin_read) ENABLED START #
        return int(self.camParameter["gainMin"])
        # PROTECTED REGION END #    //  AlliedCamera.gainMin_read

    def read_img(self):
        # PROTECTED REGION ID(AlliedCamera.img_read) ENABLED START #
        # self.push_change_event("img",self.imgData)
        return self.imgData
        # PROTECTED REGION END #    //  AlliedCamera.img_read

    # --------
    # Commands
    # --------

    @command
    @DebugIt()
    def Play(self):
        # PROTECTED REGION ID(AlliedCamera.Play) ENABLED START #
        # data=(50*np.random.rand(200,300)).round() + 150
        # self.newImage(data)
        self.acq=AcquisitionThread(self)
        self.acq.start()
        # PROTECTED REGION END #    //  AlliedCamera.Play

    @command
    @DebugIt()
    def Stop(self):
        # PROTECTED REGION ID(AlliedCamera.Stop) ENABLED START #
        self.acq.stopThread()
        # PROTECTED REGION END #    //  AlliedCamera.Stop

    @command
    @DebugIt()
    def Grab(self):
        # PROTECTED REGION ID(AlliedCamera.Grab) ENABLED START #
        self.acqOne=AcquisitionOneThread(self)
        self.acqOne.start()
        # PROTECTED REGION END #    //  AlliedCamera.Grab

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(AlliedCamera.main) ENABLED START #
   
    import tango
    return tango.server.run((AlliedCamera,), args=args, **kwargs)
    # PROTECTED REGION END #    //  AlliedCamera.main

if __name__ == '__main__':
    main()

#
# craftbeerpi3ArduinoTempProbes (CBP3ATP)
#
# Connects via serial to any arduino and reads out an analog temperature cable probe.
#
# Christian
# graetz23@gmail.com
# created 20200403
# version 20200403
#
# MIT License
#
# Copyright (c) 2020 CBP3ATP Christian (graetz23@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import os, sys, threading, time, serial
from modules import cbpi, app
from modules.core.hardware import SensorPassive
from modules.core.props import Property
from coolPSSM import PSSM_Client, PSSM_Command, PSSM_Hardware, PSSM_Message_Resolver, PSSM_XML

# for listing arduino's ttyACM0, ttyACM1, ..., in hardware settings
def searchTTYACM():
    try:
        arr = []
        for portTTY in os.listdir('/dev'):
            if (portTTY.startswith("ttyACM")):
                arr.append(portTTY)
        return arr
    except:
        return [] # not found then list nothing

# for listing arduino's possible baud rates in hardware settings
def genBaudRate():
    arr = [2400,4800,9600,19200,38400,57600,115200]
    return arr

# getting the string identifier for analog ports ..
def genArduinoAnalogPorts():
    HARDWARE = PSSM_Hardware( )
    arr = [ HARDWARE.ANLG0.TAG,
            HARDWARE.ANLG1.TAG,
            HARDWARE.ANLG2.TAG,
            HARDWARE.ANLG3.TAG,
            HARDWARE.ANLG4.TAG,
            HARDWARE.ANLG5.TAG ]
    return arr

# select adding system temperature
def getYesNo():
    arr = ['yes','no']
    return arr

class PSSM_ClientThread (threading.Thread):

    value = float( 0 )

    def __init__(self, id, name, port, baud, acmd):

        threading.Thread.__init__(self)

        self.ID = id
        self.NAME = name
        self.PORT = "/dev/" + port
        self.BAUD = baud
        self.ACMD = acmd
        self.PSSM_XML = PSSM_XML( )
        self.PSSM = PSSM_Client( self.PORT, self.BAUD )
        time.sleep(0.25) # give arduino some time
        self.value = float( 1 )
        self.runnig = True

    def shutdown(self):
        # if self.PSSM.SERIAL.isOpen( ):
        #      self.PSSM.writeID( self.PSSM.CMDS.STOP )
        #      time.sleep(0.25)
        #      self.PSSM.SERIAL.close( )
        #      time.sleep(0.25)
        pass

    def stop(self):
        # if self.PSSM.SERIAL.isOpen( ):
        #      self.PSSM.writeID( self.PSSM.CMDS.STOP )
        #      time.sleep(0.25)
        #      self.PSSM.SERIAL.close( )
        #      time.sleep(0.25)
        self.runnig = False

    def run(self):
        i = 0
        time.sleep(0.5)
        self.PSSM.writeID( self.PSSM.CMDS.RMD1 )
        time.sleep(0.5)
        while True:
            # try:
            # if self.PSSM.SERIAL.isOpen( ):
            self.PSSM.writeID( self.ACMD )
            time.sleep(1)
            xml = self.PSSM.getANSWER( ) # <A0>9.567</A0>
            pssm_msg = self.PSSM_XML.bake( xml ) # bake object
            temp = pssm_msg.DATA # 9.567
            self.value = float( temp )
            # else:
            #     self.value = 0 # error value ...
            # except:
            #     pass
            time.sleep( 4 )

@cbpi.sensor
class ArduinoTempSensors(SensorPassive):
    sensor_name = Property.Select( "arduino's analog port", genArduinoAnalogPorts(), description="Select the the analog port to read out NTC or PTC probes.")
    sensor_baud = Property.Select( "arduino's baud rate", genBaudRate(), description="Select the baud rate defined in your arduino program.")
    sensor_port = Property.Select( "arduino's /dev/ttyACM?", searchTTYACM(), description="Possible devices where an arduino is connected; if empty, no arduino connected.")
    #sensor_actv = Property.Select( "System Temperature", getYesNo(), description="Select to add CBP's system temperature or not.")
    #sensor_strt = Property.Select( "Startup Message", getYesNo(), description="Select to send the start up message: \"CBP3SerialSensors\"; to let arduino recognizing a starting point for data processing.")

    PSSM_Message_Resolver = None
    ACMD = None

    def init(self):

        # getting some object with ID and TAG
        pssm_MSG_RESOLVER = PSSM_Message_Resolver( )
        self.ACMD = pssm_MSG_RESOLVER.tryBuildFromAll( self.sensor_name )

        self.t = PSSM_ClientThread(self.id, self.sensor_name, self.sensor_port, self.sensor_baud, self.ACMD)
        time.sleep(0.25) # let time to set up internal thread for reading serial

        # def shutdown():
        #     shutdown.cb.shutdown()
        # shutdown.cb = self.t

        self.t.start()

    def stop(self):
        try:
            self.t.stop()
        except:
            pass

    def read(self):
        if self.get_config_parameter("unit", "C") == "C":
            self.data_received(round(self.t.value, 2))
            #self.data_received(round(4.2342, 2))
        else:
            self.data_received(round(9.0 / 5.0 * self.t.value + 32, 2))
            #self.data_received(round(9.0 / 5.0 * 4.2342 + 32, 2))

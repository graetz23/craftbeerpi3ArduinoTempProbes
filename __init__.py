#
# craftbeerpi3ArduinoTempProbes (CBP3ATP)
#
# Connects via serial to any arduino and reads out six analog temperature cable
# probe. The necessary arduino project for serving the probes:
# https://github.com/graetz23/ArduinoSerialStateTempProbes
#
# Christian
# graetz23@gmail.com
# created 20200403
# version 20200411
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

    value = float( 0 ) # no idea why, but CPB3 seems to need this var as float??

    XML_ANLG0 = None
    XML_ANLG1 = None
    XML_ANLG2 = None
    XML_ANLG3 = None
    XML_ANLG4 = None
    XML_ANLG5 = None

    DELAY = 0.10

    # def __init__(self, id, name, port, baud, acmd):
    def __init__(self, id, name, port, baud):

        threading.Thread.__init__(self)

        self.ID = id
        self.NAME = name
        self.PORT = "/dev/" + port
        self.BAUD = baud
        self.PSSM_XML = PSSM_XML( )
        self.PSSM = PSSM_Client( self.PORT, self.BAUD )
        time.sleep( self.DELAY * 2 )
        self.value = float( 1 )
        self.runnig = True

    def shutdown(self):
        if self.PSSM.SERIAL.isOpen( ):
             self.PSSM.writeID( self.PSSM.CMDS.STOP )
             time.sleep( self.DELAY * 2 )
             self.PSSM.SERIAL.close( )
             time.sleep( self.DELAY )
        self.runnig = False

    def stop(self):
        if self.PSSM.SERIAL.isOpen( ):
             self.PSSM.writeID( self.PSSM.CMDS.STOP )
             time.sleep( self.DELAY * 2 )
             self.PSSM.SERIAL.close( )
             time.sleep( self.DELAY )
        self.runnig = False

    def run(self):
        self.PSSM.writeID( self.PSSM.CMDS.RMD1 )
        # self.PSSM.writeID( self.PSSM.CMDS.RMD1.COPY( ) ) # PROTOTYP pattern
        time.sleep( self.DELAY )
        self.ANSWER = self.PSSM.getANSWER( ) # <A0>9.567</A0>
        time.sleep( self.DELAY * 2 )
        while self.runnig:
            # try:
            # do some run mode RECOVERY
            self.PSSM.writeID( self.PSSM.CMDS.STAT ) # <10>
            time.sleep( self.DELAY )
            self.STATUS = self.PSSM.getANSWER( ) # <RMD1/>
            time.sleep( self.DELAY )
            if self.STATUS != self.PSSM.STATES.MODE1.TAG:
                self.PSSM.writeID( self.PSSM.CMDS.RMD1 ) # <11>
                time.sleep( self.DELAY )
                self.ANSWER = self.PSSM.getANSWER( ) # <AKNW/>
                time.sleep( self.DELAY * 2 )

            # CYCLIC stress arduino for sensor values; here analog values
            self.PSSM.writeID( self.PSSM.HARDWARE.ANLG0 ) # <40>
            time.sleep( self.DELAY )
            self.XML_ANLG0 = self.PSSM.getANSWER( ) # <A0>9.567</A0>
            time.sleep( self.DELAY )
            self.PSSM.writeID( self.PSSM.HARDWARE.ANLG1 ) # <41>
            time.sleep( self.DELAY )
            self.XML_ANLG1 = self.PSSM.getANSWER( ) # <A1>9.567</A1>
            time.sleep( self.DELAY )
            self.PSSM.writeID( self.PSSM.HARDWARE.ANLG2 ) # <42>
            time.sleep( self.DELAY )
            self.XML_ANLG2 = self.PSSM.getANSWER( ) # <A2>9.567</A2>
            time.sleep( self.DELAY )
            self.PSSM.writeID( self.PSSM.HARDWARE.ANLG3 ) # <43>
            time.sleep( self.DELAY )
            self.XML_ANLG3 = self.PSSM.getANSWER( ) # <A3>9.567</A3>
            time.sleep( self.DELAY )
            self.PSSM.writeID( self.PSSM.HARDWARE.ANLG4 ) # <44>
            time.sleep( self.DELAY )
            self.XML_ANLG4 = self.PSSM.getANSWER( ) # <A4>9.567</A4>
            time.sleep( self.DELAY )
            self.PSSM.writeID( self.PSSM.HARDWARE.ANLG5 ) # <45>
            time.sleep( self.DELAY )
            self.XML_ANLG5 = self.PSSM.getANSWER( ) # <A5>9.567</A5>
            time.sleep( self.DELAY )

    def getData(self, acmd):
        temp = float( 1 )
        data = float( 1 )
        # select which to bake ..
        if acmd.TAG == self.PSSM.HARDWARE.ANLG0.TAG:
            pssm_msg = self.PSSM_XML.bake( self.XML_ANLG0 ) # bake object
        elif acmd.TAG == self.PSSM.HARDWARE.ANLG1.TAG:
            pssm_msg = self.PSSM_XML.bake( self.XML_ANLG1 ) # bake object
        elif acmd.TAG == self.PSSM.HARDWARE.ANLG2.TAG:
            pssm_msg = self.PSSM_XML.bake( self.XML_ANLG2 ) # bake object
        elif acmd.TAG == self.PSSM.HARDWARE.ANLG3.TAG:
            pssm_msg = self.PSSM_XML.bake( self.XML_ANLG3 ) # bake object
        elif acmd.TAG == self.PSSM.HARDWARE.ANLG4.TAG:
            pssm_msg = self.PSSM_XML.bake( self.XML_ANLG4 ) # bake object
        elif acmd.TAG == self.PSSM.HARDWARE.ANLG5.TAG:
            pssm_msg = self.PSSM_XML.bake( self.XML_ANLG5 ) # bake object
        else:
            pssm_msg = PSSM_Data( "AX", "-1" )
        temp = pssm_msg.DATA # 9.567
        data = float( temp )
        return data

@cbpi.sensor
class ArduinoTempProbes(SensorPassive):
    sensor_name = Property.Select( "arduino's analog port", genArduinoAnalogPorts(), description="Select the the analog port to read out NTC or PTC probes.")
    sensor_baud = Property.Select( "arduino's baud rate", genBaudRate(), description="Select the baud rate defined in your arduino program.")
    sensor_port = Property.Select( "arduino's /dev/ttyACM?", searchTTYACM(), description="Possible devices where an arduino is connected; if empty, no arduino connected.")

    PSSM_Message_Resolver = None
    ACMD = None

    def init(self):

        # getting some object with ID and TAG
        pssm_MSG_RESOLVER = PSSM_Message_Resolver( )
        self.ACMD = pssm_MSG_RESOLVER.tryBuildFromAll( self.sensor_name )

        sensor_port_no = int( self.sensor_port.replace("ttyACM", "") )# => {0,1,..}

        pssm_Client = None

        # if there is already a TASK running the that serial device, get it
        if 'pssm_Clients' in globals( ):
            noOfClients = len( pssm_Clients )
            if noOfClients - 1 >= sensor_port_no :
                pssm_Client = pssm_Clients[ sensor_port_no ] # <= existing client for ttyACM{0,1,..}

        if pssm_Client == None :
            global pssm_Clients
            pssm_Clients = []
            pssm_Client = PSSM_ClientThread(self.id, self.sensor_name, self.sensor_port, self.sensor_baud )
            pssm_Clients.append( pssm_Client )
            self.t = pssm_Client
            # def shutdown():
            #     shutdown.cb.shutdown()
            # shutdown.cb = self.t
            self.t.start( ) # start thread for me and others
        else:
            self.t = pssm_Client # should be running already started by some other

        # TODO if pssm_Client is still None, something is wrong, break down

    def stop(self):
        try:
            self.t.stop()
        except:
            pass

    def read(self):
        if self.get_config_parameter("unit", "C") == "C":
            result = self.t.getData( self.ACMD )
            self.data_received( round( result, 2 ) )
        else:
            result = self.t.getData( self.ACMD )
            self.data_received( round( 9.0 / 5.0 * result + 32, 2 ) )

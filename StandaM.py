'''
Motors:
    Move a given number of steps                            DONE
    Set current position to zero                            DONE
    Get current position                                    DONE

'''
# ref: https://files.xisupport.com/other_files/JupyterNotebook/Standa_8SMC5_USB_Python_tutorial.html
import pathlib
import os
import time
import libximc.highlevel as ximc

from tango import AttrQuality, AttrWriteType, DevState, DispLevel, AttReqType, Database
from tango.server import Device, attribute, command
from tango.server import class_property, device_property

db = Database()
try:
   prop = db.get_property('ORBendPoint', 'Pool/' + instance_name)
   orb_end_point = prop['Pool/' + instance_name][0]
   os.environ["ORBendPoint"] = orb_end_point
except:
   pass

class StandaM(Device):
    _my_current = 2.3456
    _my_range = 0.0
    _my_compliance = 0.0
    _output_on = False
    _available_cameras = ""
    _device_uri="Rossa"
    _axis = ""

    host = device_property(dtype=str, default_value="localhost")
    port = class_property(dtype=int, default_value=10000)
    #@command(dtype_in=float, dtype_out=str)
    #cmd_list = { 'move_calibrat' : [  [float , "Number" ], [ str, "Number * 2" ] ] }

    def init_device(self):
        super().init_device()
        self.info_stream(f"Power supply connection details: {self.host}:{self.port}")
        self.set_state(DevState.ON)
		# Devices search
        devices = ximc.enumerate_devices(ximc.EnumerateFlags.ENUMERATE_NETWORK | ximc.EnumerateFlags.ENUMERATE_PROBE)
        if len(devices) == 0:
            self.info_stream("The real devices were not found. A virtual device will be used.")
        else:
            # Print real devices list
            self.info_stream("Found {} real device(s):".format(len(devices)))
            for device in devices:
                self.info_stream("  {}".format(device))
        self.set_status("Standa Motor is ON")
        self.info_stream("\r Standa Motor is ON \r")

    def delete_device(self):
        return


    device_uri = attribute(
        label="Device that is going to be use",
        dtype=str,
        fget="get_divece",
    )
    

    # Standa
    def GetDivece(self):
        return self._device_uri
    
    @command(dtype_out=str)
    def GetListDiveces(self):
        report = ""
        devices = ximc.enumerate_devices(ximc.EnumerateFlags.ENUMERATE_NETWORK | ximc.EnumerateFlags.ENUMERATE_PROBE)
        if len(devices) == 0:
            self.info_stream("The real devices were not found. A virtual device will be used.")
        else:
            # Print real devices list
            self.info_stream("Found {} real device(s):".format(len(devices)))
            for device in devices:
                report += str(device)+"\t"
        return "Dice found: "+report
	
    @command(dtype_in=str, dtype_out=str)    
    def SetDevice(self, device):
        self._device_uri = r"xi-com:\\.\COM"+str(device)
        return "it was selected the device "+device
    
    @command( dtype_out=str)    
    def SetDeviceAsVirtual(self):
        virtual_device_filename = "virtual_motor_controller_1.bin"
        virtual_device_file_path = os.path.join(pathlib.Path().cwd(), virtual_device_filename)
        self._device_uri = "xi-emu:///{}".format(virtual_device_file_path)
        return "it was selected the device "+self._device_uri
    


        
    @command( dtype_out=str)
    def ConnectMotor(self):
        try:
            self._axis = ximc.Axis(self._device_uri)
            # To open the connection, you must manually call `open_device()` method
            self._axis.open_device()
            return "Connection established"
        except:
            self.info_stream("Problem on open_connection")
            return "Problem on open_connection"
    
    @command( dtype_out=str)
    def DisconnectMotor(self):
        try:
            self._axis.close_device()
            print("Device disconnected")
            return "Device disconnected"
        except:
            self.info_stream("Problem on close_connection")
            return "Problem on close_connection"
 
#____________ Get current position  __________________  
    @command(dtype_out=str)
    def GetPosition(self):
        position = self._axis.get_position()
        return str(position)

#____________ Set current position to zero __________________
    @command(dtype_out=str)
    def SetZero(self):
        self._axis.command_zero()
        return "Current position is set as zero"
    
#____________ Absolute movement to the position __________________
    @command(dtype_in=int,dtype_out=str)
    def MoveTo(self,next_position):
        # get_position method returns position_t object
        position = self._axis.get_position()
        self.info_stream("Initial position:"+ str(position.Position))
        
        self._axis.command_move(next_position, 0)
        print("Moving...")
        self._axis.command_wait_for_stop(100)

        position = self._axis.get_position()
        self.info_stream("Final position:"+ str(position.Position))
        return "Stop moving at "+ str(position.Position)
    
#____________ Relative movement to the position __________________    
    @command(dtype_in=int, dtype_out=str)
    def RelativeShift(self,relative_shift):
        print("Perform a relative shift by", relative_shift)
        print("So we are going to", position.Position, "+", relative_shift, " =", position.Position + relative_shift)
        self._axis.command_movr(relative_shift, 0)

        print("Moving...")
        self._axis.command_wait_for_stop(100)

        position = self._axis.get_position()
        print("Current position:", position.Position)

        return "Stop moving at "+ str(position.Position)
    
#____________ Movement Using user units __________________
    @command(dtype_in=float, dtype_out=str)
    def SetUserUnit(self,unit_coef):
        # ==== User unit setup ====
        # We will use mm as user units
        # In our example conversion coefficient will be 0.0025 mm / step.
        # Set conversion coefficient for your stage here if needed
        step_to_mm_conversion_coeff = unit_coef  # mm / step

        # Get information about microstep mode
        engine_settings = self._axis.get_engine_settings()

        # Now we can set calibration settings for our axis
        self._axis.set_calb(step_to_mm_conversion_coeff, engine_settings.MicrostepMode)

        # ==== Perform a shift by using user units (mm in our case) ====
        position_calb = self._axis.get_position_calb()
        return "Unit was set as: "+ str(position_calb.Position) +" mm / step"
    
    @command(dtype_in=float, dtype_out=str)
    def MoveCalibrate(self,next_position_in_mm):
        # ==== Perform a shift by using user units (mm in our case) ====
        position_calb = self._axis.get_position_calb()
        print("Current position:", position_calb.Position, "mm")

        print("Move to position:", next_position_in_mm, "mm")
        self._axis.command_move_calb(next_position_in_mm)

        print("Moving...")
        self._axis.command_wait_for_stop(100)

        position_calb = self._axis.get_position_calb()
        return "Perform a shift: " +str(position_calb.Position) + " mm"

        
if __name__ == "__main__":
    StandaM.run_server()



#  Because we are using the 'with' statement context-manager, disposal has been taken care of.

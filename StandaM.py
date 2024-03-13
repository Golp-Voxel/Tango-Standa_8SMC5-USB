import pathlib
import os
import time
import libximc.highlevel as ximc

from tango import AttrQuality, AttrWriteType, DevState, DispLevel, AttReqType, Database
from tango.server import Device, attribute, command
from tango.server import class_property, device_property



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
    cmd_list = { 'move_calibrat' : [  [float , "Number" ], [ str, "Number * 2" ] ] }

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

    current = attribute(
        label="Current",
        dtype=float,
        display_level=DispLevel.EXPERT,
        access=AttrWriteType.READ_WRITE,
        unit="A",
        format="8.4f",
        min_value=0.0,
        max_value=8.5,
        min_alarm=0.1,
        max_alarm=8.4,
        min_warning=0.5,
        max_warning=8.0,
        fget="get_current",
        fset="set_current",
        doc="the power supply current",
    )


    device_uri = attribute(
        label="Device that is going to be use",
        dtype=str,
        fget="get_divece",
    )
    
    @attribute
    def voltage(self):
        return 10.0

    def get_current(self):
        return self._my_current

    def set_current(self, current):
        print("Current set to %f" % current)
        self._my_current = current

    # Standa
    def get_divece(self):
        return self._device_uri
    
    @command(dtype_out=str)
    def get_list_diveces(self):
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
    def set_device(self, device):
        self._device_uri = r"xi-com:\\.\COM"+str(device)
        return "it was selected the device "+device
    
    @command( dtype_out=str)    
    def set_device_as_virtual(self):
        virtual_device_filename = "virtual_motor_controller_1.bin"
        virtual_device_file_path = os.path.join(pathlib.Path().cwd(), virtual_device_filename)
        self._device_uri = "xi-emu:///{}".format(virtual_device_file_path)
        return "it was selected the device "+self._device_uri
    
    
    def open_connection(self):
        try:
            self._axis = ximc.Axis(self._device_uri)
            # To open the connection, you must manually call `open_device()` method
            self._axis.open_device()
            return "Connection established"
        except:
            self.info_stream("Problem on open_connection")
            return "Problem on open_connection"
        
    def close_connection(self):
        try:
            self._axis.close_device()
            print("Device disconnected")
            return "Device disconnected"
        except:
            self.info_stream("Problem on close_connection")
            return "Problem on close_connection"
        
    @command(dtype_in=str, dtype_out=str)
    def connection(self,state):
        if state == "open":
           return self.open_connection()
        elif state == "close":
            return self.close_connection()
        else:
            return state + "not define"
        
    @command(dtype_out=str)
    def set_zero(self):
        self._axis.command_zero()
        return "Current position is set as zero"
    
#____________ Absolute movement to the position __________________
    @command(dtype_in=int,dtype_out=str)
    def move_to(self,next_position):
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
    def relative_shift(self,relative_shift):
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
    def set_user_unit(self,unit_coef):
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
        return "Current position: "+ str(position_calb.Position) +" mm"
    
    @command(dtype_in=float, dtype_out=str)
    def  move_calibrat(self,next_position_in_mm):
        # ==== Perform a shift by using user units (mm in our case) ====
        position_calb = self._axis.get_position_calb()
        print("Current position:", position_calb.Position, "mm")

        print("Move to position:", next_position_in_mm, "mm")
        self._axis.command_move_calb(next_position_in_mm)

        print("Moving...")
        self._axis.command_wait_for_stop(100)

        position_calb = self._axis.get_position_calb()
        return "Current position:" +str(position_calb.Position) + " mm"
    # @command(dtype_in=str, dtype_out=str)    
    # def get_foto(self, name):
    #     with TLCameraSDK() as sdk:
    #         available_cameras = sdk.discover_available_cameras()
    #         with sdk.open_camera(available_cameras[0]) as camera:
    #             camera.exposure_time_us = 10000  # set exposure to 11 ms
    #             camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
    #             camera.image_poll_timeout_ms = 1000  # 1 second polling timeout
        
    #             camera.arm(2)
        
    #             camera.issue_software_trigger()
        
    #             frame = camera.get_pending_frame_or_null()
    #             if frame is not None:
    #                 print("frame #{} received!".format(frame.frame_count))
    #                 frame.image_buffer
    #                 image_buffer_copy = np.copy(frame.image_buffer)
    #                 numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
    #                 nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels, 3), 0, dtype=np.uint8)
    #                 nd_image_array[:,:,0] = numpy_shaped_image
    #                 nd_image_array[:,:,1] = numpy_shaped_image
    #                 nd_image_array[:,:,2] = numpy_shaped_image
    #                 if name == "":
    #                     filename="tango_works.jpg"
    #                 else:
    #                     filename=name
    #                 cv2.imwrite(filename,nd_image_array)
    #                 #cv2.imshow("Image From TSI Cam", nd_image_array)
    #             else:
    #                 print("Unable to acquire image, program exiting...")
    #                 exit()
                    
    #             cv2.waitKey(0)
    #             camera.disarm()
				
    #         return str(os.path.abspath(os.getcwd()))+"\\" + filename + was taken"

    range = attribute(label="Range", dtype=float)

    @range.setter
    def range(self, new_range):
        self._my_range = new_range

    @range.getter
    def current_range(self):
        return self._my_range, time(), AttrQuality.ATTR_WARNING

    @range.is_allowed
    def can_range_be_changed(self, req_type):
        if req_type == AttReqType.WRITE_REQ:
            return not self._output_on
        return True

    compliance = attribute(label="Compliance", dtype=float)

    @compliance.read
    def compliance(self):
        return self._my_compliance

    @compliance.write
    def new_compliance(self, new_compliance):
        self._my_compliance = new_compliance

    @command(dtype_in=bool, dtype_out=bool)
    def output_on_off(self, on_off):
        self._output_on = on_off
        return self._output_on
        
if __name__ == "__main__":
    StandaM.run_server()



#  Because we are using the 'with' statement context-manager, disposal has been taken care of.

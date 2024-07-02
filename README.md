# Standa 8SMC5-USB Controller - Tango Device Server

This repository contains the driver for controlling an SLM with the Tango Control. After cloning this repository with the following command

```
git clone https://github.com/Golp-Voxel/Tango_Standa_8SMC5-USB.git
```

It is necessary to create the `tango-env` using the following command:

```
python -m venv tango-env
```

After activating it you can install all the models to run this tool by using the command:

```
pip install -r Requirements.txt
```

To complete the installation, it is necessary to copy the `StandaM.bat` template and change the paths to the installation folder. And the command to run the `...\tango-env\Scripts\activate` script. 

## Available commands

After installing the Tango Device server, that can detect and connect to a Standa Controller 8SMC5-USB, being able to move the motors connect to the it.

- [GetListDiveces](#GetListDiveces)
- [SetDevice](#SetDevice)
- [ConnectMotor](#ConnectMotor)
- [DisconnectMotor](#DisconnectMotor)
- [GetPosition](#GetPosition)
- [SetZero](#SetZero)
- [MoveTo](#MoveTo)
- [RelativeShift](#RelativeShift)
- [SetUserUnit](#SetUserUnit)
- [MoveCalibrate](#MoveCalibrate)

### GetListDiveces

Lists the diveces connected to the PC.

```python
GetListDevices()
```

### SetDevice

The command recives the SerialCOM number of the device(`int`) to be connected. 

```python
SetDevice(device)
```

### ConnectMotor

Connect the Device that was set using the function `SetDevice(device)`.

```python
ConnectDevice()
```

### DisconnectMotor

Disconnects the device that is connected to the server.

```python
DisconnectMotor()
```

### GetPosition

This command returns the current position of the the motor connected to the controller Standa 8SMC5-USB.

```python
GetPosition()
```

### SetZero

Set the current position us the origin (to zero).

```python
SetZero()
```

### MoveTo

You can use this command to move axis to a specific absolute position respectively.

```python
MoveTo(next_position)
```

### RelativeShift

You can use this command to move axis to a specific relative position respectively.


```python
RelativeShift(relative_shift)
```

### SetUserUnit

By default all values (position, speed, acceleration…) are represented in motor steps and microsteps. 

To use user units you should know conversion coefficient in units per step. In most cases you can find such coefficient in specification for your stage.


```python
SetUserUnit(unit_coef)
```

### MoveCalibrate

This command uses calibrate unit done in `SetUserUnit(unit_coef)` to move the motor (You can use more convenient custom units such as millimeters, inches, degrees,radians...).

```python
MoveCalibrate(next_position_in_mm)
```


## Example of Tango client 

```python
import tango
```


## Reference 

- [Standa 8SMC5-USB Python tutorial](https://files.xisupport.com/other_files/JupyterNotebook/Standa_8SMC5_USB_Python_tutorial.html)
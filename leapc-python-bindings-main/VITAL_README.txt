Requirement for using LeapMotion Hand Tracking Device:

1. Install Python version 3.8.x only

2. Install the latest Ultraleap Gemini for desktop version
   (https://leap2.ultraleap.com/downloads/leap-motion-controller-2/)

3. Install Germini LeapC Python Bindings from Github
   (https://github.com/ultraleap/leapc-python-bindings)

4. Type the following commands in cmd for libraries installation:
   pip install build
   pip install cffi
   pip install opencv-python
   pip install numpy
   pip install pyserial
   pip install leapc-python-api

5. Go to this directory using cmd
   C:\Users\Intel NUC\Desktop\leapc-python-bindings-main\leapc-python-bindings-main\examples
   type the following command to start the program of controlling the robot arm:
   python visualiser.py

Troubleshooting:
1. Import error: cannot import leap as "something"
Solution:
- Go to this directory below and copy all the python files
  C:\Users\Intel NUC\Desktop\leapc-python-bindings-main\leapc-python-bindings-main\leapc-python-api\src\leap

- Go to this directory below, delete all the python files and paste the previously copied python files here
  C:\Users\Intel NUC\AppData\Local\Programs\Python\Python38\Lib\site-packages\leap

2. Attribut error: COMX cannot be found
- Go to Device Manager> Ports
- Check the COM number of the USB serial device of Teensy 4.1
- Go to this python file 
  C:\Users\Intel NUC\Desktop\leapc-python-bindings-main\leapc-python-bindings-main\examples\pyduino.py
- Go to line 11 of the python file and change the COM number
- Remember to save the python file!

----------------------------- or -----------------------------------
- Opening the visualiser.py and the AR4_teensy_serial_communicator.ino file at the same time is disallowed
- Only open one file to run: the python file, visualiser.py\
- Close other unecessary windows, especially the AR4_teensy_serial_communicator.ino

3. Teensy program 
- Go to this INO file
  C:\Users\Intel NUC\Desktop\leapc-python-bindings-main\leapc-python-bindings-main\examples\AR4_teensy_serial_communicator
- Run the program to the Teensy 4.1
- Close the INO file once the program is uploaded

Reminder when controlling the robot arm:
- Power up the robot arm first before initializing the python program
- The robot will automatically go to the reset mode, each motor touches its limit switch
- Once reset is done, initialize the python program
- When robot arm is not in used, please replug the power port for resetting its position


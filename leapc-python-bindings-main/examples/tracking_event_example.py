"""Prints the palm position of each hand, every frame. When a device is 
connected we set the tracking mode to desktop and then generate logs for 
every tracking frame received. The events of creating a connection to the 
server and a device being plugged in also generate logs. 
"""

import leap
import time
from pyduino import *


class MyListener(leap.Listener):
    oldtime = time.time()
    newtime = time.time()
    
    # FIXME if servo is not attached to pin 2
    SERVO_PIN = 2 # Azimuthal Servo motor pin
    AZIMUTHAL_LIMIT = 180 # we want our motor to go between 0 and 180



    def on_connection_event(self, event):
        # if your arduino was running on a serial port other than '/dev/ttyACM0/'
        self.a = Arduino()
        
        # sleep to ensure ample time for computer to make serial connection 
        time.sleep(3)
        print("Connected")


    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def on_exit(self, controller):
        
        # Reset servo position when you stop program
        self.a.servo_write(self.SERVO_PIN,90) 
        self.a.close()

        print("Exited")

    def on_tracking_event(self, event):

        self.newtime = time.time()

        if self.newtime - self.oldtime >0.1:

            print(f"Frame {event.tracking_frame_id} with {len(event.hands)} hands.")
            # if len(event.hands) == 0:
            #     x = 180
            for hand in event.hands:                
                hand_type = "left" if str(hand.type) == "HandType.Left" else "right"
                x= hand.palm.position.x
                print(
                    f"Hand id {hand.id} is a {hand_type} hand with position ({hand.palm.position.x}, {hand.palm.position.y}, {hand.palm.position.z})."
                )


            # FIXME depending on orientation of servo motor
            # if motor is upright, Leap Device will register a 0 degree angle if hand is all the way to the left
            #XPOS_servo = abs(MyListener.AZIMUTHAL_LIMIT-hand.palm.position.x*MyListener.AZIMUTHAL_LIMIT)
            if len(event.hands) != 0 and hand_type == "right":
                XPOS_servo = x
                if XPOS_servo >180:
                    XPOS_servo = 180
                if XPOS_servo <0:
                    XPOS_servo = 0
                print(" Servo Angle = %d " %(180-int(XPOS_servo)))
                    
                # write the value to servo on arduino
                self.a.servo_write(self.SERVO_PIN,180-int(XPOS_servo)) # turn LED on
                # update the old time
            self.oldtime = self.newtime
        else:
            pass

def main():
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)
        while running:
            time.sleep(1)


if __name__ == "__main__":
    main()

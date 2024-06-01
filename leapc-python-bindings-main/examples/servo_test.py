# Simple Leap motion program to track the position of your hand and move one servo
# import the libraries where the LeapMotionSDK is
import sys

import leap, _thread, time
#from leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from pyduino import *

class SampleListener(leap.Listener):
    
    oldtime = time.time()
    newtime = time.time()

    # FIXME if servo is not attached to pin 2
    SERVO_PIN = 2 # Azimuthal Servo motor pin
    AZIMUTHAL_LIMIT = 180 # we want our motor to go between 0 and 180

    def on_init(self, event):

        # if your arduino was running on a serial port other than '/dev/ttyACM0/'
        # declare: a = Arduino(serial_port='/dev/ttyXXXX')
        self.a = Arduino()
        
        # sleep to ensure ample time for computer to make serial connection 
        time.sleep(3)
        
        print("Initialized")

    def on_connect(self, event):
        print("Connected")

        # Enable gestures
        event.enable_gesture(leap.Gesture.TYPE_CIRCLE);
        event.enable_gesture(leap.Gesture.TYPE_KEY_TAP);
        event.enable_gesture(leap.Gesture.TYPE_SCREEN_TAP);
        event.enable_gesture(leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, event):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, event):
        
        # Reset servo position when you stop program
        self.a.servo_write(self.SERVO_PIN,90) 
        self.a.close()

        print("Exited")

    def on_frame(self, event):

        # we only want to get the position of the hand every so often
        self.newtime = time.time()
        if self.newtime-self.oldtime > 0.1: # if difference between times is 10ms

            print(f"Frame {event.tracking_frame_id} with {len(event.hands)} hands.")
            
            # Get hands
            for hand in event.hands:

                handType = "Left hand" if hand.is_left else "Right hand"
                
                print("  %s, id %d, x-position: %s" % (handType, hand.id, hand.palm.position.x ))
                print("  %s, id %d, y-position: %s" % (handType, hand.id, hand.palm.position.y ))
                print("  %s, id %d, z-position: %s" % (handType, hand.id, hand.palm.position.z ))
 
            # FIXME depending on orientation of servo motor
            # if motor is upright, Leap Device will register a 0 degree angle if hand is all the way to the left
            XPOS_servo = abs(SampleListener.AZIMUTHAL_LIMIT-hand.palm.position.x*SampleListener.AZIMUTHAL_LIMIT) 
            print(" Servo Angle = %d " %(int(XPOS_servo)))
            
            # write the value to servo on arduino
            self.a.servo_write(self.SERVO_PIN,int(XPOS_servo)) # turn LED on

            # update the old time
            self.oldtime = self.newtime
        else:
            pass # keep advancing in time until 10 millisecond is reached

def main():

    # Create a sample listener and controller
    my_listener = SampleListener()
    connection = leap.Connection()

    # Have the sample listener receive events from the controller
    connection.add_listener(my_listener)

    # Keep this process running until Enter is pressed
    print("Press Enter to quit...")
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
import leap
import numpy as np
import cv2
import time
from pyduino import *
from leap import datatypes as ldt
import math
import numpy

x = 500 #500
y = 700 #700
#---------- Define the tracking mode ----------
_TRACKING_MODES = {
    leap.TrackingMode.Desktop: "Desktop",
    leap.TrackingMode.HMD: "HMD",
    leap.TrackingMode.ScreenTop: "ScreenTop",
}

def location_end_of_finger(hand: ldt.Hand, digit_idx: int) -> ldt.Vector:
    digit = hand.digits[digit_idx]
    return digit.distal.next_joint


def sub_vectors(v1: ldt.Vector, v2: ldt.Vector) -> list:
    return map(float.__sub__, v1, v2)


def fingers_pinching(thumb: ldt.Vector, index: ldt.Vector):
    diff = list(map(abs, sub_vectors(thumb, index)))

    if diff[0] < 18 and diff[1] < 18 and diff[2] < 18:
        return True, diff
    else:
        return False, diff
    
class Canvas:
    def __init__(self):
        self.name = "Python Gemini Visualiser"
        self.screen_size = [x, y]
        self.hands_colour = (255, 255, 255)
        self.font_colour = (0, 255, 44)
        self.hands_format = "Skeleton"
        self.output_image = np.zeros((self.screen_size[0], self.screen_size[1], 3), np.uint8)
        self.tracking_mode = None

    def set_tracking_mode(self, tracking_mode):
        self.tracking_mode = tracking_mode

    def toggle_hands_format(self):
        self.hands_format = "Dots" if self.hands_format == "Skeleton" else "Skeleton"
        print(f"Set hands format to {self.hands_format}")

    def get_joint_position(self, bone):
        if bone:
            return int(bone.x + (self.screen_size[1] / 2)), int(bone.z + (self.screen_size[0] / 2))
        else:
            return None

    def render_hands(self, event):
        # Clear the previous image
        self.output_image[:, :] = 0

        cv2.putText(
             self.output_image,
             f"Tracking Mode: {_TRACKING_MODES[self.tracking_mode]}",
             (10, self.screen_size[0] - (x-30)),
             cv2.FONT_HERSHEY_SIMPLEX,
             0.5,
             self.font_colour,
             1,
        )

        if len(event.hands) == 0:
            return

        for i in range(0, len(event.hands)):
            hand = event.hands[i]
            hand_type = "left" if str(hand.type) == "HandType.Left" else "right"

            if (hand_type == "left"):
                self.org = 170
            if (hand_type == "right"):
                self.org = y-120

            for index_digit in range(0, 5):
                digit = hand.digits[index_digit]
                for index_bone in range(0, 4):
                    bone = digit.bones[index_bone]
                    if self.hands_format == "Dots":
                        prev_joint = self.get_joint_position(bone.prev_joint)
                        next_joint = self.get_joint_position(bone.next_joint)
                        if prev_joint:
                            cv2.circle(self.output_image, prev_joint, 2, self.hands_colour, -1)

                        if next_joint:
                            cv2.circle(self.output_image, next_joint, 2, self.hands_colour, -1)

                    if self.hands_format == "Skeleton":
                        wrist = self.get_joint_position(hand.arm.next_joint)
                        elbow = self.get_joint_position(hand.arm.prev_joint)
                        if wrist:
                            cv2.circle(self.output_image, wrist, 3, self.hands_colour, -1)

                        if elbow:
                            cv2.circle(self.output_image, elbow, 3, self.hands_colour, -1)

                        if wrist and elbow:
                            cv2.line(self.output_image, wrist, elbow, self.hands_colour, 2)

                        bone_start = self.get_joint_position(bone.prev_joint)
                        bone_end = self.get_joint_position(bone.next_joint)

                        if bone_start:
                            cv2.circle(self.output_image, bone_start, 3, self.hands_colour, -1)

                        if bone_end:
                            cv2.circle(self.output_image, bone_end, 3, self.hands_colour, -1)

                        if bone_start and bone_end:
                            cv2.line(self.output_image, bone_start, bone_end, self.hands_colour, 2)

                        if ((index_digit == 0) and (index_bone == 0)) or (
                            (index_digit > 0) and (index_digit < 4) and (index_bone < 2)
                        ):
                            index_digit_next = index_digit + 1
                            digit_next = hand.digits[index_digit_next]
                            bone_next = digit_next.bones[index_bone]
                            bone_next_start = self.get_joint_position(bone_next.prev_joint)
                            if bone_start and bone_next_start:
                                cv2.line(
                                    self.output_image,
                                    bone_start,
                                    bone_next_start,
                                    self.hands_colour,
                                    2,
                                )

                        if index_bone == 0 and bone_start and wrist:
                            cv2.line(self.output_image, bone_start, wrist, self.hands_colour, 2)
                        
                cv2.putText(
                self.output_image,
                #f"Frame {event.tracking_frame_id} with {len(event.hands)} hands.",
                f"Hand id {hand.id}: {hand_type} hand",
                (self.org-170, self.screen_size[0]-130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.font_colour,
                1,
                )

                cv2.putText(
                self.output_image,
                f"Position X: {hand.palm.position.x:.3f}",
                (self.org- 170, self.screen_size[0] - 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.font_colour,
                1,
                )

                cv2.putText(
                self.output_image,
                f"Position Y: {hand.palm.position.y:.3f}",
                (self.org-170, self.screen_size[0] - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.font_colour,
                1,
                )

                cv2.putText(
                self.output_image,
                f"Position Z: {hand.palm.position.z:.3f}",
                (self.org-170, self.screen_size[0] - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.font_colour,
                1,
                )


                


class TrackingListener(leap.Listener):
    oldtime = time.time()
    newtime = time.time()

    # FIXME if servo is not attached to pin 2
    J5stepPin = 8 # Azimuthal Servo motor pin
    J5dirPin = 9
    J2stepPin = 2
    J2dirPin = 3
    AZIMUTHAL_LIMIT = 180 # we want our motor to go between 0 and 180
    SERVO_PINZ = 4 #Altitude Servo motor pin
    ALTITUDE_LIMIT = 90
    SERVO_PINY = 7 
    LEDPIN = 13

    def __init__(self, canvas):
        self.canvas = canvas

    def on_connection_event(self, event):
        # if your arduino was running on a serial port other than '/dev/ttyACM0/'
        self.a = Arduino()
        
        # sleep to ensure ample time for computer to make serial connection 
        time.sleep(3)
        print("Connected")

    def on_tracking_mode_event(self, event):
        self.canvas.set_tracking_mode(event.current_tracking_mode)
        print(f"Tracking mode changed to {_TRACKING_MODES[event.current_tracking_mode]}")

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")
        
    def on_tracking_event(self, event):

        self.newtime = time.time()

        if self.newtime - self.oldtime >0.1:
            self.canvas.render_hands(event)
            #print(f"Frame {event.tracking_frame_id} with {len(event.hands)} hands.")
            # if len(event.hands) == 0:
            #     x = 180
            for hand in event.hands:                
                hand_type = "left" if str(hand.type) == "HandType.Left" else "right"
                c = hand.grab_strength
                x = hand.palm.position.x
                z = hand.palm.position.z
                y = hand.palm.position.y
                #w = leap.hand.arm.rotation
            
            # FIXME depending on orientation of servo motor
            # if motor is upright, Leap Device will register a 0 degree angle if hand is all the way to the left
            #XPOS_servo = abs(MyListener.AZIMUTHAL_LIMIT-hand.palm.position.x*MyListener.AZIMUTHAL_LIMIT)
            if len(event.hands) != 0 and hand_type == "right":
                XPOS = x
                ZPOS = z
                YPOS = y
                CPOS = c

                a1 = numpy.conj(hand.palm.orientation.w)*hand.arm.rotation.w 
                a2 = numpy.conj(hand.palm.orientation.x)*hand.arm.rotation.x 
                a3 = numpy.conj(hand.palm.orientation.y)*hand.arm.rotation.y         
                a4 = numpy.conj(hand.palm.orientation.z)*hand.arm.rotation.z 

                t0 = +2.0 * (a1 * a2 + a3 * a4)
                t1 = +1.0 - 2.0 * (a2 * a2 + a3 * a3)
                roll_x = math.degrees(math.atan2(t0, t1))
                FPOS = round(roll_x)

                t3 = +2.0 * (hand.arm.rotation.w * hand.arm.rotation.z + hand.arm.rotation.x * hand.arm.rotation.y)
                t4 = +1.0 - 2.0 * (hand.arm.rotation.y * hand.arm.rotation.y + hand.arm.rotation.z * hand.arm.rotation.z)
                WPOS = math.degrees(math.atan2(t3, t4))

                if CPOS == 1:
                    self.C = 0
                else:
                    self.C = 60

                if FPOS >= -2 and FPOS <= 2:
                    self.F = 500*FPOS + 1000

                if FPOS <-2:
                    self.F = 0
                
                if FPOS > 2:
                    self.F = 2000

                if WPOS >= -180 and WPOS <= -0:
                    self.W = -round(WPOS,0) * 20.8 #(0,180) to (0, 3750)
                
                if WPOS >=180 and WPOS <= 120:
                    self.W = 3744
                
                if WPOS >= 0 and WPOS <=120:
                    self.W = 0

                if XPOS >= -100 and XPOS <= 200:
                    self.X = 300*(int(XPOS)) + 30000
                
                if XPOS <-100:
                    self.X = 0

                if XPOS >200:
                    self.X = 90000

                if YPOS >= 200 and YPOS <=400:
                     self.Y = 40*int(YPOS) - 8000
                
                if YPOS <200:
                     self.Y = 0
                
                if YPOS >400:
                     self.Y = 8000

                if ZPOS >=-140 and ZPOS <=110:
                     self.Z = -36*int(ZPOS) + 3960

                if (ZPOS <-140):
                    self.Z = 9000
                
                if (ZPOS >110):
                    self.Z = 0

                cv2.putText(
                    self.canvas.output_image,
                    f"Grab: {self.C}",
                    (self.canvas.org, self.canvas.screen_size[0] - 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    self.canvas.font_colour,
                    1,
                )

                cv2.putText(
                    self.canvas.output_image,
                    f"Palm: {self.F}",
                    (self.canvas.org, self.canvas.screen_size[0] - 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    self.canvas.font_colour,
                    1,
                )

                cv2.putText(
                    self.canvas.output_image,
                    f"Base: {self.X}",
                    (self.canvas.org, self.canvas.screen_size[0] - 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    self.canvas.font_colour,
                    1,
                )

                cv2.putText(
                self.canvas.output_image,
                f"Arm: {self.Y}",
                (self.canvas.org, self.canvas.screen_size[0] - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.canvas.font_colour,
                1,
                )

                cv2.putText(
                self.canvas.output_image,
                f"Elbow: {self.Z}",
                (self.canvas.org, self.canvas.screen_size[0] - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.canvas.font_colour,
                1,
                )

                cv2.putText(
                self.canvas.output_image,
                f"Wrist: {int(self.W)}",
                (self.canvas.org, self.canvas.screen_size[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.canvas.font_colour,
                1,
                )

                cv2.putText(
                self.canvas.output_image,
                f"Rotation: {round(WPOS,0):.0f}",
                (self.canvas.org-170, self.canvas.screen_size[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.canvas.font_colour,
                1,
                )

                cv2.putText(
                self.canvas.output_image,
                f"Clamp: {int(CPOS)}",
                (self.canvas.org-170, self.canvas.screen_size[0] - 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.canvas.font_colour,
                1,
                )

                cv2.putText(
                self.canvas.output_image,
                f"Flex: {round(roll_x,0):.0f}",
                (self.canvas.org-170, self.canvas.screen_size[0] - 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.canvas.font_colour,
                1,
                )

                # # write the value to servo on arduino
                # self.a.stepper_write(self.J5stepPin,self.J5dirPin, int(self.I)) # turn LED on
                # self.a.stepper_write(self.J2stepPin,self.J2dirPin,int(self.K)) # turn LED on
                self.a.stepper_write(0,int(self.Z),int(self.Y), int(self.W), int(self.C), int(self.X)) # turn LED on
                #self.a.stepper_write(int(self.X),int(self.Z),int(self.Y), int(self.W), int(self.C), int(self.F)) # turn LED on
                # self.a.servo_write(self.SERVO_PINZ,180-int(self.J)) # turn LED on
                # # update the old time
                
            self.oldtime = self.newtime
        else:
            pass
        # print(f"Frame {event.tracking_frame_id} with {len(event.hands)} hands.")
        # for hand in event.hands:
        #     hand_type = "left" if str(hand.type) == "HandType.Left" else "right"
        #     print(
        #         f"Hand id {hand.id} is a {hand_type} hand with position ({hand.palm.position.x}, {hand.palm.position.y}, {hand.palm.position.z})."
        #     )
            


def main():
    canvas = Canvas()

    print(canvas.name)
    print("")
    print("Press <key> in visualiser window to:")
    print("  x: Exit")
    print("  h: Select HMD tracking mode")
    print("  s: Select ScreenTop tracking mode")
    print("  d: Select Desktop tracking mode")
    print("  f: Toggle hands format between Skeleton/Dots")

    tracking_listener = TrackingListener(canvas)

    connection = leap.Connection()
    connection.add_listener(tracking_listener)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)
        canvas.set_tracking_mode(leap.TrackingMode.Desktop)

        while running:
            cv2.imshow(canvas.name, canvas.output_image)

            key = cv2.waitKey(1)

            if key == ord("x"):
                break
            elif key == ord("h"):
                connection.set_tracking_mode(leap.TrackingMode.HMD)
            elif key == ord("s"):
                connection.set_tracking_mode(leap.TrackingMode.ScreenTop)
            elif key == ord("d"):
                connection.set_tracking_mode(leap.TrackingMode.Desktop)
            elif key == ord("f"):
                canvas.toggle_hands_format()


if __name__ == "__main__":
    main()

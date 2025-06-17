from ultrasonic import Ultrasonic
from motor import Ordinary_Car
from servo import Servo
from infrared import Infrared
from camera import Camera
from adc import ADC
import cv2
import numpy as np
import time
import math
import utils2 as utils

import curses

class Car:
    def __init__(self):
        self.servo = None
        self.sonic = None
        self.motor = None
        self.infrared = None
        self.adc = None
        self.camera = None
        self.car_record_time = time.time()
        self.car_sonic_servo_angle = 30
        self.car_sonic_servo_dir = 1
        self.car_sonic_distance = [30, 30, 30]
        self.time_compensate = 3 #Depend on your own car,If you want to get the best out of the rotation mode, change the value by experimenting.
        self.start()

    def start(self):  
        if self.servo is None:
            self.servo = Servo()
        if self.sonic is None:
            self.sonic = Ultrasonic()
        if self.motor is None:
            self.motor = Ordinary_Car()
        if self.infrared is None:
            self.infrared = Infrared()
        if self.adc is None:
            self.adc = ADC() 
        if self.camera is None:
            self.camera = Camera()
        self.speed = 1500

    def close(self):
        self.motor.set_motor_model(0,0,0,0)
        self.sonic.close()
        self.motor.close()
        self.infrared.close()
        self.adc.close_i2c()
        self.servo = None
        self.sonic = None
        self.motor = None
        self.infrared = None
        self.adc = None


    def forward(self, speed=1500):
        self.motor.set_motor_model(speed, speed, speed, speed)

    def backward(self, speed=1500):
        self.motor.set_motor_model(-speed, -speed, -speed, -speed)

    def turn_left(self, speed=1500):
        self.motor.set_motor_model(-speed, -speed, speed, speed)

    def turn_right(self, speed=1500):
        self.motor.set_motor_model(speed, speed, -speed, -speed)

    def stop(self):
        self.motor.set_motor_model(0, 0, 0, 0)

   
def control_car(car, stdscr):
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)  # don't block on getch()
    stdscr.clear()
    stdscr.addstr("Press arrow keys (Ctrl+C to quit):\n")
    stdscr.refresh()


    try:
        while True:
            key = stdscr.getch()

            if car.sonic is not None:
                # Get distance from ultrasonic sensor
                distance = car.sonic.get_distance()
                if distance is not None:
                    if distance < 45:
                        #stdscr.addstr("Obstacle detected! Stopping car.\n")
                        car.stop()
                        car.backward(800)  # Back up for 1 second
                        time.sleep(0.5)
                        car.stop()
                        stdscr.addstr("Obstacle detected! Backing up.\n")
                        continue

            if key == -1:
                # No key pressed right now
                time.sleep(0.05)
                continue

            if key == curses.KEY_UP:
               
                stdscr.addstr("Up pressed\n")
                car.forward()
            elif key == curses.KEY_DOWN:
                stdscr.addstr("Down pressed\n")
                car.backward()
            elif key == curses.KEY_LEFT:
            
                stdscr.addstr("Left pressed\n")
                car.turn_left()
            elif key == curses.KEY_RIGHT:
                stdscr.addstr("Right pressed\n")
                car.turn_right()
            elif key == ord('s'):
                stdscr.addstr("Stop pressed\n")
                car.stop()
            elif key == ord('1'):
                car.speed = 400
                car.forward(car.speed)
                stdscr.addstr("Speed set to 400\n")
            elif key == ord('2'):
                car.speed = 600
                car.forward(car.speed)
                stdscr.addstr("Speed set to 600\n")
            elif key == ord('3'):
                car.speed = 800
                car.forward(car.speed)
                stdscr.addstr("Speed set to 800\n")
            elif key == ord('4'):
                car.speed = 1000
                car.forward(car.speed)
                stdscr.addstr("Speed set to 1000\n")
            elif key == ord('5'):
                car.speed = 1200
                car.forward(car.speed)
                stdscr.addstr("Speed set to 1200\n")
            elif key == ord('6'):
                car.speed = 1500
                car.forward(car.speed)
                stdscr.addstr("Speed set to 1500\n")
            elif key == ord('7'):
                car.speed = 1800
                car.forward(car.speed)
                stdscr.addstr("Speed set to 1800\n")

            else:
                stdscr.addstr("Unknown key pressed\n")
                car.stop()
            stdscr.refresh()
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

def test_car_light():
    car = Car()
    try:
        print("Program is starting...")
        while True:
            car.mode_light()
    except KeyboardInterrupt:
        car.close()
        print("\nEnd of program")

def test_car_rotate():
    car = Car()
    print("Program is starting...")
    try:
        car.mode_rotate(0)
    except KeyboardInterrupt:
        print ("\nEnd of program")
        car.motor.set_motor_model(0,0,0,0)
        car.close()

def get_direction(camera):
    """Determine the direction based on the image.
    Args:
        image: The image captured from the camera.
    Returns:
        An angle between 45 and 135 degrees"""
    frame = car.camera.get_frame()  # Get the current frame from the camera
    img = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)
    img = utils.prep_image(img, 1, 1, trimFromTop = 0.3)
    cv2.imshow("Frame", img)  # Display the frame using OpenCV
    cv2.waitKey(1)  # Wait for a short time to allow OpenCV to update the display

    return 90 # corresponds to straight ahead, placeholder angle

def test_cam_nav():
    """Test camera navigation."""
    car = Car()
    # initscr = curses.initscr()
    # curses.curs_set(0)  # Hide the cursor
    # initscr.clear()
    # initscr.refresh()
    try:
        print("Press Ctrl+C to stop the program...")

        left_speed = 1500
        right_speed = 1500
        turn_factor = 5  # Adjust this factor to control the turning sensitivity
       
        while True:
            left_speed = 1500
            right_speed = 1500
            angle = get_direction(car.camera)  # Get the direction from the camera

            # Big angle, make a sharper turn, smaller angle, make a slight turn
            # Can't test it but we will put some temp code here

            if angle > 135 or angle < 45:
                print("Bad angle")
            
            if angle < 90:
                # Turn left
                print("Turning left with angle:", angle)
                delta = (90 - angle) * turn_factor
                left_speed -= delta

            elif angle > 90:
                # Turn right
                print("Turning right with angle:", angle)
                delta = (angle - 90) * turn_factor
                right_speed -= delta

    except KeyboardInterrupt:
        print("\nEnd of program")
        car.camera.close()  # Close the camera

if __name__ == '__main__':

    print('Program is starting ... ')  # Print a message indicating the start of the program
    test_cam_nav()  # Test camera navigation
    # car = Car()
    # initscr = curses.initscr()
    # curses.curs_set(0)  # Hide the cursor
    # initscr.clear()
    # initscr.refresh()
    # try:
    #     # Uncomment the function you want to test
    #     control_car(car, initscr)  # Control car with arrow keys
    #     # test_car_light()  # Test car light mode
    #     # test_car_rotate()  # Test car rotation mode
    # except KeyboardInterrupt:
    #     print("\nEnd of program")
    # finally:
    #     initscr.clear()
    #     initscr.refresh()
    #     curses.endwin()
    #     car.close()
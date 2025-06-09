from ultrasonic import Ultrasonic
from motor import Ordinary_Car
from servo import Servo
from infrared import Infrared
from adc import ADC
import time
import math

import curses

class Car:
    def __init__(self):
        self.servo = None
        self.sonic = None
        self.motor = None
        self.infrared = None
        self.adc = None
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

   
def control_car(stdscr):
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.clear()
    stdscr.addstr("Press arrow keys (Ctrl+C to quit):\n")

    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP:
            stdscr.addstr("Up arrow pressed\n")
            car.forward()
        elif key == curses.KEY_DOWN:
            stdscr.addstr("Down arrow pressed\n")
            car.backward()
        elif key == curses.KEY_LEFT:
            stdscr.addstr("Left arrow pressed\n")
            car.turn_left() 
        elif key == curses.KEY_RIGHT:
            stdscr.addstr("Right arrow pressed\n")
            car.turn_right()
        elif key == ord('q'):
            stdscr.addstr("Quitting...\n")
            car.stop()
            break
        elif key == ord('s'):
            stdscr.addstr("Stopping...\n")
            car.stop()
        else:
            stdscr.addstr("Invalid key pressed\n")
            car.stop()
        stdscr.refresh()

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

if __name__ == '__main__':
    car = Car()
    try:
        # Uncomment the function you want to test
        control_car(curses.initscr())  # Control car with arrow keys
        # test_car_light()  # Test car light mode
        # test_car_rotate()  # Test car rotation mode
    except KeyboardInterrupt:
        print("\nEnd of program")
        car.close()
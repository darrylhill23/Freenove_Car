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

if __name__ == '__main__':
    car = Car()
    initscr = curses.initscr()
    curses.curs_set(0)  # Hide the cursor
    initscr.clear()
    initscr.refresh()
    try:
        # Uncomment the function you want to test
        control_car(car, initscr)  # Control car with arrow keys
        # test_car_light()  # Test car light mode
        # test_car_rotate()  # Test car rotation mode
    except KeyboardInterrupt:
        print("\nEnd of program")
    finally:
        initscr.clear()
        initscr.refresh()
        curses.endwin()
        car.close()
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
import cam_utils

from pyzbar.pyzbar import decode


import curses

servo0Center = 95
servo1Down = 60
servo1Straight = 90

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



count = 0
def get_direction(camera):
    """Determine the direction based on the image.
    Args:
        image: The image captured from the camera.
    Returns:
        An angle between 45 and 135 degrees"""
    frame = camera.get_frame()  # Get the current frame from the camera
    img = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)
    img = utils.prep_image(img, 1, 1, trimFromTop = 0.3)

    global count
    count += 1
    if count % 10 == 0:
        print("Processing frame number: ", count)
    if img is None:
        print("Failed to decode image from camera stream.")
        return 90


    cv2.imwrite(f"frame-{count}.jpg", img)  # Save the image to a file for debugging

    #warped = cam_utils.birdseye(img)
    # cv2.imshow("Frame", img)  # Display the frame using OpenCV
    # cv2.waitKey(1)  # Wait for a short time to allow OpenCV to update the display
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    # # Apply Gaussian blur - doens't work well
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    #blurred = gray.copy()
    

    # # Apply Canny edge detection
    edges = cv2.Canny(blurred, 20, 60)
    

    # # Dilate and erode the image
    # dilated = cv2.dilate(edges, None, iterations=1)
    # eroded = cv2.erode(dilated, None)

    contours = cam_utils.find_contours(edges)

    print("Number of contours: ", len(contours))
    contours = utils.reduce_contours(contours)
    print("Number of contours after reduction: ", len(contours))
    contours = cam_utils.warped_contours(contours)

    average_angle = 0
    total_length = 0

    for contour in contours:
            
        #cv2.drawContours(result_image, [contour], -1, (0, 255, 0), 3)
        segment_points = cam_utils.get_segments(contour)
        
        for i, segment in enumerate(segment_points):
            #cv2.drawContours(result_image, [[segment]], -1, (0, 255, 0), 3)
            #cv2.line(result_image, segment[0], segment[1], (0, 255, 0), 2)
            angle = cam_utils.get_angle_segment(segment[0], segment[1])   
            angle = cam_utils.convert_angle(angle)
            if angle > 135 or angle < 45:
                print("*********Bad angle for segment******* ", angle)
            

            length = cam_utils.get_length_segment(segment[0], segment[1])
            total_length += length
            average_angle += angle*length
            #print(f"Segment {i}: Start: {segment[0]}, End: {segment[1]}, Angle: {angle:.2f} degrees, Length: {length:.2f} pixels")
            # cv2.imshow('Contours', result_image)
            # cv2.waitKey(0)
        
    if total_length > 0:
        average_angle /= total_length

    print(f"Average angle: {average_angle:.2f} degrees")

    #write the average angle to a file for debugging
    with open(f"average_angle-{count}.txt", "w") as f:
        f.write(f"Average angle for frame {count}: {average_angle:.2f} degrees\n")
        f.write(f"Total length: {total_length:.2f} pixels\n")
        f.write(f"Number of contours: {len(contours)}\n")

    return average_angle 



qrcount = 0
def get_qr_code(car):
    """Get QR code from the camera stream."""
    '''Bring the camera up - assume the stream is started'''

    global qrcount

    for i in range(servo1Down, servo1Straight+1, 1):
        car.servo.set_servo_pwm('1', i)
        time.sleep(0.1)

    time.sleep(0.2)
    frame = car.camera.get_frame()  # Get the current frame from the camera
    img = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print("Failed to decode image from camera stream.")
        return None

    cv2.imwrite(f"qrcode-{qrcount}.jpg", img)  

    qrcount = qrcount + 1

    decoded_objects = decode(img)
    

    for i in range(servo1Straight, servo1Down-1, -1):
        car.servo.set_servo_pwm('1', i)
        time.sleep(0.1)

    for obj in decoded_objects:
        print("QR Code detected:", obj.data.decode('utf-8'))
        return obj.data.decode('utf-8')

    print("No QR Code detected.")
    return None

piccount = 0
def take_pic(car):
    """Get QR code from the camera stream."""
    '''Bring the camera up - assume the stream is started'''

    global piccount

    for i in range(servo1Down, servo1Straight+1, 1):
        car.servo.set_servo_pwm('1', i)
        time.sleep(0.1)

    time.sleep(0.8)
    frame = car.camera.get_frame()  # Get the current frame from the camera
    img = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print("Failed to decode image from camera stream.")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # # Apply Gaussian blur - doens't work well
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    #blurred = gray.copy()
    
    # # Apply Canny edge detection
    edges = cv2.Canny(blurred, 20, 60)
    

    ''' 
        Dilate and erode the image - when the camera is shaky, which
        is anytime the robot is moving, these two things make 
        contour detection more difficult.
    '''
    # dilated = cv2.dilate(edges, None, iterations=1)
    # eroded = cv2.erode(dilated, None)

    contours = cam_utils.find_contours(edges)

    print("Number of contours: ", len(contours))

    # this attempts to make every contour at most 4 segments. 
    # This will make things better when there is little noise,
    # or sometimes worse if there is a lot of noise 
    contours = utils.reduce_contours(contours)
    print("Number of contours after reduction: ", len(contours))

    #draw contours on the image
    cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
    
    #save the images
    cv2.imwrite(f"pics-{piccount}.jpg", img)  
    cv2.imwrite(f"edges-{piccount}.jpg", edges)

    piccount = piccount + 1
    
    # replace the servos to a downward direction
    for i in range(servo1Straight, servo1Down-1, -1):
        car.servo.set_servo_pwm('1', i)
        time.sleep(0.1)

    print("Done taking pic ", piccount)
    

def test_stop_and_take_pic():
    car = Car()
    try:
        print("Press Ctrl+C to stop the program...")
        car.camera.start_stream()  # Start the camera
        
        # start with servos pointing down
        car.servo.set_servo_pwm('0', servo0Center)
        car.servo.set_servo_pwm('1', servo1Down)

        car.motor.set_motor_model(0,0,0,0)  # Stop the caro

        while True:
            #get_qr_code(car)
            take_pic(car)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nEnd of program")
        car.motor.set_motor_model(0,0,0,0)
        car.camera.stop_stream()
        car.camera.close()  # Close the camera

def test_cam_nav():
    """Test camera navigation."""
    car = Car()
    
    try:
        print("Press Ctrl+C to stop the program...")
        car.camera.start_stream()  # Start the camera
        speed = 1000
        left_speed = speed
        right_speed = speed - 100 # the car seems to favour turning left
        
        turn_factor = 50  # Adjust this factor to control the turning sensitivity
        
        # optimal servo placement to look at the floor
        servo0Center = 95
        servo1Down = 60
       
        while True:
            car.servo.set_servo_pwm('0', servo0Center)
            car.servo.set_servo_pwm('1', servo1Down)
            left_speed = speed
            right_speed = speed - 100

            # careful as this may take a long time
            angle = get_direction(car.camera)  # Get the direction from the camera

            # readjust to 90 by turning left or right

            if angle > 135 or angle < 45:
                print("Bad angle, this means a bug in get_direction, angle: ", angle)
            
            elif angle < 90:
                # Turn left
                print("Turning left with angle:", angle)
                delta = (90 - angle) * turn_factor
                left_speed -= delta

            elif angle > 90:
                # Turn right
                print("Turning right with angle:", angle)
                delta = (angle - 90) * turn_factor
                right_speed -= delta

            right_speed = int(right_speed)
            left_speed = int(left_speed)
            print("Setting left speed ",left_speed)
            print("Setting right speed", right_speed)

            # it's a four wheel drive, hence two left motors and two right motors
            car.motor.set_motor_model(left_speed, left_speed, right_speed, right_speed)
            #car.motor.set_motor_model(0,0,0,0)  # Stop the caro
            print("sleeping...")
            
            # if it keeps overcorrecting, maybe sleep less
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nEnd of program")
        car.motor.set_motor_model(0,0,0,0)
        car.camera.stop_stream()
        car.camera.close()  # Close the camera


if __name__ == '__main__':

    print('Program is starting ... ')  # Print a message indicating the start of the program
    test_cam_nav()  # Test camera navigation
    #test_get_qr_code()
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

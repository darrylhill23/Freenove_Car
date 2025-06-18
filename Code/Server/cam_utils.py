import cv2

import numpy as np
from typing import List
import utils2 as utils
import functools
import sys
import os


import time

NUM_PAGES = 4
NUM_QUESTIONS = 17


def find_contours(image: np.ndarray) -> List[np.ndarray]:
    """
    Find contours in the given image.

    Args:
        image (np.ndarray): The input image.

    Returns:
        List[np.ndarray]: A list of contours found in the image.
    """
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def draw_contours(image: np.ndarray, contours: List[np.ndarray]) -> np.ndarray:
    """
    Draw contours on the given image.

    Args:
        image (np.ndarray): The input image.
        contours (List[np.ndarray]): A list of contours to draw.

    Returns:
        np.ndarray: The image with drawn contours.
    """
    for contour in contours:
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 3)
    return image

def get_segments(countour):
    """
    Get segments from the contours.

    Args:
        countours (List[np.ndarray]): The contours to get segments from.

    Returns:
        List[np.ndarray]: A list of segments.
    """
    if len(countour) < 2:
        return []

    # Ensure the contour is a 2D array
    if countour.ndim == 1:
        countour = countour.reshape(-1, 1, 2)
    elif countour.ndim != 3:
        raise ValueError("Contour must be a 2D or 3D array.")
    if countour.shape[1] != 1 or countour.shape[2] != 2:
        raise ValueError("Contour must have shape (n, 1, 2) where n is the number of points.")

    segments = []
    for i in range(len(countour)):
        if countour[i].shape[0] != 1 or countour[i].shape[1] != 2:
            raise ValueError("Each contour point must have shape (1, 2).")
        segments.append([countour[i-1][0], countour[i][0]])
    return segments

def convert_angle(angle):
    """
    Take an angle in degrees and convert it to a value between 45 and 135 degrees.
    We want the angle from orthongal - so the difference between our angle and 0 or 90 or 180 or 270 degrees, whichever is closest.
    """
    if angle < 0:
        angle += 360
    angle = angle % 360  # Normalize angle to [0, 360)
    if angle >=45 and angle <= 135:
        return angle
    if angle > 135 and angle <= 225:
        return angle - 90
    if angle > 225 and angle <= 315:
        return angle - 180
    if angle > 315:
        return angle - 270
    return angle + 90  # This will convert angles < 45 to a value between 45 and 135 degrees
    


def get_angle_segment(p1, p2):
    """
    Calculate the angle between two points.

    Args:
        p1 (tuple): The first point (x1, y1).
        p2 (tuple): The second point (x2, y2).

    Returns:
        float: The angle in degrees.
    """
    if p1[0] == p2[0]:  # vertical line
        return 90.0
    elif p1[1] == p2[1]:  # horizontal line
        return 0.0

    # Calculate the angle in radians
    angle = np.arctan2(p2[1] - p1[1], p2[0] - p1[0])
    
    # Convert to degrees
    angle = np.degrees(angle)

    return angle

def get_length_segment(p1, p2):
    """
    Calculate the length of a segment between two points.

    Args:
        p1 (tuple): The first point (x1, y1).
        p2 (tuple): The second point (x2, y2).

    Returns:
        float: The length of the segment.
    """
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

def get_angle(countour):
    """
    Calculate the average angle of a contour, where each angle is weighted by the length of the segment.

    Args:
        countour (np.ndarray): The contour to calculate the angle for.

    Returns:
        float: The angle of the contour in degrees.
    """
    if len(countour) < 2:
        return 0.0

    # Ensure the contour is a 2D array
    if countour.ndim == 1:
        countour = countour.reshape(-1, 1, 2)
    elif countour.ndim != 3:
        raise ValueError("Contour must be a 2D or 3D array.")
    if countour.shape[1] != 1 or countour.shape[2] != 2:
        raise ValueError("Contour must have shape (n, 1, 2) where n is the number of points.")

    for i in range(len(countour)):
        if countour[i].shape[0] != 1 or countour[i].shape[1] != 2:
            raise ValueError("Each contour point must have shape (1, 2).")
        print(f"Contour point {i-1}: {countour[i-1][0]}")
        print(f"Contour point {i}: {countour[i][0]}")
        print(f"Angle: {get_angle_segment(countour[i-1][0], countour[i][0])}")
        print(f"Length: {get_length_segment(countour[i-1][0], countour[i][0])}")


        # p1 = countour[i-1][0]
        # p2 = countour[i][0]

    #return get_angle_segment(p1, p2)

def birdseye(img):
    pt1 = (120,0)
    pt2 = (400-pt1[0], pt1[1])
    pt3 = (400, 210)
    pt4 = (0, 210)
    points = [pt1, pt2, pt3, pt4]

    width, height = 400, 800
    pts_src = np.array(points, dtype="float32")

    
    pts_dst = np.array([
        [0, 0],              # top-left
        [width - 1, 0],      # top-right
        [width - 1, height - 1],  # bottom-right
        [0, height - 1]      # bottom-left
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(pts_src, pts_dst)
    warped = cv2.warpPerspective(img, M, (width, height))
    return warped

def warped_contours(contours):
    pt1 = (120,0)
    pt2 = (400-pt1[0], pt1[1])
    pt3 = (400, 210)
    pt4 = (0, 210)
    points = [pt1, pt2, pt3, pt4]

    width, height = 400, 800
    pts_src = np.array(points, dtype="float32")

    
    pts_dst = np.array([
        [0, 0],              # top-left
        [width - 1, 0],      # top-right
        [width - 1, height - 1],  # bottom-right
        [0, height - 1]      # bottom-left
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(pts_src, pts_dst)
    contours_float = [np.array(cnt, dtype=np.float32) for cnt in contours]

    # Apply perspective transform to each contour
    warped_contours = [cv2.perspectiveTransform(cnt, M) for cnt in contours_float]
    for i in range(len(warped_contours)):
        warped_contours[i] = np.round(warped_contours[i]).astype(int)
    #print("Warped contours: ", warped_contours)
    return warped_contours

def main():
    # Read the image
    
    # pages = convert_from_path('mc-sheets/mybuble.pdf')
    #pages = convert_from_path('mc-sheets/deferred-test.pdf')
    # pages = convert_from_path('mc-sheets/multiple.pdf')
    # pages = convert_from_path('mc-sheets/mc-sheet-scan.pdf')
    # # Convert the first page to an image
   
    # # Save the image
    # img.save('mc-sheet.png', 'PNG')read_bubbles.py
    # # # Read the image
    # # img = cv2.imread('mc-sheet.png')

    # start a timer
    start_time = time.time()

    filenames = ['i2', 'i3', 'i4', 'i5', 'i6']
    filetype = 'jpg'
    filetype = 'png'
    #filenames = ['o1', 'o2', 'o3', 'o4', 'o5']
    # filenames = ["image-1", "image-2", "image-3", "image-4", "image-5", "image-6"]
    #filenames = ["image"]

    for filename in filenames:
        #img = cv2.imread(f'output/{filename}_birdseye.{filetype}')
        img = cv2.imread(f'{filename}.{filetype}')
        if img is None:
            print(f"Error: Could not read image {filename}.{filetype}")
            exit(1)

        cv2.imshow("Original Image", img)
        cv2.waitKey(0)

        cv2.destroyAllWindows()

        img = utils.prep_image(img, 1, 1, trimFromTop = 0.3)

        # technically we don't need the warped image for processing, we can just use the warped contours.
        # but we can use it to visualize the contours
        warped = birdseye(img)
        cv2.imshow("Prepared Image", img)
        cv2.imshow("Birdeye Image", warped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # cv2.imwrite(f"output/{filename}_aprepared.jpg", img)


        # cv2.imshow("Prepared Image", img)
        # cv2.waitKey(0)
    
    

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


        # # Apply Gaussian blur
        # #blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        blurred = gray.copy()
        

        # # Apply Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        

        # # Dilate and erode the image
        dilated = cv2.dilate(edges, None, iterations=1)
        eroded = cv2.erode(dilated, None)
    
        # end_time = time.time()
        # print(f"Processing time: {end_time - start_time:.2f} seconds")

        # cv2.imwrite("gray.jpg", gray)   
        # cv2.imwrite("blurred.jpg", blurred)
        # cv2.imwrite(f"output/{filename}_edges.jpg", edges)
        # cv2.imwrite("dilated.jpg", dilated)
        # cv2.imwrite("eroded.jpg", eroded)

        # imageList = {"gray":gray, "blurred":blurred, "edges":edges, "dilated":dilated, "eroded":eroded}
        
        # for image in imageList:
        #     cv2.imshow(image, imageList[image])
        #     cv2.waitKey(0)
        # cv2.imshow("Image", dilated)
        # cv2.imshow("Edges", edges)
        # cv2.waitKey(0)
    

        # # Find contours
        bigCountours = find_contours(edges)

        print("Number of contours: ", len(bigCountours))


        # # Draw contours on the original image
        # # result_image = draw_contours(img.copy(), contours)
        
        result_image = warped.copy()
        # result_image2 = img.copy()

        contours = bigCountours
        
        contours = utils.reduce_contours(contours)
        print("Number of contours after reduction: ", len(contours))
        contours = warped_contours(contours)
        #print(f"\nSegments: \n{get_segments(contours)}")
        for contour in contours:
            
            cv2.drawContours(result_image, [contour], -1, (0, 255, 0), 3)
            #segment_points = get_segments(contour)
            #print(f"Contour segment points: \n{segment_points}")
            # for i in range(len(contour)):
            #     pt1 = tuple(contour[i][0])
            #     pt2 = tuple(contour[(i + 1) % len(contour)][0])  # wrap around to start if closed
            #     cv2.line(result_image, pt1, pt2, (0, 255, 0), 2)
            #     print(f"Contour point {i}: {pt1} to {pt2}")
            #     cv2.imshow('Contours', result_image)
            #     cv2.waitKey(0)
            # for i, segment in enumerate(segment_points):
            #     #cv2.drawContours(result_image, [[segment]], -1, (0, 255, 0), 3)
            #     cv2.line(result_image, segment[0], segment[1], (0, 255, 0), 2)
            #     angle = get_angle_segment(segment[0], segment[1])   
            #     angle = convert_angle(angle)

            #     length = get_length_segment(segment[0], segment[1])
            #     print(f"Segment {i}: Start: {segment[0]}, End: {segment[1]}, Angle: {angle:.2f} degrees, Length: {length:.2f} pixels")
            #     cv2.imshow('Contours', result_image)
            #     cv2.waitKey(0)
            

            print(f"Contour: \n{contour}")
            
            print("Angle: ")
            get_angle(contour)
            print("End countour")
            cv2.imshow('Contours', result_image)
            cv2.waitKey(0)

        cv2.destroyAllWindows()


        #cv2.imwrite(f"output/{filename}_contours.jpg", result_image)
        # # print("Image shape: ", result_image.shape)
        
        # # reduce the contours to minimum number of points   
        # bigCountours = utils.reduce_contours(bigCountours)
        # #sort in order of decreasing area
        # bigCountours = sorted(bigCountours, key=cv2.contourArea, reverse=True)

        # # we skip the first (student number) contour
        # # and take the next 9 contours

        # print("Number of contours: ", len(bigCountours))

        # bigCountours = bigCountours[1:10]

        # print("Number of contours: ", len(bigCountours))


        # rectangles = []

        # # let's see what order they are in
        # for contour in bigCountours:
        #     x, y, w, h = cv2.boundingRect(contour)
        #     print(f"Contour: {x}, {y}, {w}, {h}")
        #     rectangles.append((x, y, w, h))

        # print("Number of rectangles: ", len(rectangles))
        # #sort the rectangles
        # # rectangles = sorted(rectangles, key=functools.cmp_to_key(utils.compare_rectangles))

        # rectangles = rectSort.quickSort(rectangles)

        # # print("Sorted rectangles: ")

        # # for i in range(len(rectangles)):
        # #     print(f"Contour: {i}: {rectangles[i]}")

        
        # # # sort the contours based on their position using the compare_contours function
        # # # this currently does not work
        # # bigCountours = sorted(bigCountours, key=functools.cmp_to_key(utils.compare_contours))
        
        # # cv2.drawContours(result_image, bigCountours, -1, (0, 255, 0), 3)
        # # cv2.imshow('Contours', result_image)
        # # cv2.waitKey(0)

        # questions_processed = 0
        # answers = []
        # for (x, y, w, h) in rectangles:
        #     roi = img[y:y+h, x:x+w]
        #     # utils.markBlock(roi)
        #     answers.extend(utils.selectedLetters(roi))
        #     questions_processed = questions_processed + 5
        #     if questions_processed >= NUM_QUESTIONS:
        #         break

        # answers = answers[:NUM_QUESTIONS]

        # print("Answers", answers)

        # with open(f"submissions/{submission}/answers.txt", "w") as answerfile:
        #     for i, answer in enumerate(answers):
        #         answerfile.write(f"{i+1:<4} "+",".join(answer)+"\n")
                

        
        


if __name__ == "__main__":
    main()
# This code is a simple example of how to find and draw contours in an image using OpenCV.
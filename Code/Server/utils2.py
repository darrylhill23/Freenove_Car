import cv2

import numpy as np
from typing import List
from pdf2image import convert_from_path
import sys
PIXEL_THRESHOLD = 220
THRESHOLD = 1.4
MULT_SELECT_THRESHOLD = 1.4
SN_THRESHOLD = 1.6
# given a list of countours, reduce contours with more than 4 points to 4 points

def reduce_contours(contours: List[np.ndarray]) -> List[np.ndarray]:
    """
    Reduce contours with more than 4 points to 4 points.

    Args:
        contours (List[np.ndarray]): A list of contours.

    Returns:
        List[np.ndarray]: A list of reduced contours.
    """
    reduced_contours = []
    for contour in contours:
        if len(contour) > 4:
            # Reduce the contour to 4 points
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            reduced_contours.append(approx)
        else:
            reduced_contours.append(contour)
    return reduced_contours


# trim an image so that it is still centered, but the width is divisible by numCols, and the height is divisible by numRows

def prep_image(image: np.ndarray, numCols: int, numRows: int, trimFromTop: float = 0, trimFromBottom: float = 0, trimFromRight: float = 0, trimFromLeft: float = 0) -> np.ndarray:
    """
    Trim the image so that its width is divisible by numCols and its height is divisible by numRows.

    Args:
        image (np.ndarray): The input image.
        numCols (int): The desired column width.
        numRows (int): The desired row height.

    Returns:
        np.ndarray: The trimmed image.
    """
    # start by trimming the image from the top and bottom
    # trimFromTop is the fraction of the image to trim from the top
    # trimFromBottom is the fraction of the image to trim from the bottom
    # trimFromRight is the fraction of the image to trim from the right
    # trimFromLeft is the fraction of the image to trim from the left

    #convert each fraction to a number of pixels
    trimFromTop = int(trimFromTop * image.shape[0])
    trimFromBottom = int(trimFromBottom * image.shape[0])
    trimFromRight = int(trimFromRight * image.shape[1])
    trimFromLeft = int(trimFromLeft * image.shape[1])
    # trim the image
    if trimFromTop > 0:
        image = image[trimFromTop:]
    if trimFromBottom > 0:
        image = image[:-trimFromBottom]
    if trimFromRight > 0:
        image = image[:, :-trimFromRight]
    if trimFromLeft > 0:
        image = image[:, trimFromLeft:]
    

    # now trim the image so that its width is divisible by numCols and its height is divisible by numRows
    # get the width and height of the image

    height, width = image.shape[:2]
    new_width = width - (width % numCols)
    new_height = height - (height % numRows)
    x_offset = (width - new_width) // 2
    y_offset = (height - new_height) // 2
    trimmed_image = image[y_offset:y_offset + new_height, x_offset:x_offset + new_width]
    return trimmed_image


# compare two contours c1 and c2. c1 < c2 if the rightmost point of c1 is to the left of the leftmost point of c2
# or if the bottommost point of c1 is above the topmost point of c2
def compare_contours(c1: np.ndarray, c2: np.ndarray) -> bool:
    """
    Compare two contours to determine their relative positions.

    Args:
        c1 (np.ndarray): The first contour.
        c2 (np.ndarray): The second contour.

    Returns:
        bool: True if c1 is to the left of c2, False otherwise.
    """
    x1, y1, w1, h1 = cv2.boundingRect(c1)
    x2, y2, w2, h2 = cv2.boundingRect(c2)
    return (x1 + w1 < x2) or (y1 + h1 < y2) 


def processRowMultipleSelect(row, numCols):
    """
    This will likely be less reliable than single select,
    and it runs on the assumption that at least one letter is not selected.
    """
    letters = ['A','B','C','D','E']
    allPixels = [0,0,0,0,0]
    cols = np.hsplit(row, numCols)
    minPixels = 0
    
    # print("\n\nNew Row:")
    for j, col in enumerate(cols):
        # pixels = cv2.countNonZero(col)
        allPixels[j] = col.sum()

        if allPixels[j] < minPixels or minPixels == 0:
            minPixels = allPixels[j]
    
    answers = []
    for j, pixels in enumerate(allPixels):
        if (pixels > MULT_SELECT_THRESHOLD * minPixels):
            answers.append(letters[j])
    if len(answers) == 0:
        return ["None"]
    else:
        return answers

def processRow(row, numCols):
    letters = ['A','B','C','D','E']
    cols = np.hsplit(row, numCols)
    # for now just find the one with the most pixels
    maxPixels = 0
    secondMaxPixels = 0
    minPixels = 0
    currentLetter = 'A'
    print("\n\nNew Row:")
    for j, col in enumerate(cols):
        # pixels = cv2.countNonZero(col)
        pixels = col.sum()
        print("Pixels ",pixels)
        print("Sum    ",col.sum())
        # cv2.imshow("col", col)
        # cv2.waitKey(0)
        if pixels > maxPixels:
            secondMaxPixels = maxPixels
            maxPixels = pixels
            currentLetter = letters[j]
        if pixels < minPixels or minPixels == 0:
            minPixels = pixels
    print("MinPixels: ", minPixels)
    print("MaxPixels: ", maxPixels)
    if (maxPixels > THRESHOLD * secondMaxPixels):
        return [currentLetter]
    else:
        return ["None"]
        

# return a list of (5 or fewer) selected letters
def selectedLetters(roi):
    # cv2.imshow('ROI', roi)
    # cv2.waitKey(0)
    # print("In selected letters")
    numRows = 5
    numCols = 5
    roi = prep_image(roi, numCols, numRows, trimFromTop=0.06, trimFromBottom=0.06, trimFromRight=0.04, trimFromLeft=0.18)
    # cv2.imshow('ROI', roi)
    # cv2.waitKey(0)
    
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    wut = cv2.threshold(roi, PIXEL_THRESHOLD, 255, cv2.THRESH_BINARY_INV)
    roi = wut[1]

    rows = np.vsplit(roi, numRows)

    answers = []
    letters = ['A','B','C','D','E']
    for i, row in enumerate(rows):
        # print("Row Shape: ",row.shape)
        # cv2.imshow("row", row)
        # cv2.waitKey(0)
        
        # answers.append(processRow(row, numCols))
        answers.append(processRowMultipleSelect(row, numCols))
        

    # for i, row in enumerate(rows):
    #     print(f"row {i} shape: {row.shape}")

        

    # print(answers)
    # cv2.imshow('ROI', roi)
    # cv2.waitKey(0)
    # print("Exiting selectedLetters")
    return answers
            # pass
    #draw a horizontal line in the middle of the image
    # cv2.line(roi, (0, roi.shape[0] // 4), (roi.shape[1], roi.shape[0] // 4), (255, 0, 0), 2)

    # turn this image into an array of images with 9 columns and 10 rows

# return a list of (5 or fewer) selected letters
def extractStudentNumber(roi):
    
    # cv2.imshow('ROI', roi)
    # cv2.waitKey(0)
    print("In extract student numbers")
    numRows = 10
    numCols = 9

    roi = prep_image(roi, numCols, numRows, trimFromTop=0.24, trimFromRight=0.05, trimFromLeft=0.06, trimFromBottom=0.018)
    # cv2.imshow('ROI', roi)
    # cv2.waitKey(0)
    print("Shape: ",roi.shape)
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    wut = cv2.threshold(roi, PIXEL_THRESHOLD, 255, cv2.THRESH_BINARY_INV)
    roi = wut[1]

    cols = np.hsplit(roi, numCols)

    answers = []
    letters = ['0','1','2','3','4','5','6','7','8','9']
    for i, col in enumerate(cols):
        print("Column Shape: ",col.shape)
        # cv2.imshow("col", col)
        # cv2.waitKey(0)
        
        
        # rows = prep_image(col, 1, numRows)
        rows = np.vsplit(col, numRows)
        # for now just find the one with the most pixels
        maxPixels = 0
        secondMaxPixels = 0

        minPixels = 0
        currentLetter = '0'
        print("\n\nNew Row:")
        for j, row in enumerate(rows):
            # cv2.imshow("row", row)
            # cv2.waitKey(0)
            
            ''' So 9 has a row of pixels at the bottom that is fucking things up. Have
                trim it a little better
            '''
            # pixels = cv2.countNonZero(col)
            pixels = row.sum()
            print("Pixels ",pixels)
            # print("Sum    ",col.sum())
            if pixels >= maxPixels:
                secondMaxPixels = maxPixels
                maxPixels = pixels
                currentLetter = letters[j]
            if pixels < minPixels or minPixels == 0:
                minPixels = pixels
        print("MinPixels: ", minPixels)
        print("SecondMaxPixels: ", secondMaxPixels)
        print("MaxPixels: ", maxPixels)
        if (maxPixels > SN_THRESHOLD * secondMaxPixels):
            answers.append(currentLetter)
        else:
            answers.append("None")
        print("Answer: ", answers[-1])
        

    # for i, row in enumerate(rows):
    #     print(f"row {i} shape: {row.shape}")

    #     cv2.imshow(f'row {i}', row)
    #     cv2.waitKey(0)

    print(answers)
    
    print("Exiting extractStudentNumbers")
    # cv2.imshow('ROI', roi)
    # cv2.waitKey(0)

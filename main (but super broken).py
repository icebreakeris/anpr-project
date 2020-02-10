#pylint: disable=no-member

import sys
import numpy as np
import cv2
import imutils
import pytesseract
from pytesseract import Output
import os
import time
from matplotlib import pyplot as plt

"""
TODO: 
    Code needs cleaning up
    Add more file validation
    Implement ROI 
    Implement additional contour validation to reduce number of false positives
    Implement recognized plate saving
        save to memory? 
        save to file? 
        
    Implement plate image preprocessing 
    Implement ocr to string 

"""


class PlateScanner:
    def __init__(self, img_url, tesseract_url, show_steps = False): 
        self.image = None
        self.url = img_url
        
        #self.width = width
        #self.height = height
        self.show_steps = show_steps
        self.morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(20,4))
        self.plate_kernel = np.ones((5,), np.uint8)
        self.contrast_kernel = np.array([[-1,0,1],[-2,0,2],[1,0,1]])
        self.plate_candidates = []

        self.ocr_config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6'
        pytesseract.pytesseract.tesseract_cmd = tesseract_url        
        
    def scan_plate(self): 
        #add more file validation
        #zzz...

        if not os.path.isfile(self.url): 
            print("[-] File not found. Enter the correct url and try again.") 
            return

        self.image = cv2.imread(self.url) 
        self.image = imutils.resize(self.image, width=600)

        self.preprocess_image()
        #self.find_roi()

    def set_roi(self):
        (y, x) = self.image.shape[:2]

        p1 = (int(x/4), int(2*y/4))
        p2 = (int(x*4/5), int(2*y))

        #cv2.rectangle(self.image, p1, p2, (255, 0, 0), 2)
        roi = self.image[p1[1]:p2[1], p1[0]:p2[0], :]
        return roi

    def enhance(self, image):
        return cv2.filter2D(image, -1, self.contrast_kernel)

    def preprocess_image(self):
        start = time.time()
        
        if self.show_steps: cv2.imshow("Original image", self.image)

        self.image = self.set_roi()
        #self.image = imutils.resize(self.image, width=600)
        #r = cv2.selectROI(self.image) #for testing purposes (testing successful 20/23 plates found using roi)
        
        #self.image = self.image[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        #gray = self.enhance(gray) #increase contrast of image for better results? 

        if self.show_steps: cv2.imshow("Grayscale conversion", gray)
        
        blurred = cv2.bilateralFilter(gray, 11, 50, 50)
        #blurred = cv2.GaussianBlur(gray, (5,5), 0)

        if self.show_steps: cv2.imshow("Blurred image", blurred)

        sobel_x = cv2.Sobel(blurred, cv2.CV_8U, 1, 0, ksize=3, borderType=cv2.BORDER_DEFAULT) 
        

        #sobel_x = cv2.Canny(blurred, 50, 270, apertureSize=3, L2gradient=True)
        
        #sobel_y = cv2.Sobel(blurred, cv2.CV_8U, 0, 1, ksize=3, borderType=cv2.BORDER_DEFAULT) 
        #abs_sobel_x = cv2.convertScaleAbs(sobel_x)
        #abs_sobel_y = cv2.convertScaleAbs(sobel_y) 
        #sobel = cv2.addWeighted(abs_sobel_x, 0.5, abs_sobel_y, 0.5, 0)
   
        if self.show_steps: cv2.imshow("Sobel image", sobel_x)

        _, threshold = cv2.threshold(sobel_x, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
     
        if self.show_steps: cv2.imshow("threshold image", threshold)

        morph = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, self.morph_kernel)

        if self.show_steps: cv2.imshow("morph image", morph)
        
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        candidate_num = 0 #debug
        for a in contours: 

            #shows all potential candidates
            #implement additional contour validation to reduce false positives

            candidate_num = candidate_num + 1 #debug
            candidate = cv2.minAreaRect(a)

            #box = cv2.boxPoints(candidate)
            #points = np.int0(box)
            #cv2.drawContours(self.image, [points], 0, (255, 2, 10), 2)

            #(x,y), (width, height), angle = candidate

            #check whether the found rectangle meets the size requirements of a plate
            if self.check_size(candidate, candidate_num):
                box = cv2.boxPoints(candidate)
                points = np.int0(box)

                x,y,w,h = cv2.boundingRect(points)
    
                if (x > 0 and y > 0 and w > h): #possibly put w > h into check_size()?
                    new_img = self.image[y:y + h, x:x + w]
                    if self.check_edge_density(new_img) > 0.475:
                        cv2.imshow(f"cropped_plate{candidate_num}.png", new_img)

                        processed_plate = self.preprocess_plate(new_img)

                        predicted_plate = self.get_plate_string(processed_plate)

                        #print("Predicted plates: ")
                        #for a in predicted_plate:
                            #print(a)

                        cv2.drawContours(self.image, [points], 0, (255, 2, 10), 2)
                        cv2.putText(self.image, predicted_plate, (int(box[0][0]), int(box[0][1]) + 20), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 2)
                    
        if self.show_steps: cv2.imshow("last image", self.image)

        end = time.time()
        print(f"Time elapsed: {int((end-start)*1000)}ms")
        cv2.waitKey(0)
 
    #takes cut out plate img 
    def check_edge_density(self, plate_img):
        #refactor

        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        _, plate_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        cv2.imshow("edge_den", plate_thresh)

        white_count = 0
        for x in range(plate_thresh.shape[0]):
            for y in range(plate_thresh.shape[1]):
                if plate_thresh[x][y] == 255:
                    white_count += 1

        edge_density = float(white_count)/(plate_thresh.shape[0]*plate_thresh.shape[1])
        print(f"edge_density of candidate: {edge_density}")

        return edge_density

    def preprocess_plate(self, plate_img): 
        plate_img = cv2.resize(plate_img, (500, 125))
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        ret, threshold = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY_INV)
        threshold = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 75, 10)
        threshold = cv2.bitwise_not(threshold)

        cv2.imshow("platethresh", threshold)

        ctrs, hier = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(plate_img, ctrs, -1, (0,255,0), 3)
        
        sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

        for i, ctr in enumerate(sorted_ctrs):
            x,y,w,h = cv2.boundingRect(ctr)

            roi = plate_img[y:y+h, x:x+w]

            cv2.imshow(f"character{i}", roi)
        
        cv2.imshow("contours", plate_img)
        cv2.waitKey(0)
        
        """


        
        #preprocess plate image and get ready for ocr 
        plate_img = cv2.resize(plate_img, (500, 125))
        #mask = np.zeros(plate_img.shape, dtype=np.uint8)
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        
        #gray = cv2.bitwise_not(gray)


        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        plate_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1] 
        
        opening = cv2.morphologyEx(plate_thresh, cv2.MORPH_CLOSE, self.plate_kernel)
        erosion = cv2.erode(opening, self.plate_kernel, iterations=1)
        dilated = cv2.dilate(erosion, self.plate_kernel, iterations=1)
        cv2.imshow("preprocessed_plate2", dilated)

        self.segment_plate(dilated)
        return dilated

        """

    def segment_plate(self, plate_img):
        img = plate_img
        

        
        """img = plate_img
        threshold = cv2.bitwise_nt
        ctrs, hier = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
        cv2.drawContours(plate_img, ctrs, -1, (0,255,0), 3)
        print(contours)
        cv2.imshow("contours", plate_img)

        

        d = 0
        for ctr in contours:
            x, y, w, h = cv2.boundingRect(ctr)

            roi = plate_img[y:y+h, x:x+w]
            cv2.imshow(f"character{d}", roi)

            d += 1

        cv2.waitKey(0)"""

        
    def get_key_by_value(self, dictionary, value): 
        for a in dictionary.items(): 
            if a[1] == value:
                return a[0]

    def string_has_numbers(self, string): 
        return any(i.isdigit() for i in string)

    def get_plate_string(self, img): 
        """
        confusing_chars = {'B' : '8', 'D': '0', 'E': '3', 'G' :'6', 'I' : '1', 'S' : '5', 'T' : '7'}
        
        candidate_plates = []
        #use ocr to get the string 
        #use uk plate rules to determine whether the plate is correct

        #next two characters can only be numbers

        plate_data = list(pytesseract.image_to_string(img, lang="eng", config=self.ocr_config))
        original_plate = "".join(plate_data)

        if self.string_has_numbers("".join(plate_data[:2])):
            for i in plate_data[:2]:
                if i in confusing_chars.keys() or i in confusing_chars.values():
                    plate_data[plate_data.index(i)] = self.get_key_by_value(confusing_chars, i)
            candidate_plates.append("".join(plate_data))


        for i in plate_data[2:4:]:
            if i in confusing_chars.keys(): 
                plate_data[plate_data.index(i)] = confusing_chars.get(i)
        candidate_plates.append("".join(plate_data))

        candidate_plates.append(original_plate)
        """

        return pytesseract.image_to_string(img, config=self.ocr_config)

    def check_size(self, candidate, candidate_num):
        control_aspect = 4.68 # 520mm / 111mm (standard uk number plate size)

        (x,y), (width, height), angle = candidate #gets candidate rectangle parameters
        
        angle = (angle + 180) if width < height else (angle + 90) 

        if width <= 0 or height <= 0:
            return False 

        area = float(width * height)

        if width > height:
            aspect_ratio = float(width) / height 
        else:
            #in case if the program gives rotated rectangle and width and height are mixed up
            aspect_ratio = float(height) / width 

        #print(f"[{candidate_num}], x: {x}, y: {y}, width: {width}, height: {height}, a_r: {aspect_ratio}")

        error_margin = 0.4

        min_aspect_ratio = control_aspect - control_aspect * error_margin
        max_apsect_ratio = control_aspect + control_aspect * error_margin

        print(f"[{candidate_num}]\tw: {width}\th: {height}\ta_r: {aspect_ratio}\tarea: {area}\tangle: {angle}\tmax_aspect: {max_apsect_ratio}\tmin_aspect: {min_aspect_ratio}")
        
        if (aspect_ratio > min_aspect_ratio and aspect_ratio <= max_apsect_ratio) and (area > 500 and area <= 15000) and angle >= 20: 
            return True
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PlateScanner(sys.argv[1], r"C:\Users\minda\AppData\Local\Tesseract-OCR\tesseract.exe", True).scan_plate()


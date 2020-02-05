#pylint: disable=no-member

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
        self.morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(17,4))
        self.plate_kernel = np.ones((5,5), np.uint8)
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

        self.preprocess_image()
        

    def find_roi(self):

        pass
    def enhance(self, image):
        return cv2.filter2D(image, -1, self.contrast_kernel)

    def preprocess_image(self):
        self.image = cv2.imread(self.url)

        self.image = imutils.resize(self.image, width = 600)
        
        #r = cv2.selectROI(self.image) #for testing purposes (testing successful 20/23 plates found using roi)
        
        #img_crop = self.image[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

        if self.show_steps: cv2.imshow("Original image", self.image)

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

            #(x,y), (width, height), angle = candidate

            #check whether the found rectangle meets the size requirements of a plate
            if self.check_size(candidate, candidate_num):
                
                box = cv2.boxPoints(candidate)
                points = np.int0(box)

                x,y,w,h = cv2.boundingRect(points)
    
                if (x > 0 and y > 0 and w > h): #possibly put w > h into check_size()?
                    new_img = self.image[y:y + h, x:x + w]
                    if self.check_edge_density(new_img) > 0.5:
                        cv2.imshow(f"cropped_plate{candidate_num}.png", new_img)
                        processed_plate = self.preprocess_plate(new_img)
                        #d = pytesseract.image_to_data(processed_plate, output_type=Output.DICT)

                        cv2.drawContours(self.image, [points], 0, (255, 2, 10), 2)
                        test = pytesseract.image_to_string(processed_plate, lang="eng", config=self.ocr_config)
                        print(test)
                        cv2.putText(self.image, f"{test}", (int(box[0][0]), int(box[0][1]) + 20), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 2)
                    #self.plate_candidates.append(candidate)

        if self.show_steps: cv2.imshow("last image", self.image)

        cv2.waitKey(0)
 
    #takes cut out plate img 
    def check_edge_density(self, plate_img):
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        _, plate_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        white_pixels = 0

        for x in range(plate_thresh.shape[0]):
            for y in range(plate_thresh.shape[1]):
                if plate_thresh[x][y] == 255:
                    white_pixels += 1

        edge_density = float(white_pixels)/(plate_thresh.shape[0]*plate_thresh.shape[1])
        print(f"edge_density of candidate: {edge_density}")
        return edge_density

    def preprocess_plate(self, plate_img): 
        #preprocess plate image and get ready for ocr 
        plate_img = cv2.resize(plate_img, (500, 125))
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        
        #gray = cv2.bitwise_not(gray)


        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        plate_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1] 
        
        opening = cv2.morphologyEx(plate_thresh, cv2.MORPH_CLOSE, self.plate_kernel)
        erosion = cv2.erode(opening, self.plate_kernel, iterations=1)
        dilated = cv2.dilate(erosion, self.plate_kernel, iterations=1)

        
        
        #plate_thresh = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

        """
        coords = np.column_stack(np.where(plate_thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        (h, w) = plate_thresh.shape[:2]
        center = (w // 2, h//2)
        m = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(plate_thresh, m, (w,h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        """

        cv2.imshow("preprocessed_plate", dilated)
        
        cv2.waitKey(0)

        return dilated

    def get_plate_string(self, img): 
        #use ocr to get the string 
        pass

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
    PlateScanner("plates/17.jpg", r"C:\Users\minda\AppData\Local\Tesseract-OCR\tesseract.exe", True).scan_plate()


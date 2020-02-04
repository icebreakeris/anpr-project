#pylint: disable=no-member

import numpy as np
import cv2
import imutils
import pytesseract
import os

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
        self.contrast_kernel = np.array([[-1,0,1],[-2,0,2],[1,0,1]])
        self.plate_candidates = []

        pytesseract.pytesseract.tesseract_cmd = tesseract_url        
        
    def scan_plate(self): 
        #add more file validation
        #zzz...

        if not os.path.isfile(self.url): 
            print("[-] File not found. Enter the correct url and try again.") 
            return

        self.preprocess_image()

    def find_roi(self):
        #find region of interest
        
        pass
        
    def enhance(self, image):
        return cv2.filter2D(image, -1, self.contrast_kernel)

    def preprocess_image(self):
        self.image = cv2.imread(self.url)

        self.image = imutils.resize(self.image, width = 600)

        if self.show_steps: cv2.imshow("Original image", self.image)

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        #gray = self.enhance(gray) #increase contrast of image for better results? 

        if self.show_steps: cv2.imshow("Grayscale conversion", gray)
        
        blurred = cv2.bilateralFilter(gray, 11, 50, 50)
        #blurred = cv2.GaussianBlur(gray, (5,5), 0)

        if self.show_steps: cv2.imshow("Blurred image", blurred)

        sobel_x = cv2.Sobel(blurred, cv2.CV_8U, 1, 0, ksize=3, borderType=cv2.BORDER_DEFAULT) 
        
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

        candidate_num = 0
        for a in contours: 
            #shows all potential candidates
            #implement additional contour validation to reduce false positives
            candidate_num = candidate_num + 1

            candidate = cv2.minAreaRect(a)
            (x,y), (width, height), angle = candidate

            box = cv2.boxPoints(candidate)
  
            points = np.int0(box)

            cv2.drawContours(self.image, [points], 0, (0, 255, 0), 2)
            cv2.putText(self.image, f"{candidate_num}", (int(box[0][0]), int(box[0][1]) + 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1)
            #check whether the found rectangle meets the size requirements of a plate
            if self.check_size(candidate, candidate_num):
                self.plate_candidates.append(candidate)

        i = 1
        for b in self.plate_candidates:
            print(f"[?] Candidate {candidate_num}: ", b)
            box = cv2.boxPoints(b)
            points = np.int0(box)

            #outputs potential candidate cut outs
            x,y,w,h = cv2.boundingRect(points)

            cv2.putText(self.image, f"{i}", (x,y + 20), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 2)
            #cv2.drawContours(self.image, [points], 0, (0, 255, 0), 2)

            #todo: if edge density true (higher than threshold) then it must be plate
            if x > 0 and y > 0:
                new_img = self.image[y:y + h, x:x + w]
                cv2.imshow(f"cropped_plate{i}.png", new_img)
                #new = PlateScanner(f"cropped_plate{i}.png", "", True).scan_plate()
            i = i + 1
            
        if self.show_steps: cv2.imshow("last image", self.image)

        cv2.waitKey(0)

    def check_edge_density(self, candidate, morphed_image):
        #check whether the edge density in the given plate is higher than others
        pass

    def preprocess_plate(self, plate_img): 
        #preprocess plate image and get ready for ocr 
        pass 

    def get_plate_string(self, img): 
        #use ocr to get the string 
        pass

    def check_size(self, candidate, candidate_num):
        aspect = 4.68 # 520mm / 111mm (standard uk number plate size)

        (x,y), (width, height), angle = candidate #gets candidate rectangle parameters
        
        area = float(width * height)

        if width <= 0 or height <= 0:
            return False 

        if width > height:               

            aspect_ratio = float(width) / height 

        else:

            aspect_ratio = float(height) / width 
        #print(f"[{candidate_num}], x: {x}, y: {y}, width: {width}, height: {height}, a_r: {aspect_ratio}")

        error_margin = 0.4
        min_aspect_ratio = aspect - aspect * error_margin
        max_apsect_ratio = aspect + aspect * error_margin

        print(f"[{candidate_num}]\tw: {width}\th: {height}\ta_r: {aspect_ratio}\tarea: {area}\tangle: {angle}\tmax_aspect: {max_apsect_ratio}\tmin_aspect: {min_aspect_ratio}")
        
        if (aspect_ratio > min_aspect_ratio and aspect_ratio <= max_apsect_ratio) and (area > 500 and area <= 15000) and angle >= -20:
            return True
        
        return False


if __name__ == "__main__":
    
    PlateScanner("plates/10.jpg", r"C:\Users\minda\AppData\Local\Tesseract-OCR\tesseract.exe", True).scan_plate()


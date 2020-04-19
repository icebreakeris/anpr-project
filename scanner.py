#pylint: disable=no-member

import sys
import numpy as np
import cv2
import imutils
import pytesseract
import pathlib

import os
import time
import config


class PlateScanner():
    def __init__(self, img_url, cfg):
        self.cfg = cfg
        self.step_images = []
        
        self.show_steps = self.cfg["show_steps"]
        self.save_images = self.cfg["save_images"]
        pytesseract.pytesseract.tesseract_cmd = self.cfg["tesseract_url"] 

        self.image = None
        self.plate_img = None
        self.url = img_url

        self.plate_text = ""
        self.morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize=(20,4))
        self.plate_kernel = np.ones((5,2), np.uint8)

        #editing the tesseract character whitelist ensures that characters such as #./!":@% etc. are not processed.
        #Letter Q has been removed from the whitelist as it is not used on UK number plates and confuses tesseract 
        self.ocr_config = r'-c tessedit_char_whitelist=ABCDEFGHJKILMNOPRSTUVWXYZ23456789 --psm 7' #7
        
    def scan_plate(self): 
        if not os.path.isfile(self.url): 
            print("[-] File not found. Enter the correct url and try again.") 
            return

        self.image = cv2.imread(self.url)

        #scales the images to width 600
        #it is more difficult and a lot slower to process high resolution images 
        self.image = imutils.resize(self.image, width=600)

        #starts the preprocessing
        return self.preprocess_image()


    def set_roi(self, image):
        #sets the main region of interest in the image to reduce the amount of false positives
        (y, x) = image.shape[:2]

        p1 = (int(x/4), int(2*y/4)) 
        p2 = (int(x*4/5), int(2*y))

        #slices the current saved image using the points calculated above
        roi = image[p1[1]:p2[1], p1[0]:p2[0], :]
        return roi

    def preprocess_image(self):
        start = time.time()
        
        #cv2.imshow("Original image", self.image)

        self.roi = self.set_roi(self.image)
        #turns image to grayscale
        gray = cv2.cvtColor(self.roi, cv2.COLOR_BGR2GRAY)

        if self.show_steps: self.step_images.append(gray)
    
        #blurs image using bilateral filter to reduce noise
        blurred = cv2.bilateralFilter(gray, 11, 50, 50)
        #blurred = cv2.GaussianBlur(gray, (5,5), 0)
        if self.show_steps: self.step_images.append(blurred)
        
        #sobel edge detection
        sobel_x = cv2.Sobel(blurred, cv2.CV_8U, 1,0, ksize=3, borderType=cv2.BORDER_DEFAULT) 
        if self.show_steps: self.step_images.append(sobel_x)
    
        #gets threshold of sobel image using otsu algorithm
        _, threshold = cv2.threshold(sobel_x, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
     
        if self.show_steps: self.step_images.append(threshold)
        
        #performs closing operation on thresholded image
        morph = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, self.morph_kernel)

        if self.show_steps: self.step_images.append(morph)
            
        #finds all external contours while ignoring child contours
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        for a in (contours): 
            #shows all potential candidates
            #implement additional contour validation to reduce false positives
            candidate = cv2.minAreaRect(a)

            #check whether the found rectangle meets the size requirements of a plate
            if self.check_plate_size(candidate):
                box = cv2.boxPoints(candidate)
                points = np.int0(box)
                
                #create plate candidate
                x,y,w,h = cv2.boundingRect(points)
    
                #check if candidate is not just a line
                if (x > 0 and y > 0 and w > h):
                    new_img = self.roi[y:y + h, x:x + w]
                    if self.check_edge_density(new_img) > 0.475:
                        if self.show_steps: self.step_images.append(new_img)
                        #preprocess plate
                        processed_plate = self.preprocess_plate(new_img)
                        #scan plate
                        self.plate_text = pytesseract.image_to_string(processed_plate, config=self.ocr_config)

                        cv2.drawContours(self.roi, [points], 0, (255, 2, 10), 2)
                        #create bordered text
                        cv2.putText(self.roi, self.plate_text, (30, 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 5)
                        cv2.putText(self.roi, self.plate_text, (30, 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255,255, 255), 2)
            
        #cv2.imshow("last image", self.image)
        #calculates processing time
        end = time.time()
        end_time = int((end - start) * 1000)
        #print(f"Time elapsed: {int((end-start)*1000)}ms")

        #save_images variable in config.json
        if self.save_images:
            if self.roi is not None and self.plate_img is not None:

                pathlib.Path("final_images/").mkdir(parents=True, exist_ok=True)
                
                cv2.imwrite("final_images/Final Image.png", self.roi)
                cv2.imwrite("final_images/Final Plate.png", self.plate_img)

        return end_time, self.plate_text, self.roi, self.plate_img, self.step_images
        #cv2.waitKey(0)
 
    #takes morphed image
    def check_edge_density(self, morphed_img):

        gray = cv2.cvtColor(morphed_img, cv2.COLOR_BGR2GRAY)
        _, plate_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        #calculates how many white pixels there are in the threshold image
        white_count = 0
        for x in range(plate_thresh.shape[0]):
            for y in range(plate_thresh.shape[1]):
                if plate_thresh[x][y] == 255:
                    white_count += 1

        #calculates the density of white pixels
        edge_density = float(white_count)/(plate_thresh.shape[0]*plate_thresh.shape[1])
        #print(f"edge_density of candidate: {edge_density}")

        return edge_density

    def preprocess_plate(self, plate_img):
        plate_img = cv2.resize(plate_img, (500, 125))
        plate_img_copy = plate_img.copy()

        #creates a blank mask that will be used to mask out plate characters
        mask = np.zeros(plate_img.shape, dtype="uint8")
        mask.fill(255)

        #plate preprocessing
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        
        _, threshold = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        eroded = cv2.erode(threshold, self.plate_kernel, iterations=1)
        #invert threshold
        threshold_inv = cv2.bitwise_not(eroded)

        if self.show_steps: self.step_images.append(eroded)

        ctrs, _ = cv2.findContours(threshold_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        cv2.drawContours(plate_img_copy, ctrs, -1, (0,255,0), 2)

        sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
        #look through all contours
        for ctr in sorted_ctrs:
            #create character candidate
            x,y,w,h = cv2.boundingRect(ctr)
            
            #cut character out
            roi = plate_img[y:y+h, x:x+w]
            
            #validate candidate
            if self.check_character_size(roi):
                #if valid, put candidate on white mask
                mask[y:y+h, x:x+w] = plate_img[y:y+h, x:x+w]
                cv2.rectangle(plate_img_copy, (x,y), (x+w, y+h), 255, 2)

        if self.show_steps: self.step_images.append(mask)

        gray_mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        _, mask_thresh = cv2.threshold(gray_mask, 110, 255, cv2.THRESH_BINARY)
        mask_eroded = cv2.erode(mask_thresh, self.plate_kernel, iterations=1)


        if self.show_steps: self.step_images.append(mask_thresh)

        if self.show_steps: self.step_images.append(plate_img_copy)
        
        self.plate_img = mask_eroded
        return mask_eroded

    def check_character_size(self, character):
        control_aspect = 50.0 / 79.0 #theoretical character dimensions
        control_aspect1 = 14.0 / 79.0 #theoretical character "1" dimensions

        (height, width, _) = character.shape

        if height <= 0 or width <= 0: 
            return False

        char_aspect = float(width) / float(height)

        min_height, min_width = 65, 10
        max_height, max_width = 120, 100

        min_aspect = control_aspect1 - control_aspect1 * 0.3
        max_aspect = control_aspect + control_aspect * 0.3

        if char_aspect > min_aspect and char_aspect < max_aspect and height > min_height and height < max_height and width > min_width and width < max_width:
            #print(height, width, char_aspect, min_aspect, max_aspect)
            return True 
        else:
            return False

    def check_plate_size(self, candidate):
        control_aspect = 4.68 # 520mm / 111mm (standard uk number plate size)

        (_,_), (width, height), angle = candidate #gets candidate rectangle parameters
        
        #ensures that the angle of the candidate plate is not upside down
        #as this could affect the end results

        if width < height: 
            angle = angle + 180
        else: 
            angle = angle + 90

        if width <= 0 or height <= 0:
            return False 

        area = float(width * height)

        if width > height:
            aspect_ratio = float(width) / height 
        else:
            #in case if the program gives rotated rectangle and width and height are mixed up
            aspect_ratio = float(height) / width 

        #gets the minimum and maximum aspect ratio with the allowed error ratio of 0.4
        min_aspect_ratio = control_aspect - control_aspect * 0.4
        max_apsect_ratio = control_aspect + control_aspect * 0.4

        #print(f"[]\tw: {width}\th: {height}\ta_r: {aspect_ratio}\tarea: {area}\tangle: {angle}\tmax_aspect: {max_apsect_ratio}\tmin_aspect: {min_aspect_ratio}")
        
        #checks if the aspect ratio is within the guidelines
        if (aspect_ratio > min_aspect_ratio and aspect_ratio <= max_apsect_ratio) and (area > 500 and area <= 15000) and angle >= 20: 
            return True
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cfg = config.check_config()
        if not cfg:
            exit()
        

        time, plate, image, plate_image, step_images = PlateScanner(sys.argv[1], cfg).scan_plate()
        if cfg["show_steps"]:
            if len(step_images) > 0:    
                for i, image in enumerate(step_images):
                    cv2.imshow(f"{i}", image)

        print(f"Process time: {time}ms\nRecognised plate: {plate}")
        cv2.imshow("Vehicle", image)
        cv2.imshow("Plate Image", plate_image)

        cv2.waitKey(0)




#pylint: disable=no-member

import unittest
import hashlib
from scanner import PlateScanner
import config
import cv2
import imutils




class ANPRTests(unittest.TestCase):
    def setUp(self):
        
        self.url = "pdataset/1.jpg"
        
        self.hashes = {"78ff6f1bf2c7abb16f54a3b0987f54ce",
        "96010754c19663913cd22207fead7832"}
        self.roi_values = {"p1": (150, 216), "p2": (480, 866) }

        self.control_plate = "SP56AOS"
        
        self.scanner = PlateScanner(self.url, config.check_config())
        
        
    def test_image_reading(self):
        _, _, _, _, _ = self.scanner.scan_plate()
        self.assertIsNotNone(self.scanner.image)

    def test_image_size(self):
        _, _, _, _, _ = self.scanner.scan_plate()
        (_, width) = self.scanner.image.shape[:2]
        self.assertEqual(width, 600)


    def hash_image(self, image):
        return hashlib.md5(image.tostring()).hexdigest()

    def test_image_hashes(self):
        _, _, plate_img, img, _ = self.scanner.scan_plate()
        self.assertEqual(self.hashes.__contains__(self.hash_image(plate_img)), True)
        self.assertEqual(self.hashes.__contains__(self.hash_image(img)), True)

    def test_roi(self):
        _, _, _, _, _ = self.scanner.scan_plate()
        (y, x) = self.scanner.image.shape[:2]

        p1 = (int(x/4), int(2*y/4)) 
        p2 = (int(x*4/5), int(2*y))

        self.assertEqual(p1, self.roi_values["p1"])
        self.assertEqual(p2, self.roi_values["p2"])

    #checks if the system processes image
    def test_image_processing(self):
        _, _, plate_img, img, _ = self.scanner.scan_plate()
        self.assertIsNotNone(plate_img)
        self.assertIsNotNone(img)

    #checks if the resultant end text is equal to the contorl plate 
    def test_image_plate(self):
        _, end_text, _, _, _ = self.scanner.scan_plate()
        self.assertEqual(end_text, self.control_plate)
    
    #check if processing time is less than 500
    def test_process_time(self): 
        end_time, _, _, _, _ = self.scanner.scan_plate()
        self.assertLess(end_time, 500)

   


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ANPRTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

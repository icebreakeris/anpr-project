#pylint: disable=no-member

import unittest
import hashlib
from scanner import PlateScanner
import config
import cv2



class ANPRTests(unittest.TestCase):

    def setUp(self):
        self.hashes = {"78ff6f1bf2c7abb16f54a3b0987f54ce",
        "96010754c19663913cd22207fead7832"}

        self.control_plate = "SP56AOS"

        self.end_time, self.end_text, self.plate_img, self.img, _ = PlateScanner("pdataset/1.jpg", config.check_config()).scan_plate()

    def hash_image(self, image):
        return hashlib.md5(image.tostring()).hexdigest()
    
    #checks if the system processes image
    def test_image_processing(self):
        self.assertIsNotNone(self.plate_img)
        self.assertIsNotNone(self.img)

    #compares if the resultant images are identical to the control images
    def test_image_hashes(self):
        self.assertEqual(self.hashes.__contains__(self.hash_image(self.plate_img)), True)
        self.assertEqual(self.hashes.__contains__(self.hash_image(self.img)), True)
    
    #checks if the resultant end text is equal to the contorl plate 
    def test_image_plate(self):
        self.assertEqual(self.end_text, self.control_plate)
    
    #check if processing time is less than 500
    def test_process_time(self): 
        self.assertLess(self.end_time, 500)

    

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ANPRTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

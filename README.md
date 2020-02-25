
# anpr-project
## A Team Software Engineering project. 
An Automatic Number Plate Recognition application that uses OpenCV and Tesseract OCR.

# Dependencies

- OpenCV
- PyQt5?
- Python 3.7+
- imutils
- Google Tesseract OCR


# Installing Dependencies

To install all Python library requirements, in the command-line run:

    pip install requirements.txt

## Installing Tesseract

### Windows 

Download and install Tesseract 4.0.x from [here](https://github.com/UB-Mannheim/tesseract/wiki). 

### Linux 

As per Tesseract-OCR [wiki](https://github.com/tesseract-ocr/tesseract/wiki), run:
    
    sudo apt install tesseract-ocr
    sudo apt install libtesseract-dev

# Using the program
At this stage, you can only launch `main.py` through the command-line.

Type in `python main.py [image.jpg/png]`

**__Ensure you have installed all the dependencies first and have completed the config.__**

# Configuration
1. Launch the program first to create the config file if one not present.

2. Open `config.json` 

3. Enter the file url of `tesseract.exe` into the `tesseract_url` variable. If you cannot find `tesseract.exe`, ensure it is installed first.  

4. If you wish to view the steps the program has taken to get the result, set `show_steps` to `true`, otherwise leave it as `false`.

5. Launch the program again and you should get the results. 

# Dataset
A dataset has been provided. Download `pdataset.zip` to view the images.

## Using VirtualEnv
It is recommended to use a python virtual environment for this project, as it installs quite a few additional pip packages.

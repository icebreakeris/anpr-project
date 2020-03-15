
# anpr-project
## A Team Software Engineering project. 
An Automatic Number Plate Recognition application that uses OpenCV and Tesseract OCR.

# Dependencies

- OpenCV
- Numpy
- PyQt5
- Python 3.7+
- imutils
- Google Tesseract OCR 4.0.x


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
There are **three** ways of using the program.

The first way is to launch `scanner.py` through command line, type in:

    python scanner.py [image.jpg/png]

The second way is to launch `eval.py`, type in: 
    
    python eval.py

This is used to evaluate the performance of the system. It goes through every image in the dataset, saves the results into the `finalplates` directory and outputs the evaluated performance.

The third way is to use the GUI.

Type into the command line: 

    python gui.py

This will launch a GUI that you can use instead.

**__Ensure you have installed all the dependencies first and have completed the config, otherwise this system will not work properly.__**

# Configuration

## Using the GUI
1. Launch `gui.py`.

2. This will automatically create a configuration file

3. In the settings group, you will need to locate the tesseract.exe file.

4. Then you are given an option to save the images. Check it if you wish to do so.

5. You are also given the choice of showing processing steps. Check it if you wish to do so.


## Using command-line

1. Launch the program using `scanner.py` or `eval.py` first.

2. Open `config.json` 

3. Enter the file url of `tesseract.exe` into the `tesseract_url` variable. If you cannot find `tesseract.exe`, ensure it is installed first.  

4. If you wish to view the steps the program has taken to get the result, set `show_steps` to `true`, otherwise leave it as `false`.

5. Launch the program again and you should get the results. 

# Dataset
A dataset has been provided. Download `pdataset.zip` to view the images.

## Using VirtualEnv
It is recommended to use a python virtual environment for this project, as it installs quite a few additional pip packages.


# anpr-project
## A Team Software Engineering project. 
An Automatic Number Plate Recognition application that uses OpenCV and Tesseract OCR.

Preview video: https://www.youtube.com/watch?v=KPHP257mb5o

[![Preview](https://i.ytimg.com/vi_webp/KPHP257mb5o/maxresdefault.webp)](https://www.youtube.com/watch?v=KPHP257mb5o)

# Dependencies

- Python 3.7+
- OpenCV
- Numpy
- PyQt5
- imutils
- setuptools 40.8.0
- pywin32
- Google Tesseract OCR 5.0.0 alpha

# Installing Dependencies

To install all Python library requirements, in the command-line run:

    pip install -r requirements.txt

## Installing Tesseract

### Windows 

Download and install Tesseract 5.0.0 alpha from [here](https://github.com/UB-Mannheim/tesseract/wiki). 

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

The third way is to use the GUI, type in: 

    python gui.py

This will launch a fully functional GUI.

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

5. If you wish to save the resultant images, set `save_images` to `true`, otherwise leave it as `false`.

6. Launch the program again and you should get the results. 

# Dataset
A dataset has been provided in `example_dataset` folder.

## Using VirtualEnv
It is recommended to use a python virtual environment for this project, as it installs quite a few additional pip packages.

You can find documentation for VirtualEnv [here](https://virtualenv.pypa.io/en/latest/).

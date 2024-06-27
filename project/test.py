import cv2 as cv
import pyautogui
import ctypes
import time
import numpy as np
from PIL import Image
import pytesseract
from enum import Enum, auto
import re


pyautogui.moveTo(1574, 845)

import ctypes

# Attempt a different DPI awareness setting if the previous one didn't work
ctypes.windll.user32.SetProcessDPIAware()

# Debugging: Print the output of GetGlobalItemCenterPosition
test_point = (100, 100)  # Example point
pyautogui.moveTo(1574, 845)  # Replace 100, 100 with known good coordinates for testing
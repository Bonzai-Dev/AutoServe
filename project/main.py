#System requirements: CUDA version 12.0 and tesseract OCR downloaded onto the system

#Start date: 6/22/2024
#Last update: ?/?/2024

import cv2 as cv
import pyautogui
import ctypes
import time
import numpy as np
import pytesseract
import re
import ctypes
import traceback
import threading
import autoit

from numba import jit, cuda 
from enum import Enum, auto
from PIL import Image

# Make the program DPI aware to handle display scaling properly
ctypes.windll.shcore.SetProcessDpiAwareness(1)
pytesseract.pytesseract.tesseract_cmd = r"project\Tesseract-OCR\tesseract.exe"

dialogueRegion = (787, 290, 355, 140) # x, y, width, height
menuRegion = (1373, 210, 550, 700)

screenShotRate = 0.2 # in seconds
dialogueWindowName = "Dialogue AI view"
menuWindowName = "Menu AI view"
#windowWidth = 300; # in pixels and will automatically adjust its height

dialogue = None
dialogueRgb = None
dialogueBgr = None
dialogueGray = None

menu = None
menuRgb = None
menuBgr = None
menuGray = None

class ItemTypes():
    MENU_ITEM = "MenuItem"
    DIALOGUE_ITEM = "DialogueItem"

class OrderSizes(Enum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()

class OrderState(Enum):
    BURGER = auto()
    FRIES = auto()
    DRINK = auto()
    FINISH = auto()

currentOrderState = OrderState.BURGER
detectedOrderedItems = []
detectedMenuItems = []
detectedItems = []

#region Classes
#NOTE IF STARTPOSITION IS SET TO 0,0 IT WILL NOT WORK
class Item:
    def __init__(self, image : str, outlineColor : tuple[int, int, int], itemName: str, itemType : ItemTypes, positionOnScreen : tuple[int, int] = (0, 0), requestedAmount : int = 1):
        self.image = image # Image path
        self.outlineColor = outlineColor # Format in BGR
        self.itemName = itemName
        self.itemType = itemType
        self.positionOnScreen = positionOnScreen
        self.requestedAmount = requestedAmount

# Images for menu items including buttons
burgerMenuButton = Item(r"project\img\menuItems\BurgerMenuButton.png", (0, 225, 255), "Burger menu button", ItemTypes.MENU_ITEM)
friesMenuButton = Item(r"project\img\menuItems\friesMenuButton.png", (100, 0, 255), "Fry menu button", ItemTypes.MENU_ITEM)
drinkMenuButton = Item(r"project\img\menuItems\DrinkMenuButton.png", (225, 60, 255), "Drink menu button", ItemTypes.MENU_ITEM)
menuFinishButton = Item(r"project\img\menuItems\FinishButton.png", (0, 0, 255), "Finish menu button", ItemTypes.MENU_ITEM)

burgerBunTopItem = Item(r"project\img\menuItems\ingredients\burger\BurgerMenuBunTop.png", (0, 255, 0), "Bun menu top", ItemTypes.MENU_ITEM)
burgerCheeseItem = Item(r"project\img\menuItems\ingredients\burger\CheeseMenu.png", (0, 255, 0), "Cheese menu", ItemTypes.MENU_ITEM)
burgerPattyVeganItem = Item(r"project\img\menuItems\ingredients\burger\PattyVeganMenu.png", (0, 255, 0), "Vegan menu patty", ItemTypes.MENU_ITEM)
burgerPattyMeatItem = Item(r"project\img\menuItems\ingredients\burger\PattyMeatMenu.png", (0, 255, 0), "Meat menu patty", ItemTypes.MENU_ITEM)
burgerBunBottomItem = Item(r"project\img\menuItems\ingredients\burger\BurgerMenuBunBottom.png", (0, 255, 0), "Bun menu bottom", ItemTypes.MENU_ITEM)

normalFriesItem = Item(r"project\img\menuItems\ingredients\fries\FryNormalMenu.png", (0, 255, 0), "Fry normal menu", ItemTypes.MENU_ITEM)

# Images for dialogue items
# NOTE: ALL THE DIALOGUE ITEMS NAME MUST END WITH AN "order". EX.: "Cheese order" AND DO NOT ADD ANY ITEMTYPE TO THE SIZES
cheeseOrder = Item(r"project\img\dialogueItems\burger\CheeseDialogue.png", (255, 0, 0), "Cheese order", ItemTypes.DIALOGUE_ITEM)
pattyMeatDialogue = Item(r"project\img\dialogueItems\burger\PattyMeatDialogue.png", (0, 255, 0), "Patty meat order", ItemTypes.DIALOGUE_ITEM)
pattyVeganDialogue = Item(r"project\img\dialogueItems\burger\PattyVeganDialogue.png", (0, 20, 0), "Patty vegan order", ItemTypes.DIALOGUE_ITEM)
normalFryOrder = Item(r"project\img\dialogueItems\fries\FryNormalDialogue.png", (0, 255, 0), "Normal fry order", ItemTypes.DIALOGUE_ITEM)
normalDrinkOrder = Item(r"project\img\dialogueItems\drinks\DrinkNormalDialogue.png", (0, 255, 0), "Normal drink order", ItemTypes.DIALOGUE_ITEM)

smallSizeMenu = Item(r"project\img\sizes\menu\Small.png", (0, 255, 0), "Small size menu", ItemTypes.MENU_ITEM)
mediumSizeMenu = Item(r"project\img\sizes\menu\Medium.png", (0, 255, 0), "Medium size menu", ItemTypes.MENU_ITEM)
largeSizeMenu = Item(r"project\img\sizes\menu\Large.png", (0, 255, 0), "Lage size menu", ItemTypes.MENU_ITEM)

smallSizeDialogue = Item(r"project\img\sizes\dialogue\Small.png", (0, 255, 0), "Small size dialogue", ItemTypes.DIALOGUE_ITEM)
mediumSizeDialogue = Item(r"project\img\sizes\dialogue\Medium.png", (0, 255, 0), "Medium size dialogue", ItemTypes.DIALOGUE_ITEM)
largeSizeDialogue = Item(r"project\img\sizes\dialogue\Large.png", (0, 255, 0), "Large size dialogue", ItemTypes.DIALOGUE_ITEM)

# Lists containing all the items for each region. Ex.: the dialogue is one region, so the patty and cheese order is in that list
menuItems = [
    smallSizeMenu,
    mediumSizeMenu,
    largeSizeMenu,
    
    burgerMenuButton, 
    friesMenuButton,
    drinkMenuButton,
    menuFinishButton,
    
    normalFriesItem,
    
    burgerBunTopItem,
    burgerCheeseItem,
    burgerPattyVeganItem,
    burgerPattyMeatItem,
    burgerBunBottomItem,
]

dialogueItems = [
    smallSizeDialogue,
    mediumSizeDialogue,
    largeSizeDialogue,
    
    cheeseOrder, 
    pattyMeatDialogue,
    pattyVeganDialogue,
    normalFryOrder,
    normalDrinkOrder,
]
#endregion

#region Functions
def ClickOnItem(item : Item):
    positionX = item.positionOnScreen[0]
    positionY = item.positionOnScreen[1]
    autoit.mouse_click("left", positionX, positionY, item.requestedAmount, 2)

def ClickOnItemSize():
    # Removing all of the items from list once detected so that we can readd them again to prevent duplicates
    if (smallSizeDialogue.itemName in detectedOrderedItems):
        ClickOnItem(smallSizeMenu)
        print("SMALL SIZE DETECTED")
        detectedOrderedItems.remove(smallSizeDialogue.itemName)
    elif (mediumSizeDialogue.itemName in detectedOrderedItems):
        ClickOnItem(mediumSizeMenu)
        print("MEDIUM SIZE DETECTED")
        detectedOrderedItems.remove(mediumSizeDialogue.itemName)
    elif (largeSizeDialogue.itemName in detectedOrderedItems):
        ClickOnItem(largeSizeMenu)
        print("LARGE SIZE DETECTED")
        detectedOrderedItems.remove(largeSizeDialogue.itemName)


def GetTextFromImage(image, name):
    # Convert the image to grayscale
    grayImage = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Increase contrast
    alpha = 1  # Contrast control (1.0-3.0)
    beta = 0    # Brightness control (0-100)
    contrastedImage = cv.convertScaleAbs(grayImage, alpha=alpha, beta=beta)

    # Apply sharpening filter
    sharpeningKernel = np.array([[-1, -1, -1],
                                 [-1, 9, -1],
                                 [-1, -1, -1]])
    sharpenedImage = cv.filter2D(contrastedImage, -1, sharpeningKernel)

    # Apply adaptive thresholding
    thresholdedImage = cv.adaptiveThreshold(sharpenedImage, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv.THRESH_BINARY, 11, 2)

    # Scale the image (making it larger can help OCR accuracy)
    scaleFactor = 4
    newWidth = int(thresholdedImage.shape[1] * scaleFactor)
    newHeight = int(thresholdedImage.shape[0] * scaleFactor)
    scaledImage = cv.resize(thresholdedImage, (newWidth, newHeight), interpolation=cv.INTER_LINEAR)

    # Extracting text from the scaled image using custom configurations
    # Using PSM 6 (Assume a single uniform block of text) and whitelisting characters
    customConfig = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    text = pytesseract.image_to_string(scaledImage, config=customConfig)
    #print("extracted text from: " + name + " is: " + text)
    return text

def GetAmountOfItems(itemImage, name): # Gets the amount of ordered items based on an image
    text = GetTextFromImage(itemImage, name)
    numbers = re.findall(r'\d+', text)
    if (numbers): 
        return int(numbers[0])
    return 1

def GetGlobalItemCenterPosition(point, template, name, regionTopLeft):
    centerX = int(point[0] + template.shape[1] // 2 + regionTopLeft[0])
    centerY = int(point[1] + template.shape[0] // 2 + regionTopLeft[1])
    #print(f"{name} Global Center: ({centerX}, {centerY})")
    return (centerX, centerY)

def DetectElementInRegion(regionRgb, regionGray, itemsList, threshold: float = 0.8):
    try:
        global currentOrderState
        for item in itemsList:
            template = cv.imread(item.image, cv.IMREAD_GRAYSCALE)
            template = cv.adaptiveThreshold(template, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
            regionAdaptiveThresh = cv.adaptiveThreshold(regionGray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
            w, h = template.shape[::-1]
            resolution = cv.matchTemplate(regionAdaptiveThresh, template, cv.TM_CCOEFF_NORMED)
            locate = np.where(resolution >= threshold)
            points = list(zip(*locate[::-1]))
            
            filteredPoints = []
            for point in points:
                if all(np.linalg.norm(np.array(point) - np.array(p)) >= 10 for p in filteredPoints):
                    filteredPoints.append(point)
                    break  
            
            for point in filteredPoints:
                # Check if any item in detectedItems has the same itemName as the current item
                if not any(detected.itemName == item.itemName for detected in detectedItems):
                    detectedItems.append(item)
                    item.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuRegion[0:2])
                    match item.itemType:    
                        case ItemTypes.DIALOGUE_ITEM:
                            detectedOrderedItems.append(item.itemName)

                            # Only does this for the burger items so that we get the amounts
                            if (item.itemName == pattyMeatDialogue.itemName or item.itemName == pattyVeganDialogue.itemName or item.itemName == cheeseOrder.itemName):
                                item.requestedAmount = GetAmountOfItems(regionRgb[point[1]:point[1]+h, point[0]:point[0]+w], item.itemName) # Weird for cropped image lol
                                #print(f"The npc has ordered {str(item.requestedAmount)} {item.itemName}")
                        
                        case ItemTypes.MENU_ITEM:
                            detectedMenuItems.append(item.itemName)
                            
                cv.rectangle(regionRgb, point, (point[0] + w, point[1] + h), item.outlineColor, 3)
                cv.putText(regionRgb, item.itemName, (point[0], point[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)            
                cv.circle(regionRgb, (point[0] + template.shape[1] // 2, point[1] + template.shape[0] // 2), 5, (255, 255, 255), 2)
            
        if (len(detectedOrderedItems) > 0):
            if item.positionOnScreen != (0, 0):
                match currentOrderState:
                    case OrderState.BURGER:
                        # Add a extra check here so that it checks if the NPC has ordered a patty. This is to wait until the order loads.
                        if (pattyMeatDialogue.itemName in detectedOrderedItems or pattyVeganDialogue.itemName in detectedOrderedItems):
                            ClickOnItem(burgerBunBottomItem)
                            
                            if (pattyMeatDialogue.itemName in detectedOrderedItems):
                                ClickOnItem(burgerPattyMeatItem)
                            elif (pattyVeganDialogue.itemName in detectedOrderedItems):
                                ClickOnItem(burgerPattyVeganItem)
                            
                            if (cheeseOrder.itemName in detectedOrderedItems):
                                ClickOnItem(burgerCheeseItem)
                                print(burgerCheeseItem.requestedAmount)
                            
                            ClickOnItem(burgerBunTopItem)
                            
                            ClickOnItem(friesMenuButton)
                            time.sleep(1)
                            currentOrderState = OrderState.FRIES
                    case OrderState.FRIES:
                        # Check if the fries order is in the detectedOrderedItems list, since theres still orders that we havent unlocked yet
                        if (normalFryOrder.itemName in detectedOrderedItems):
                            if (normalFryOrder.itemName in detectedOrderedItems):
                                ClickOnItem(normalFriesItem)

                            ClickOnItemSize()
                            
                            ClickOnItem(drinkMenuButton)
                            time.sleep(1)
                            currentOrderState = OrderState.DRINK
                    case OrderState.DRINK:
                        if (normalDrinkOrder.itemName in detectedOrderedItems):
                            if (normalDrinkOrder.itemName in detectedOrderedItems):
                                print(normalDrinkOrder.positionOnScreen)
                                ClickOnItem(normalDrinkOrder)

                            '''print(detectedOrderedItems)
                            ClickOnItemSize()
                            
                        ClickOnItem(menuFinishButton)'''
                        #currentOrderState = OrderState.FINISH
                    case OrderState.FINISH:
                        currentOrderState = OrderState.BURGER
                        #reset all
                        
    except Exception as e:
        tb = traceback.format_exc()
        print(f"An error occurred in DetectElementInRegion: {e}\nTraceback: {tb}")
        
def TakeScreenshot():
    global dialogue, dialogueRgb, dialogueBgr, dialogueGray, menu, menuRgb, menuBgr, menuGray
    dialogue = pyautogui.screenshot(region=dialogueRegion)
    dialogue = np.array(dialogue)
    dialogueRgb = cv.cvtColor(dialogue, cv.COLOR_BGR2RGB)
    dialogueBgr = cv.cvtColor(dialogue, cv.COLOR_RGB2BGR)
    dialogueGray = cv.cvtColor(dialogue, cv.COLOR_BGR2GRAY)    
    
    menu = pyautogui.screenshot(region=menuRegion)
    menu = np.array(menu)
    menuRgb = cv.cvtColor(menu, cv.COLOR_BGR2RGB)
    menuBgr = cv.cvtColor(menu, cv.COLOR_RGB2BGR)
    menuGray = cv.cvtColor(menu, cv.COLOR_BGR2GRAY)
    
def ShowWindow(image, windowName : str, screenWidth : int):
    h, w = image.shape[0:2]
    neww = screenWidth
    newh = int(neww*(h/w))
    cv.imshow(windowName, cv.resize(image, (neww, newh)))
    cv.setWindowProperty(windowName, cv.WND_PROP_TOPMOST, 1)  # Set the window property to always on top
#endregion

TakeScreenshot()
try:
    while True:
        TakeScreenshot()
        threading.Thread(DetectElementInRegion(dialogueRgb, dialogueGray, dialogueItems, 0.6)).start()
        threading.Thread(DetectElementInRegion(menuRgb, menuGray, menuItems, 0.6)).start()

        ShowWindow(dialogueRgb, dialogueWindowName, 400)
        ShowWindow(menuRgb, menuWindowName, 400)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(screenShotRate)

except Exception as e:
    print(f"An error occurred: {e}")


'''for item in detectedOrderedItems:
    print(item)'''
    

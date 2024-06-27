#System requirements: CUDA version 12.0 and tesseract OCR downloaded onto the system

#Start date: 6/22/2024
#Last update: ?/?/2024

import cv2 as cv
import pyautogui
import ctypes
import time
import numpy as np
from PIL import Image
import pytesseract
from enum import Enum, auto
import re
import ctypes
import traceback

# Make the program DPI aware to handle display scaling properly
ctypes.windll.shcore.SetProcessDpiAwareness(1)
pytesseract.pytesseract.tesseract_cmd = r"project\Tesseract-OCR\tesseract.exe"

dialogueRegion = (787, 290, 355, 140) # x, y, width, height
menuRegion = (1373, 210, 550, 700)

screenShotRate = 0.5 # in seconds
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

class OrderSizes(Enum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()

class OrderState(Enum):
    BURGER = auto()
    DRINK = auto()
    FRIES = auto()
    FINISH = auto()

currentOrderState = OrderState.BURGER
currentOrderedItems = []
currentOrderSize = None

#region Classes
#NOTE IF STARTPOSITION IS SET TO 0,0 IT WILL NOT WORK
class Item:
    def __init__(self, image : str, outlineColor : tuple[int, int, int], itemName: str, itemType : str = "", positionOnScreen : tuple[int, int] = (500, 500)):
        self.image = image # Image path
        self.outlineColor = outlineColor # Format in BGR
        self.itemName = itemName
        self.itemType = itemType
        self.positionOnScreen = positionOnScreen

# Images for menu items including buttons
burgerMenuButton = Item(r"project\img\menuItems\BurgerMenuButton.png", (0, 225, 255), "Burger menu button", "MenuItem")
fryMenuButton = Item(r"project\img\menuItems\FryMenuButton.png", (100, 0, 255), "Fry menu button", "MenuItem")
drinkMenuButton = Item(r"project\img\menuItems\DrinkMenuButton.png", (225, 60, 255), "Drink menu button", "MenuItem")
menuFinishButton = Item(r"project\img\menuItems\FinishButton.png", (0, 0, 255), "Finish menu button", "MenuItem")

burgerBunTopItem = Item(r"project\img\menuItems\ingredients\burger\BurgerMenuBunTop.png", (0, 255, 0), "Bun menu top", "MenuItem")
burgerCheeseItem = Item(r"project\img\menuItems\ingredients\burger\CheeseMenu.png", (0, 255, 0), "Cheese menu", "MenuItem")
burgerPattyVeganItem = Item(r"project\img\menuItems\ingredients\burger\PattyVeganMenu.png", (0, 255, 0), "Vegan menu patty", "MenuItem")
burgerPattyMeatItem = Item(r"project\img\menuItems\ingredients\burger\PattyMeatMenu.png", (0, 255, 0), "Meat menu patty", "MenuItem")
burgerBunBottomItem = Item(r"project\img\menuItems\ingredients\burger\BurgerMenuBunBottom.png", (0, 255, 0), "Bun menu bottom", "MenuItem")

normalFriesItem = Item(r"project\img\menuItems\ingredients\fries\FryNormalMenu.png", (0, 255, 0), "Fry normal menu", "MenuItem")

# Images for dialogue items
# NOTE: ALL THE DIALOGUE ITEMS NAME MUST END WITH AN "order". EX.: "Cheese order" AND DO NOT ADD ANY ITEMTYPE TO THE SIZES
cheeseOrder = Item(r"project\img\dialogueItems\burger\CheeseDialogue.png", (255, 0, 0), "Cheese order", "DialogueItem")
pattyMeatDialogue = Item(r"project\img\dialogueItems\burger\PattyMeatDialogue.png", (0, 255, 0), "Patty meat order", "DialogueItem")
pattyVeganDialogue = Item(r"project\img\dialogueItems\burger\PattyVeganDialogue.png", (0, 20, 0), "Patty vegan order", "DialogueItem")
normalFryOrder = Item(r"project\img\dialogueItems\fries\FryNormalDialogue.png", (0, 255, 0), "Normal fry order", "DialogueItem")
normalDrinkOrder = Item(r"project\img\dialogueItems\drinks\DrinkNormalDialogue.png", (0, 255, 0), "Normal drink order", "DialogueItem")

smallSizeMenu = Item(r"project\img\sizes\menu\Small.png", (0, 255, 0), "Small size menu", "Size")
mediumSizeMenu = Item(r"project\img\sizes\menu\Medium.png", (0, 255, 0), "Medium size menu", "Size")
largeSizeMenu = Item(r"project\img\sizes\menu\Large.png", (0, 255, 0), "Lage size menu", "Size")

smallSizeDialogue = Item(r"project\img\sizes\dialogue\Small.png", (0, 255, 0), "Small size dialogue", "Size")
mediumSizeDialogue = Item(r"project\img\sizes\dialogue\Medium.png", (0, 255, 0), "Medium size dialogue", "Size")
largeSizeDialogue = Item(r"project\img\sizes\dialogue\Large.png", (0, 255, 0), "Large size dialogue", "Size")

# Lists containing all the items for each region. Ex.: the dialogue is one region, so the patty and cheese order is in that list
menuItems = [
    smallSizeMenu,
    mediumSizeMenu,
    largeSizeMenu,
    
    burgerMenuButton, 
    fryMenuButton,
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
def GetTextFromImage(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    text = pytesseract.image_to_string(thresh)
    return text

def GetAmountOfItems(itemImage): # Gets the amount of ordered items based on an image
    text = GetTextFromImage(itemImage)
    hasNumber = any(char.isdigit() for char in text)
    if (hasNumber): 
        print(re.findall(r'\d+', text))
        return map(int, re.findall(r'\d+', text))
    return None
        
def GetSizeOfItem(item : Item):
    size = None
    # NOTE USE ITEM TYPES IN FUTURE
    match item.itemName:
        case name if "Small" in name:
            size = OrderSizes.SMALL
        case name if "Medium" in name:
            size = OrderSizes.MEDIUM
        case name if "Large" in name:
            size = OrderSizes.LARGE        
    return size

def GetGlobalItemCenterPosition(point, template, name, regionTopLeft):
    # Calculate center position with global offset
    centerX = int(point[0] + template.shape[1] // 2 + regionTopLeft[0])
    centerY = int(point[1] + template.shape[0] // 2 + regionTopLeft[1])
    print(f"{name} Global Center: ({centerX}, {centerY})")
    return (centerX, centerY)

def ClickOnItem(item : Item):
    positionX = item.positionOnScreen[0]
    positionY = item.positionOnScreen[1]
    
    print(f"Coordinates of: {item.itemName} is: ", positionX, positionY)
    pyautogui.click(positionX, positionY)
    time.sleep(0.5)

def DetectElementInRegion(regionRgb, regionGray, itemsList, threshold: float = 0.8):
    global currentOrderState, currentOrderSize
    try:
        detectedItems = []
        for item in itemsList:
            template = cv.imread(item.image, cv.IMREAD_GRAYSCALE)
            template = cv.adaptiveThreshold(template, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
            regionAdaptiveThresh = cv.adaptiveThreshold(regionGray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
            w, h = template.shape[::-1]
            resolution = cv.matchTemplate(regionAdaptiveThresh, template, cv.TM_CCOEFF_NORMED)
            locate = np.where(resolution >= threshold)
            points = list(zip(*locate[::-1]))
            
            filtered_points = []
            for point in points:
                if all(np.linalg.norm(np.array(point) - np.array(p)) >= 10 for p in filtered_points):
                    filtered_points.append(point)
                    break  

            for point in filtered_points:
                #print(GetAmountOfItems(regionRgb))    
                cv.rectangle(regionRgb, point, (point[0] + w, point[1] + h), item.outlineColor, 3)
                cv.putText(regionRgb, item.itemName, (point[0], point[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)            
                cv.circle(regionRgb, (point[0] + template.shape[1] // 2, point[1] + template.shape[0] // 2), 5, (255, 255, 255), 2)
                
                # Detects all the items and adds values
                if (item.itemName not in detectedItems):
                    match item.itemType:
                        case "Size":
                            currentOrderSize = GetSizeOfItem(item)
                        case "DialogueItem":
                            if (item.itemName not in currentOrderedItems):
                                currentOrderedItems.append(item.itemName)
                                detectedItems.append(item.itemName)
                                
                        case "MenuItem":
                            detectedItems.append(item.itemName)
                            menuTopLeft = (menuRegion[0], menuRegion[1])
                            match item.itemName:
                                case "Bun menu top":
                                    burgerBunTopItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(1)
                                case "Cheese menu":
                                    burgerCheeseItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(2)
                                case "Vegan menu patty":
                                    burgerPattyVeganItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(3)
                                case "Meat menu patty":
                                    burgerPattyMeatItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(4)
                                case "Bun menu bottom":
                                    burgerBunBottomItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(5)
                                case "Finish menu button":
                                    menuFinishButton.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(6)
                                case "Burger menu button":
                                    burgerMenuButton.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(7)
                                case "Fry menu button":
                                    fryMenuButton.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(8)
                                case "Drink menu button":
                                    drinkMenuButton.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(9)
                                case "Fry normal menu":
                                    normalFriesItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(10)
                                case "Small size menu":
                                    smallSizeMenu.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(11)
                                case "Medium size menu":
                                    mediumSizeMenu.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(12)
                                case "Large size menu":
                                    largeSizeMenu.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                    print(13)
                    
                    match currentOrderState:
                        case OrderState.BURGER:
                            ClickOnItem(burgerBunBottomItem)
                            if (pattyMeatDialogue.itemName in currentOrderedItems):
                                ClickOnItem(burgerPattyMeatItem)
                            elif (pattyVeganDialogue.itemName in currentOrderedItems):
                                ClickOnItem(burgerPattyVeganItem)
                            
                            ClickOnItem(burgerCheeseItem)
                            ClickOnItem(burgerBunTopItem)
                            ClickOnItem(fryMenuButton)
                            
                            currentOrderState = OrderState.FRIES
                        case OrderState.FRIES:
                            '''ClickOnItem(normalFriesItem)
                            
                            match currentOrderSize:
                                case OrderSizes.SMALL:
                                    ClickOnItem(smallSizeMenu)
                                case OrderSizes.MEDIUM:
                                    ClickOnItem(mediumSizeMenu)
                                case OrderSizes.LARGE:
                                    ClickOnItem(largeSizeMenu)'''
                            
                            currentOrderState = OrderState.DRINK
                        case OrderState.DRINK:
                            '''ClickOnItem(drinkMenuButton)
                            
                            match currentOrderSize:
                                case OrderSizes.SMALL:
                                    ClickOnItem(smallSizeMenu)
                                case OrderSizes.MEDIUM:
                                    ClickOnItem(mediumSizeMenu)
                                case OrderSizes.LARGE:
                                    ClickOnItem(largeSizeMenu)
                            
                            GetSizeOfItem(item)
                            currentOrderState = OrderState.FINISH'''
                        case OrderState.FINISH:
                            # reset everything
                            return
                                    
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
#endregion

TakeScreenshot()
try:
    while True:
        TakeScreenshot()
        DetectElementInRegion(dialogueRgb, dialogueGray, dialogueItems, 0.6)
        DetectElementInRegion(menuRgb, menuGray, menuItems, 0.6)

        ShowWindow(dialogueRgb, dialogueWindowName, 400)
        ShowWindow(menuRgb, menuWindowName, 400)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(screenShotRate)

except Exception as e:
    print(f"An error occurred: {e}")
    
print(currentOrderedItems)
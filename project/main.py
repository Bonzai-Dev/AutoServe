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

# Make the program DPI aware to handle display scaling properly
ctypes.windll.shcore.SetProcessDpiAwareness(1)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\2690360\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

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
class Item:
    def __init__(self, image : str, outlineColor : tuple[int, int, int], itemName: str, itemType : str = "", positionOnScreen : tuple[int, int] = (0, 0)):
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

# Images for dialogue items
# NOTE: ALL THE DIALOGUE ITEMS NAME MUST END WITH AN "order". EX.: "Cheese order" AND DO NOT ADD ANY ITEMTYPE TO THE SIZES
cheeseOrder = Item(r"project\img\dialogueItems\burger\CheeseDialogue.png", (255, 0, 0), "Cheese order", "DialogueItem")
pattyOrder = Item(r"project\img\dialogueItems\burger\PattyDialogue.png", (0, 255, 0), "Patty order", "DialogueItem")
normalFryOrder = Item(r"project\img\dialogueItems\fries\FryNormalDialogue.png", (0, 255, 0), "Normal fry order", "DialogueItem")
normalDrinkOrder = Item(r"project\img\dialogueItems\drinks\DrinkNormalDialogue.png", (0, 255, 0), "Normal drink order", "DialogueItem")

smallSizeMenu = Item(r"project\img\sizes\menu\Small.png", (0, 255, 0), "Small size menu")
mediumSizeMenu = Item(r"project\img\sizes\menu\Medium.png", (0, 255, 0), "Medium size menu")
largeSizeMenu = Item(r"project\img\sizes\menu\Large.png", (0, 255, 0), "Lage size menu")

smallSizeDialogue = Item(r"project\img\sizes\dialogue\Small.png", (0, 255, 0), "Small size dialogue")
mediumSizeDialogue = Item(r"project\img\sizes\dialogue\Medium.png", (0, 255, 0), "Medium size dialogue")
largeSizeDialogue = Item(r"project\img\sizes\dialogue\Large.png", (0, 255, 0), "Large size dialogue")

# Lists containing all the items for each region. Ex.: the dialogue is one region, so the patty and cheese order is in that list
menuItems = [
    smallSizeMenu,
    mediumSizeMenu,
    largeSizeMenu,
    
    burgerMenuButton, 
    fryMenuButton,
    drinkMenuButton,
    menuFinishButton,
    
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
    pattyOrder,
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

def GetWordInPhrase(wordToFind : str, phrase : str):
    return wordToFind if wordToFind in phrase.split() else None

def GetGlobalItemCenterPosition(point, template, name, regionTopLeft):
    # Calculate center position with global offset
    centerX = int(point[0] + template.shape[1] // 2 + regionTopLeft[0])
    centerY = int(point[1] + template.shape[0] // 2 + regionTopLeft[1])
    print(f"{name} Global Center: ({centerX}, {centerY})")
    return (centerX, centerY)

def DetectElementInRegion(regionRgb, regionGray, itemsList, threshold: float = 0.8):
    global orderedItem
    try:
        for item in itemsList: 
            template = cv.imread(item.image, cv.IMREAD_GRAYSCALE)
            _, binary_image = cv.threshold(template, 128, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
            w, h = template.shape[::-1]

            resolution = cv.matchTemplate(regionGray, template, cv.TM_CCOEFF_NORMED)
            locate = np.where(resolution >= threshold)
            points = list(zip(*locate[::-1]))
            filtered_points = []
            for point in points:
                if all(np.linalg.norm(np.array(point) - np.array(p)) >= 10 for p in filtered_points):
                    filtered_points.append(point)
                    break 

            for point in filtered_points:
                #print(GetAmountOfItems(regionRgb))
                menuTopLeft = (menuRegion[0], menuRegion[1])
                cv.circle(regionRgb, (point[0] + template.shape[1] // 2, point[1] + template.shape[0] // 2), 5, (255, 255, 255), 2)
                if (item.itemName not in currentOrderedItems):
                    match item.itemType:
                        case "DialogueItem":
                            currentOrderedItems.append(item.itemName)
                        case "MenuItem":
                            item.positionOnScreen = point
                            match item.itemName:
                                case "Bun menu top":
                                    burgerBunTopItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                case "Cheese menu":
                                    burgerCheeseItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                case "Vegan menu patty":
                                    burgerPattyVeganItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                case "Meat menu patty":
                                    burgerPattyMeatItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                case "Bun menu bottom":
                                    burgerBunBottomItem.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                                case "Finish menu button":
                                    menuFinishButton.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuTopLeft)
                    
                cv.rectangle(regionRgb, point, (point[0] + w, point[1] + h), item.outlineColor, 3)
                cv.putText(regionRgb, item.itemName, (point[0], point[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        match currentOrderState:
            case OrderState.BURGER:
                pyautogui.moveTo(burgerBunBottomItem.positionOnScreen[0], burgerBunBottomItem.positionOnScreen[1])
                pyautogui.moveTo(burgerPattyMeatItem.positionOnScreen[0], burgerPattyMeatItem.positionOnScreen[1])
                pyautogui.moveTo(burgerPattyVeganItem.positionOnScreen[0], burgerPattyVeganItem.positionOnScreen[1])
                pyautogui.moveTo(burgerCheeseItem.positionOnScreen[0], burgerCheeseItem.positionOnScreen[1])
                pyautogui.moveTo(burgerBunTopItem.positionOnScreen[0], burgerBunTopItem.positionOnScreen[1])
                
                currentOrderState = OrderState.FRIES
            case OrderState.FRIES:
                print("fries")
                GetSizeOfItem(item)
            case OrderState.DRINK:
                print("drink")
                GetSizeOfItem(item)
            case OrderState.FINISH:
                print("finished order")
                return

    except Exception as e:
        print(f"An error occurred in DetectElementInRegion: {e}")
        
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
        DetectElementInRegion(dialogueRgb, dialogueGray, dialogueItems, 0.67)
        DetectElementInRegion(menuRgb, menuGray, menuItems)

        ShowWindow(dialogueRgb, dialogueWindowName, 400)
        ShowWindow(menuRgb, menuWindowName, 400)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(screenShotRate)

except Exception as e:
    print(f"An error occurred: {e}")
    
print(currentOrderedItems)
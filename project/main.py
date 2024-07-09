#Start date: 6/22/2024
#Last update: ?/?/2024

import cv2 as cv
import pyautogui
import ctypes
import time
import numpy as np
import traceback
import autoit
import json
import keyboard
import threading

from enum import Enum, auto

# Make the program DPI aware to handle display scaling properly
ctypes.windll.shcore.SetProcessDpiAwareness(1)
#pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR\tesseract.exe" # keep just in case

settingsJsonPath : str = r"settings.json"
with open (settingsJsonPath, "r") as f:  
    settings : json = json.load(f)

dialogueRegion = tuple(map(int, settings["dialogueRegion"].strip("()").split(", ")))
menuRegion = tuple(map(int, settings["menuRegion"].strip("()").split(", ")))

screenShotRate = 0.8 # in seconds
dialogueWindowName = "Dialogue AI view"
menuWindowName = "Menu AI view"

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
detectedItemAmount = []

#region Classes
class Item:
    def __init__(self, image : str, outlineColor : tuple[int, int, int], itemName: str, itemType : ItemTypes, positionOnScreen : tuple[int, int] = (0, 0), requestedAmount : int = 1, detectionThreshold : float = 0.6):
        self.image = image # Image path
        self.outlineColor = outlineColor # Format in BGR
        self.itemName = itemName
        self.itemType = itemType
        self.positionOnScreen = positionOnScreen
        self.requestedAmount = requestedAmount
        self.detectionThreshold = detectionThreshold

# Images for menu items including buttons
burgerMenuButton = Item(r"img\menuItems\BurgerMenuButton.png", (0, 225, 255), "Burger menu button", ItemTypes.MENU_ITEM, detectionThreshold=settings["burgerMenuButtonDetectionThreshold"])
friesMenuButton = Item(r"img\menuItems\friesMenuButton.png", (100, 0, 255), "Fry menu button", ItemTypes.MENU_ITEM, detectionThreshold=settings["friesMenuButtonDetectionThreshold"])
drinkMenuButton = Item(r"img\menuItems\DrinkMenuButton.png", (225, 60, 255), "Drink menu button", ItemTypes.MENU_ITEM, detectionThreshold=settings["drinkMenuButtonDetectionThreshold"])
menuFinishButton = Item(r"img\menuItems\FinishButton.png", (0, 0, 255), "Finish menu button", ItemTypes.MENU_ITEM, detectionThreshold=settings["menuFinishButtonDetectionThreshold"]    )

burgerBunTopItem = Item(r"img\menuItems\ingredients\burger\BurgerMenuBunTop.png", (0, 255, 0), "Bun menu top", ItemTypes.MENU_ITEM, detectionThreshold=settings["burgerBunTopItemDetectionThreshold"])
burgerCheeseItem = Item(r"img\menuItems\ingredients\burger\CheeseMenu.png", (0, 255, 0), "Cheese menu", ItemTypes.MENU_ITEM, detectionThreshold=settings["burgerCheeseItemDetectionThreshold"])
burgerPattyVeganItem = Item(r"img\menuItems\ingredients\burger\PattyVeganMenu.png", (0, 255, 0), "Vegan menu patty", ItemTypes.MENU_ITEM, detectionThreshold=settings["burgerPattyVeganItemDetectionThreshold"])
burgerPattyMeatItem = Item(r"img\menuItems\ingredients\burger\PattyMeatMenu.png", (0, 255, 0), "Meat menu patty", ItemTypes.MENU_ITEM, detectionThreshold=settings["burgerPattyMeatItemDetectionThreshold"])
burgerTomatoeItem = Item(r"img\menuItems\ingredients\burger\TomatoeMenu.png", (0, 255, 0), "Tomatoe menu", ItemTypes.MENU_ITEM, detectionThreshold=settings["burgerTomatoeItemDetectionThreshold"])
burgerLettuceItem = Item(r"img\menuItems\ingredients\burger\LettuceMenu.png", (0, 255, 0), "Lettuce menu", ItemTypes.MENU_ITEM, detectionThreshold=settings["burgerLettuceItemDetectionThreshold"])
burgerBunBottomItem = Item(r"img\menuItems\ingredients\burger\BurgerMenuBunBottom.png", (0, 255, 0), "Bun menu bottom", ItemTypes.MENU_ITEM, detectionThreshold=settings["burgerBunBottomItemDetectionThreshold"])

normalFriesItem = Item(r"img\menuItems\ingredients\fries\FryNormalMenu.png", (0, 255, 0), "Fry normal menu", ItemTypes.MENU_ITEM, detectionThreshold=settings["normalFriesItemDetectionThreshold"])
mozzarellaSicksItem = Item(r"img\menuItems\ingredients\fries\MozzarellaSticksMenu.png", (0, 255, 0), "Mozzarella sticks menu", ItemTypes.MENU_ITEM, detectionThreshold=settings["mozzarellaSicksItemDetectionThreshold"])

normalDrinkItem = Item(r"img\menuItems\ingredients\drinks\DrinkNormalMenu.png", (0, 255, 0), "Drink normal menu", ItemTypes.MENU_ITEM, detectionThreshold=settings["normalDrinkItemDetectionThreshold"])

# Images for dialogue items
# NOTE: ALL THE DIALOGUE ITEMS NAME MUST END WITH AN "order". EX.: "Cheese order" AND DO NOT ADD ANY ITEMTYPE TO THE SIZES
cheeseDialogue = Item(r"img\dialogueItems\burger\CheeseDialogue.png", (255, 0, 0), "Cheese order", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["cheeseDialogueDetectionThreshold"])
pattyMeatDialogue = Item(r"img\dialogueItems\burger\PattyMeatDialogue.png", (0, 255, 0), "Patty meat order", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["pattyMeatDialogueDetectionThreshold"])
pattyVeganDialogue = Item(r"img\dialogueItems\burger\PattyVeganDialogue.png", (0, 20, 0), "Patty vegan order", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["pattyVeganDialogueDetectionThreshold"])
tomatoeDialogue = Item(r"img\dialogueItems\burger\TomatoeDialogue.png", (0, 20, 0), "Tomatoe order", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["tomatoeDialogueDetectionThreshold"])
lettuceDialogue = Item(r"img\dialogueItems\burger\LettuceDialogue.png", (0, 255, 0), "Lettuce order", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["lettuceDialogueDetectionThreshold"])
 
mozzarellaSticksOrder = Item(r"img\dialogueItems\fries\MozzarellaSticksDialogue.png", (0, 255, 0), "Mozzarella sticks order", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["mozzarellaSticksOrderDetectionThreshold"])
normalFryOrder = Item(r"img\dialogueItems\fries\FryNormalDialogue.png", (0, 255, 0), "Normal fry order", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["normalFryOrderDetectionThreshold"])

normalDrinkOrder = Item(r"img\dialogueItems\drinks\DrinkNormalDialogue.png", (0, 255, 0), "Normal drink order", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["normalDrinkOrderDetectionThreshold"])


oneItemOrder = Item(r"img\dialogueItems\numberAmount\amountOne.png", (0, 0, 255), "One item amount", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["oneItemOrderDetectionThreshold"])
twoItemOrder = Item(r"img\dialogueItems\numberAmount\amountTwo.png", (255, 0, 0), "Two item amount", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["twoItemOrderDetectionThreshold"])


smallSizeMenu = Item(r"img\sizes\menu\Small.png", (0, 255, 0), "Small size menu", ItemTypes.MENU_ITEM, detectionThreshold=settings["smallSizeMenuDetectionThreshold"])
mediumSizeMenu = Item(r"img\sizes\menu\Medium.png", (0, 255, 0), "Medium size menu", ItemTypes.MENU_ITEM, detectionThreshold=settings["mediumSizeMenuDetectionThreshold"])
largeSizeMenu = Item(r"img\sizes\menu\Large.png", (0, 255, 0), "Lage size menu", ItemTypes.MENU_ITEM, detectionThreshold=settings["largeSizeMenuDetectionThreshold"])

smallSizeDialogue = Item(r"img\sizes\dialogue\Small.png", (0, 255, 0), "Small size dialogue", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["smallSizeDialogueDetectionThreshold"])
mediumSizeDialogue = Item(r"img\sizes\dialogue\Medium.png", (0, 255, 0), "Medium size dialogue", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["mediumSizeDialogueDetectionThreshold"])
largeSizeDialogue = Item(r"img\sizes\dialogue\Large.png", (0, 255, 0), "Large size dialogue", ItemTypes.DIALOGUE_ITEM, detectionThreshold=settings["largeSizeDialogueDetectionThreshold"])

# Lists containing all the items for each region. Ex.: the dialogue is one region, so the patty and cheese order is in that list
menuItems = [
    smallSizeMenu,
    mediumSizeMenu,
    largeSizeMenu,
    
    burgerMenuButton, 
    friesMenuButton,
    drinkMenuButton,
    menuFinishButton,
        
    burgerBunTopItem,
    burgerCheeseItem,
    burgerPattyVeganItem,
    burgerPattyMeatItem,
    burgerTomatoeItem,
    burgerLettuceItem,
    burgerBunBottomItem,
    
    normalFriesItem,
    mozzarellaSicksItem,
    
    normalDrinkItem,
]

dialogueItems = [
    smallSizeDialogue,
    mediumSizeDialogue,
    largeSizeDialogue,

    cheeseDialogue, 
    pattyMeatDialogue,
    pattyVeganDialogue,
    tomatoeDialogue,
    lettuceDialogue,
    
    normalFryOrder,
    mozzarellaSticksOrder,
    
    normalDrinkOrder,
]

itemAmounts = [
    oneItemOrder,
    twoItemOrder,
]
#endregion

#region Functions
def ClickOnItem(item : Item):
    positionX = item.positionOnScreen[0]
    positionY = item.positionOnScreen[1]
    print(item.itemName,item.requestedAmount)
    for i in range(item.requestedAmount):
        autoit.mouse_click("left", positionX, positionY, 1, 2)
        time.sleep(0.3)

def ClickOnItemSize():
    # Removing all of the items from list once detected so that we can readd them again to prevent duplicates
    if (smallSizeDialogue in detectedOrderedItems):
        ClickOnItem(smallSizeMenu)
        print("SMALL SIZE DETECTED")
        detectedOrderedItems.remove(smallSizeDialogue)
    elif (mediumSizeDialogue in detectedOrderedItems):
        ClickOnItem(mediumSizeMenu)
        print("MEDIUM SIZE DETECTED")
        detectedOrderedItems.remove(mediumSizeDialogue)
    elif (largeSizeDialogue in detectedOrderedItems):
        ClickOnItem(largeSizeMenu)
        print("LARGE SIZE DETECTED")
        detectedOrderedItems.remove(largeSizeDialogue)

def GetAmountOfItems(region):
    try:
        for amount in itemAmounts:
            template = cv.imread(amount.image, cv.IMREAD_GRAYSCALE)
            template = cv.adaptiveThreshold(template, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
            resolution = cv.matchTemplate(region, template, cv.TM_CCOEFF_NORMED)
            locate = np.where(resolution >= amount.detectionThreshold)
            points = list(zip(*locate[::-1]))
            filteredPoints = []
            for point in points:
                if all(np.linalg.norm(np.array(point) - np.array(p)) >= 10 for p in filteredPoints):
                    filteredPoints.append(point)
            
            for point in filteredPoints:
                match amount.itemName:
                    case oneItemOrder.itemName:
                        return 1
                    case twoItemOrder.itemName:
                        return 2
                    
        return 1
    
    except Exception as e:
        tb = traceback.format_exc()
        print(f"An error occurred in GetAmountOfItems function: {e}\nTraceback: {tb}")
        
def GetGlobalItemCenterPosition(point, template, name, regionTopLeft):
    centerX = int(point[0] + template.shape[1] // 2 + regionTopLeft[0])
    centerY = int(point[1] + template.shape[0] // 2 + regionTopLeft[1])
    #print(f"{name} Global Center: ({centerX}, {centerY})")
    return (centerX, centerY)

def DetectElementInRegion(regionRgb, regionGray, itemsList):
    try:
        global currentOrderState
        
        regionAdaptiveThresh = cv.adaptiveThreshold(regionGray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
        for item in itemsList:
            template = cv.imread(item.image, cv.IMREAD_GRAYSCALE)
            template = cv.adaptiveThreshold(template, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
            w, h = template.shape[::-1]
            resolution = cv.matchTemplate(regionAdaptiveThresh, template, cv.TM_CCOEFF_NORMED)
            locate = np.where(resolution >= item.detectionThreshold)
            points = list(zip(*locate[::-1]))
            
            filteredPoints = []
            for point in points:
                if all(np.linalg.norm(np.array(point) - np.array(p)) >= 10 for p in filteredPoints):
                    filteredPoints.append(point)
                    break
        
            for point in filteredPoints:
                if (item not in detectedItems):
                    detectedItems.append(item)
                    item.positionOnScreen = GetGlobalItemCenterPosition(point, template, item.itemName, menuRegion[0:2])
                
                match item.itemType:                        
                    case ItemTypes.DIALOGUE_ITEM:
                        if (item not in detectedOrderedItems):
                            detectedOrderedItems.append(item)

                        # Get amount of items based on the dialogue item
                        match item.itemName:
                            case cheeseDialogue.itemName:
                                burgerCheeseItem.requestedAmount = GetAmountOfItems(regionGray[point[1]:point[1]+h, point[0]:point[0]+w])
                            case pattyMeatDialogue.itemName:
                                burgerPattyMeatItem.requestedAmount = GetAmountOfItems(regionGray[point[1]:point[1]+h, point[0]:point[0]+w])
                            case pattyVeganDialogue.itemName:
                                burgerPattyVeganItem.requestedAmount = GetAmountOfItems(regionGray[point[1]:point[1]+h, point[0]:point[0]+w])
                            case tomatoeDialogue.itemName:
                                burgerTomatoeItem.requestedAmount = GetAmountOfItems(regionGray[point[1]:point[1]+h, point[0]:point[0]+w])
                            case lettuceDialogue.itemName:
                                burgerLettuceItem.requestedAmount = GetAmountOfItems(regionGray[point[1]:point[1]+h, point[0]:point[0]+w])
                                            
                    case ItemTypes.MENU_ITEM:
                        if (item not in detectedMenuItems):
                            detectedMenuItems.append(item)
                                
                cv.rectangle(regionRgb, point, (point[0] + w, point[1] + h), item.outlineColor, 3)
                cv.putText(regionRgb, item.itemName, (point[0], point[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)            
                cv.circle(regionRgb, (point[0] + template.shape[1] // 2, point[1] + template.shape[0] // 2), 5, (255, 255, 255), 2)
        
    except Exception as e:
        tb = traceback.format_exc()
        print(f"An error occurred in DetectElementInRegion: {e}\nTraceback: {tb}")
        
def ProcessOrder():
    global currentOrderState
    
    if all(item.positionOnScreen != (0, 0) for item in detectedMenuItems):
        match currentOrderState:
            case OrderState.BURGER:
                # Add a extra check here so that it checks if the NPC has ordered a patty. This is to wait until the order loads.
                if any(item in detectedOrderedItems for item in [pattyMeatDialogue, pattyVeganDialogue, tomatoeDialogue, lettuceDialogue, cheeseDialogue]):
                    ClickOnItem(burgerBunBottomItem)
                    
                    if (pattyMeatDialogue in detectedOrderedItems):
                        ClickOnItem(burgerPattyMeatItem)
                    elif (pattyVeganDialogue in detectedOrderedItems):
                        ClickOnItem(burgerPattyVeganItem)
                    
                    if (cheeseDialogue in detectedOrderedItems):
                        ClickOnItem(burgerCheeseItem)
                    
                    if (lettuceDialogue in detectedOrderedItems):
                        ClickOnItem(burgerLettuceItem)
                    
                    if (tomatoeDialogue in detectedOrderedItems):
                        ClickOnItem(burgerTomatoeItem)
                    
                    
                    ClickOnItem(burgerBunTopItem)
                    
                    ClickOnItem(friesMenuButton)
                    currentOrderState = OrderState.FRIES
            case OrderState.FRIES:
                # Check if the fries order is in the detectedOrderedItems list, since theres still orders that we havent unlocked yet
                if any(item in detectedOrderedItems for item in [mozzarellaSticksOrder, normalFryOrder]):
                    if (normalFryOrder in detectedOrderedItems):
                        ClickOnItem(normalFriesItem)
                    if (mozzarellaSticksOrder in detectedOrderedItems):
                        print("Ms detected")
                        ClickOnItem(mozzarellaSicksItem)

                    ClickOnItemSize()
                    
                    ClickOnItem(drinkMenuButton)
                    currentOrderState = OrderState.DRINK
            case OrderState.DRINK:
                if (normalDrinkOrder in detectedOrderedItems):
                    if (normalDrinkOrder in detectedOrderedItems):
                        ClickOnItem(normalDrinkItem)

                    ClickOnItemSize()
                    
                ClickOnItem(menuFinishButton)
                currentOrderState = OrderState.FINISH
            case OrderState.FINISH:
                time.sleep(1)
                currentOrderState = OrderState.BURGER
                detectedOrderedItems.clear()
                return
        
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

isRunning = True

def keyInputDetection():
    global isRunning
    while isRunning:
        if keyboard.is_pressed("q"):
            isRunning = False
            break
        
        time.sleep(0.1)


def Main():
    TakeScreenshot()
    keyThread = threading.Thread(target=keyInputDetection)
    keyThread.start()

    try:
        while isRunning:
            cv.waitKey(1)
        
            TakeScreenshot()
            
            DetectElementInRegion(dialogueRgb, dialogueGray, dialogueItems)
            DetectElementInRegion(menuRgb, menuGray, menuItems)

            if (settings["aiViewEnabled"]):
                ShowWindow(dialogueRgb, dialogueWindowName, 400)
                ShowWindow(menuRgb, menuWindowName, 400)

            ProcessOrder()
            time.sleep(screenShotRate)

        cv.destroyAllWindows()
        
    except Exception as e:
        print(f"An error occurred: {e}")
#endregion
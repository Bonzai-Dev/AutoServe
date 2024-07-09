import FreeSimpleGUI as sg
import json
import re

import main

settingsJsonPath : str = r"settings.json"
with open (settingsJsonPath, "r") as f:  
    settings : json = json.load(f)

#region UI settings
font : str = "Helvetica"

sizeSmall : int = 10
sizeMedium : int= 12
sizeLarge : int = 14
sizeXLarge : int = 18

regionInputSize : tuple[int, int] = (20, 1) # Width, height
numberInputSize : tuple[int, int] = (7, 1) # Width, height

appVersion = 1.0
sg.theme('Dark Grey 2')

layout = [  
    [sg.Push(), sg.Text("AutoServe Control Panel", font=(font, sizeXLarge, "bold")), sg.Push()],
        
    [sg.Push(), sg.Frame("AutoServe Settings", [
        [sg.Text("Dialogue region", font=(font, sizeSmall)), sg.InputText(key="dialogueRegion", default_text=settings["dialogueRegion"], size=regionInputSize)],
        [sg.Text("Menu region", font=(font, sizeSmall)), sg.InputText(key="menuRegion", default_text=settings["menuRegion"], size=regionInputSize)],
        
        [sg.Text(" ", size=(1, 1))],
        
        [sg.Text("AI View Enabled", font=(font, sizeSmall)), sg.Checkbox("", key="aiViewEnabled", default=settings["aiViewEnabled"])]
    ], font=(font, sizeLarge)), sg.Push()],
    
    [sg.Text(" ", size=(1, 1))],
    
    [sg.Push(), sg.Frame("Items Detection Threshold", [
        [sg.Push(), sg.Text("Menu Items Buttons", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("Burger menu button", font=(font, sizeSmall)), sg.InputText(key="burgerMenuButtonDetectionThreshold", default_text=settings["burgerMenuButtonDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Fry menu button", font=(font, sizeSmall)), sg.InputText(key="friesMenuButtonDetectionThreshold", default_text=settings["friesMenuButtonDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Drink menu button", font=(font, sizeSmall)), sg.InputText(key="drinkMenuButtonDetectionThreshold", default_text=settings["drinkMenuButtonDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Finish menu button", font=(font, sizeSmall)), sg.InputText(key="menuFinishButtonDetectionThreshold", default_text=settings["menuFinishButtonDetectionThreshold"], size=numberInputSize)],
       
        [sg.Text("Bun menu top", font=(font, sizeSmall)), sg.InputText(key="burgerBunTopItemDetectionThreshold", default_text=settings["burgerBunTopItemDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Cheese menu", font=(font, sizeSmall)), sg.InputText(key="burgerCheeseItemDetectionThreshold", default_text=settings["burgerCheeseItemDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Vegan menu patty", font=(font, sizeSmall)), sg.InputText(key="burgerPattyVeganItemDetectionThreshold", default_text=settings["burgerPattyVeganItemDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Meat menu patty", font=(font, sizeSmall)), sg.InputText(key="burgerPattyMeatItemDetectionThreshold", default_text=settings["burgerPattyMeatItemDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Tomatoe menu", font=(font, sizeSmall)), sg.InputText(key="burgerTomatoeItemDetectionThreshold", default_text=settings["burgerTomatoeItemDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Lettuce menu", font=(font, sizeSmall)), sg.InputText(key="burgerLettuceItemDetectionThreshold", default_text=settings["burgerLettuceItemDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Bun menu bottom", font=(font, sizeSmall)), sg.InputText(key="burgerBunBottomItemDetectionThreshold", default_text=settings["burgerBunBottomItemDetectionThreshold"], size=numberInputSize)],
       
        [sg.Text("Fry normal menu", font=(font, sizeSmall)), sg.InputText(key="normalFriesItemDetectionThreshold", default_text=settings["normalFriesItemDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Mozzarella sticks menu", font=(font, sizeSmall)), sg.InputText(key="mozzarellaSicksItemDetectionThreshold", default_text=settings["mozzarellaSicksItemDetectionThreshold"], size=numberInputSize)],
        
        [sg.Text("Drink normal menu", font=(font, sizeSmall)), sg.InputText(key="normalDrinkItemDetectionThreshold", default_text=settings["normalDrinkItemDetectionThreshold"], size=numberInputSize)],
        
        [sg.Text(" ", size=(1, 1))],  # Adding a bit of vertical space
        
        [sg.Push(), sg.Text("Dialogue Items", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("Cheese order", font=(font, sizeSmall)), sg.InputText(key="cheeseDialogueDetectionThreshold", default_text=settings["cheeseDialogueDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Patty meat order", font=(font, sizeSmall)), sg.InputText(key="pattyMeatDialogueDetectionThreshold", default_text=settings["pattyMeatDialogueDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Patty vegan order", font=(font, sizeSmall)), sg.InputText(key="pattyVeganDialogueDetectionThreshold", default_text=settings["pattyVeganDialogueDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Tomatoe order", font=(font, sizeSmall)), sg.InputText(key="tomatoeDialogueDetectionThreshold", default_text=settings["tomatoeDialogueDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Lettuce order", font=(font, sizeSmall)), sg.InputText(key="lettuceDialogueDetectionThreshold", default_text=settings["lettuceDialogueDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Mozzarella sticks order", font=(font, sizeSmall)), sg.InputText(key="mozzarellaSticksOrderDetectionThreshold", default_text=settings["mozzarellaSticksOrderDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Normal fry order", font=(font, sizeSmall)), sg.InputText(key="normalFryOrderDetectionThreshold", default_text=settings["normalFryOrderDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Normal drink order", font=(font, sizeSmall)), sg.InputText(key="normalDrinkOrderDetectionThreshold", default_text=settings["normalDrinkOrderDetectionThreshold"], size=numberInputSize)],
        
        [sg.Text(" ", size=(1, 1))],  # Adding a bit of vertical space

        [sg.Push(), sg.Text("Items Amount", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("One item amount", font=(font, sizeSmall)), sg.InputText(key="oneItemOrderDetectionThreshold", default_text=settings["oneItemOrderDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Two item amount", font=(font, sizeSmall)), sg.InputText(key="twoItemOrderDetectionThreshold", default_text=settings["twoItemOrderDetectionThreshold"], size=numberInputSize)],
        
        [sg.Text(" ", size=(1, 1))],  # Adding a bit of vertical space
        
        [sg.Push(), sg.Text("Items Size", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("Small size menu", font=(font, sizeSmall)), sg.InputText(key="smallSizeMenuDetectionThreshold", default_text=settings["smallSizeMenuDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Medium size menu", font=(font, sizeSmall)), sg.InputText(key="mediumSizeMenuDetectionThreshold", default_text=settings["mediumSizeMenuDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Lage size menu", font=(font, sizeSmall)), sg.InputText(key="largeSizeMenuDetectionThreshold", default_text=settings["largeSizeMenuDetectionThreshold"], size=numberInputSize)],
        
        [sg.Text("Small size dialogue", font=(font, sizeSmall)), sg.InputText(key="smallSizeDialogueDetectionThreshold", default_text=settings["smallSizeDialogueDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Medium size dialogue", font=(font, sizeSmall)), sg.InputText(key="mediumSizeDialogueDetectionThreshold", default_text=settings["mediumSizeDialogueDetectionThreshold"], size=numberInputSize)],
        [sg.Text("Large size dialogue", font=(font, sizeSmall)), sg.InputText(key="largeSizeDialogueDetectionThreshold", default_text=settings["largeSizeDialogueDetectionThreshold"], size=numberInputSize), ],
        
    ], font=(font, sizeLarge)), sg.Push()],
    
    [sg.Text(" ", size=(1, 1))],
    
    [sg.Push(), sg.Button("Run Bot", font=(font, sizeSmall)), sg.Push()]
]

scrollableLayout = [
    [sg.Column(layout, scrollable=True, vertical_scroll_only=True, element_justification='center', justification='center')]
]
#endregion

# Create the Window
window = sg.Window(f"AutoServe v{appVersion}", scrollableLayout, icon=r"img\icons\AutoServe.ico")

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "Run Bot":  
        main.Main()
        
        allValuesValid = True
        for key in values:
            if key == "dialogueRegion" or key == "menuRegion":
                if not re.match(r'^\(\d+,\d+,\d+,\d+\)$', values[key].replace(" ", "")):
                    allValuesValid = False 
                    sg.popup_error(f'Invalid value for "{key}". Check the GitHub Wiki for more information.')
                    break
                
            elif key != "aiViewEnabled":
                try:
                    values[key] = float(values[key])
                except ValueError:
                    allValuesValid = False 
                    sg.popup_error(f'Invalid value for "{key}". Check the GitHub Wiki for more information.')
                    break 
    
        if allValuesValid: 
            with open(settingsJsonPath, "w") as f:
                json.dump(values, f, indent=4)
        
window.close()
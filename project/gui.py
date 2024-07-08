import FreeSimpleGUI as sg
import json

with open (r"project\settings.json", "r") as f:  
    settings : json = json.load(f)

font : str = "Helvetica"

# Font sizes
sizeSmall : int = 10
sizeMedium : int= 12
sizeLarge : int = 14
sizeXLarge : int = 18

inputSize : tuple[int, int] = (15, 1) # Width, height

appVersion = 1.0
sg.theme('Dark Grey 2')

layout = [  
    [sg.Push(), sg.Text("AutoServe Control Panel", font=(font, sizeXLarge, "bold")), sg.Push()],
        
    [sg.Push(), sg.Frame("AutoServe Settings", [
        [sg.Text("Dialogue region", font=(font, sizeSmall)), sg.InputText(key="DialogueRegion", default_text=tuple(settings["dialogueRegion"]), size=inputSize)],
        [sg.Text("Menu region", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=tuple(settings["menuRegion"]), size=inputSize)],
        
        [sg.Text(" ", size=(1, 1))],
        
        [sg.Text("AI View Enabled", font=(font, sizeSmall)), sg.Checkbox("", key="MenuRegion", default=settings["aiViewEnabled"])]
    ], font=(font, sizeLarge)), sg.Push()],
    
    [sg.Text(" ", size=(1, 1))],
    
    [sg.Push(), sg.Frame("Items Detection Threshold", [
        [sg.Push(), sg.Text("Menu Items Buttons", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("Burger menu button", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["burgerMenuButtonDetectionThreshold"], size=inputSize)],
        [sg.Text("Fry menu button", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["friesMenuButtonDetectionThreshold"], size=inputSize)],
        [sg.Text("Drink menu button", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["drinkMenuButtonDetectionThreshold"], size=inputSize)],
        [sg.Text("Finish menu button", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["menuFinishButtonDetectionThreshold"], size=inputSize)],
       
        [sg.Text("Bun menu top", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["burgerBunTopItemDetectionThreshold"], size=inputSize)],
        [sg.Text("Cheese menu", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["burgerCheeseItemDetectionThreshold"], size=inputSize)],
        [sg.Text("Vegan menu patty", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["burgerPattyVeganItemDetectionThreshold"], size=inputSize)],
        [sg.Text("Meat menu patty", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["burgerPattyMeatItemDetectionThreshold"], size=inputSize)],
        [sg.Text("Tomatoe menu", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["burgerTomatoeItemDetectionThreshold"], size=inputSize)],
        [sg.Text("Lettuce menu", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["burgerLettuceItemDetectionThreshold"], size=inputSize)],
        [sg.Text("Bun menu bottom", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["burgerBunBottomItemDetectionThreshold"], size=inputSize)],
       
        [sg.Text("Fry normal menu", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["normalFriesItemDetectionThreshold"], size=inputSize)],
        [sg.Text("Mozzarella sticks menu", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["mozzarellaSicksItemDetectionThreshold"], size=inputSize)],
        
        [sg.Text("Drink normal menu", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["normalDrinkItemDetectionThreshold"], size=inputSize)],
        
        [sg.Text(" ", size=(1, 1))],  # Adding a bit of vertical space
        
        [sg.Push(), sg.Text("Dialogue Items", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("Cheese order", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["cheeseDialogueDetectionThreshold"], size=inputSize)],
        [sg.Text("Patty meat order", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["pattyMeatDialogueDetectionThreshold"], size=inputSize)],
        [sg.Text("Patty vegan order", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["pattyVeganDialogueDetectionThreshold"], size=inputSize)],
        [sg.Text("Tomatoe order", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["tomatoeDialogueDetectionThreshold"], size=inputSize)],
        [sg.Text("Lettuce order", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["lettuceDialogueDetectionThreshold"], size=inputSize)],
        [sg.Text("Mozzarella sticks order", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["mozzarellaSticksOrderDetectionThreshold"], size=inputSize)],
        [sg.Text("Normal fry order", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["normalFryOrderDetectionThreshold"], size=inputSize)],
        [sg.Text("Normal drink order", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["normalDrinkOrderDetectionThreshold"], size=inputSize)],
        
        [sg.Text(" ", size=(1, 1))],  # Adding a bit of vertical space

        [sg.Push(), sg.Text("Items Amount", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("One item amount", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["oneItemOrderDetectionThreshold"], size=inputSize)],
        [sg.Text("Two item amount", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["twoItemOrderDetectionThreshold"], size=inputSize)],
        
        [sg.Text(" ", size=(1, 1))],  # Adding a bit of vertical space
        
        [sg.Push(), sg.Text("Items Size", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("Small size menu", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["smallSizeMenuDetectionThreshold"], size=inputSize)],
        [sg.Text("Medium size menu", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["mediumSizeMenuDetectionThreshold"], size=inputSize)],
        [sg.Text("Lage size menu", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["largeSizeMenuDetectionThreshold"], size=inputSize)],
        
        [sg.Text("Small size dialogue", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["smallSizeDialogueDetectionThreshold"], size=inputSize)],
        [sg.Text("Medium size dialogue", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["mediumSizeDialogueDetectionThreshold"], size=inputSize)],
        [sg.Text("Large size dialogue", font=(font, sizeSmall)), sg.InputText(key="MenuRegion", default_text=settings["largeSizeDialogueDetectionThreshold"], size=inputSize), ],
        
    ], font=(font, sizeLarge)), sg.Push()],
    
    [sg.Text(" ", size=(1, 1))],
    
    [sg.Push(), sg.Button("Run Bot", font=(font, sizeSmall)), sg.Push()]
]

scrollableLayout = [
    [sg.Column(layout, scrollable=True, vertical_scroll_only=True, element_justification='center', justification='center')]
]

# Create the Window
window = sg.Window(f"AutoServe v{appVersion}", scrollableLayout, finalize=True)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    print('You entered ', values[0])

window.close()
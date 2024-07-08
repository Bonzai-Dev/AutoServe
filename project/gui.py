import FreeSimpleGUI as sg

#region Functions   
#endregion

windowHeight : int = 500

font : str = "Helvetica"

# Font sizes
sizeSmall : int = 10
sizeMedium : int= 12
sizeLarge : int = 14
sizeXLarge : int = 18

inputSize : tuple[int, int] = (10, 1) # Width, height

appVersion = 1.0
sg.theme('Dark Grey 2')

# All the stuff inside window.
layout = [  
    [sg.Push(), sg.Text("AutoServe Control Panel", font=(font, sizeXLarge, "bold")), sg.Push()],
        
    [sg.Push(), sg.Frame("AutoServe Settings", [
        [sg.Text("Dialogue region", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Menu region", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        
        [sg.Text(" ", size=(1, 1))],
        sg.Checkbox("", default=True)
    ], font=(font, sizeLarge)), sg.Push()],
    
    [sg.Text(" ", size=(1, 1))],
    
    [sg.Push(), sg.Frame("Items Detection Threshold", [
        [sg.Push(), sg.Text("Menu Items Buttons", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("Burger menu button", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Fry menu button", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Drink menu button", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Finish menu button", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
       
        [sg.Text("Bun menu top", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Cheese menu", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Vegan menu patty", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Meat menu patty", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Tomatoe menu", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Lettuce menu", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Bun menu bottom", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
       
        [sg.Text("Fry normal menu", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Mozzarella sticks menu", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Drink normal menu", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        
        [sg.Text(" ", size=(1, 1))],  # Adding a bit of vertical space
        
        [sg.Push(), sg.Text("Dialogue Items", font=(font, sizeMedium, "bold")), sg.Push()],
        [sg.Text("Cheese order", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Patty meat order", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Patty vegan order", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Tomatoe order", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Lettuce order", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Mozzarella sticks order", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Normal fry order", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Normal drink order", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        
        [sg.Text(" ", size=(1, 1))],  # Adding a bit of vertical space

        [sg.Push(), sg.Text("Items Amount", font=(font, sizeSmall, "bold")), sg.Push()],
        [sg.Text("One item amount", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Two item amount", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        
        [sg.Text(" ", size=(1, 1))],  # Adding a bit of vertical space
        
        [sg.Push(), sg.Text("Items Size", font=(font, sizeSmall, "bold")), sg.Push()],
        [sg.Text("Small size menu", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Medium size menu", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Lage size menu", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        
        [sg.Text("Small size dialogue", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Medium size dialogue", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        [sg.Text("Large size dialogue", font=(font, sizeSmall)), sg.InputText(size=inputSize)],
        
    ], font=(font, sizeLarge)), sg.Push()],
    
    [sg.Push(), sg.Button("Run", font=(font, sizeSmall)), sg.Push()]
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
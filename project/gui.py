import overlay_lib
from overlay_lib import Vector2D, RgbaColor, SkDrawCircle

import FreeSimpleGUI as sg

#region Functions   
def DrawRectangle():
    overlay = overlay_lib.Overlay(
        drawlistCallback=[DrawRectangle(Vector2D(960, 540), 10, RgbaColor(255, 255, 255, 255), 1)],
        refreshTimeout=1
    )
    overlay.spawn()
#endregion

appVersion = 1.0
sg.theme('Dark Grey 2')

# All the stuff inside window.
layout = [  [sg.Text("Dialogue region"), sg.InputText()],
            [sg.Text("Menu region"), sg.InputText()],
            [sg.Button("Run")] ]

# Create the Window
window = sg.Window(f"AutoServe v{appVersion}", layout)
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    print('You entered ', values[0])

window.close()
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

import threading
import pygetwindow as gw

windowName = "Bloxburg cash farm control panel v.1.0"

Window.size = (400, 600)

class MainWindow(BoxLayout):
    def __init__(self):
        super().__init__()
        self.padding = 10
        self.spacing = 10

        # Apply a background
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Dark grey background
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[(10, 10)])
            self.bind(size=self._update_rect, pos=self._update_rect)

        #region Program settings
        self.isComputerViewEnabled = False
        self.currentProgramState = "Start"
        #endregion
        
        #region GUI
        self.orientation = 'vertical'
                
        self.settingsHeader = Label(text="Settings", font_size='20sp', size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.add_widget(self.settingsHeader)
        
        self.computerViewButton = ToggleButton(text=f"Computer view: {self.isComputerViewEnabled}", background_normal='', background_color=(0.3, 0.3, 0.8, 1))
        self.computerViewButton.bind(on_press=self.toggleComputerView)
        self.add_widget(self.computerViewButton)
        
        self.programExecutionHeader = Label(text="Program Execution", font_size='20sp', size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.add_widget(self.programExecutionHeader)
        
        self.toggleProgramExecutionButton = ToggleButton(text="Start", background_normal='', background_color=(0.537, 1, 0.275, 1))
        self.toggleProgramExecutionButton.bind(on_press=self.toggleProgramExecution)
        self.add_widget(self.toggleProgramExecutionButton)
        #endregion
        
    #region Event handlers
    def toggleComputerView(self, event):
        self.isComputerViewEnabled = not self.isComputerViewEnabled
        self.computerViewButton.text = f'Computer view: {self.isComputerViewEnabled}'
    
    def toggleProgramExecution(self, event):
        if self.toggleProgramExecutionButton.text == "Stop":
            self.toggleProgramExecutionButton.text = "Start"
            self.toggleProgramExecutionButton.background_color = (0.667, 0.922, 0.271)
        else:
            self.toggleProgramExecutionButton.text = "Stop"
            self.toggleProgramExecutionButton.background_color = (1, 0, 0)
    #endregion

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class Program(App):
    def build(self):
        self.title = windowName
        return MainWindow()

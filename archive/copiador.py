import pyWinhook
import pywin32
import pyautogui
import os
import time

# Set the destination folder path
destination_folder = 'C:\\Users\\glauc\\Desktop\\dest'

# Define a function to copy the current image and paste it into the destination folder
def copy_and_paste_image():
    # Use pyautogui to select the current image and copy it
    pyautogui.hotkey('ctrl', 'a')  # select the current image
    pyautogui.hotkey('ctrl', 'c')  # copy the selected image

    # Open the destination folder
    os.startfile(destination_folder)  # open the folder

    # Wait for the folder to open
    time.sleep(5)

    # Use pyautogui to paste the copied image into the destination folder
    pyautogui.hotkey('ctrl', 'v')  # paste the copied image

# Define a key press callback function
def on_key_press(event):
    # Check if the "1" key was pressed
    if event.Ascii == 49:
        copy_and_paste_image()

# Create a hook manager
hm = pyWinhook.HookManager()

# Register the key press callback function
hm.KeyDown = on_key_press

# Set the hook and start monitoring key presses
hm.HookKeyboard()

# Run the hook manager
pywin32.PumpMessages()

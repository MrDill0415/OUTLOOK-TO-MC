import pyautogui
import time
import os

def main():
    os.system('cls')
    print("==================================================")
    print("         ENI'S PIXEL CALIBRATION TOOL             ")
    print("==================================================")
    print("1. Open the Minecraft Launcher and MAXIMIZE it.")
    print("2. Hover your mouse over the button you need.")
    print("3. Read the X, Y coordinates below.")
    print("4. Update the COORDS in ui_automation.py.")
    print("--------------------------------------------------")
    print("Press Ctrl+C to exit.\n")

    try:
        while True:
            x, y = pyautogui.position()
            # The spaces at the end prevent ghost characters when numbers get shorter
            print(f"Current Position ->  X: {x} | Y: {y}        ", end="\r")
            time.sleep(0.5)
    except KeyboardInterrupt:
        last_x, last_y = pyautogui.position()
        print(f"\n\n[!] Stopped. Last position: ({last_x}, {last_y})")

if __name__ == "__main__":
    main()

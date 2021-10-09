from Libraries.Reciever import Reciever
import pyautogui

reciever = Reciever(timing=0)

last_move = -1
while True:
    mode, x, y, z = reciever.fetch_data()
    if last_move > 10:  # if its been 10 iterations since last move, disable pan
        pyautogui.mouseUp(button='middle')
        last_move = -1
        print('pan disabled')
    if abs(x) < 10:
        x = 0
    if abs(y) < 10:
        y = 0
    if abs(z) < 10:
        z = 0

    if x != 0 or y != 0 or z != 0:
        mx_current, my_current = pyautogui.position()
        mx_new = mx_current + int(((.71*x) + (-.71*z)) / 3)
        my_new = my_current + int(((.71*x) + (.71*z) + y) / 3)
        if last_move == -1:
            pyautogui.mouseDown(button='middle')
            print('pan enabled')
        last_move = 0
        pyautogui.moveTo(x=mx_new, y=my_new)
        print('moving..')
    elif last_move != -1:
        last_move = last_move + 1

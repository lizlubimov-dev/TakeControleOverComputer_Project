import socket
from time import sleep
import pyautogui
import io
import pynput
import screeninfo
import tkinter as tk
import threading

"3 ports are needed"
CHAR_SIZE_IN_BYTES = 1
INT_SIZE_IN_BYTES = 4
STR_CONVERTION = "utf-8"
INT_CONVERTION = "big"

def connect_to_server(port):
    SERVER_IP = "10.100.102.23"

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((SERVER_IP, port))

    return soc;

def keyboard_controle():
    SERVER_PORT = 32444
    global CHAR_SIZE_IN_BYTES
    global STR_CONVERTION
    
    soc = connect_to_server(SERVER_PORT)
    keyboard = pynput.keyboard.Controller()
    to_do = "unknown"
    while True:
        to_do = soc.recv(CHAR_SIZE_IN_BYTES).decode(STR_CONVERTION)
        """if shift_pressed:
            with keyboard.pressed(keyboard.key.shift):
                press_release_key(soc=soc, keyboard=keyboard, to_do=to_do, shift_pressed=shift_pressed)
                GGGGGGHHHHHHHGSSSAAAAAXXVVggggAAAADFFFFGGGGGDDDDDddd        \\
                PPPpppp
                103FDSSS"""
        if to_do == 'p':
            key = soc.recv(INT_SIZE_IN_BYTES)
            key = int.from_bytes(key, INT_CONVERTION)
            key = key_from_vk(key)
            keyboard.press(key)

        if to_do == 'r':
            key = soc.recv(INT_SIZE_IN_BYTES)
            key = int.from_bytes(key, INT_CONVERTION)
            key = key_from_vk(key)
            keyboard.release(key)
            


def key_from_vk(vk):
    for special_key in pynput.keyboard.Key:
        if special_key.value.vk == vk:
            return special_key

    return pynput.keyboard.KeyCode.from_vk(vk)
        
def share_screen():
    SERVER_PORT = 32445
    global INT_CONVERTION
    soc = connect_to_server(SERVER_PORT)
    
    while True:
        image = pyautogui.screenshot()
        buffer = io.BytesIO()
        image.save(buffer, format='png')
        num = soc.send(len(buffer.getvalue()).to_bytes(INT_SIZE_IN_BYTES, byteorder=INT_CONVERTION))
        num = soc.send(buffer.getvalue())
    
def mouse_controle():
    SERVER_PORT = 32446
    soc = connect_to_server(SERVER_PORT)
    
    global INT_SIZE_IN_BYTES
    global CHAR_SIZE_IN_BYTES
    global STR_CONVERTION
    global INT_CONVERTION
    
    client_mouse = pynput.mouse.Controller()    
    data_size = int.from_bytes(soc.recv(INT_SIZE_IN_BYTES), INT_CONVERTION)
    server_screen_bin = soc.recv(data_size)
    server_screen_tuple = bin_to_tuple(server_screen_bin)
    client_screen = (screeninfo.get_monitors()[0].width, screeninfo.get_monitors()[0].height)

    width_ratio = client_screen[0]/server_screen_tuple[0]
    height_ratio = client_screen[1]/server_screen_tuple[1]
    while True:
        to_do = soc.recv(CHAR_SIZE_IN_BYTES).decode(STR_CONVERTION)
        
        if to_do == 'm':
            data_size = int.from_bytes(soc.recv(INT_SIZE_IN_BYTES), INT_CONVERTION)
            server_position_bin = soc.recv(data_size)
            server_position_tuple = bin_to_tuple(server_position_bin)
            client_position = (server_position_tuple[0]*width_ratio, server_position_tuple[1]*height_ratio)
            client_mouse.position = client_position
        elif to_do == 'c':
            data_size = int.from_bytes(soc.recv(INT_SIZE_IN_BYTES), INT_CONVERTION)
            to_do = soc.recv(data_size).decode(STR_CONVERTION)
            
            if to_do == "lp":
                client_mouse.press(pynput.mouse.Button.left)
            elif to_do == "rp":
                client_mouse.press(pynput.mouse.Button.right)
            elif to_do == "lr":
                client_mouse.release(pynput.mouse.Button.left)
            elif to_do == "rr":
                client_mouse.release(pynput.mouse.Button.right)
        elif to_do == 's':
            data_size = int.from_bytes(soc.recv(INT_SIZE_IN_BYTES), INT_CONVERTION)
            scroll_info_bin = soc.recv(data_size)
            scroll_info_tuple = bin_to_tuple(scroll_info_bin)
            dx = scroll_info_tuple[0]
            dy = scroll_info_tuple[1]
            
            client_mouse.scroll(dx, dy)

def bin_to_tuple(bin_data):
    global STR_CONVERTION
    str_data = bin_data.decode(STR_CONVERTION)
    str_tuple_data = str_data.split(',')
    int_tuple_data = string_tuple_to_int_tuple(str_tuple_data)
    return int_tuple_data

def string_tuple_to_int_tuple(str_tup):
    i = 0
    int_tup = ()
    for st in str_tup:
        int_tup = int_tup + (int(st),)
        i += 1
    return int_tup

def computer_controle():
    threading.Thread(target=mouse_controle).start()
    threading.Thread(target=keyboard_controle).start()
    threading.Thread(target=share_screen).start()

root = tk.Tk()
root.geometry("500x375")
button = tk.Button(root,
                   text="start",
                   command=computer_controle)
button.pack()

root.mainloop()
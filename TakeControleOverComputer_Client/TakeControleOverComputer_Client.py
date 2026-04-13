from http import client
import socket
from time import sleep
import pyautogui
import io
import turtle
from pynput.mouse import Button, Controller
import screeninfo

"3 ports are needed"

def connect_to_server(port):
    SERVER_IP = "10.100.102.23"

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soc.connect((SERVER_IP, port))
    except ConnectionRefusedError:
        """label_file_name.set("An exception occured while connecting")"""
        return

    return soc;

def controle_keyboard(soc):
    pass

def screen_share():
    SERVER_PORT = 32445

    soc = connect_to_server(SERVER_PORT)

    while True:
        image = pyautogui.screenshot()
        buffer = io.BytesIO()
        image.save(buffer, format='png')

        soc.send(len(buffer.getvalue()).to_bytes(4, byteorder='big'))
        soc.sendall(buffer.getvalue())

        sleep(0.1)


def mouse_controle():
    SERVER_PORT = 32446
    soc = connect_to_server(SERVER_PORT)
    
    INT_SIZE_IN_BYTES = 4
    CHAR_SIZE_IN_BYTES = 1
    client_mouse = Controller()    
    data_size = int.from_bytes(soc.recv(INT_SIZE_IN_BYTES), "big")
    server_screen_bin = soc.recv(data_size)
    server_screen_tuple = bin_to_tuple(server_screen_bin)
    client_screen = (screeninfo.get_monitors()[0].width, screeninfo.get_monitors()[0].height)

    width_ratio = client_screen[0]/server_screen_tuple[0]
    height_ratio = client_screen[1]/server_screen_tuple[1]
    while True:
        to_do = soc.recv(CHAR_SIZE_IN_BYTES).decode("utf-8")
        
        if to_do == 'm':
            data_size = int.from_bytes(soc.recv(INT_SIZE_IN_BYTES), "big")
            server_position_bin = soc.recv(data_size)
            server_position_tuple = bin_to_tuple(server_position_bin)
            client_position = (server_position_tuple[0]*width_ratio, server_position_tuple[1]*height_ratio)
            client_mouse.position = client_position
        elif to_do == 'c':
            data_size = int.from_bytes(soc.recv(INT_SIZE_IN_BYTES), "big")
            to_do = soc.recv(data_size).decode("utf-8")
            
            if to_do == "lp":
                client_mouse.press(Button.left)
            elif to_do == "rp":
                client_mouse.press(Button.right)
            elif to_do == "lr":
                client_mouse.release(Button.left)
            elif to_do == "rr":
                client_mouse.release(Button.right)
        elif to_do == 's':
            data_size = int.from_bytes(soc.recv(INT_SIZE_IN_BYTES), "big")
            scroll_info_bin = soc.recv(data_size)
            scroll_info_tuple = bin_to_tuple(scroll_info_bin)
            dx = scroll_info_tuple[0]
            dy = scroll_info_tuple[1]
            
            client_mouse.scroll(dx, dy)

def bin_to_tuple(bin_data):
    str_data = bin_data.decode("utf-8")
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

mouse_controle()
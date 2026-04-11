import socket
from time import sleep
import pyautogui
import io

"3 ports are needed"

def connect_to_server(port):
    SERVER_IP = "127.0.0.1"

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soc.connect((SERVER_IP, port))
    except ConnectionRefusedError:
        label_file_name.set("An exception occured while connecting")
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
        image.save(buffer, format='jpeg')

        soc.send(len(buffer.getvalue()).to_bytes(4, byteorder='big'))
        soc.sendall(buffer.getvalue())

        sleep(0.1)


from asyncio.windows_events import NULL
import socket
from pynput import mouse
from pynput import keyboard
import tkinter as tk
from PIL import Image, ImageTk
import io
import screeninfo
import threading

HOST_IP = "10.100.102.23"
"3 ports are needed"
INT_SIZE_IN_BYTES = 4
STR_CONVERTION = "utf-8"
INT_BYTEORDER = "big"
INT_LENGTH = 4
CUR_IMG = NULL

def create_port_for_client(HOST_IP ,PORT):
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		soc.bind((HOST_IP, PORT))
	except:
		print("exception occured")
	soc.listen()
	client_socket, client_address = soc.accept()

	return client_socket

keyboard_socket = None

def keyboard_controle_prep():
	PORT = 32444
	global keyboard_socket
	keyboard_socket = create_port_for_client(HOST_IP, PORT)	

	with keyboard.Listener(
		on_press=on_key_press,
		on_release=on_key_release
		) as listener: listener.join()

def on_key_press(key):
	global keyboard_socket
	global STR_CONVERTION
	global INT_BYTEORDER
	global INT_LENGTH

	press_sign = 'p'
	keyboard_socket.send(press_sign.encode(STR_CONVERTION))
	
	try:
		message = key.vk
	except AttributeError:
		message = key.value.vk
	
	keyboard_socket.sendall(message.to_bytes(length=INT_LENGTH, byteorder=INT_BYTEORDER))

def on_key_release(key):
	global keyboard_socket
	global STR_CONVERTION
	global INT_BYTEORDER
	global INT_LENGTH
	press_sign = 'r'
	keyboard_socket.send(press_sign.encode(STR_CONVERTION)) 
	try:
		message = key.vk
	except AttributeError:
		message = key.value.vk
		
	keyboard_socket.sendall(message.to_bytes(length=INT_LENGTH, byteorder=INT_BYTEORDER))

def show_screen():
	PORT = 32445
	soc = create_port_for_client(HOST_IP, PORT)

	global INT_SIZE_IN_BYTES
	global INT_BYTEORDER
	SERVER_WIDTH_SIZE = screeninfo.get_monitors()[0].width
	SERVER_HEIGHT_SIZE = screeninfo.get_monitors()[0].height

	while True:
		data_size = soc.recv(INT_SIZE_IN_BYTES)
		data_size = int.from_bytes(data_size, byteorder=INT_BYTEORDER)
		screen_shot = bytearray()
		to_recieve = data_size
		while len(screen_shot) < data_size:
			packet = soc.recv(to_recieve)
			to_recieve -= len(packet)
			screen_shot.extend(packet)

		stream_img = io.BytesIO(screen_shot)
		pil_img = Image.open(stream_img)
		pil_img = resize_image(pil_img, SERVER_WIDTH_SIZE, SERVER_HEIGHT_SIZE)

S		tk_image = ImageTk.PhotoImage(pil_img)
		backgroundImage.config(image=tk_image)
		backgroundImage.image = tk_image
		window.update()

def resize_image(image, max_width, max_height):
	width, height = image.size
	ratio = min(max_width / width, max_height / height)
	new_size = (int(width * ratio), int(height * ratio))
	return image.resize(new_size)

mouse_socket = None

def mouse_controle_prep():
	PORT = 32446
	global mouse_socket
	global INT_SIZE_IN_BYTES
	global INT_BYTEORDER
	mouse_socket = create_port_for_client(HOST_IP, PORT)
	server_screen_tuple = (screeninfo.get_monitors()[0].width, screeninfo.get_monitors()[0].height)
	server_screen_bin = tuple_to_bin(server_screen_tuple)
	data_size = len(server_screen_bin).to_bytes(INT_SIZE_IN_BYTES, INT_BYTEORDER)

	mouse_socket.send(data_size)
	mouse_socket.send(server_screen_bin)

	with mouse.Listener(
		on_move=on_move,
		on_click=on_click,
		on_scroll=on_scroll
		) as listener: listener.join()

def tuple_to_bin(tuple_data):
	global STR_CONVERTION
	str_data = ','.join(str(val) for val in tuple_data)
	bin_data = str_data.encode(STR_CONVERTION)
	return bin_data

def on_move():
	global STR_CONVERTION
	global INT_BYTEORDER
	move_sign = 'm'
	server_mouse = mouse.Controller()
	server_position_tuple = server_mouse.position
	server_position_bin = tuple_to_bin(server_position_tuple)
	data_size = len(server_position_bin).to_bytes(INT_SIZE_IN_BYTES, INT_BYTEORDER)

	global mouse_socket
	mouse_socket.send(move_sign.encode(STR_CONVERTION))
	mouse_socket.send(data_size)
	mouse_socket.send(server_position_bin)

def on_click(x, y, button, pressed):
	click_sign = 'c'
	global INT_SIZE_IN_BYTES
	global STR_CONVERTION
	global INT_BYTEORDER

	side = button.name
	str_send = ""
	if side == "left":
		str_send = "l"
	else:
		str_send = "r"

	if pressed:
		str_send += "p"
	else:
		str_send += "r"

	data_size = len(str_send).to_bytes(INT_SIZE_IN_BYTES, INT_BYTEORDER)

	global mouse_socket
	mouse_socket.send(click_sign.encode(STR_CONVERTION))
	mouse_socket.send(data_size)
	mouse_socket.send(str_send.encode(STR_CONVERTION))

def on_scroll(x, y, dx, dy):
	global STR_CONVERTION
	global INT_BYTEORDER
	scroll_sign = 's'
	scroll_info_tuple = (dx,dy)
	scroll_info_bin = tuple_to_bin(scroll_info_tuple)
	data_size = len(scroll_info_bin).to_bytes(INT_SIZE_IN_BYTES, INT_BYTEORDER)

	global mouse_socket
	mouse_socket.send(scroll_sign.encode(STR_CONVERTION))
	mouse_socket.send(data_size)
	mouse_socket.send(scroll_info_bin)

def computer_controle():
	threading.Thread(target=mouse_controle_prep).start()
	threading.Thread(target=keyboard_controle_prep).start()
	threading.Thread(target=show_screen).start()
	"""listener.start()"""



window = tk.Tk()
"""window.attributes("-fullscreen", True)"""
window.geometry("500x375")
window.winfo_height = 100
window.title("Main Page")
window.configure(background="#C8E9F2")

backgroundImage = tk.Label(window)
backgroundImage.pack()

start_button = tk.Button(window,
						text = "Share screen",
						command=computer_controle,
                        anchor="center",
                        bd=3,
                        cursor="hand2",
                        disabledforeground="gray",
                        font=("Arial", 14),
                        height=2,
                        justify="center",
                        padx=10,
                        pady=5,
                        width=15,
                        wraplength=100,
                        background="gold")
start_button.pack()

window.mainloop()


import socket 
import RPi.GPIO as GPIO
import json
from time import *
import threading

config_file = {}
# def listen_socket(): 
#     while True: 
#         data = firstfloor.recv(1024)
#         if not data:
#             print('Message not received')
             
#             break
#     time.sleep(1)

def load_config():
    config_file = open('config_second_floor.json')
    config_file = json.load(config_file)
    print(config_file)
    GPIO.setmode(GPIO.BCM)

    for output in config_file['output']: 
        GPIO.setup(output['porta'], GPIO.OUT)

    for inp in config_file['input']: 
        GPIO.setup(inp['porta'], GPIO.IN)
    return config_file

# def socket_init():
#     global firstfloor
#     ip = config_file["ip_central"]
#     port = config_file["porta_central"]
#     addr = (ip,port)
#     while(True): 
#         try: 
#             print("Iniciando conexão do socket")
#             firstfloor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#             firstfloor.connect(addr)  
#             break
#         except: 
#             time.sleep(1)

def read_status(config_file): 
    while(True): 
        if GPIO.input(config_file['input'][1]["porta"]) == GPIO.HIGH or GPIO.input(config_file['input'][1]["porta"]) == GPIO.HIGH:
            verificar_ordem_sensores(config_file)


def verificar_ordem_sensores(config_file):
    if GPIO.input(config_file['input'][1]["porta"]) == GPIO.HIGH:
        print("Carro subindo do 1º para o 2º andar")
    elif GPIO.input(config_file['input'][2]["porta"]) == GPIO.HIGH:
        print("Carro descendo do 2º para o 1º andar")

def open_gate(config_file):
    print(config_file)
    GPIO.output(config_file["output"][4]["porta"], GPIO.HIGH)
    sleep(5)
    GPIO.output(config_file["output"][4]["porta"], GPIO.LOW)

# def calculate_number_people_entering(pin):
#   global start_time_entering, end_time_entering, qtd_pessoas
#   start_time_entering = time.time()
#   while(1):
#     tmp = GPIO.input(pin)
#     if(tmp == 0):
#       end_time_entering = time.time()
#       full_time = end_time_entering - start_time_entering
#       qtd_pessoas += round(full_time/0.2)
#       break
#     else:
#       time.sleep(0.1)

# def count_entering_people():
#   global config_data
#   entering_pin = config_data["inputs"][4]["gpio"]
#   GPIO.add_event_detect(entering_pin, GPIO.RISING, callback=lambda x: calculate_number_people_entering(entering_pin))


# def count_leaving_people():
#   global  config_data
#   leaving_pin = config_data["inputs"][5]["gpio"]
#   GPIO.add_event_detect(leaving_pin, GPIO.RISING, callback=lambda x: calculate_number_people_leaving(leaving_pin))

def count_number_cars(): 
    pass

def format_message(): 
    pass

def main():
    config_file = load_config()
    #socket_init()
    read_status(config_file)

main()
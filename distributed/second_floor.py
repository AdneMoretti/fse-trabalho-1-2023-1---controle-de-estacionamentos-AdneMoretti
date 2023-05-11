import socket 
import RPi.GPIO as GPIO
import json
import time
from threading import Thread
from uuid import uuid4

response_message = {
    "value": 0,
    "vaga": -1, 
    "id":1
}

entering_message = {
    "qtd_cars": 0, 
    "id": 0, 
    "gate": 0
}

state = []
car_id = ""
qtd_cars = 0
start_time_entering = 0
vaga = 0

def initialize_response(): 
    global state
    for i in range(8):
        state.append({"state":0})

# def listen_socket(): 
#     while True: 
#         data = firstfloor.recv(1024)
#         if not data:
#             print(data)
#             print('Message not received')
             
#             break
#     time.sleep(1)
def send_gate(): 
    data_new = json.dumps(entering_message).encode()
    firstfloor.send(data_new)
    
def send_socket(): 
   data = (json.dumps(create_message()))
   data = data.encode()
   firstfloor.send(data)
    
def load_config():
    global config_file
    config_file = open('config_first_floor.json')
    config_file = json.load(config_file)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    for output in config_file['output']: 
        GPIO.setup(output['gpio'], GPIO.OUT)

    for inp in config_file['input']: 
        GPIO.setup(inp['gpio'], GPIO.IN)

def socket_init():
    global firstfloor
    ip = config_file["ip_central"]
    port = int(config_file["porta_central"])
    addr = (ip,port)
    while(True): 
        try: 
            print("Iniciando conexão do socket")
            firstfloor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            firstfloor.connect(addr)  
            print("connected")
            break
        except: 
            time.sleep(1)

def vacancy_monitor():
    global config_file, car_id, vaga, state
    while(True):
        counter = 0
        gpio = [config_file["output"][0]["gpio"], config_file["output"][1]["gpio"],config_file["output"][2]["gpio"]]
        while counter < 8:
            GPIO.output(gpio, (
                GPIO.HIGH if counter & 0b0100 else GPIO.LOW ,
                GPIO.HIGH if counter & 0b0010 else GPIO.LOW,
                GPIO.HIGH if counter & 0b0001 else GPIO.LOW,
                )
            )
            time.sleep(0.1)
            entering = config_file["input"][0]["gpio"]
            if(GPIO.input(entering)==1 and state[counter]["state"]==0):
                state[counter]["state"] = 1
                response_message["vaga"] = vaga
                send_socket()
                response_message["vaga"] = -1

            elif(GPIO.input(entering)==0 and state[counter]["state"]==1):
                state[counter]["state"] = 0
                response_message["vaga"] = vaga
                send_socket()
            # GPIO.add_event_detect(entering, GPIO.RISING, callback=lambda x: add_id_to(counter))
            counter += 1
            time.sleep(0.1)

def calculate_number_people_entering(pin):
    global config_file, qtd_cars
    global start_time_entering
    GPIO.output(config_file["output"][4]["gpio"], GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(config_file["output"][4]["gpio"], GPIO.LOW)
    # qtd_cars+=1
    entering_message["qtd_cars"]+=1
    send_gate(qtd_cars)

def calculate_number_people_leaving(pin):
    print("estou aqui")
    global config_file, qtd_cars, response_message, vaga
    global end_time_entering
    GPIO.output(config_file["output"][5]["gpio"], GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(config_file["output"][5]["gpio"], GPIO.LOW)
    # exit_time = time.time()
    # # car_value = round(((exit_time - state[vaga]["time"])/60)*0.15)
    # car_value = round((((exit_time - state[vaga]["time"])/60)*0,15))
    # qtd_cars-=1
    entering_message["qtd_cars"] -= 1
    # response_message["value"] += round(car_value, 2)
    send_gate(qtd_cars)

def count_enter_cars():
    global config_file
    entering_pin = config_file["input"][1]["gpio"]
    leaving_pin = config_file["input"][3]["gpio"]
    GPIO.add_event_detect(entering_pin, GPIO.RISING, callback=lambda x: calculate_number_people_entering(entering_pin))
    GPIO.add_event_detect(leaving_pin, GPIO.RISING, callback=lambda x: calculate_number_people_leaving(leaving_pin))

def create_message(): 
    global response_message,state
    response_message["cars"] = qtd_cars
    response_message["state"] = state
    return response_message

def main():
    global config_file
    load_config()
    initialize_response()
    socket_thread = Thread(target=socket_init, args=())
    socket_thread.start()
    monitoring = Thread(target=vacancy_monitor, args=())
    monitoring.start()
    count_thread = Thread(target=count_enter_cars, args=())
    count_thread.start()
    

main()
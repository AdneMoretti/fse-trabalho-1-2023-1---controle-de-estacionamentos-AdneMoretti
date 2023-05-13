import socket 
import RPi.GPIO as GPIO
import json
import time
from threading import Thread
from uuid import uuid4

response_message = {
    "value": 0,
    "vaga": -1, 
    "id":2
}

entering_message = {
    "id": 3, 
    "gate": 0
}

state = []
car_id = ""
start_time_entering = 0
vaga = 0
first_sensor = 0
second_sensor = 0

def initialize_response(): 
    global state
    for i in range(8):
        state.append({"state":0})

def listen_socket(): 
    while True: 
        data = firstfloor.recv(1024)
        if not data:
            print(data)
            print('Message not received')
            
            break
        else: 
            received_message = data.decode('utf-8')
            received_message = json.loads(received_message)
            execute_command(received_message)
                
        time.sleep(1)
        firstfloor.close()

def execute_command(received_message): 
    lotado = config_file["output"][3]["gpio"]
    if received_message["SINAL_DE_LOTADO_FECHADO_2"] == 0:
        GPIO.output(lotado, GPIO.HIGH)
    elif received_message["SINAL_DE_LOTADO_FECHADO_2"] == 0:
        GPIO.output(lotado, GPIO.LOW)

def send_gate(): 
    data_new = json.dumps(entering_message).encode()
    firstfloor.send(data_new)
    
def send_socket(): 
    global response_message
    data = (json.dumps(response_message))
    data = data.encode()
    firstfloor.send(data)
    
def load_config():
    global config_file
    config_file = open('config_second_floor.json')
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
    global config_file, car_id, start_time_entering, vaga,state
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
            entering = GPIO.input(config_file["input"][0]["gpio"])
            if(entering==1 and state[counter]["state"]==0):
                state[counter]["state"] = 1
                response_message["vaga"] = counter
                print("carro entrou na vaga")
                send_socket()

            elif(entering==0 and state[counter]["state"]==1):
                state[counter]["state"] = 0
                response_message["vaga"] = counter
                send_socket()
            # GPIO.add_event_detect(entering, GPIO.RISING, callback=lambda x: add_id_to(counter))
            counter += 1

def calculate_qtd_cars_entering(pin):
    global entering_message
    entering_message["gate"]=1
    send_gate()

# def close_cancel(pin):
#     GPIO.output(pin, GPIO.LOW)

# def close_cancel_leave(pin): 
#     GPIO.output(pin, GPIO.LOW)

def calculate_qtd_cars_leaving(pin):
    global entering_message
    entering_message["gate"]=0
    send_gate()

def calculating_time_first(): 
    global first_sensor
    first_sensor = time.time()

def calculating_time_second(): 
    global second_sensor
    second_sensor = time.time()

def count_enter_cars():
    global config_file
    print("aqui")
    first_pin = config_file["input"][1]["gpio"]
    second_pin = config_file["input"][2]["gpio"]
    GPIO.add_event_detect(first_pin, GPIO.RISING, callback=lambda x: calculating_time_first())
    GPIO.add_event_detect(second_pin, GPIO.RISING, callback=lambda x: calculating_time_second())
    if(second_sensor>first_sensor): 
        calculate_qtd_cars_entering()
    else: 
        calculate_qtd_cars_leaving()


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
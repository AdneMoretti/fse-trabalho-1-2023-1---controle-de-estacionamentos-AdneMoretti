import socket 
import RPi.GPIO as GPIO
import json
import time
from threading import Thread

response_message = {
    "value": 0,
    "vaga": -1, 
    "id": 1
}

entering_message = {
    "id": 0, 
    "gate": 0, 
    "state": []
}

state = []
received_message = {}

def initialize_response(): 
    global state
    for _ in range(8):
        state.append({"state": 0})
    response_message["state"] = state

# Socket para receber dados do servidor central
def listen_socket(): 
    global first_floor_socket
    while True: 
        data = first_floor_socket.recv(1024)
        if not data:
            print(data)
            print('Message not received')
            break
        else: 
            received_message = data.decode('utf-8')
            received_message = json.loads(received_message)
            execute_command(received_message)
    time.sleep(1)
    first_floor_socket.close()

# Executa os comandos recebidos do central
def execute_command(received_message): 
    lotado = config_file["output"][3]["gpio"]
    if received_message["SINAL_DE_LOTADO_FECHADO_1"] == 1:
        GPIO.output(lotado, GPIO.HIGH)
    elif received_message["SINAL_DE_LOTADO_FECHADO_1"] == 0:
        GPIO.output(lotado, GPIO.LOW)

# def send_gate(): 
#     data_new = json.dumps(entering_message).encode()
#     first_floor_socket.send(data_new)
    
def send_socket(message): 
    try:
        data = (json.dumps(message))
        data = data.encode()
        first_floor_socket.send(data)
    except:
        print("Erro ao tentar enviar mensagem")
        first_floor_socket.close()
        socket_init()

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
    global first_floor_socket
    ip = config_file["ip_central"]
    port = int(config_file["porta_central"])
    addr = (ip, port)
    while(True): 
        try: 
            print("Iniciando conexão do socket")
            first_floor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            first_floor_socket.connect(addr)  
            print("Connected")
            break
        except: 
            time.sleep(1)

def vacancy_monitor():
    global config_file, state, response_message
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
                send_socket(response_message)

            elif(entering==0 and state[counter]["state"]==1):
                state[counter]["state"] = 0
                response_message["vaga"] = counter
                send_socket(response_message)
            counter += 1

def calculate_qtd_cars_entering(pin):
    global config_file, entering_message
    print("entrei aqui")
    motor = config_file["output"][4]["gpio"]
    GPIO.output(motor, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(motor, GPIO.LOW)
    # pin = config_file["input"][2]["gpio"]
    # GPIO.add_event_detect(pin, GPIO.RISING, callback=lambda x: close_cancel(motor))
    entering_message["gate"]=1
    send_socket(entering_message)

# def close_cancel(pin):
#     GPIO.output(pin, GPIO.LOW)

# def close_cancel_leave(pin): 
#     GPIO.output(pin, GPIO.LOW)

def calculate_qtd_cars_leaving(pin):
    print("estou aqui")
    global config_file, entering_message
    global end_time_entering
    motor = config_file["output"][5]["gpio"]
    GPIO.output(motor, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(motor, GPIO.LOW)

    # pin = config_file["input"][4]["gpio"]
    # motor = config_file["output"][5]["gpio"]
    # GPIO.add_event_detect(pin, GPIO.RISING, callback=lambda x: close_cancel_leave(motor))
    entering_message["gate"]=0
    send_socket(entering_message)

def count_cars():
    global config_file
    entering_pin = config_file["input"][1]["gpio"]
    leaving_pin = config_file["input"][3]["gpio"]
    GPIO.add_event_detect(entering_pin, GPIO.RISING, callback=lambda x: calculate_qtd_cars_entering(entering_pin))
    GPIO.add_event_detect(leaving_pin, GPIO.RISING, callback=lambda x: calculate_qtd_cars_leaving(leaving_pin))

def main():
    global config_file
    load_config()
    initialize_response()
    socket_thread = Thread(target=socket_init, args=())
    socket_thread.start()
    count_thread = Thread(target=count_cars, args=())
    count_thread.start()
    monitoring = Thread(target=vacancy_monitor, args=())
    monitoring.start()
    listen_socket()

main()
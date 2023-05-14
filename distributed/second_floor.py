import socket 
import RPi.GPIO as GPIO
import json
import time
from threading import Thread

response_message = {
    "value": 0,
    "vaga": -1, 
    "id": 2
}

entering_message = {
    "id": 3, 
    "gate": 0
}

state = []
first_sensor = 0
second_sensor = 0


def initialize_response(): 
    global state
    for _ in range(8):
        state.append({"state":0})
        response_message["state"] = state

def listen_socket(): 
    while True: 
        data = second_floor_socket.recv(1024)
        if not data:
            print('Message not received')
            break
        else: 
            received_message = data.decode('utf-8')
            received_message = json.loads(received_message)
            print(received_message)
            execute_command(received_message)
                
    time.sleep(1)
    second_floor_socket.close()

def execute_command(received_message): 
    lotado = config_file["output"][3]["gpio"]
    if received_message["SINAL_DE_LOTADO_FECHADO_2"] == 1:
        GPIO.output(lotado, GPIO.HIGH)
    elif received_message["SINAL_DE_LOTADO_FECHADO_2"] == 0:
        GPIO.output(lotado, GPIO.LOW)

def send_socket(message): 
    try:
        data = (json.dumps(message))
        data = data.encode()
        second_floor_socket.send(data)
    except:
        print("Erro ao tentar enviar mensagem")
        second_floor_socket.close()
        socket_init()
    
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
    global second_floor_socket
    ip = config_file["ip_central"]
    port = int(config_file["porta_central"])
    addr = (ip, port)
    while(True): 
        try: 
            print("Iniciando conexão do socket")
            second_floor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            second_floor_socket.connect(addr)  
            print("Socket conectado")
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
                print(response_message)
                send_socket(response_message)

            elif(entering==0 and state[counter]["state"]==1):
                state[counter]["state"] = 0
                response_message["vaga"] = counter
                print(response_message)
                send_socket(response_message)
            counter += 1

def calculate_qtd_cars_entering():
    global entering_message
    entering_message["gate"]=1
    send_socket(entering_message)
    time.sleep(2)

def calculate_qtd_cars_leaving():
    global entering_message
    entering_message["gate"]=0
    send_socket(entering_message)
    time.sleep(2)

def count_cars():
    global config_file
    first_pin = config_file["input"][1]["gpio"]
    second_pin = config_file["input"][2]["gpio"]
    while(True):
        if(GPIO.input(first_pin) and not GPIO.input(second_pin)): 
            print("Subindo")
            calculate_qtd_cars_entering()
        if(not GPIO.input(first_pin) and GPIO.input(second_pin)): 
            print("Descendo")
            calculate_qtd_cars_leaving()

def main():
    global config_file
    load_config()
    initialize_response()
    socket_thread = Thread(target=socket_init, args=())
    socket_thread.start()
    monitoring = Thread(target=vacancy_monitor, args=())
    monitoring.start()
    count_thread = Thread(target=count_cars, args=())
    count_thread.start()
    listen_socket()

if __name__ == '__main__': 
    main()
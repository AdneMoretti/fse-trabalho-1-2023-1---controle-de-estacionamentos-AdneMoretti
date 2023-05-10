import socket 
import RPi.GPIO as GPIO
import json
import time
from threading import Thread
from uuid import uuid4

response_message = {
    "value": 0,
    "status": []
}
status = []
car_id = ""
qtd_cars = 0
start_time_entering = 0
vaga = 0

def initialize_response(): 
    global status
    for i in range(8):
        status.append({"ocupada":0, "id": "", "time": 0})

def listen_socket(): 
    while True: 
        data = firstfloor.recv(1024)
        if not data:
            print('Message not received')
             
            break
    time.sleep(1)

def load_config():
    global config_file
    config_file = open('config_first_floor.json')
    config_file = json.load(config_file)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    for output in config_file['output']: 
        GPIO.setup(output['porta'], GPIO.OUT)

    for inp in config_file['input']: 
        GPIO.setup(inp['porta'], GPIO.IN)

def socket_init():
    global firstfloor
    ip = config_file["ip_central"]
    port = config_file["porta_central"]
    addr = (ip,port)
    while(True): 
        try: 
            print("Iniciando conexão do socket")
            firstfloor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            firstfloor.connect(addr)  
            break
        except: 
            time.sleep(1)


def vacancy_monitor():
    global config_file, car_id, start_time_entering, vaga
    while(True):
        counter = 0
        gpio = [config_file["output"][0]["porta"], config_file["output"][1]["porta"],config_file["output"][2]["porta"]]
        while counter < 8:
            GPIO.output(gpio, (
                GPIO.HIGH if counter & 0b0100 else GPIO.LOW ,
                GPIO.HIGH if counter & 0b0010 else GPIO.LOW,
                GPIO.HIGH if counter & 0b0001 else GPIO.LOW,
                )
            )
            time.sleep(0.1)
            entering = config_file["input"][0]["porta"]
            if(GPIO.input(entering)==1 and status["status"][counter]["ocupada"]==0):
                status[counter]["id"] = car_id
                status[counter]["time"] = start_time_entering
                status[counter]["ocupada"] = 1

            elif(GPIO.input(entering)==0 and status["status"][counter]["ocupada"]==1):
                status[counter]["id"] = ""
                status[counter]["ocupada"] = 0
                status[counter]["time"] = start_time_entering
                vaga = counter
            # GPIO.add_event_detect(entering, GPIO.RISING, callback=lambda x: add_id_to(counter))
            counter += 1
            time.sleep(0.1)



def calculate_number_people_entering(pin):
    global config_file, qtd_cars
    global start_time_entering
    GPIO.output(config_file["output"][4]["porta"], GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(config_file["output"][4]["porta"], GPIO.LOW)
    # GPIO.output(config_file["output"][4]["porta"], GPIO.LOW)
    print("aqui")
    start_time_entering = time.time()
    qtd_cars+=1
    # while(True): 
    #     if(GPIO.input(pin)==0):
    #         qtd_cars+=1
    #         break
    print(qtd_cars)

def calculate_number_people_leaving(pin):
    global config_file, qtd_cars, response_message
    global end_time_entering
    GPIO.output(config_file["output"][5]["porta"], GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(config_file["output"][5]["porta"], GPIO.LOW)
    exit_time = time.time()
    car_value = exit_time - status[vaga]["time"]
    response_message["value"]+=car_value
    # while(True): 
    #     if(GPIO.input(pin)==0):
    #         qtd_cars-=1
    #         break
    qtd_cars-=1
    print(qtd_cars)


def count_enter_cars():
    global config_file
    entering_pin = config_file["input"][1]["porta"]
    leaving_pin = config_file["input"][3]["porta"]
    # while(True):
        # if(GPIO.input(entering_pin)==1):
        #     GPIO.output(config_file["output"][4]["porta"], GPIO.HIGH)
        #     car_id = uuid4()
        # if(GPIO.input(config_file['input'][2]["porta"])==1):
        #     GPIO.output(config_file["output"][4]["porta"], GPIO.LOW)
        #     calculate_number_people_entering(config_file["input"][2]["porta"])

    GPIO.add_event_detect(entering_pin, GPIO.RISING, callback=lambda x: calculate_number_people_entering(entering_pin))
    GPIO.add_event_detect(leaving_pin, GPIO.RISING, callback=lambda x: calculate_number_people_leaving(leaving_pin))

def create_message(): 
    response_message["cars"] = qtd_cars

def main():
    global config_file
    load_config()
    initialize_response()
    # socket_thread = Thread(sockset_init(), args=)
    monitoring = Thread(target=vacancy_monitor, args=())
    monitoring.start()
    count_thread = Thread(target=count_enter_cars, args=())
    count_thread.start()
    

main()
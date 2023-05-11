import socket
import sys
from threading import Thread
import json
import time
from uuid import uuid4

total_value = 0
message_1 = {
    "cars": 0
}
message_2 = {
    "cars": 0
}
qtd_cars = 0
qtd_cars_2 = 0
car_id = ""
entering_time = 0
parking_1 = 0
parking_2 = 0
command = {}

def present_menu(): 
    while(True):
        print("----------------- Menu --------------\n"+
        "1. Fechar o estacionamento\n"+
        "2. Ativar o sinal de Lotado\n"+
        "3. Desativar o sinal de lotado\n"
        "4. Bloquear o segundo andar\n"+
        "5. Sair")
        # option = int(input())
        # if(option==5): 
        #     break


def show_states(): 
    global qtd_cars, qtd_cars_2, parking_1, parking_2
    print("\n------------------States ----------------\n")
    print(f"Valor total pago: {total_value}")
    print(f"Quantidade de carros no estacionamento: {qtd_cars}")
    print("1º andar:\n"+
        f"Quantidade de vagas disponíveis: {8-parking_1}\n"+
        f"Quantidade de carros: {qtd_cars - qtd_cars_2}\n")
    print("2º andar:\n " +
          f"Quantidade de vagas disponíveis: {8-parking_2}"+
          f"Quantidade de carros: {qtd_cars_2}")


# def calculate_exit_time(): 
#     global total_value
#     vaga =  message_1["vaga"]
#     vaga2 = message_2["vaga"]

    # if(vaga!=-1 and message_1["status"][vaga]["ocupada"]==0):
    #     exit = time.time()
    #     total_value += exit - message_1["status"][vaga]["time"]

    # elif(vaga2!=-1 and message_2["status"][vaga]["ocupada"]==1):  
    #     message_2["status"][vaga]["time"] = message_1["car_entering_time"]

    # elif(vaga!=-1 and message_1["status"][vaga]["ocupada"]==1):
    #     message_1["status"][vaga]["time"] = message_1["car_entering_time"]

    # elif(vaga2!=-1 and message_2["status"][vaga]["ocupada"]==0):  
    #     total_value += exit - message_1["status"][vaga]["time"]
def check_first_floor(): 
    global car_id, entering_time, total_value
    vaga = message_1["vaga"]
    if(message_1["state"][vaga]["state"]==0): 
        parking_1-=1
        print("Carro saiu na vaga do segundo andar")
        total_time = time.time() - message_1["state"][vaga]["entering_time"]
        total_value += round((total_time/60)*0.15, 3)
    else: 
        print("carro entrou na vaga do primeiro andar")
        parking_1 += 1
        message_1["state"][vaga]["entering_time"] = entering_time
        message_1["state"][vaga]["car_id"] = entering_time

def check_second_floor(): 
    global car_id, entering_time
    vaga = message_2["vaga"]
    if(message_2["state"][vaga]["state"]==0): 
        parking_2-=1
        print("Carro saiu da vaga do segundo andar")
        total_time = time.time() - message_2["state"][vaga]["entering_time"]
        total_value += round((total_time/60)*0.15, 3)
    else: 
        parking_2+=1
        print("carro entrou na vaga do segundo andar")
        message_2["state"][vaga]["entering_time"] = entering_time
        message_2["state"][vaga]["car_id"] = entering_time

def receive(conection): 
    global message_1, message_2, qtd_cars, qtd_cars_2, car_id, entering_time
    while(True): 
        data = conection.recv(2048)
        data = json.loads(data.decode())
        if data["id"] == 1:
            message_1 = data
            check_first_floor()

        elif data["id"] == 2:
            message_2 = data
            check_second_floor()

        elif data["id"] == 0:
            qtd_cars = data["qtd_cars"]
            if(data["gate"]==1): 
                car_id = uuid4()
                entering_time = time.time()

        elif data["id"] == 3:
            qtd_cars_2 = data["qtd_cars"]

        if not data:
            print('Message not received')
            break

def send(connection, addr): 
    global command
    command_socket = json.dumps(command)

def socket_init(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = host, port
    server.bind(addr)
    server.listen()
    print("Iniciando conexao")
    while True:
        conn, addr = server.accept() 
        listen_thread = Thread(target=receive, args=(conn, addr ))
        listen_thread.start()
        send_thread = Thread(target=show_states, args=())
        send_thread.start()

def main(): 
    host = sys.argv[1]
    port = int(sys.argv[2])
    server_socket_1 = Thread(target=socket_init, args=(host, port))
    server_socket_1.start()

if __name__ == '__main__': 
    main()
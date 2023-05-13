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
command = {
    "SINAL_DE_LOTADO_FECHADO_1": 0,
    "SINAL_DE_LOTADO_FECHADO_2": 0
}
times = []

def initialize_times():
    global times
    for _ in range(8):
        times.append({"car_id":"", "entering_time": 0})

def present_menu(conn, addr): 
    global qtd_cars, qtd_cars_2
    while(True):
        print("----------------- Menu --------------\n"+
        "1. Fechar o estacionamento\n"+
        "2. Abrir o estacionamento\n"+
        "3. Bloquear segundo andar\n"+
        "4. Desbloquar segundo andar\n"+
        "5.Ver status do estacionamento\n"
        "6. Sair")
        option = int(input())
        if option == 6: 
            break
        elif option == 1 and command["SINAL_DE_LOTADO_FECHADO_1"] == 0:
            command["SINAL_DE_LOTADO_FECHADO_1"] = 1
        elif option == 2 and command["SINAL_DE_LOTADO_FECHADO_1"] == 0: 
            if(qtd_cars<16):
                command["SINAL_DE_LOTADO_FECHADO_1"] = 0
            else: 
                print("Estacionamento já está lotado")
        elif option == 3:
            command["SINAL_DE_LOTADO_FECHADO_2"] = 1
        elif option == 4:
            if(qtd_cars_2<8):
                command["SINAL_DE_LOTADO_FECHADO_2"] = 0
            else: 
                print("Andar 2 já está lotado")
        elif(option==5): 
            show_states()
        send(conn, addr)

def show_states(): 
    global qtd_cars, qtd_cars_2, parking_1, parking_2
    print("\n------------------States ----------------\n")
    print(f"Valor total pago: {total_value}")
    print(f"Quantidade de carros no estacionamento: {qtd_cars}")
    print("1º andar:\n"+
        f"Quantidade de vagas disponíveis: {8-parking_1}\n"+
        f"Quantidade de carros: {qtd_cars - qtd_cars_2}\n")
    print("2º andar:\n " +
          f"Quantidade de vagas disponíveis: {8-parking_2}\n"+
          f"Quantidade de carros: {qtd_cars_2}\n")


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
    global car_id, entering_time, total_value, parking_1, parking_2
    print(message_1)
    vaga = message_1["vaga"]
    if(message_1["state"][vaga]["state"]==0): 
        parking_1 -= 1
        print("Carro saiu na vaga do primeiro andar")
        total_time = time.time() - times[vaga]["entering_time"]
        total_value += round((total_time/60)*0.15, 3)
    else: 
        print("carro entrou na vaga do primeiro andar")
        parking_1 += 1
        times[vaga]["entering_time"] = entering_time
        times[vaga]["car_id"] = car_id

def check_second_floor(): 
    global car_id, entering_time
    vaga = message_2["vaga"]
    if(message_2["state"][vaga]["state"]==0): 
        parking_2-=1
        print("Carro saiu da vaga do segundo andar")
        total_time = time.time() - times[vaga]["entering_time"]
        total_value += round((total_time/60)*0.15, 3)
    else: 
        parking_2+=1
        print("carro entrou na vaga do segundo andar")
        times[vaga]["entering_time"] = entering_time
        times[vaga]["car_id"] = car_id

def receive(connection, addr): 
    global message_1, message_2, qtd_cars, qtd_cars_2, car_id, entering_time
    while(True): 
        data = connection.recv(2048)
        data = json.loads(data.decode('utf-8'))
        # data = json.loads(data)
        if data["id"] == 1:
            message_1 = data
            check_first_floor()

        elif data["id"] == 2:
            message_2 = data
            check_second_floor()

        elif data["id"] == 0:
            if(data["gate"]==1):
                print("Alguem entrou no estacionamento") 
                qtd_cars +=1
                car_id = uuid4()
                entering_time = time.time()
            else: 
                print("Alguem saiu do estacionamento")
                qtd_cars-=1

        elif data["id"] == 3:
            if(data["gate"]==1):
                print("Alguem entrou do segundo") 
                qtd_cars2 +=1

            else: 
                print("Alguem saiu do segundo")
                qtd_cars2-=1
        
        if(qtd_cars==16): 
            command["SINAL_DE_LOTADO_FECHADO_1"] = 1
            send(connection, addr)

        if(qtd_cars_2==8): 
            command["SINAL_DE_LOTADO_FECHADO_2"] = 1
            send(connection, addr)

        if not data:
            print('Message not received')
            break

def send(connection, addr): 
    global command
    command_socket = json.dumps(command).encode()
    connection.send(command_socket)


def socket_init(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = host, port
    server.bind(addr)
    server.listen()
    print("Iniciando conexao")
    while True:
        conn, addr = server.accept() 
        listen_thread = Thread(target=receive, args=(conn, addr))
        listen_thread.start()
        send_thread = Thread(target=present_menu, args=(conn, addr))
        send_thread.start()

def main(): 
    initialize_times()
    host = sys.argv[1]
    port = int(sys.argv[2])
    server_socket_1 = Thread(target=socket_init, args=(host, port))
    server_socket_1.start()

if __name__ == '__main__': 
    main()
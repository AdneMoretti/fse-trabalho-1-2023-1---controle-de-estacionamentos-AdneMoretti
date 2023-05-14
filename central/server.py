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
times_1 = []
times_2 = []

def initialize_times():
    global times_1
    for _ in range(8):
        times_1.append({"car_id":"", "entering_time": 0})
        times_2.append({"car_id":"", "entering_time": 0})

def present_menu(connection_1, connection_2): 
    global qtd_cars, qtd_cars_2, conn, addr
    while(True):
        print("----------------- Menu --------------\n"+
        "1. Fechar o estacionamento\n"+
        "2. Abrir o estacionamento\n"+
        "3. Bloquear segundo andar\n"+
        "4. Desbloquar segundo andar\n"+
        "5. Ver status do estacionamento\n"
        "6. Sair")
        option = int(input())
        if option == 6: 
            exit(0)
        elif option == 1 and command["SINAL_DE_LOTADO_FECHADO_1"] == 0:
            command["SINAL_DE_LOTADO_FECHADO_1"] = 1
            send_socket(connection_1)
        elif option == 2: 
            if(qtd_cars<16):
                command["SINAL_DE_LOTADO_FECHADO_1"] = 0
            else: 
                print("Estacionamento já está lotado")
            send_socket(connection_1)
        elif option == 3:
            command["SINAL_DE_LOTADO_FECHADO_2"] = 1
            send_socket(connection_2)
        elif option == 4:
            if(qtd_cars_2 < 8):
                command["SINAL_DE_LOTADO_FECHADO_2"] = 0
            else: 
                print("Andar 2 já está lotado")
            send_socket(connection_2)
        elif(option==5): 
            show_states()

def show_states(): 
    global qtd_cars, qtd_cars_2, parking_1, parking_2
    print("\n------------------States ----------------\n")
    print(f"Valor total pago: {total_value}")
    print(f"Quantidade de carros no estacionamento: {qtd_cars}")
    print("--- 1º andar: ----\n"+
        f"Quantidade de vagas disponíveis: {8-parking_1}\n"+
        f"Quantidade de carros: {qtd_cars - qtd_cars_2}\n")
    print("---- 2º andar: ----\n" +
          f"Quantidade de vagas disponíveis: {8-parking_2}\n"+
          f"Quantidade de carros: {qtd_cars_2}\n")

def check_first_floor(connection): 
    global car_id, entering_time, total_value, parking_1
    total_time = 0
    vaga = message_1["vaga"]
    if(message_1["state"][vaga]["state"]==0): 
        parking_1 -= 1
        total_time = time.time() - times_1[vaga]["entering_time"]
        total_value += round((total_time/60)*0.15, 3)
    else: 
        parking_1 += 1
        times_1[vaga]["entering_time"] = entering_time
        times_1[vaga]["car_id"] = car_id
        if (parking_1 == 8 and command["SINAL_DE_LOTADO_FECHADO_2"]==1) or (parking_1==8 and parking_2==8): 
            command["SINAL_DE_LOTADO_FECHADO_1"] = 1
            send_socket(connection)
        else: 
            command["SINAL_DE_LOTADO_FECHADO_1"] = 0
            send_socket(connection)

def check_second_floor(connection): 
    global car_id, entering_time, times_2, parking_2, total_value
    vaga = message_2["vaga"]
    if(message_2["state"][vaga]["state"]==0): 
        parking_2-=1
        total_time = time.time() - times_2[vaga]["entering_time"]
        total_value += round((total_time/60)*0.15, 3)
    else: 
        parking_2+=1
        times_2[vaga]["entering_time"] = entering_time
        times_2[vaga]["car_id"] = car_id
        if(parking_2 == 8): 
            command["SINAL_DE_LOTADO_FECHADO_2"] = 1
            send_socket(connection)
        else: 
            command["SINAL_DE_LOTADO_FECHADO_2"] = 0
            send_socket(connection)

def receive(connection, addr): 
    global message_1, message_2, qtd_cars, qtd_cars_2, car_id, entering_time
    while(True): 
        data = connection.recv(2048)
        data = json.loads(data.decode('utf-8'))
        if data["id"] == 1:
            message_1 = data
            check_first_floor(connection)

        elif data["id"] == 2:
            message_2 = data
            check_second_floor(connection)

        elif data["id"] == 0:
            if(data["gate"]==1):
                qtd_cars +=1
                car_id = uuid4()
                entering_time = time.time()
            else: 
                qtd_cars-=1

        elif data["id"] == 3:
            if(data["gate"]==1):
                qtd_cars_2 += 1
            else: 
                qtd_cars_2 -= 1 
            
        if not data:
            print('Message not received')
            break

def send_socket(connection):
    try:
        global command
        command_socket = json.dumps(command).encode()
        connection.send(command_socket)
    except:
        print("Erro ao tentar enviar mensagem")
        connection.close()
        socket_init() 

def socket_init(host, port):
    global server, conn, addr, conn2, addr2
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = host, port
    server.bind(addr)
    server.listen()
    print("Iniciando conexao do socket")
    connected_socket = []
    while True:
        conn, addr = server.accept() 
        connected_socket.append(conn)
        listen_thread = Thread(target=receive, args=(conn, addr))
        listen_thread.start()
        if len(connected_socket) == 2:

            send_thread = Thread(target=present_menu, args=(connected_socket))
            send_thread.start()

def main(): 
    initialize_times()
    host = sys.argv[1]
    port = int(sys.argv[2])
    server_socket = Thread(target=socket_init, args=(host, port))
    server_socket.start()


if __name__ == '__main__': 
    main()
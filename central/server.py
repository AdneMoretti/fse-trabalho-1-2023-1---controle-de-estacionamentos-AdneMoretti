import socket
import sys
from threading import Thread

# Manter conexão com os servidores distribuídos (TCP/IP);
# Prover uma interface que mantenham atualizadas as seguintes informações:
# a. Número de carros em cada andar (Não necessariamente nas vagas, um carro pode estar a caminho da vaga);
# b. Número total de carros no estacionamento; c. Número de Vagas disponíveis em cada andar; d. Valor total pago;
# Prover mecanismo na interface para:
# a. Fechar o estacionamento:
# 1. Manualmente: à partir de um comando de usuário ativar/desativar o sinal de Lotado/Fechado; 2. Automaticamente: à partir da contagem e lotação total das vagas de todos os andares, ativar/destivar o sinal de Lotado/Fechado; b. Bloquear o 2º Andar:
# 1. mesmo sem estar com todas as vagas ocupadas, sinalizar o impedimento ao 2º Andar ativando o "Sinal de Lotado";


def present_menu(): 
    print("----------------- Menu --------------\n"+
    "1. Fechar o estacionamento\n"+
    "2. Ativar o sinal de Lotado\n"+
    "3. Desativar o sinal de lotado"
    "4. Bloquear o segundo andar")


def show_states(): 
    print(
        "\n------------------States ----------------\n"+
        "1º andar: \n"+
        "2º andar: \n"
    )

def receive(conection, addr): 
    while(True): 
        data = conection.recv(2048)
        if not data:
            print('Message not received')
             
            break

def send(conection, addr): 
    pass

def socket_init(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = host, port
    server.bind(addr)
    server.listen()
    while True:
        conn, addr  = server.accept()  
        listen_thread = Thread(target=receive, args=(conn, addr ))
        listen_thread.start()
        send_thread = Thread(target=send, args=(conn, addr ))
        send_thread.start()

def main(): 
    host = sys.argv[1]
    port = sys.argv[2]
    addr = (host, port)
    server_socket = Thread(target=socket_init, args=(host, port))
    server_socket.start()

if __name__ == '__main__': 
    main()
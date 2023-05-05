import socket
import sys

# Manter conexão com os servidores distribuídos (TCP/IP);
# Prover uma interface que mantenham atualizadas as seguintes informações:
# a. Número de carros em cada andar (Não necessariamente nas vagas, um carro pode estar a caminho da vaga);
# b. Número total de carros no estacionamento; c. Número de Vagas disponíveis em cada andar; d. Valor total pago;
# Prover mecanismo na interface para:
# a. Fechar o estacionamento:
# 1. Manualmente: à partir de um comando de usuário ativar/desativar o sinal de Lotado/Fechado; 2. Automaticamente: à partir da contagem e lotação total das vagas de todos os andares, ativar/destivar o sinal de Lotado/Fechado; b. Bloquear o 2º Andar:
# 1. mesmo sem estar com todas as vagas ocupadas, sinalizar o impedimento ao 2º Andar ativando o "Sinal de Lotado";

def show_states(): 
    print(
        "\n------------------States ----------------\n"+
        "1º andar: \n"+
        "2º andar: \n"
    )

def main(): 
    host = sys.argv[1]
    port = sys.argv[2]
    addr = (host, port)
    # Aqui será criado o mecanismo de socket para receber a conexão, nesse caso TCP/IP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Zerar time wait do socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(addr)
    server.listen()

if __name__ == '__main__': 
    main()
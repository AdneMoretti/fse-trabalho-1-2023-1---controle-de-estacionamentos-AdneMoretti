import socket 
import RPi.GPIO as gpio

ip = ''
port = 'TO DO'
addr = (ip,port)

firstfloor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
firstfloor.connect(addr) 
# firstfloor.send(mensagem) 
firstfloor.close()

gpio.output()


def main(): 
    pass

def socket_init(): 
    pass

## sys passadno porta e host como parametro
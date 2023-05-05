import socket 
import RPi.GPIO as gpio
import json

ip = ''
port = 'TO DO'
addr = (ip,port)

firstfloor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
firstfloor.connect(addr) 
# firstfloor.send(mensagem) 
firstfloor.close()

def socket_init():
    pass


def main(): 
    pass
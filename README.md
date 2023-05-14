# Fundamentos de Sistemas Embarcados 2023.1

Trabalho desenvolvido na disciplina de Fundamentos de Sistemas Embarcados da Universidade de Brasília com o tema de estacionamento automatizado. 

## Servidor central
O servidor central recebe as informações de dois servidores distribuídos, que são o primeiro e o segundo andar e atualiza as informações a medida que recebe as informações. 

Para o projeto foi utilizado o Python 3.9.2. Para rodar o servidor central basta entrar na pasta do central e rodar o seguinte comando: 

```cd central```
``` python server.py <IP> <PORT>```

De acordo com a porta e o IP da placa em questão. 

## Primeiro andar 

O primeiro andar deve ser rodado antes do segundo andar para que seja mantida a normalidade do sistema de acordo com os sockets conectados. 

Para configurar as portas da placa no primeiro andar existe um arquivo config_second_floor.json. É necessário atualizar também o IP do servidor central nesse  Ao configurar as portas basta rodar o seguinte comando: 

```cd distributed```
```python first_floor.py```

## Segundo andar 

O segundo andar deve ser rodado depois do primeiro andar para que seja mantida a normalidade do sistema de acordo com os sockets conectados. 

Para configurar as portas da placa no primeiro andar existe um arquivo config_second_floor.json. É necessário atualizar também o IP do servidor central nesse  Ao configurar as portas basta rodar o seguinte comando: 

```cd distributed```
```python second_floor.py```

## Dependências
 - Rpi.GPIO
 - Python 3.9.2


## Vídeo de apresentação do sistema em funcionamento

O vídeo a seguir apresenta o funcionamento do trabalho de forma rápida e simplificada, apresentando rapidamente o código desenvolvido e o funcionamento ao utilizar os dashboards e realizar diferentes ações.


Observa-se que no vídeo, quando um carro desce o segundo andar quando está lotado, o sensor de lotação não desligou, mas em momento posterior a gravação do vídeo isso foi arrumado, se comportando da forma como deveria. 


<<<<<<< HEAD
- [Link para o vídeo:](https://www.youtube.com/watch?v=5PJN8lX-4vs) 
=======

<iframe width="560" height="315" src="https://www.youtube.com/embed/5PJN8lX-4vs" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen/>
>>>>>>> cc41f074775ddc5302f159193966a97444755189

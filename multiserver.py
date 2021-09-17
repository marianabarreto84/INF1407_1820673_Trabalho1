'''
Programa Principal - Servidor Web
'''

from sys import exit
from socket import socket, AF_INET, SOCK_STREAM
from os import fork
from arquivos import porta
from pedido_cliente import gera_resposta, trata_pedido

def main():
    bufferSize = 1024
    host = ''
    port = porta
    tcpSocket = socket(AF_INET, SOCK_STREAM)
    origem = (host, port)
    tcpSocket.bind(origem)
    tcpSocket.listen(1)
    print("Servidor pronto, conectado na porta: %d" %port)
    while True:
        con, cliente = tcpSocket.accept()
        pid = fork()
        if pid == 0:
            tcpSocket.close()
            print("Servidor conectado com ", cliente)
            while True:
                msg = con.recv(bufferSize).decode("utf-8")
                if not msg:
                    break
                lista_resposta = trata_pedido(msg)
                lista_de_envio = gera_resposta(lista_resposta[0], lista_resposta[1], lista_resposta[2], lista_resposta[3], lista_resposta[4], lista_resposta[5])
                mensagem_de_envio = lista_de_envio[0]
                arquivo = lista_de_envio[1]
                con.send(bytearray(mensagem_de_envio, 'utf-8'))
                con.send(arquivo)
            print("Conexão terminada com ", cliente)
            con.close()
            exit()
        else:
            con.close()
    return

if __name__ == '__main__':
    main()

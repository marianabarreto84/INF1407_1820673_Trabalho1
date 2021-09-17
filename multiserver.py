'''
Programa Principal - Servidor Web
'''

from sys import exit
from socket import socket, AF_INET, SOCK_STREAM
from os import fork, abort
from arquivos import porta, path, pagina_erro, lista_arquivos_default
from time import sleep
from pedido_cliente import gera_resposta, trata_pedido

'''
FUNCAO PARA TESTAR CONFIGURACOES
Essa função serve apenas para ajudar caso as configurações não tenham sido definidas corretamente. Se esse for o caso, 
então o servidor nem é aberto.
'''
def testa_config():
    if type(porta) != int:
        print("ERRO: A porta não foi configurada como requisitado. Verifique se ela é do tipo inteiro.")
        abort()
    elif type(path) != str:
        print("ERRO: A referência ao diretório físico do servidor não foi configurada como requisitado.")
        abort()
    elif "//" not in path and ("/" in path or "\\" in path):
        print("ERRO: A referência ao diretório físico do servidor não foi configurada como requisitado.")
        abort()
    elif type(pagina_erro) != str:
        print("ERRO: A variável referente ao arquivo da página 404 não foi configurada como requisitado.")
        abort()
    elif type(lista_arquivos_default) != list:
        print("ERRO: A lista de arquivos default não foi configurada como requisitado.")
        abort()
    return


'''
FUNÇÃO MAIN DE IMPLEMENTAÇÃO DO SERVIDOR WEB.
A partir da porta que foi configurada no arquivos.py, o servidor se conecta a ela.
Para saber se o servidor está conectado, uma mensagem é exibida, dizendo em que porta ele está conectado.
Para saber se o cliente conseguiu se conectar ao servidor, uma mensagem também é exibida especificando qual cliente se conectou.
Para saber se a conexão com o cliente foi terminada, uma mensagem é exibida especificando qual cliente terminou sua conexão.
'''
def main():
    bufferSize = 1024
    host = ''
    port = porta
    testa_config()
    print("Configurações OK")
    tcpSocket = socket(AF_INET, SOCK_STREAM)
    origem = (host, port)
    try:
        tcpSocket.bind(origem)
    except Exception as e:
        print("ERRO: A porta que você está tentando escutar (%d) não está disponível no momento. Por favor espere um pouco, tente trocar de porta ou tente matar o processo que esteja utilizando-a." %porta)
        abort()
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
                lista_de_envio = gera_resposta(lista_resposta)
                mensagem_de_envio = lista_de_envio[0]
                arquivo = lista_de_envio[1]
                con.send(bytearray(mensagem_de_envio, 'utf-8'))
                con.send(arquivo)
            # print("Dando os 10 segundos de delay")
            # sleep(10)
            # Deixei essa parte comentada apenas porque no enunciado foi dito como uma sugestão. Já havia verificado antes de implementar a requisição GET que o servidor lidar com mais de um cliente simultaneamente
            print("Conexão terminada com ", cliente)
            con.close()
            exit()
        else:
            con.close()
    return

if __name__ == '__main__':
    main()

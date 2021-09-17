'''
Módulo para tratar a mensagem de pedido do cliente e formatar mensagem de resposta do servidor.
Esse módulo lida apenas com strings e aberturas de arquivo. Toda a parte do servidor está presente em multiserver.py
O multiserver.py apenas importa duas funções deste módulo: trata_pedido e gera_resposta.
'''

from arquivos import path, pagina_erro, lista_arquivos_default
import os
from os import abort
from datetime import datetime

def retorna_tipo_conteudo(extensao):
    if extensao == "html":
        return "text/html"
    if extensao == "js":
        return "text/javascript"
    if extensao == "gif" or extensao == "jpeg" or extensao == "jpg" or extensao == "png":
        if extensao == "jpg":
            extensao = "jpeg"
        return "image/"+ extensao
    print("ERRO: O cliente pediu um arquivo cuja extensão não é comportada pelo servidor")
    abort()
    return

def resultado_pagina_404():
    codigo_da_resposta = 404
    arquivo_imagem = b''
    try:
        arquivo = open(path+pagina_erro, "rb")
        lista_resposta = [codigo_da_resposta, "text/html", os.path.getsize(path+pagina_erro), arquivo.read(), arquivo_imagem]
        return lista_resposta
    except Exception as e:
        print("ERRO DE CONFIGURAÇÃO: Não foi possível exibir a página em caso de erro.")
        abort()
    return

def resultado_arquivo_especificado(referencia):
    referencia = path + referencia[1:] #Assim como no enunciado do trabalho, em path teríamos "C:/trabalho/trabalho1/" e na referencia "UmDiretorio/OutroDiretorio/MaisDiretorios/arquivo.html"
    lista_resposta = []
    arquivo = ''
    arquivo_imagem = b''
    try:
        nome_arquivo = referencia.split("/")[-1]
        index_extensao = nome_arquivo.find(".")
        extensao = nome_arquivo[index_extensao+1:]
        if extensao == "gif" or extensao == "png" or extensao == "jpeg" or extensao == "jpg":
            arquivo_imagem = open(referencia, "rb").read()
        else:
            arquivo = open(referencia, "rb").read()
        codigo_da_resposta = 200
        tamanho_conteudo = os.path.getsize(referencia)
        tipo_conteudo = retorna_tipo_conteudo(extensao)
        lista_resposta = [codigo_da_resposta, tipo_conteudo, tamanho_conteudo, arquivo, arquivo_imagem]
    except Exception as e:
        lista_resposta = resultado_pagina_404()
    return lista_resposta

def resultado_lista_default(referencia):
    referencia = path + referencia[1:]
    lista_resposta = []
    arquivo = ''
    arquivo_imagem = b''
    for nome_arquivo in lista_arquivos_default:
            try:
                index_extensao = nome_arquivo.find(".")
                extensao = nome_arquivo[index_extensao+1:]
                if extensao == "gif" or extensao == "png" or extensao == "jpeg" or extensao == "jpg":
                    arquivo_imagem = open(referencia+nome_arquivo, "rb").read()
                else:
                    arquivo = open(referencia+nome_arquivo, "rb").read()
                codigo_da_resposta = 200
                tamanho_conteudo = os.path.getsize(referencia)
                tipo_conteudo = retorna_tipo_conteudo(extensao)
                lista_resposta = [codigo_da_resposta, tipo_conteudo, tamanho_conteudo, arquivo, arquivo_imagem]
                return lista_resposta # se achou o arquivo na lista default, então sai do loop com as informações certas
            except Exception as e:
                pass # se não conseguiu abrir o arquivo, provavelmente porque não existe no diretório
    #se chegou até esse ponto, é porque não conseguiu encontrar e por isso a página 404 deve ser acionada
    lista_resposta = resultado_pagina_404()
    return lista_resposta

def trata_arquivo(referencia):
    lista = referencia.split("/")
    nome_arquivo = lista[-1]
    if nome_arquivo:
        #caso em que o cliente especifica nome do arquivo
        lista_resposta = resultado_arquivo_especificado(referencia)
    else: 
        #caso em que o cliente não especifica o nome do arquivo
        lista_resposta = resultado_lista_default(referencia)
    return lista_resposta


def trata_mensagem_get(texto):
    lista = texto.split(" ") # lista[0] = GET - lista[1] = referencia a um arquivo que está dentro do diretório raiz do site - lista[2] = HTTP/1.1
    referencia = lista[1]
    tipo_http = "HTTP/1.1"
    lista_resposta = trata_arquivo(referencia)
    lista_resposta.append(tipo_http)
    return lista_resposta

'''
Essa função recebe um texto que é a mensagem decodificada do pedido do cliente.
A partir desse texto, ele retorna uma lista, chamada lista_get, que possui todas as especificações necessárias para montar a mensagem de resposta.
Note que em todos os testes apenas um GET era enviado, assim como no enunciado. Não houve problemas como o GET do favicon, por exemplo, mesmo testando a partir do localhost.
'''
def trata_pedido(texto):
    arquivo = ''
    lista = texto.split("\n")
    for linha in lista:
        if linha[0:3] == "GET":
            if arquivo == '': # apenas o primeiro get de um mesmo pedido é tratado
                lista_get = trata_mensagem_get(linha)
                return lista_get
    print("ERRO: Não foi possível encontrar requisição GET")
    abort()
    return 


'''
Função para converter a data em que a mensagem é gerada para o formato adequado pro HTTP.
Essa função eu achei uma solução que atende ao que preciso na internet e a autoria se encontra abaixo.
Créditos: Florian Bösch - https://stackoverflow.com/questions/225086/rfc-1123-date-representation-in-python
'''
def retorna_data_http():
    dt = datetime.now()
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month, dt.year, dt.hour, dt.minute, dt.second)


def gera_resposta(codigo_da_resposta, tipo_conteudo, tamanho_conteudo, arquivo, arquivo_imagem, tipo_http):
    #mensagem nesse caso diz respeito ao header do arquivo
    data = retorna_data_http()
    mensagem = ''
    mensagem += str(tipo_http) + " " + str(codigo_da_resposta)
    if codigo_da_resposta == 200:
        mensagem += " " + "OK\r\n"
    else:
        mensagem += " " + "Page Not Found\r\n"
    mensagem += "Server: Apache-Coyote/1.1\r\n"
    mensagem += "Content-Type: " + tipo_conteudo + "\r\n"
    mensagem += "Content-Length: " + str(tamanho_conteudo) + "\r\n"
    mensagem += "Date: " + data + "\r\n"
    mensagem += "\r\n"
    if not arquivo:
        arquivo = arquivo_imagem
    return [mensagem, arquivo]

'''
Main apenas para teste.
Lembrar de tirar depois
def main():
    f_teste = open("arquivo_teste_pedido_cliente.txt")
    mensagem = f_teste.read()
    lista = trata_pedido(mensagem)
    resposta = gera_resposta(lista[0], lista[1], lista[2], lista[3], lista[4], lista[5])
    #print(resposta[1])
    return


if __name__ == '__main__':
    main()
'''
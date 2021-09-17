'''
Pedido_Cliente - Módulo auxiliar para as requisições GET
A partir de uma string que representa o pedido do cliente, retorna uma lista com 2 elementos: um sendo o headers do HTTP em formato string e o outro sendo o arquivo em formato binário.
Esse módulo lida apenas com strings e aberturas de arquivo. Toda a parte do servidor está presente em multiserver.py
O multiserver.py apenas importa duas funções deste módulo: trata_pedido e gera_resposta.
'''

from arquivos import path, pagina_erro, lista_arquivos_default
import os
from os import abort
from datetime import datetime


'''
RETORNA TIPO CONTEÚDO (CONTENT-TYPE)
Essa função retorna no formato padronizado o content-type do arquivo. 
Ela só é acionada para o caso em que a página que o cliente está tentando acessar existe dentro do diretório do servidor.
Por exemplo, se não temos um "arquivo.txt" dentro do diretório do servidor, é enviado um erro 404, pois essa função não chega a ser chamada nesse caso.
Caso tenhamos um "arquivo.txt", a extensão enviada é None, para que na função resultado_arquivo_especificado, a página 404 seja acionada.
Ainda assim, é enviada uma mensagem de erro, apenas para que o servidor saiba o que está acontecendo. Como a página 404 ainda vai ser exibida, não há necessidade de dar o abort.
'''
def retorna_tipo_conteudo(extensao):
    if extensao == "html":
        return "text/html"
    if extensao == "js":
        return "text/javascript"
    if extensao == "gif" or extensao == "jpeg" or extensao == "jpg" or extensao == "png":
        if extensao == "jpg":
            extensao = "jpeg"
        return "image/"+ extensao
    print("ERRO: O cliente tentou abrir um arquivo que se encontra no diretório do servidor, porém a extensão não é comportada por ele.")
    return None


'''
RETORNA PÁGINA 404
Essa função, é uma das três que retornam os parâmetros dos headers pro HTTP corretos para cada caso.
Essa função é chamada em 3 casos.
Quando o arquivo é especificado não está presente no diretório.
Quando o arquivo não é específicado mas nenhum dos arquivos na lista default estão presentes no diretório.
Quando o arquivo é especificado, está presente no diretório, mas não possui uma das extensões comportadas pelo servidor (png, jpeg, jpg, gif, js, html).
Essa função coloca os parâmetros disponíveis para abrir a página 404 de Page Not Found, assim como as outras configurações de header adequadas para esse caso.
Lembrando que caso a página especificada no arquivos.py não esteja dentro do diretório raiz, então certamente nenhum arquivo poderá ser enviado na resposta. Por isso, foi pensado que seria interessante enviar uma mensagem para o cliente para que ele saiba que o problema estaria no servidor. 
'''
def resultado_pagina_404():
    codigo_da_resposta = 404
    try:
        arquivo = open(path+pagina_erro, "rb").read()
        lista_resposta = [codigo_da_resposta, "text/html", os.path.getsize(path+pagina_erro), arquivo]
    except Exception as e:
        print("ERRO DE CONFIGURAÇÃO: Não foi possível abrir o arquivo da página 404 especificado nas configurações.")
        lista_resposta = [404, None, None, None]
    return lista_resposta


'''
RETORNA PÁGINA DO ARQUIVO ESPECIFICADO
Essa é outra das 3 funções que retornam os parâmetros dos headers HTTP.
Ela é chamada apenas quando o arquivo é especificado. 
Para saber se o arquivo está dentro do diretório específicado, há várias maneiras de fazer isso.
Como só um arquivo tentará ser aberto, tentamos abrir o arquivo e se der erro na abertura porque o arquivo não foi encontrado, a página 404 é acionada.
'''
def resultado_arquivo_especificado(referencia):
    referencia = path + referencia[1:] # Assim como no enunciado do trabalho, em path teríamos "C:/trabalho/trabalho1/" e na referencia "UmDiretorio/OutroDiretorio/MaisDiretorios/arquivo.html"
    lista_resposta = []
    try:
        nome_arquivo = referencia.split("/")[-1]
        index_extensao = nome_arquivo.find(".")
        extensao = nome_arquivo[index_extensao+1:]
        arquivo = open(referencia, "rb").read()
        codigo_da_resposta = 200
        tamanho_conteudo = os.path.getsize(referencia)
        tipo_conteudo = retorna_tipo_conteudo(extensao)
        if tipo_conteudo == None:
            lista_resposta = resultado_pagina_404()
            return lista_resposta
        else:
            lista_resposta = [codigo_da_resposta, tipo_conteudo, tamanho_conteudo, arquivo]
    except Exception as e:
        lista_resposta = resultado_pagina_404()
    return lista_resposta


'''
RETORNA ARQUIVO DA LISTA DEFAULT
Essa é a última das 3 funções que retornam os parâmetros dos headers HTTP.
É chamada apenas quando o arquivo não especificado.
Ao contrário da função resultado_arquivo_especificado(), o arquivo não vai tentar ser aberto 1 vez, mas seria para cada elemento da lista. Para não ter que trabalhar com "erros esperados", foi usada a função listdir do pacote os e é verificado se o arquivo elemento da lista_default está de fato no diretório.
Caso ele esteja, será esse o arquivo que tentará se aberto para ser enviado na resposta.
Caso ele não esteja, então passa para o próximo da lista.
Caso nenhum arquivo da lista esteja no diretório, o resultado da página 404 é acionado.
'''
def resultado_lista_default(referencia):
    referencia = path + referencia[1:]
    lista_resposta = []
    for nome_arquivo in lista_arquivos_default:
            try:
                index_extensao = nome_arquivo.find(".")
                extensao = nome_arquivo[index_extensao+1:]
                if nome_arquivo in os.listdir(referencia):
                    arquivo = open(referencia+nome_arquivo, "rb").read()
                    codigo_da_resposta = 200
                    tamanho_conteudo = os.path.getsize(referencia)
                    tipo_conteudo = retorna_tipo_conteudo(extensao)
                    if tipo_conteudo == None:
                        lista_resposta = resultado_pagina_404()
                    else:
                        lista_resposta = [codigo_da_resposta, tipo_conteudo, tamanho_conteudo, arquivo]
                    return lista_resposta # se achou o arquivo na lista default, então sai do loop com a lista certa
            except Exception as e:
                print("ERRO: O arquivo foi encontrado, mas não foi possível abri-lo.")
                print(e)
                abort()
    #se chegou até esse ponto, é porque não conseguiu encontrar e por isso a página 404 deve ser acionada
    lista_resposta = resultado_pagina_404()
    return lista_resposta


'''
TRATA ARQUIVO
A partir da referencia do arquivo que foi enviada na requisição GET, chama a função correta para cada caso.
No caso em que a referencia contenha o arquivo específico, a função resultado_arquivo_especificado é chamada.
No caso em que isso não acontece, a função resultado_lista_default é chamada.
Lembrando que em ambos os casos há a possibilidade de que a página não seja encontrada e nessas funções, a função resultado_pagina_404 é chamada. 
'''
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


'''
TRATA MENSAGEM GET
O que realmente importa para o caso do trabalho é a primeira linha que contém a informação da requisição GET.
Então, nesse caso, ela retorna a lista com os parâmetros do headers HTTP mas também inclui o parâmetro "HTTP/1.1". 
Ele não é simplesmente o lista[2] porque o lista[2] está em binário, enquanto a mensagem do headers é toda em string.
'''
def trata_mensagem_get(texto):
    lista = texto.split(" ") # lista[0] = GET - lista[1] = referencia a um arquivo que está dentro do diretório raiz do site - lista[2] = HTTP/1.1
    referencia = lista[1]
    tipo_http = "HTTP/1.1"
    lista_resposta = trata_arquivo(referencia)
    if len(lista_resposta) != 0:
        lista_resposta.append(tipo_http)
    return lista_resposta


'''
TRATA PEDIDO DO CLIENTE
Essa função recebe um texto que é a mensagem decodificada do pedido do cliente.
A partir desse texto, ele retorna uma lista, chamada lista_get, que possui todas as especificações necessárias para montar a resposta (arquivo e headers HTTP).
Note que em todos os testes apenas um GET era enviado, assim como no enunciado. 
É presumido que a cada mensagem do cliente, apenas um GET é enviado. Caso contrário, isso não seria uma requisição GET
'''
def trata_pedido(texto):
    arquivo = ''
    lista = texto.split("\n")
    for linha in lista:
        if linha[0:3] == "GET":
            if arquivo == '': # apenas o primeiro get de um mesmo pedido é tratado
                lista_get = trata_mensagem_get(linha)
                return lista_get
    print("ERRO: Não foi possível encontrar requisição GET.") 
    lista_erro = None
    return lista_erro


'''
RETORNA DATA HTTP
Função para converter a data em que a mensagem é gerada para o formato adequado pro HTTP.
Essa função eu achei uma solução que atende ao que preciso na internet e a autoria se encontra abaixo.
Referência: Florian Bösch - https://stackoverflow.com/questions/225086/rfc-1123-date-representation-in-python
'''
def retorna_data_http():
    dt = datetime.now()
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month, dt.year, dt.hour, dt.minute, dt.second)


'''
GERA RESPOSTA
Essa função a partir de certos parâmetros, retorna uma lista com 2 elementos: uma mensagem em string e um arquivo em binário.
Essa mensagem em string normalmente é o headers HTTP.
O arquivo é aquele que foi requisitado pelo cliente ao servidor. 
'''
def gera_resposta(lista_resposta):
    if len(lista_resposta) == 0:
        return ["ERRO: Não foi possível encontrar requisição GET", b'']
    codigo_da_resposta = lista_resposta[0]
    tipo_conteudo = lista_resposta[1]
    tamanho_conteudo = lista_resposta[2]
    arquivo = lista_resposta[3]
    if codigo_da_resposta == 404 and arquivo == None:
        return ["Há um problema no servidor no momento, mas a página requisitada não foi encontrada. Por favor tente mais tarde.", b'']
    tipo_http = lista_resposta[4]
    data = retorna_data_http()
    headers = ''
    headers += str(tipo_http) + " " + str(codigo_da_resposta)
    if codigo_da_resposta == 200:
        headers += " " + "OK\r\n"
    else:
        headers += " " + "Page Not Found\r\n"
    headers += "Server: Apache-Coyote/1.1\r\n"
    headers += "Content-Type: " + tipo_conteudo + "\r\n"
    headers += "Content-Length: " + str(tamanho_conteudo) + "\r\n"
    headers += "Date: " + data + "\r\n"
    headers += "\r\n"
    return [headers, arquivo]
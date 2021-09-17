# INF1407_1820673_Trabalho1
Disciplina: INF1407 - Programação para Web
Nome: Mariana Porto Barreto
Matrícula: 1826073

## Criando um Servidor Web (multiserver.py)

A primeira coisa foi criar um servidor Web que aceitasse múltiplos clientes. Então foi criado o multiserver.py, baseado inteiramente no arquivo multiServer.py disponibilizado pelo professor Alexandre Meslin nas aulas de INF1407. Para testar se o servidor de fato funcionava com mais de um cliente simultaneamente, foi feito uma espécie de chat. Modificando levemente o arquivo client_tcp.py também disponibilizado nas aulas, um cliente era capaz de mandar uma mensagem (em string que depois era convertida para binário) para o servidor ao mesmo tempo que outro cliente. As duas eram exibidas no terminal do servidor. O teste foi feito com três terminais abertos: dois clientes e o do servidor. Um delay de 10 segundos foi acrescentado antes da conexão do cliente ser fechada, apenas para apresentar que outro cliente poderia mandar mensagem enquanto outro cliente permanecia com a sua conexão ativa.
Todos os testes foram feitos por meio do WSL do Windows e funcionaram normalmente. Alguns alunos relataram que o WSL estava exibindo problemas de firewall em alguns casos para o multiserver.py, mas isso não foi observado neste trabalho.
Outra funcionalidade que inclui nesse módulo foi uma verificação das configurações. Caso quem esteja configurando não estivesse atento às especificações deixadas nos comentários do módulo arquivos.py e configurasse alguma variável com algum tipo diferente ou se especificasse errado a path, não teria problema. O multiserver.py simplesmente apresentaria um erro e abortaria antes mesmo do servidor inicializar.

## Lidando com as requisições GET (pedido_cliente.py)

Com o servidor pronto, foi pensado então em fazer um módulo a parte chamado "pedido_cliente.py", que lida com a string de requisição do cliente e devolve uma resposta (lista com 2 elementos, uma mensagem em string e um arquivo lido em binário). Dessa maneira, como no próprio multiserver.py é feita a decodificação para UTF-8, o pedido_cliente.py apenas precisa lidar com a string do pedido do cliente e devolver a resposta de acordo. Por isso, para testar esse módulo, foi utilizado um arquivo .txt teste que representava a mensagem de requisição do cliente. Dessa forma, o servidor não precisava ficar sendo inicializado toda vez para testar mudanças na formatação da mensagem de resposta ou na extração das informações da mensagem de requisição. 

## Integrando os dois módulos

Nesse caso, pouco teve que ser feito para integrar o pedido_cliente.py com o multiserver.py. Basicamente, o servidor chamava a função trata_pedido enviando como argumento a mensagem do cliente já decodificada em UTF-8. Além disso, ele usa a lista resultante dessa função para chamar a função gera_resposta, em que é devolvida a tal lista com 2 elementos de mensagem e do arquivo. 

## Criando o arquivos.py

Como foi pedido pelo enunciado, também foi implementado o arquivos.py, que possui apenas variáveis a serem configuradas por quem quer que queira rodar o servidor em sua própria máquina. Ou seja, opções customizáveis como sobre qual porta será escutada, sobre qual o nome do arquivo da página de erro 404, foram disponibilizadas em formas de variáveis que eram importadas tanto pelo multiserver.py quanto pelo arquivo.py. Além disso, instruções sobre como elas devem ser inseridas por quem for configurar também foram colocadas em forma de comentários.

## Testando o programa

Utilizando, principalmente, o localhost nos navegadores. Então, sempre que era necessário testar o servidor, era inserido no Google Chrome "localhost:xxxx/y" em que xxxx representa a porta que o servidor está escutando e y o arquivo (ou não) que o cliente deseja requisitar. Foi testado casos em que:
1. O arquivo é especificado e está presente no diretório raiz do servidor
2. O arquivo é especificado e não está presente no diretório raiz do servidor
3. O arquivo não é especificado mas um dos arquivos presentes na lista de arquivos default está presente no diretório raiz do servidor 
4. O arquivo não é especificado e nenhum dos arquivos presentes na lista de arquivos default está presente no diretório raiz do serivodr
5. O arquivo é especificado porém a extensão dele não é comportada pelas especificações do servidor (impostas pelo enunciado - jpeg, jpg, png, gif, html, css) e ele não está presente no diretório raiz do servidor
6. O arquivo é especificado porém a extensão dele não é comportada pelas especificações do servidor (impostas pelo enunciado - jpeg, jpg, png, gif, html, css) e ele está presente no diretório raiz do servidor

Para os casos 2, 4, 5 e 6 a página 404 (caso ela esteja corretamente especificada no arquivos.py e caso ela esteja presente no diretório raiz do servidor Web) é exibida e a resposta é 404 - Page Not Found.
Para o caso 1, o arquivo pedido é exibido no navegador. 
Para o caso 3, o primeiro arquivo na lista de arquivos default que foi encontrado no diretório raiz do servidor é exibido.

Ainda foi testado também, sem utilizar o localhost, o caso em que o cliente nem mande uma requisição GET, mas mande alguma mensagem. Nesse caso, é enviada uma mensagem de erro para o cliente (para caso ele esteja exibindo as respostas do servidor, ele consegue saber que há algo de errado) e esse erro também é exibido por parte do servidor para questões de monitoramento.

Outro caso que também foi testado mas que não dependia da requisição do cliente é quando variável da página de erro 404 não estivesse configurada corretamente. Nesse caso, claramente, não há páginas que podem ser exibidas e, por isso, uma mensagem é exibida no servidor para que ele saiba que há algo de errado e uma mensagem é enviada para o cliente para que ele, caso esteja acompanhando as respostas do servidor, saiba que há algo de errado por parte do servidor. O servidor nunca é fechado ou abortado por algum erro, pois erros por parte do servidor não necessariamente acontecerão para todos os clientes. O mesmo vale para erros por parte do cliente. Mas tudo é monitorado no servidor (claro que seria interessante guardar essas informações em um banco, por exemplo) para que quem estiver administrando tenha ideia do que está acontecendo para eventualmente fechá-lo e reparar o que está errado. 

Foram testados arquivos com extensões permitidas, arquivos sem extensão, arquivos sem extensões permitidas e em todos os casos alguma página é exibida caso o cliente faça uma requisição GET e o servidor esteja configurado corretamente.

## Problemas ao longo do trabalho

A principal questão que gerou dificuldade foi o problema de conexão infinita, ou seja, os arquivos eram exibidos quando estavam presentes no diretório raiz mas o favicon ficava carregando para sempre. Parecia que não havia indícios de que a resposta chegou ao fim. Para corrigir esse erro bastou colocar um "\r\n" ao invés do "\n" no cabeçalho HTTP e também mandar o arquivo direto em binário. Esse erro foi então corrigido.

Um erro que tive que lidar bastante e imagino que seja da configuração do servidor mesmo foi o de "OSError: [Errno 98] Address already in use" no bind pois como eu tinha que fechar abruptamente o servidor, eu imagino que o processo ainda estivesse rodando e o CTRL-C  para a interrupção não o matava completamente. Nesse casos eu simplesmente alterava a porta, esperava o processo morrer ou procurava ele por comandos como "ps -fA | grep python" e matava o processo com o "kill -9 PID". Nesse caso, apenas coloquei um try: except: no bind para que eu consiga personalizar a mensagem de erro, para que a pessoa que esteja configurando o arquivo não fique confusa sobre o erro indicado.

A porta 80 também foi um pequeno problema, pois só tinha autorização para tentar escutá-la no usuário raiz do Linux (e no Windos não tinha como rodar). Como normalmente não testo o programa no root, acabei não testando essa porta. Mas de fato acredito que ela funcionaria já que o problema de autorização que acontecia para mim não era algo que eu poderia reverter. Porém como no enunciado fala para que o servidor seja implementado ou na porta 80 ou na 8080 e não necessariamente nas duas, mesmo que de fato tivesse algum problema acredito que ainda estaria dentro das regulamentações do trabalho por conseguir escutar a 8080. Mas realmente, acho que não terá problema pois acredito que a questão está na autorização do usuário mesmo, e não algum problema de código não previsto.
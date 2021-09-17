# Data logger pocket beagle - raspberry para ScadaBR

Este tutorial mostra o passo a passo para criar um datalogger no Pocket Beagle que permite que a gente guarda dados do GPS (coordenados e velocidade), dados do funcionamento do carro (Velocidade linear, corrente e tensão elétrica) num banco de dados no Beagle, e permite depois descarregar todos estes dados de forma automático no ScadaBR. 

O ScadaBR já permite várias formas de puxar os dados do Computado de Bordo ou OBC implementado pelo Pocket Beagle, usando os protocolos MODBUS-RTU, MODBUS-IP ou HTTP Reciever.

Cada uma desses protocolos tem suas vantagens e desvantagens e conseguimos bons resultados com MODBUS-IP quando usamos uma rede local ou WiFi entre o servidor ScadaBR e o OBC. 

Quando o servidor e o OBC não estão na mesma subrede, o protocolo HTTP Reciever funcionou, entretanto, o tempo de processamento e  transmissão fica em torno de alguns segundos. Isso, torna este protocolo inviavel para operações de uma tempo de amostragem de 1 Hz como é no caso do monitoramento do veículo. 

Escolheu-se 1 Hz por ser também a taxa de envio do bloco de dados do GPS pelo protocolo NMEA. 

Para resolver isso, escolheu programar o OBC para fazer o seu registro de dados num banco de dados locais, e permitir fazer o upload dos dados no ScadaBR, assim que o veículo estiver no alcance da rede local.

Procurou-se neste desenvolvimento aproveitar ao máximo as funcionalidades já presentes no ScadaBR e o Linux, reduzindo o desenvolvimento de programas específicos ao mínimo possível.
 
Neste sentido, escolheu se para o banco de dados usar o MySQL no OBC e usar o protocolo SQL do ScadaBR. 



#1. Configuração do MariaBD no Beagle

O banco de dados escolhido foi o MariaDB que é uma versão compatível com MySQL. 

[Baseado neste tutorial 1](https://r00t4bl3.com/post/how-to-install-mariadb-server-on-debian-10-buster)

```
$ sudo apt-get install mariadb-server
```

Passei um dia brigando com a instalação do MariaDB no Beagle e no Raspberry, pois estava dando de erro na hora de baixar os arquivos. 

Depois de uma noite de sono eu tentei de novo, mas antes eu só fiz a 

```
$ sudo apt update
```
e funcionou.

Eu nao arrisquei de fazer depois o `upgrade` pois isso eu já tinha feito no dia anterior e não tinha dado sucesso. 
Deve ter alguma coisa específica na instalação do MariaBD, pois outros aplicativos instalavam normalmente usando o `apt-get`

Depois da instalação eu usei o seguinte script para fazer a configuração 

```
$ sudo mysql_secure_installation 
```

#2. Criando o primeiro acesso no MariaDB

[Baseado neste tutoria 2](https://phoenixnap.com/kb/how-to-create-mariadb-user-grant-privileges)


Apos instalado o MariaDB ainda tem uma confusão de como entrar. `mysql -u root -p` nao funcionou.

Consegui somente com `sudo mysql -u root`


## 2.1. Criando usuário 

```
> create user 'debian'@localhost identified by 'sleutel';
> select user from mysql.user;
> grant all privileges on *.* to 'debian'@localhost identified by 'sleutel';
> flush privileges;
> SHOW GRANTS FOR 'debian'@localhost;
```


## 2.2. Alimentando a base de dados
Agora pode entrar com usuario normal 
 
```
debian@beaglebone:~/src$ mysql -p
```

Depois de entrar no ambiente pode se criar a base de dados e abri-lo para uso.

```
> create database base_GPS;
> show databases;
> use base_GPS;
```

O próximo passo é a criação da tabela com os dados monitorados pelo OBC. 
Depois de varias tentativas pesquisando a melhor opção de fazer a integração entre MariaDB e ScadaBR chegamos a seguinte configuração.


```
> create table dados (nome VARCHAR(100), valor float, hora timestamp);
> insert into dados values ("velocidade", 12.1,  now());
> insert into dados values ("latitude", 4.1,  now());
> select * from dados;
```

A tabela de `dados` tem a seguinte estrutura e permitiu a integração direta com o SQL do ScadaBR, buscando de forma automático as variáveis, os valore e o horário que foi medido.

| nome       | valor | hora                |
|------------|-------|---------------------|
| velocidade |  12.1 | 2021-09-15 19:06:41 |
| latitude   |   4.1 | 2021-09-16 00:45:25 |

Para chegar a essa forma gastamos pelo menos uns 3 dias, tentando entender a lógica da construção do banco de dados do ScadaBR e como a busca era feita pelo SQL. 

Algumas coisas que descobrimos é que esse formato só funciona se os valores medidos estão em ordem cronológico de tempo na tabela. O ScadaBR varre os registros pegando a variavel declarada no campo `nome` e armazena o valor com o `timestamp` que está no campo `hora`.

Se ele encontra um registro com uma `hora` anterior que a hora lido no registr anterior, o ScadaBR termine a varredura e ignora o registro novo. 

Mais detalhes da configuração do ScadaBR para fazer essa varredura e upload dos dados está no item 4.



#3. Configurando acesso remoto no Beagle
Uma vez definido o banco de dados e sua estrutura o próximo passo é permitir o acesso ao banco.

A primeira tentativa de acesso remoto fiz com o programa [DBEAVER](https://dbeaver.io) e ao colocar os dados do 
server, username e password não houve nenhuma resposta do MariaBD. 

Fiz algumas modificações 
[baseado neste tutorial 3](https://leandroramos.debxp.org/configurando-o-mariadb-server-para-acesso-remoto-debian-e-ubuntu/).

No arquivo `/etc/mysql/mariadb.conf.d/50-server.cnf` alterou o bind-address de `127.0.0.1` para `0.0.0.0`

Depois de alterado reinicia MariaDB com ` sudo systemctl restart mariadb`

Mesmo assim quando faço o acesso remoto usando, por exemplo Dbeaver recebo a seguinte mensagem de erro 

```
Could not connect to HostAddress{host='192.168.1.88', port=3306, type='master'}. Host '192.168.1.67' is not allowed to connect to this MariaDB server
  Host '192.168.1.67' is not allowed to connect to this MariaDB server
  Host '192.168.1.67' is not allowed to connect to this MariaDB server
```

Para resolver isso, teve que voltar a entrar no MariaDB como root e inserir os seguintes comandos no banco de dados.

```
> grant all privileges on *.* to 'debian'@'192.168.1.67' identified by 'sleutel';
> flush privileges;
```

Com isso foi possivel acessar o banco de dados a partir do dBeaver.

# 4. Configurando ScadaBR
Para permitir o acesso pelo ScadaBR tive que também habilitar o endereço do IP do servidor no MariaDB e com isso conseguimos acesar o banco de daods conforme mostrada na figura a seguir.

![](figuras/Tela_ScadaBR_SQL.jpg)

Importante destacar na hora de configurar o datasource que os dados devem ser organizados no forma de `Row-based query` 

Dessa forma a busca executado pela sentença SQL `select * from dados;`
faz a varredura do banco de dados, fazendo a busca das variáveis e atribui o valor e o `timestamp` nas colunas de cada registro. 

A vantagem dessa abordagem é que permite depois customizar a busca, modificando a sentença do SQL. 

Até descobrir os detalhes levou uns três dias hackeando o ScadaBR.

## 3.1. SQL query no ScadaBR

Ainda há um problema para resolver. 
Quando a base de dados começa a encher, o query `select * from dados;` pode retornar centenas de registros. 
O problema é que dentro do ScadaBR somente os primeiros 50 registros são processados. 

O desafio é de montar um query que retorna sempre as últimas 50 registros


# 5. Programando o Python para alimentar o banco do dados

A primeira tentativa de usar o banco de dados foi feito usando o SQLite3 que é uma versão simplificado do SQL. Foi importante ter usado lo para se acostumar com o SQL no Beagle e testar a programação em Python. 



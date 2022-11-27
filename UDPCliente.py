# Igor Wandermurmem Dummer
from socket import *
from statistics import mean, stdev
import sys
import time

# Endereço IP do servidor
host = '127.0.0.1'
# a porta que o servidor está
port = 30000

# Há opção de passar o ip e a porta do servidor como argumento
if len(sys.argv) > 1:
    host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

""" As mensagens terão o seguinte formato:
- 5 Bytes : Numero de sequência (identificação)
- 1 Byte : 1 - Ping / 0 - Pong
- 4 Bytes: Timestamp
- 30 Bytes: Mensagem do pacote
"""
mensagem = 'IgorDummer'  # mensagem do pacote

# quantidade de mensagens a serem enviadas
quantPing = 10

# lista de mensagens atrasadas
atrasados = []
# define o socket
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Tempo máximo de espera: 1 seg
clientSocket.settimeout(1)


def converteMilisegundos(rtt):
    return rtt/1000000


def verificaMensagem(enviada, recebida):
    if len(recebida) != 40:		# Caso a mensagem recebida nao tenha 40 caracteres
        return True
    elif recebida[0:5] != enviada[0:5]:  # Caso o identificador não seja o mesmo
        return True
    elif recebida[5:6] != '1':  # Caso não seja um Ping
        return True
    elif recebida[6:10] != enviada[6:10]:  # Caso o Timestamp nao seja o mesmo
        return True
    elif recebida[10:30] != enviada[10:30]:  # Caso a mensagem do pacote seja diferente
        return True

    return False  # Se respeitar todas as verificações acima


def main():
    pacotesEnviados = 0
    pacotesRecebidos = 0
    rtts = []
    tempoTotal = time.time_ns()
    for i in range(quantPing):
        rtt = time.time_ns()

        # Define o formato do pacote, como especificado no início do código
        id = str(i).rjust(5, '0')
        timestamp = str(int(rtt / 1000000) % 10000).rjust(4, '0')
        msg = str(mensagem).ljust(30, '\0')
        msgFinal = id + '0' + timestamp + msg

        # Envia a mensagem através do socket
        clientSocket.sendto(msgFinal.encode(), (host, port))

        # Incrementa a quantidade de pacotes enviados
        pacotesEnviados = pacotesEnviados + 1

        try:
            # Retorno do servidor
            msgServidor, servidor = clientSocket.recvfrom(40)
            msgServidor = msgServidor.decode()

            idRecebido = int(msgServidor[0:5])
            # Se entrar no while, recebeu pacote atrasado
            while idRecebido < int(msgFinal[0:5]):
                # Realiza o loop até encontrar o pacote
                atrasados.append(
                    (msgServidor,  converteMilisegundos(time.time_ns() - rtt)))
                msgServidor, servidor = clientSocket.recvfrom(40)
                msgServidor = msgServidor.decode()
                idRecebido = int(msgServidor[0:5])

            #rtt = converteMilisegundos((time.time_ns() - rtt))
            rtt = converteMilisegundos(time.time_ns() - rtt)

            # Se verificar e não cumprir com o padrao
            if(verificaMensagem(msgFinal, msgServidor)):
                print('O pacote ' + str(i+1) + ' é inválido.')
                continue

            pacotesRecebidos = pacotesRecebidos + 1
            rtts.append(rtt)

        except:  # Caso tenha excedido o tempo
            print("From " + str(host) + ":" + str(port) +
                  ": udp_seq= " + str(i+1) + " Connection time out")

        else:
            print('40 bytes from ', host, ': icmp_seq=', int(id)+1,
                  'time=', rtt)

    for msg, tempo in atrasados:
        print('40 bytes from ', host, ': icmp_seq=', int(msg[0:5])+1,
              'time=', tempo, '(Delayed package)')

    tempoTotal = converteMilisegundos((time.time_ns() - tempoTotal))

    if pacotesRecebidos != 0:
        pacotesPerdidos = 100 - (pacotesRecebidos/pacotesEnviados*100)
        rttMin = min(rtts)
        rttAvg = mean(rtts)
        rttMax = max(rtts)
        rttStdev = stdev(rtts)
        print('\n --- ' + host + ' ping statistics ---')
        print(str(pacotesEnviados) + ' packets transmitted,', end=' ')
        print(str(pacotesRecebidos) + ' packets received,', end=' ')
        print(str(pacotesPerdidos) + '% packet loss,', end=' ')
        print('time ' + str(tempoTotal) + ' ms', end=' ')
        print('\nrtt min/avg/max/mdev', end=' ')
        print(f'{rttMin:.4}/ ', end='')
        print(f'{rttAvg:.4}/ ', end='')
        print(f'{rttMax:.4}/ ', end='')
        print(f'{rttStdev:.4} ms')

    else:
        print('Nenhum pacote foi recebido.')


if __name__ == "__main__":
    main()

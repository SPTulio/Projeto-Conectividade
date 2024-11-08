import socket as sock
import threading

# dicionario dos clientes conectados, com nome e socket
clientes_conectados = {}

def broadcast(mensagem, cliente_remetente=None, unicast_destinatario=None):
    #se a mensagem for unicast manda so pro destunatario
    if unicast_destinatario:
        try:
            unicast_destinatario.sendall(mensagem.encode())
        except:
            #tira o cliente da lista em caso de erro
            for nome, cliente in list(clientes_conectados.items()):
                if cliente == unicast_destinatario:
                    del clientes_conectados[nome]
                    break
    else:
        #se nao for unicast manda broadcast
        for cliente in clientes_conectados.values():
            if cliente != cliente_remetente:
                try:
                    cliente.sendall(mensagem.encode())
                except:
                    # tira o cliente em caso de erro
                    for nome, cliente_socket in list(clientes_conectados.items()):
                        if cliente_socket == cliente:
                            del clientes_conectados[nome]
                            break

def recebe_dados(sock_cliente, endereço):
    try:
        # adiciona o nome do cliente e o socket no dicionario
        nome = sock_cliente.recv(1024).decode()
        clientes_conectados[nome] = sock_cliente
        print(f"{nome} entrou no chat.")
        
        #faz um broadcast alertando quem entrou no chat
        broadcast(f"{nome} entrou no chat.")
    except:
        print("Erro ao receber o nome do cliente.")
        sock_cliente.close()
        return
    #loop pra checar o recebimento de mensagens
    while True:
        try:
            mensagem = sock_cliente.recv(1024).decode()
            if mensagem:
                if mensagem.startswith('/'):
                    #pega so o nome do comando /nome mensagem
                    try:
                        destinatario, msg = mensagem[1:].split(' ', 1)
                        if destinatario in clientes_conectados:
                            # envia unicast so pra ele
                            mensagem_formatada = f"[Privado de {nome}] {msg}"
                            broadcast(mensagem_formatada, unicast_destinatario=clientes_conectados[destinatario])
                        else:
                            #se o usuario nao existe
                            sock_cliente.sendall(f"[Servidor] Usuário '{destinatario}' não encontrado.".encode())
                    except ValueError:
                        sock_cliente.sendall("[Servidor] Comando inválido. Use: /nomedousuario mensagem".encode())
                else:
                    #mensagem aparecer nome>> mensagem
                    print(f"{nome}>> {mensagem}")
                    broadcast(f"{nome}>> {mensagem}", sock_cliente)
            else:
                #ficar reiniciando o loop enquanto ate chegar msg
                break
        #fechar caso de desconexao ou erro
        except:
            print(f"Erro ao receber mensagem de {nome}... fechando")
            sock_cliente.close()
            del clientes_conectados[nome]
            broadcast(f"{nome} saiu do chat.")
            return

# Configuração do servidor
HOST = '26.114.18.147'
PORTA = 9999

#config host e porta
sock_server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
sock_server.bind((HOST, PORTA))
#coloca o servidor em modo de escuta
sock_server.listen()
print(f"O servidor {HOST}:{PORTA} está aguardando conexões...")

#loop para aceitar varias conexoes
while True:
    #accept retorna ip e porta
    sock_conn, ender = sock_server.accept()
    print(f"Conexão com sucesso do cliente: {ender}")
    # thread para ficar recebendo dados do cliente em loop
    thread_cliente = threading.Thread(target=recebe_dados, args=[sock_conn, ender])
    thread_cliente.start()

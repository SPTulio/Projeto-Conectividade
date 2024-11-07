import socket as sock
import threading

# Lista para armazenar os clientes conectados, incluindo seus nomes e sockets
clientes_conectados = {}

def broadcast(mensagem, cliente_remetente=None, unicast_destinatario=None):
    # Se unicast_destinatario é definido, enviamos a mensagem só para ele
    if unicast_destinatario:
        try:
            unicast_destinatario.sendall(mensagem.encode())
        except:
            # Caso ocorra um erro, o cliente é removido
            for nome, cliente in list(clientes_conectados.items()):
                if cliente == unicast_destinatario:
                    del clientes_conectados[nome]
                    break
    else:
        # Caso contrário, enviamos a mensagem para todos os clientes
        for cliente in clientes_conectados.values():
            if cliente != cliente_remetente:
                try:
                    cliente.sendall(mensagem.encode())
                except:
                    # Remover o cliente se houver um erro ao enviar a mensagem
                    for nome, cliente_socket in list(clientes_conectados.items()):
                        if cliente_socket == cliente:
                            del clientes_conectados[nome]
                            break

def recebe_dados(sock_cliente, endereço):
    try:
        # Recebe o nome do cliente e o adiciona à lista de clientes conectados
        nome = sock_cliente.recv(1024).decode()
        clientes_conectados[nome] = sock_cliente
        print(f"{nome} entrou no chat.")
        
        # Avisa a todos que um novo usuário entrou
        broadcast(f"{nome} entrou no chat.")
    except:
        print("Erro ao receber o nome do cliente.")
        sock_cliente.close()
        return

    while True:
        try:
            mensagem = sock_cliente.recv(1024).decode()
            if mensagem:
                if mensagem.startswith('/'):
                    # Extrai o nome do destinatário e a mensagem
                    try:
                        destinatario, msg = mensagem[1:].split(' ', 1)
                        if destinatario in clientes_conectados:
                            # Envia mensagem unicast
                            mensagem_formatada = f"[Privado de {nome}] {msg}"
                            broadcast(mensagem_formatada, unicast_destinatario=clientes_conectados[destinatario])
                        else:
                            sock_cliente.sendall(f"[Servidor] Usuário '{destinatario}' não encontrado.".encode())
                    except ValueError:
                        sock_cliente.sendall("[Servidor] Comando inválido. Use: /nomedousuario mensagem".encode())
                else:
                    # Mensagem pública para todos
                    print(f"{nome}>> {mensagem}")
                    broadcast(f"{nome}>> {mensagem}", sock_cliente)
            else:
                break
        except:
            print(f"Erro ao receber mensagem de {nome}... fechando")
            sock_cliente.close()
            del clientes_conectados[nome]
            broadcast(f"{nome} saiu do chat.")
            return

# Configuração do servidor
HOST = '26.114.18.147'
PORTA = 9999

sock_server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
sock_server.bind((HOST, PORTA))
sock_server.listen()
print(f"O servidor {HOST}:{PORTA} está aguardando conexões...")

# Loop para aceitar múltiplas conexões
while True:
    sock_conn, ender = sock_server.accept()
    print(f"Conexão com sucesso do cliente: {ender}")
    # Inicia uma nova thread para o cliente
    thread_cliente = threading.Thread(target=recebe_dados, args=[sock_conn, ender])
    thread_cliente.start()

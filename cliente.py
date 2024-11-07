import socket
import threading
import sys

# Configurações do servidor
HOST = '26.114.18.147'
PORTA = 9999

def receive_messages(socket_cliente):
    """Função para receber e exibir mensagens do servidor."""
    while True:
        try:
            mensagem = socket_cliente.recv(1024).decode()
            if mensagem:
                print(mensagem)
            else:
                break
        except:
            print("Conexão com o servidor perdida.")
            break

def main():
    # Conectar ao servidor
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_cliente.connect((HOST, PORTA))

    # Solicitar o nome do usuário e enviá-lo ao servidor
    nome = input("Informe seu nome para entrar no chat: ")
    socket_cliente.sendall(nome.encode())
    
    # Iniciar uma thread para receber mensagens do servidor
    threading.Thread(target=receive_messages, args=(socket_cliente,), daemon=True).start()
    
    print("Conectado ao chat. \nUse /nomedousuario para enviar uma mensagem privada.")
    print("Use /sair para sair do chat.")

    # Loop de envio de mensagens
    while True:
        mensagem = input()
        if mensagem:
            if mensagem == "/sair":
                print("Saindo do chat...")
                socket_cliente.sendall(mensagem.encode())
                socket_cliente.close()
                sys.exit()  # Encerra a execução do cliente
            elif mensagem.startswith('/'):
                try:
                    destinatario, msg = mensagem[1:].split(' ', 1)
                    print(f"[Privado para {destinatario}] {msg}")
                except ValueError:
                    print("[Erro] Comando inválido. Use: /nomedousuario mensagem")
                    continue
            else:
                print(f"[Você] {mensagem}")
            
            # Enviar mensagem ao servidor
            socket_cliente.sendall(mensagem.encode())

if __name__ == "__main__":
    main()

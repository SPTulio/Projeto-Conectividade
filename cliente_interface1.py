import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys

# definir ip e porta
HOST = '26.154.186.237'
PORTA = 9999

# dados do cliente
root = tk.Tk()  #janela
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #cria o socket
entry_nome = None  # campo de nome
entry_mensagem = None  # campo de mensagem
text_area = None  # campo de exibicao mensagens

# criar os widgets
def create_widgets():
    global entry_nome, entry_mensagem, text_area #funcao consegue alterar variaveis fora dela

    #titulo janela
    root.title("Chat Conectividade - Adnan e Sérgio")

    # campo de nome
    frame_nome = tk.Frame(root)
    tk.Label(frame_nome, text="Nome:").pack(side=tk.LEFT)  #label
    #entrada
    entry_nome = tk.Entry(frame_nome, width=20)
    entry_nome.pack(side=tk.LEFT)
    #botao pra conectar
    tk.Button(frame_nome, text="Entrar no Chat", command=connect_to_server).pack(side=tk.LEFT)
    frame_nome.pack(pady=5)  

    #area mensagens
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=15)
    text_area.pack(pady=10)  #rolagem

    #mensagens instrucoes
    text_area.config(state='normal') 
    text_area.insert(tk.END, "Use /nomedousuario para enviar uma mensagem privada.\n")
    text_area.insert(tk.END, "Use /sair para sair do chat.\n")
    text_area.config(state='disabled')  

    # entrada mensagens e enviar
    frame_mensagem = tk.Frame(root)
    entry_mensagem = tk.Entry(frame_mensagem, width=40) #entrada mensagem
    entry_mensagem.pack(side=tk.LEFT, padx=5)
    entry_mensagem.bind("<Return>", lambda event: send_message())  #enviar no enter
    tk.Button(frame_mensagem, text="Enviar", command=send_message).pack(side=tk.LEFT)  #botao de envio
    frame_mensagem.pack(pady=5)

# conectar no servidor
def connect_to_server():
    nome = entry_nome.get()  #nome
    if not nome:  # ve se tem nome digitado
        messagebox.showwarning("Nome Inválido", "Por favor, insira um nome.")
        return

    try:
        # Conecta no ip e na porta
        socket_cliente.connect((HOST, PORTA))
        # envia o nome no servidor
        socket_cliente.sendall(nome.encode())
        # nao deixa editar o nome depois de conectar
        entry_nome.config(state='disabled')

        #thread pra receber em loop as mensagens
        thread_recebe = threading.Thread(target=receive_messages)
        thread_recebe.start()
    except Exception as e:
        #msg de erro conexao
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao servidor: {e}")

#receber mensagens
def receive_messages():
    while True:
        try:
            #tenta receber msg
            mensagem = socket_cliente.recv(1024).decode()  
            if mensagem:
                display_message(mensagem)  #mostrar msg no chat
            else:
                break  # fecha o loop se fechar a conexao
        except:
            #mensagem de erro
            display_message("Conexão com o servidor perdida.")
            break

# mostrar msg no frame de texto
def display_message(mensagem):
    text_area.config(state='normal')  #area de texto disponivel pra edicao
    text_area.insert(tk.END, mensagem + "\n")  # aparece a mensagem no final da area de texto
    text_area.config(state='disabled')  # desabilita edicao da area de texto

# enviar msg p servidor
def send_message():
    mensagem = entry_mensagem.get()  # pega o texto
    if mensagem:
        if mensagem == "/sair":  # se for /sair, sai
            socket_cliente.sendall(mensagem.encode())  #envia a mensagem pro servidor
            socket_cliente.close()  # sai do chat
            root.quit()  # fecha a janela
            root.destroy()  #fecha o loop da janela
            sys.exit()  # encerra o script

        if mensagem.startswith('/'):  # verifica o /nome msg
            try:
                # trata a string
                destinatario, msg = mensagem[1:].split(' ', 1)
                display_message(f"[Privado para {destinatario}] {msg}")  # mostra a msg privada
            except ValueError:
                # tratamento de erro
                display_message("[Erro] Comando inválido. Use: /nomedousuario mensagem")
        else:
            # se nao for privada mostra pra todos
            display_message(f"[Você] {mensagem}")

        #encoda a mensagem e manda pro servidor
        socket_cliente.sendall(mensagem.encode())
        # limpa o input de msg
        entry_mensagem.delete(0, tk.END)

#inicia os widgets
create_widgets()
root.mainloop()  # mantem a janela em loop

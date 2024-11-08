import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys

#definir host e porta
HOST = '26.114.18.147'
PORTA = 9999

#corpo do chat
class Chat:
    def __init__(self, root):
        self.root = root
        #definir nome janela
        self.root.title("Chat Conectividade - Adnan e Sérgio")
        #criar o socket pra conectar no servidor
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #iniciar os widgets
        self.create_widgets()

    def create_widgets(self):
        #criar o campo para nome
        frame_nome = tk.Frame(self.root)
        tk.Label(frame_nome, text="Nome:").pack(side=tk.LEFT)
        self.entry_nome = tk.Entry(frame_nome, width=20)
        self.entry_nome.pack(side=tk.LEFT)
        #botao pra entrar no chat
        tk.Button(frame_nome, text="Entrar no Chat", command=self.connect_to_server).pack(side=tk.LEFT)
        frame_nome.pack(pady=5)

        #area das mensagens
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', width=50, height=15)
        self.text_area.pack(pady=10)

        #instrucoes iniciais
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, "Use /nomedousuario para enviar uma mensagem privada.\n")
        self.text_area.insert(tk.END, "Use /sair para sair do chat.\n")
        self.text_area.config(state='disabled')

        #campo entrada de mensagens
        frame_mensagem = tk.Frame(self.root)
        self.entry_mensagem = tk.Entry(frame_mensagem, width=40)
        self.entry_mensagem.pack(side=tk.LEFT, padx=5)
        self.entry_mensagem.bind("<Return>", lambda event: self.send_message())
        #botao para enviar as mensagens
        tk.Button(frame_mensagem, text="Enviar", command=self.send_message).pack(side=tk.LEFT)
        frame_mensagem.pack(pady=5)

    def connect_to_server(self):
        #confere se tem um nome digitado
        self.nome = self.entry_nome.get()
        if not self.nome:
            messagebox.showwarning("Nome Inválido", "Por favor, insira um nome.")
            return

        try:
            #conectar no servidor
            self.socket_cliente.connect((HOST, PORTA))
            #enviar o nome
            self.socket_cliente.sendall(self.nome.encode())
            #desabilitar o campo nome
            self.entry_nome.config(state='disabled')
            #thread para ficar sempre recebendo mensagens
            thread_recebe = threading.Thread(target=self.receive_messages)
            thread_recebe.start()
            #tratar excessoes e erros e informar ao usuario
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao servidor: {e}")
            return

    def receive_messages(self):
        #loop infinito de receber mensagens
        while True:
            try:
                mensagem = self.socket_cliente.recv(1024).decode()
                if mensagem:
                    self.display_message(mensagem)
                else:
                    break
            #sair caso perca conexao
            except:
                self.display_message("Conexão com o servidor perdida.")
                break

    def display_message(self, mensagem):
        #mensagem na area de texto
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, mensagem + "\n")
        self.text_area.config(state='disabled')

    def send_message(self):
        #pega a mensagem inserida pelo ususario
        mensagem = self.entry_mensagem.get()
        if mensagem:
            #se a mensagem for /sair fecha a conexao
            if mensagem == "/sair":
                self.socket_cliente.sendall(mensagem.encode())
                self.socket_cliente.close()
                self.root.quit()  #fecha a janela do tkinter
                self.root.destroy()
                sys.exit()  #encerra

            #identifica mensagem privada
            if mensagem.startswith('/'):
                try:
                    destinatario, msg = mensagem[1:].split(' ', 1)
                    self.display_message(f"[Privado para {destinatario}] {msg}")
                except ValueError:
                    self.display_message("[Erro] Comando inválido. Use: /nomedousuario mensagem")
            else:
                #exibe mensagem broadcast
                self.display_message(f"[Você] {mensagem}")
            
            #manda a mensagem pro servidor
            self.socket_cliente.sendall(mensagem.encode())
            #limpa o campo de entrada da mensagem
            self.entry_mensagem.delete(0, tk.END)

#abre a janela
root = tk.Tk()
app = Chat(root)
#mantem aberta a janela
root.mainloop()

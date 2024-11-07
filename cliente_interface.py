import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys

# Configurações do servidor
HOST = '26.114.18.147'
PORTA = 9999

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Conectividade - Adnan e Sérgio")
        
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.create_widgets()

    def create_widgets(self):
        frame_nome = tk.Frame(self.root)
        tk.Label(frame_nome, text="Nome:").pack(side=tk.LEFT)
        self.entry_nome = tk.Entry(frame_nome, width=20)
        self.entry_nome.pack(side=tk.LEFT)
        tk.Button(frame_nome, text="Entrar no Chat", command=self.connect_to_server).pack(side=tk.LEFT)
        frame_nome.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', width=50, height=15)
        self.text_area.pack(pady=10)

        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, "Use /nomedousuario para enviar uma mensagem privada.\n")
        self.text_area.insert(tk.END, "Use /sair para sair do chat.\n")
        self.text_area.config(state='disabled')

        frame_mensagem = tk.Frame(self.root)
        self.entry_mensagem = tk.Entry(frame_mensagem, width=40)
        self.entry_mensagem.pack(side=tk.LEFT, padx=5)
        self.entry_mensagem.bind("<Return>", lambda event: self.send_message())
        tk.Button(frame_mensagem, text="Enviar", command=self.send_message).pack(side=tk.LEFT)
        frame_mensagem.pack(pady=5)

    def connect_to_server(self):
        self.nome = self.entry_nome.get()
        if not self.nome:
            messagebox.showwarning("Nome Inválido", "Por favor, insira um nome.")
            return

        try:
            self.socket_cliente.connect((HOST, PORTA))
            self.socket_cliente.sendall(self.nome.encode())
            self.entry_nome.config(state='disabled')
            thread_recebe = threading.Thread(target=self.receive_messages)
            thread_recebe.start()
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao servidor: {e}")
            return

    def receive_messages(self):
        while True:
            try:
                mensagem = self.socket_cliente.recv(1024).decode()
                if mensagem:
                    self.display_message(mensagem)
                else:
                    break
            except:
                self.display_message("Conexão com o servidor perdida.")
                break

    def display_message(self, mensagem):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, mensagem + "\n")
        self.text_area.config(state='disabled')

    def send_message(self):
        mensagem = self.entry_mensagem.get()
        if mensagem:
            if mensagem == "/sair":
                self.socket_cliente.sendall(mensagem.encode())
                self.socket_cliente.close()
                self.root.quit()  # Fecha a janela do Tkinter
                self.root.destroy()
                sys.exit()  # Encerra a execução do cliente

            # Exibe a mensagem localmente antes de enviar
            if mensagem.startswith('/'):
                try:
                    destinatario, msg = mensagem[1:].split(' ', 1)
                    self.display_message(f"[Privado para {destinatario}] {msg}")
                except ValueError:
                    self.display_message("[Erro] Comando inválido. Use: /nomedousuario mensagem")
            else:
                self.display_message(f"[Você] {mensagem}")
            
            # Envia a mensagem ao servidor
            self.socket_cliente.sendall(mensagem.encode())
            # Limpa a entrada de mensagem
            self.entry_mensagem.delete(0, tk.END)

root = tk.Tk()
app = ChatClient(root)
root.mainloop()

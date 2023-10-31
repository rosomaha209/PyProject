import tkinter as tk
import socket
import threading

HOST = "localhost"
PORT = 8080


class ChatClient(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Chat Client")

        self.message_entry = tk.Entry(self)
        self.message_entry.pack()

        self.send_button = tk.Button(self, text="Send", command=self.send_message)
        self.send_button.pack()

        self.chat_box = tk.Text(self)
        self.chat_box.pack()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

        self.thread = threading.Thread(target=self.receive_messages)
        self.thread.start()

    def send_message(self):
        message = self.message_entry.get()

        self.socket.send(message.encode())

        self.chat_box.insert("end", f"[Me] {message}\n")

        self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            message = self.socket.recv(1024).decode()

            self.chat_box.insert("end", f"[Other] {message}\n")


if __name__ == "__main__":
    client = ChatClient()
    client.mainloop()

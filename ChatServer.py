import asyncio
import socket

HOST = "localhost"
PORT = 8080


class ChatServer:
    def __init__(self, loop):
        self.loop = loop
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(5)

    async def handle_connection(self, reader, writer):
        while True:
            data = await reader.read(1024)
            message = data.decode()

            for client in self.clients:
                await client.writer.write(message.encode())

    async def run(self):
        while True:
            connection, address = await self.server.accept()
            print(f"[New connection from {address[0]}]")

            client = ChatClient(self.loop, connection)
            self.clients.append(client)
            await client.start()

    def start(self):
        self.loop.run_until_complete(self.run())


class ChatClient:
    def __init__(self, loop, connection):
        self.loop = loop
        self.connection = connection
        self.writer = connection.writer

    async def start(self):
        while True:
            data = await self.reader.read(1024)
            message = data.decode()

            print(f"[Me] {message}")

    def send(self, message):
        self.writer.write(message.encode())
        self.writer.flush()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    server = ChatServer(loop)
    loop.run_until_complete(server.start())

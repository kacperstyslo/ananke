# Ananke

## Description
This script allows you to connect to the computer remotely using the socket module. Once connected, we can execute commands directly on the remote computer.
Script create revers_tcp connection between computers.

## Setup
On linux
```commandline
    Listening computer: python3 ananke.py -l -p 7777 -c
    Connecting computer: python3 ananke.py -t 192.168.0.2 -p 7777 
```
On Windows
```commandline
    Listening computer: python ananke.py -l -p 7777 -c
    Connecting computer: python ananke.py -t 192.168.0.2 -p 7777 
```



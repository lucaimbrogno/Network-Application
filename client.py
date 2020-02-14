'''
Luca Imbrogno 160319390 - kwon3110
Jonathon Kwon 106593110 - Imbr9390
'''
import socket
import threading
import sys
import time


disconnected = False
flag = True
def receive_data(socket, signal):
    while signal:
        try:
            data = socket.recv(1024)

            if data.decode('utf-8') == "DISCONNECT":
                global disconnected
                disconnected = True
                print('Disconnecting from server...')
                s.close()

            else:
                print(str(data.decode("utf-8")))
                print()
        except:
            print("You have been disconnected from the server")
            signal = False
            break



#Provide user menu to select options from
print(''' 
1-connect
2-disconnect
3-POST
4-GET
5-PIN
6-UNPIN
7-CLEAR
''')
print()

try:
    user_selection = int(input("Select #: "))
    while user_selection != 1:
        print("Must connect with server first (1-connect)")
        user_selection = int(input("Enter 1 to start connection with server: "))

    host = input("Enter the host address: ")
    port = int(input("Enter port # to be used: "))


except ValueError:
    print("Cannot accept non-int types - must select from client menu")
    input("Enter 'quit' to restart client and try again: ")
    sys.exit(0)


while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        print('Connected to server')
        s.sendall(str.encode("1"))

        msg = s.recv(1024).decode('utf-8')
        print(msg)
        break
    except:
        print("Error - please check your host address and port #")
        host = input("Re-enter the host address: ")
        port = int(input("Re-enter port # to be used: "))



threads = []
data_thread = threading.Thread(target = receive_data, args = (s, True))
data_thread.start()
threads.append(data_thread)


options = ['1', '2', '3', '4', '5', '6', '7']
while not disconnected:
    print(''' 
    1-connect
    2-disconnect
    3-POST
    4-GET
    5-PIN
    6-UNPIN
    7-CLEAR
    ''')
    user_selection2 = input("Select #: ")
    if user_selection2 not in options:
        print("Error invalid selection or did not pick a valid number option - try again")
        user_selection2 = input()
        s.sendall(str.encode(user_selection2))
    else:
        s.sendall(str.encode(user_selection2))
    message = input()
    if message == '':
        message = 'EMPTY'
    s.sendall(str.encode(message))
    time.sleep(0.3)  #time delay



'''
Luca Imbrogno 160319390 - kwon3110
Jonathon Kwon 106593110 - Imbr9390
'''
import socket
import threading
from threading import Lock
import sys
import os
from random import randint
import time


NOTE_ID = 0
notes_dict = {}
pinned_notes = []
pin_locations = []
board_width = 0
board_height = 0
board_colours = []
clients_connected = []
lock = threading.RLock()



class Note:
    def __init__(self, nid, x, y, width, height, color, msg, pin_counter):
        self.nid = nid
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.msg = msg
        self.pin_counter = pin_counter

def get_notes(color_condition, coord_condition, string_condition):
    notes_set = []
    for key, value in notes_dict.items():
        # check if color condition satisfies
        if color_condition is None or value.color == color_condition:

            upper_x = value.x + value.width
            upper_y = value.y + value.height
            # check if coordinate is contained
            if coord_condition is None or (coord_condition[0] >= value.x and coord_condition[0] <= upper_x and coord_condition[1] >= value.y and coord_condition[1] <= upper_y):
                # check if string is contained in message
                if string_condition is None or string_condition in value.msg:
                    notes_set.append(value)
    return notes_set

def close():
    socket.shutdown(socket.SHUT_RDWR)
    socket.close()
    print ("closed")


class Client(threading.Thread):
    def __init__(self, socket, address, connected):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.connected = connected

    def run(self):
        lock.acquire()
        self.socket.sendall(str.encode("You now have access to edit the board and interact with the server"))

        global NOTE_ID
        while self.connected:
            try:
                selection = str(self.socket.recv(1024).decode('utf-8'))
                data = str.encode("connecting")
                if selection != '1':
                    data = self.socket.recv(1024)

            except:
                print("Client " + str(self.address) + " has disconnected")
                self.connected = False
                clients_connected.remove(self)
                break

            if data != "":
                decoded_data = str(data.decode("utf-8"))
                if selection == '1':
                    string = "Board Size: " + str(board_width) + "x" + str(board_height) + ", Color Options: " + str(board_colours)
                    self.socket.sendall(str.encode(string))
                elif selection == '2':
                    if decoded_data == 'DISCONNECT':
                        print("Client " + str(self.address) + " has disconnected")
                        self.connected = False
                        clients_connected.remove(self)
                        i = 0
                        self.socket.sendall(str.encode("DISCONNECT"))
                    else:
                        error = 'Invalid Request'
                        self.socket.sendall(str.encode(error))

                elif selection == '3':       #POST COMMAND
                    print('POST Request:')
                    data_array = decoded_data.split(' ')
                    if data_array[0] == 'EMPTY':
                        error = "No statement found"
                        self.socket.sendall(str.encode(error))
                    else:
                        print(data_array)

                        try:
                            command = data_array[0]
                            x = int(data_array[1])
                            y = int(data_array[2])
                            note_width = int(data_array[3])
                            note_height = int(data_array[4])
                            upper_x = x + note_width
                            upper_y = y + note_height
                            color = data_array[5]
                            note_msg = ''


                            if command != 'POST' or command is None or command == ' ':
                                error = "Key word POST missing"
                                self.socket.sendall(str.encode(error))
                            elif x > board_width or x is None or upper_x > board_width or y > board_height or y is None or upper_y > board_height:
                                error = "Cannot post note outside board dimensions - please try again"
                                self.socket.sendall(str.encode(error))
                            elif color not in board_colours or color is None:
                                error = "Note colour not acceptable"
                                self.socket.sendall(str.encode(error))
                            else:
                                for i in range(6, len(data_array)):
                                    note_msg = note_msg + data_array[i]
                                    if i < len(data_array)-1:
                                        note_msg = note_msg + ' '

                                if note_msg == '' or note_msg == ' ':
                                    error = "Cannot have empty note message - please include a message"
                                    self.socket.sendall(str.encode(error))
                                else:
                                    new_note = Note(NOTE_ID, int(x), int(y), int(note_width), int(note_height), color, note_msg, 0)
                                    error = ''
                                    for key,values in notes_dict.items():
                                        if new_note.msg == values.msg:
                                            error = "Note already exists"
                                            break
                                    if error == '':
                                        notes_dict[NOTE_ID] = new_note
                                        success = "Note has been posted"
                                        self.socket.sendall(str.encode(success))
                                        NOTE_ID += 1
                                        print(notes_dict)
                                    else:
                                        self.socket.sendall(str.encode(error))

                        except ValueError:    #if they input some unknown string as POST message
                            error = "Invalid statement"
                            self.socket.sendall(str.encode(error))
                        except IndexError:
                            error = "Incomplete statement found"
                            self.socket.sendall(str.encode(error))
                        except RuntimeError:
                            error = "Cannot release a locked lock"
                            self.socket.sendall(str.encode(error))

                elif selection == '4':
                    try:
                        data_array = decoded_data.split(' ')
                        if data_array[1] == 'PINS':
                            if len(pin_locations) == 0:
                                error = 'Error no pins available'
                                self.socket.sendall(str.encode(error))
                            else:
                                t = []
                                for pin in pin_locations:
                                    t.append(str(pin))
                                self.socket.sendall(str.encode("Pin Locations -->"))
                                for i in t:
                                    self.socket.sendall(str.encode(i))

                        else:
                            color = None
                            coord = None
                            reference_string = None

                            if '=' not in data_array[1]:
                                error = "No proper GET parameters found"
                                self.socket.sendall(str.encode(error))
                            else:
                                for i in range(0, len(data_array)):
                                    if '=' in data_array[i]:
                                        if data_array[i].split('=')[0] == 'color':
                                            color = data_array[i].split('=')[1]
                                        elif data_array[i].split('=')[0] == 'refersTo':
                                            reference_string = data_array[i].split('=')[1]
                                        else:
                                            # next two elements are the coordinates
                                            coord = [int(data_array[i + 1]), int(data_array[i + 2])]

                                valid_notes = get_notes(color, coord, reference_string)

                                i = 0
                                if len(valid_notes) == 0:
                                    self.socket.sendall(str.encode("No notes found with those parameters"))
                                else:
                                    for note in valid_notes:
                                        self.socket.sendall(str.encode("Note successfully found --> "))
                                        note_to_client = "Note " + str(i) + ': ' + ' ' + note.msg
                                        self.socket.sendall(str.encode(note_to_client))
                                        i+=1

                    except ValueError:  # if they input some unknown string as GET message
                        error = "Invalid statement"
                        self.socket.sendall(str.encode(error))
                    except IndexError:
                        error = "Incomplete statement found"
                        self.socket.sendall(str.encode(error))

                elif selection == '5':
                    try:
                        command = decoded_data.split(' ')[0]
                        pin_coords = decoded_data.split(' ')[1].split(',')
                        pin_tuple = (pin_coords[0], pin_coords[1])
                        pin_locations.append(pin_tuple)
                        pin_x = int(pin_coords[0])
                        pin_y = int(pin_coords[1])
                        print(pin_locations)

                        if command != 'PIN' or command is None or command == ' ':
                            error = "Key word PIN missing"
                            self.socket.sendall(str.encode(error))

                        elif pin_x > board_width or pin_x is None or pin_y > board_height or pin_y is None:
                            error = "Cannot place pin outside board dimensions - please try again"
                            self.socket.sendall(str.encode(error))

                        else:
                            for key, value in notes_dict.items():
                                upper_x = value.x + value.width
                                upper_y = value.y + value.height
                                if pin_x >= value.x and pin_y >= value.y and pin_x <= upper_x and pin_y <= upper_y:
                                    value.pin_counter += 1
                                    if value not in pinned_notes:
                                        pinned_notes.append(value)
                            self.socket.sendall(str.encode("Pin has been placed"))
                            print(pinned_notes)
                    except ValueError:
                        error = "Invalid statement"
                        self.socket.sendall(str.encode(error))

                    except IndexError:
                        error = "Incomplete statement found"
                        self.socket.sendall(str.encode(error))


                elif selection == '6':
                    try:
                        command = decoded_data.split(' ')[0]
                        pin_coords = decoded_data.split(' ')[1].split(',')
                        pin_tuple = (pin_coords[0], pin_coords[1])
                        pin_x = int(pin_coords[0])
                        pin_y = int(pin_coords[1])
                        if command != 'UNPIN' or command is None or command == ' ':
                            error = 'keyword UNPIN is missing'
                            self.socket.sendall(str.encode(error))

                        elif pin_tuple not in pin_locations:
                            error = "There are no pins currently at this location - please try again"
                            self.socket.sendall(str.encode(error))

                        else:
                            pin_locations.remove(pin_tuple)
                            for key, value in notes_dict.items():
                                upper_x = value.x + value.width
                                upper_y = value.y + value.height
                                if pin_x >= value.x and pin_y >= value.y and pin_x <= upper_x and pin_y <= upper_y and value.pin_counter > 0:
                                    value.pin_counter -= 1
                                    if value.pin_counter == 0:
                                        pinned_notes.remove(value)
                            self.socket.sendall(str.encode("Pin has been removed"))
                            print(pinned_notes)

                    except ValueError:
                        error = "Invalid statement"
                        self.socket.sendall(str.encode(error))

                    except IndexError:
                        error = "Incomplete statement found"
                        self.socket.sendall(str.encode(error))

                elif selection == '7':
                    if decoded_data != 'CLEAR' or decoded_data is None or decoded_data == ' ':
                        error = 'Key word CLEAR is missing'
                        self.socket.sendall(str.encode(error))

                    else:
                        notes_dict.clear()
                        pinned_notes.clear()
                        pin_locations.clear()
                        self.socket.sendall(str.encode("Cleared Board"))
                        print(notes_dict)
                        print(pinned_notes)
                        print(pin_locations)
            else:
                error = "No statement found"
                self.socket.sendall(str.encode(error))
                #print(error)

        lock.release()
        quit = input("Do you want to close the server? If yes enter: close, if no enter: no : ")
        if quit == 'close':
            os._exit(0)
            #sys.exit()



def new_clients(socket):
    while True:
        s, address = socket.accept()
        clients_connected.append(Client(s, address, True))
        clients_connected[len(clients_connected) - 1].start()
        print("New connection at ID " + str(clients_connected[len(clients_connected) - 1]))


def main():
    params = sys.argv   #read in command line arguements
    global board_width
    global board_height
    host = "127.0.0.1"
    port = int(params[1])
    board_width = int(params[2])
    board_height = int(params[3])
    i = 4
    global board_colours
    #print(len(params))
    while i <= len(params)-1:    #loop through to get the rest of the colours
        board_colours.append(params[i])
        i+=1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("Listening for clients")
    s.listen(5)

    threads = []
    new_client_thread = threading.Thread(target=new_clients, args=(s,))
    time.sleep(3)
    new_client_thread.start()
    threads.append(new_client_thread)
    for t in threads:
        t.join()


    #sys.exit(0)


main()



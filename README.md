# Network-Application

This is a simple client-server network application in Python created for my networking class. The server holds a board which manages
the placement of notes. The user will specify the size of the board, note colors, host address and port number on initialization. 
Using the commands, the user is able to post, pin, unpin, and remove notes as well as request to view notes based on certain query 
parameters.

To use the application you should start by running the server file using this command which initializes the board:

python server.py 4554 dimension_x dimension_y color_option1 color_option2 color_option3

- 4554 is the port number, you will need this when connecting from the client side
- replace dimension_x and dimension_y with some integers representing the size of the board (ex. 200 100)
- replace color_options with your choice of colors, you can specify as many colors as you like

To connect with a client start up the client file with: python client.py

Further instructions on how to interact with the notes and board can be found in the documentation.pdf file.

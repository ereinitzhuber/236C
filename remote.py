from __future__ import print_function
from inputs import get_gamepad
import socket

#Port and IP of ESP32 running server
ESP_IP = "" #YOUR ESP32 IP
ESP_PORT = # YOUR ESP32 PORT

#Button mappings
A_BUTTON = "BTN_SOUTH"
B_BUTTON = "BTN_EAST"
C_BUTTON = "BTN_WEST"
D_BUTTON = "BTN_NORTH"

#Joystick mappings   -1 = UP, 1 = DOWN, 0 = NEUTRAL
JOYSTICK_Y_AXIS = "ABS_HAT0Y"
Y_UP = -1
Y_DOWN = 1
Y_NEUTRAL = 0
#Joystick mappings   -1 = LEFT, 1 = RIGHT, 0 = NEUTRAL
JOYSTICK_X_AXIS = "ABS_HAT0X"
X_LEFT = -1
X_RIGHT = 1
X_NEUTRAL = 0

#Class to handle joystick state via 4 boolean values
class Joystick:
    def __init__(self):
        self.isUp = False
        self.isDown = False
        self.isLeft = False
        self.isRight = False
        self.next = 0

    #Computes next input based on existing state and next input from stick and stores in self.next
    def computeNext(self, nextInput):

        #Set motion states based on given code
        if nextInput == 4:
            self.isLeft = True
        elif nextInput == 6:
            self.isRight = True
        elif nextInput == 8:
            self.isUp = True
        elif nextInput == 2:
            self.isDown = True
        elif nextInput == 15:
            self.isLeft = False
            self.isRight = False
        elif nextInput == 25:
            self.isUp = False
            self.isDown = False

        #Compute next code based on existing and current values
        if self.isRight and self.isDown:
            self.next = 3
        elif self.isRight and self.isUp:
            self.next = 9
        elif self.isRight:
            self.next = 6
        elif self.isLeft and self.isDown:
            self.next = 1
        elif self.isLeft and self.isUp:
            self.next = 7
        elif self.isLeft:
            self.next = 4
        elif self.isUp:
            self.next = 8
        elif self.isDown:
            self.next = 2

    #Returns next code from stick
    def get_next(self):
        return self.next

#Updates the buffer and sends updated buffer to ESP32
def updateandsend(code, state, buffer, stick):
    next = ' '
    #Determine if button was pressed
    if code == A_BUTTON and state == 1:
        next = 'A'
    elif code == B_BUTTON and state == 1:
        next = 'B'
    elif code == C_BUTTON and state == 1:
        next = 'C'
    elif code == D_BUTTON and state == 1:
        next = 'D'
    
    #Determine if joystick was moved and if so send relevant input code to Joystick class instance.
    elif code == JOYSTICK_X_AXIS:
        if state == X_LEFT:
            stick.computeNext(4)
            next = stick.get_next()
        elif state == X_RIGHT:
            stick.computeNext(6)
            next = stick.get_next()
        elif state == X_NEUTRAL:
            stick.computeNext(15)
            #If Left or Right is pressed and next character is A/B/C/D we don't want to send the code twice
            if buffer[4] != '6' and buffer[4] != '4' and not buffer[4].isalpha():
                next = stick.get_next()
    elif code == JOYSTICK_Y_AXIS:
        if state == Y_UP:
            stick.computeNext(8)
            next = stick.get_next()
        elif state == Y_DOWN:
            stick.computeNext(2)
            next = stick.get_next()
        elif state == Y_NEUTRAL:
            stick.computeNext(25)
            #If Up or Down is pressed and next character is A/B/C/D we don't want to send the code twice
            if buffer[4] != '8' and buffer[4] != '2' and not buffer[4].isalpha():
                next = stick.get_next()


    if next != ' ':
        #Shift all values in the buffer to the left one and place the new code at the end
        tosend = ''.join(buffer)
        tosend = tosend[1:5] + str(next)
        buffer = [char for char in tosend] 
        #Send the updated 5 character buffer to the ESP32
        sock.sendto(tosend.encode(), (ESP_IP, ESP_PORT))
    
    #Pass updated buffer back to caller
    return buffer


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
buffer = [' ', ' ', ' ', ' ', ' ',]
stick = Joystick()

#Main loop. Get single event from controller and calls updateandsend()
while True:
    events = get_gamepad()
    for event in events:
        if event.ev_type != "Sync":
            buffer = updateandsend(event.code, event.state, buffer, stick)


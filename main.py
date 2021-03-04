import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200)

ser.isOpen()

print('Connection Successful\nEnter Commands below:\nType "exit" to close connection')

input = 1
while 1:
    #get keyboard input
    input = raw_input(">> ")
    if input == 'exit':
        ser.close()
        exit()
    else:
        #Send input to Prusa
        #Prusa accepts \n line termination as well as \r\n
        ser.write(input + '\n')
        out = ''
        #wait for response, 0.5 seconds seems sufficient, might be able to go lower
        time.sleep(0.5)
        
        # Wait for response
        while ser.inWaiting() > 0:
            out += ser.read(1)
        
        if out != '':
            print ">>" + out
        else:
            print "No response"

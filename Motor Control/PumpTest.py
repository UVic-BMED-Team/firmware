from adafruit_motorkit import MotorKit
import time
kit = MotorKit()

cmd = ""

while cmd != "exit":
    cmd = input(">>")
    
    if cmd=="s":
        prevThrot = 0
        while cmd != "q":
            t0 = time.time()
            cmd = input("Enter throttle value, q to exit cmd: ")
            if(cmd != prevThrot):
                kit.motor1.throttle = cmd
                t1 = time.time()
                print("Motor ran for " + (t1-t0) + " seconds at throttle of " +  prevThrot)
                prevThrot = cmd
        kit.motor1.throttle = 0

    elif cmd == "t":
        cmd = input("Enter throttle value for test: ")
        kit.motor1.throttle = cmd
        #sleep for a minute
        time.sleep(60)
        kit.motor1.throttle = 0
    elif cmd == "h":
        print("Command Descriptions:\n")
        print("q - Quits the program\n")
        print("s - starts the pump and allows for throttle adjustments")
        print("t - starts the pump at a constant throttle value, runs for a minute and automatically turns off")
    else:
        print("Invalid Command, use q to quit, s to start pump, t to do mL/min test, h for help")


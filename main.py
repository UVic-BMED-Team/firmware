import serial.tools.list_ports
import time


def main():
    baud_rate = 115200
    timeout = 5
    com_port_name = "/dev/ttyACM0"
    g_code_file_name = ""
    ser = serial.Serial(com_port_name, baud_rate, timeout)

    f = open(g_code_file_name, 'r')
    g_code_cmds = f.read().split('\n')

    for line in g_code_cmds:
        ser.write(line + "\r\n")
        time.sleep(1)
        print(ser.read())
        input("Press Enter to send the next command:")


if __name__ == '__main__':
    main()


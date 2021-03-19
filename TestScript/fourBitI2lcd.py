# -*- coding: utf-8 -*-
#edited to accomodate 4bit lcd operation 

from time import sleep
import fourBitlcdconst
from pca9535 import PCA9535
from statusflag import DelayWaiter, BusyLoop

def _checkPos(function):
    def _f(*args):
		obj = args[0]
		if args[1] >= obj.cols or args[1] < 0:
	    	raise ValueError('Column {0} is not between 0-{0}.'.format(args[1], obj.cols - 1))

		if args[2] >= obj.rows or args[2] < 0:
	    	raise ValueError('Row {0} is not between 0-{0}.'.format(args[2], obj.rows - 1))

		return function(*args)
    return _f

class I2LCD(object):
    memaddr = {	6  : {1: [0x00], },
                8  : {1: [0x00], 2: [0x40]},
				12 : {4: [0x00, 0x40, 0x0C, 0x4C]},
				16 : {0: [0x00], 1 : [0x00, 0x40], 2 : [0x00, 0x40], 4 : [0x00, 0x40, 0x10, 0x50]},
	        	20 : {2 : [0x00, 0x40], 4 : [0x00, 0x40, 0x14, 0x54]},
				24 : {2 : [0x00, 0x40]},
				40 : {2 : [0x00, 0x40]},
				}

    def __init__(self, bus, address, cols, rows):
		self.iface = PCA9535(bus, address)

		if not self.memaddr.has_key(cols):
	    	raise NotImplementedError
		if not self.memaddr[cols].has_key(rows):
	    	raise NotImplementedError

		self.rowsaddress = self.memaddr[cols][rows]
		self.cols = 16 if rows == 1 else cols
		self.rows = 2 if rows == 1 else rows if rows else 1
		self.column = 0
		self.row = 0
		self.control = 0x00
		self.setControl(self.control, 0)
		self.iface.setPortDir(lcdconst.CPORT, lcdconst.DB4 | lcdconst.DB5 | lcdconst.DB6 | lcdconst.DB7)
		self.iface.setPortDir(lcdconst.DPORT, 0x00)
		self.wait = DelayWaiter(self)
		self.iface.setPortOutput(lcdconst.DPORT, 0x00)

		self.control |= self.iface.getPortOutput(lcdconst.CPORT)
		self.setControl(self.control, 1)
		self.commands = {lcdconst.CLEAR_DISPLAY : 0,
					lcdconst.CURSOR_HOME : 0,
					lcdconst.ENTRY_MODE_SET : 0,
					lcdconst.DISPLAY_ONOFF : 0,
					lcdconst.CURSOR_DISPLAY_SHIFT : 0,
					lcdconst.FUNCTION_SET : 0,
					lcdconst.SET_CGRAM_ADDRESS : 0,
					lcdconst.SET_DDRAM_ADDRESS : 0}
		self.waitflag = 0

    def __del__(self):
		self.close()

	#display off
	def close(self):
		self.command(lcdconst.DISPLAY_ONOFF, 0x00)
		self.iface.setPortDir(lcdconst.CPORT, 0xFF)
		self.iface.setPortDir(lcdconst.DPORT, 0xFF)

    def setControl(self, control, value):
		self.control = (self.control | control) if value else (self.control & ~control)
		self.iface.setPortOutput(lcdconst.CPORT, self.control)

    def setDirection(self, direction):
		self.iface.setPortDir(lcdconst.DPORT, direction)

	def fourBit(self, value):
		# returns: fourBit[0] = high bits, fourBit[1] = low bits
		high = value & 0xF0
		low = (value<<4) & 0xF0
		return (high, low)

	#sends single byte before 4bit mode is implemented
 	def eightBitCommand(self, command, value):
		while (self.waitflag and self.readStatus()[0]):
			continue
		data = command | value
		self.setControl(lcdconst.RS | lcdconst.RW, 0)
		self.setControl(lcdconst.EN, 1)
		self.iface.setPortOutput(lcdconst.DPORT, data)
		self.setControl(lcdconst.RS | lcdconst.RW | lcdconst.EN, 0)
		self.commands[command] = value

	#sends byte as two consecutive 4bit values
    def command(self, command, value):
		while (self.waitflag and self.readStatus()[0]):
			continue
		data = command | value
		self.setControl(lcdconst.RS | lcdconst.RW, 0)
		self.setControl(lcdconst.EN, 1)
		self.iface.setPortOutput(lcdconst.DPORT, self.fourBit(data)[1]) #send high bits
		self.setControl(lcdconst.EN, 0)	
		sleep(0.000001)					# wait for bits to be recieved
		self.setControl(lcdconst.EN, 1)	
		self.iface.setPortOutput(lcdconst.DPORT, self.fourBit(data)[0]) #send low bits
		self.setControl(lcdconst.RS | lcdconst.RW | lcdconst.EN, 0) 
		self.commands[command] = value

	#Checks busy flag
    def readStatus(self):
		self.setControl(lcdconst.RS, 0)
		self.setControl(lcdconst.RW, 1)
		self.setDirection(0xFF)
		self.setControl(lcdconst.EN, 1)
		ret = self.iface.getPortInput(lcdconst.DPORT)
		self.setControl(lcdconst.RS | lcdconst.RW | lcdconst.EN, 0)
		self.setDirection(0x00)
		return (ret & lcdconst.BF, ret & ~lcdconst.BF)

    def writeByte(self, value):
		self.fourBit(value)
		self.setControl(lcdconst.RS, 1)
		self.setControl(lcdconst.RW, 0)
		self.setControl(lcdconst.EN, 1)
		self.iface.setPortOutput(lcdconst.DPORT, self.fourBit(data)[1])
		self.setControl(lcdconst.EN, 0)
		sleep(0.000001)
		self.setControl(lcdconst.EN, 1)
		self.iface.setPortOutput(lcdconst.DPORT, self.fourBit(data)[0])
		self.setControl(lcdconst.RS | lcdconst.RW | lcdconst.EN, 0)

    def writeBlock(self, values):
		self.setControl(lcdconst.RS, 1)
		self.setControl(lcdconst.RW, 0)
		for b in values:
			self.setControl(lcdconst.EN, 1)
			self.iface.setPortOutput(lcdconst.DPORT, b)
			self.iface.setPortOutput(lcdconst.DPORT, self.fourBit(b)[1])
			self.setControl(lcdconst.EN, 0)
			sleep(0.000001)
			self.setControl(lcdconst.EN, 1)
			self.iface.setPortOutput(lcdconst.DPORT, self.fourBit(b)[0])
		self.setControl(lcdconst.RS | lcdconst.RW | lcdconst.EN, 0)

	#not sure if read functions work the same in 4bit mode?
    def readDataByte(self):
		self.setControl(lcdconst.RS, 1)
		self.setControl(lcdconst.RW, 1)
		self.setDirection(0xFF)
		self.setControl(lcdconst.EN, 1)
		ret = self.iface.getPortInput(lcdconst.DPORT)
		self.setControl(lcdconst.RS | lcdconst.RW | lcdconst.EN, 0)
		self.setDirection(0x00)
		return ret

	#not sure if read functions work the same in 4bit mode?
    def readRow(self, row):
		self.command(lcdconst.SET_DDRAM_ADDRESS, self.rowsaddress[row])
		self.setControl(lcdconst.RS, 1)
		self.setControl(lcdconst.RW, 1)
		self.setDirection(0xFF)
		ret = ""
		for i in range(self.cols):
			self.setControl(lcdconst.EN, 1)
			ret += chr(self.iface.getPortInput(lcdconst.DPORT))
			self.setControl(lcdconst.EN, 0)
		self.setControl(lcdconst.RS | lcdconst.RW, 0)
		self.setDirection(0x00)
		self.setCursor(self.column, self.row)
		return ret

    @_checkPos
    def setCursor(self, column, row):
		row %= self.rows
		column %= self.cols
		self.column = column
		self.row = row
		address = self.rowsaddress[row]+column
		self.command(lcdconst.SET_DDRAM_ADDRESS, address)

    def clear(self):
		self.command(lcdconst.CLEAR_DISPLAY, 0x00)
		self.column = 0
		self.row = 0

    def home(self):
		self.command(lcdconst.CURSOR_HOME, 0x00)
		self.column = 0
		self.row = 0

    def setGC(self, number, definition):
		self.command(lcdconst.SET_CGRAM_ADDRESS, ((number & 0x07) << 3))
		self.writeBlock(definition)

    def fprint(self, string):
		column = self.column
		row = self.row

		for i, line in enumerate(string.rstrip().split('\n')):
			self.command(lcdconst.SET_DDRAM_ADDRESS, self.rowsaddress[row]+column)
			wrap = textwrap.wrap(line, self.cols if column == 0 else self.cols - column)
			for j, txt in enumerate(wrap):
			self.writeBlock([ord(c) for c in txt])
			column += len(txt)
			if column >= self.cols:
				column = 0
				row = (row + 1) % self.rows
				self.command(lcdconst.SET_DDRAM_ADDRESS, self.rowsaddress[row]+column)
			if i > 0:
			column = 0
			row = (row + 1) % self.rows
		self.column = column % self.cols
		self.row = row

    def init(self):
	
		self.eightBitCommand(lcdconst.FUNCTION_SET, lcdconst.FS_DL) #should send 0b0011----
		sleep(0.045)
		self.eightBitCommand(lcdconst.FUNCTION_SET, lcdconst.FS_DL)
		sleep(0.05)
		self.eightBitCommand(lcdconst.FUNCTION_SET, 0x00)	#4bit mode: send 0b0010----
		sleep(0.045)
		self.command(lcdconst.DISPLAY_ONOFF, 0x00) #Display off, cursor off, blinking off
		sleep(0.045)
		self.command(lcdconst.CLEAR_DISPLAY, 0x00)
		sleep(0.06)
		self.command(lcdconst.ENTRY_MODE_SET, lcdconst.EMS_ID) #Increment by 1, no shift
		sleep(0.3)
		self.command(lcdconst.DISPLAY_ONOFF, lcdconst.DOO_D) #Display ON
		sleep(0.6)
		self.waitflag = 1

    def blink(self, value):
		self.command(lcdconst.DISPLAY_ONOFF, (self.commands[lcdconst.DISPLAY_ONOFF] | lcdconst.DOO_B) if value else (self.commands[lcdconst.DISPLAY_ONOFF] & (~lcdconst.DOO_B)))

    def cursor(self, value):
		self.command(lcdconst.DISPLAY_ONOFF, (self.commands[lcdconst.DISPLAY_ONOFF] | lcdconst.DOO_C) if value else (self.commands[lcdconst.DISPLAY_ONOFF] & (~lcdconst.DOO_C)))

    def display(self, value):
		self.command(lcdconst.DISPLAY_ONOFF, (self.commands[lcdconst.DISPLAY_ONOFF] | lcdconst.DOO_D) if value else (self.commands[lcdconst.DISPLAY_ONOFF] & (~lcdconst.DOO_D)))

    def __test(self):
		self.iface.setPortDir(lcdconst.CPORT, 0x00)
		self.iface.setPortDir(lcdconst.DPORT, 0x00)
		self.iface.setPortOutput(lcdconst.CPORT, 0x00)
		self.iface.setPortOutput(lcdconst.DPORT, 0x00)
		ports = {lcdconst.CPORT: {0 : "E", 1 : "R/W", 2 : "R/S", 3 : "IRS", 4 : "PC", 5 : "UD", 6 : "CCS", 7 : "BCS"},
			lcdconst.DPORT: {0 : "D0", 1 : "D1", 2 : "D2", 3 : "D3", 4 : "D4", 5 : "D5", 6 : "D6", 7 : "D7"}}
		for port, bits in ports.iteritems():
			for bit, label in bits.iteritems():
			print "Port {0}; Bit {1}; Label {2}".format(port, bit, label)
			self.iface.setPortOutput(port, 1 << bit)
			self.wait(0.5)
			self.iface.setPortOutput(port, 0x00)

		self.iface.setPortOutput(lcdconst.CPORT, 1 | 2 | 4)
		self.wait(3)
		self.iface.setPortOutput(lcdconst.CPORT, 0x00)
		self.iface.setPortOutput(lcdconst.DPORT, 0xFF)
		self.wait(3)
		self.iface.setPortOutput(lcdconst.DPORT, 0x00)

		self.iface.setPortDir(lcdconst.CPORT, 0xFF)
		self.iface.setPortDir(lcdconst.DPORT, 0xFF)

		self.iface.setPortOutput(lcdconst.CPORT, 1 | 2 | 4)
		self.wait(1)
		self.iface.setPortOutput(lcdconst.CPORT, 0x00)

		self.iface.setPortOutput(lcdconst.DPORT, 0xFF)
		self.wait(1)
		self.iface.setPortOutput(lcdconst.DPORT, 0x00)
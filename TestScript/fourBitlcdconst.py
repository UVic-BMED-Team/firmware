#Control/Data ports numbers
CPORT = 0
DPORT = 1

#Control port bits meaning

RS = 1 << 1
RW = 1 << 2
E = 1 << 3
DB4 = 1 << 4
DB5 = 1 << 5
DB6 = 1 << 6
DB7 = 1 << 7

#LCD instructions
CLEAR_DISPLAY = 1
CURSOR_HOME = 1 << 1
ENTRY_MODE_SET = 1 << 2
DISPLAY_ONOFF = 1 << 3
CURSOR_DISPLAY_SHIFT = 1 << 4
FUNCTION_SET = 1 << 5

#Values of instructions above
#ENTRY MODE SET
EMS_S = 1		#1 - Shift display
EMS_ID = 1 << 1	#0 - Dec cursor, 1 - inc cursor pos
    
#DISPLAY ON OFF
DOO_B = 1		#1 - Blink ON, 0 - Blink OFF
DOO_C = 1 << 1	#1 - Cursor ON, 0 - Cursor OFF
DOO_D = 1 << 2	#1 - Display ON, 0 - Display OFF
    
    #CURSOR DISPLAY SHIFT
CDS_RL = 1 << 2	#1 - shift right, 0 - shift left
CDS_SC = 1 << 3	#1 - shift display, 0 - move cursor

#FUNCTION SET
FS_F = 1 << 2	#1 - 5x10 dots, 0 - 5x8 dots
FS_N = 1 << 3	#1 - 2 lines, 0 - 1 line
FS_DL = 1 << 4	#1 - 8 bit interface, 0 - 4 bit interface

#BUSY FLAG
BF = 1 << 7		#1 - busy, 0 - can accept instruction
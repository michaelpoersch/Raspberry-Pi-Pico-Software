# DM8BA10
# 10x16 Segment Display with HT1622 driver

import machine
import time

# index in this library is from right to left!

LCD_COMMAND = 0b00000100
LCD_WRITE   = 0b00000101

# Bytes to write for decimal place positions 1-9 from the right
LCD_DPBITS = [0x0100, 0x0200, 0x0400, 0x0001, 0x0002, 0x0004, 0x0100, 0x0200, 0x0400]
# Bytes to write for ASCII character set (partial)

LCD_CHAR_MAPPING = {
    ' ': 0b0000000000000000,
    #      FEDCBA9876543210
    '~': 0b1111111111111111,
    '*': 0b0101110001011100,
    '+': 0b0001010001001000,
    ',': 0b0000100000000000,
    '-': 0b0001000000001000,
    '/': 0b0000100000010000,
    '"': 0b0000000001100000,
    '#': 0b0001010101101011,
    '_': 0b0000000100000001,
    '^': 0b1110000000000100, 
    '>': 0b0100100000000000,
    '<': 0b0000000000010100,
    #      FEDCBA9876543210
    '0': 0b1010101110110011,
    '1': 0b0000000000100010,
    '2': 0b1001001110101001,
    '3': 0b1001000110101011,
    '4': 0b0011000000101010,
    '5': 0b1100000110001011,
    '6': 0b1011001110001011,
    '7': 0b1000000010100010,
    '8': 0b1011001110101011,
    '9': 0b1011000110101011,
    #      FEDCBA9876543210
    'A': 0b1011001010101010,
    'B': 0b1000010111101011,
    'C': 0b1010001110000001,
    'D': 0b1000010111100011,
    'E': 0b1011001110001001,
    'F': 0b1011001010001000,
    'G': 0b1010001110001011,
    'H': 0b0011001000101011,
    'I': 0b1000010111000001,
    'J': 0b0000001100100011,
    #      FEDCBA9876543210
    'K': 0b0011001000010100,
    'L': 0b0010001100000001,
    'M': 0b0110001000110010,
    'N': 0b0110001000100110,
    'O': 0b1010001110100011,
    'P': 0b1011001010101000,
    'Q': 0b1010001110100111,
    'R': 0b1011001010101100,
    'S': 0b1011000110001011,
    'T': 0b1000010011000000,
    #      FEDCBA9876543210
    'U': 0b0010001100100011,
    'V': 0b0010101000010000,
    'W': 0b0010101000100110,
    'X': 0b0100100000010100,
    'Y': 0b0100010000010000,
    'Z': 0b1000100110010001,
    #      FEDCBA9876543210
    '$': 0b1011010111001011,
    '@': 0b1011001101100011,
    '=': 0b0001000100001001,
    '(': 0b0000000000010100,
    ')': 0b0100100000000000,
    '{': 0b0001010011000001,
    '}': 0b1000010101001000,
    '?': 0b1000010010101000,
    '%': 0b1011010001001011,
    #      FEDCBA9876543210
    'a': 0b0001001100000111,
    'b': 0b0011001100001011,
    'c': 0b0001001100001001,
    'd': 0b0001001100101011,
    'e': 0b0001101100000001,
    'f': 0b0000100000011000,
    'g': 0b0000000100001111,
    'h': 0b0011001000001010,
    'i': 0b0000010000000000,
    'j': 0b0000000100000011,
    #      FEDCBA9876543210
    'k': 0b0011001000001100,
    'l': 0b0010001000000000,
    'm': 0b0001011000001010,
    'n': 0b0001001000001010,
    'o': 0b0001001100001011,
    'p': 0b0111001000000000,
    'q': 0b0111000000000100,
    'r': 0b0001001000001000,
    's': 0b0000000100001101,
    't': 0b0001000001001100,
    #      FEDCBA9876543210
    'u': 0b0000001100000011,
    'v': 0b0000101000000000,
    'w': 0b0000101000000110,
    'x': 0b0001110000001000,
    'y': 0b0000000100000111,
    'z': 0b0001100100000001
    #      FEDCBA9876543210
}

class DM8BA10:
    
    def __init__(self, data_pin, wr_pin, cs_pin):
        self._data = machine.Pin(data_pin, machine.Pin.OUT)
        self._wr = machine.Pin(wr_pin, machine.Pin.OUT)
        self._cs = machine.Pin(cs_pin, machine.Pin.OUT)

        self._cs.value(1)
        self._wr.value(0)
        self._data.value(0)

        self.sendcmd(0x02)  # SYS_EN
        self.sendcmd(0x30)  # RC_32K
        self.sendcmd(0x06)  # LCD_ON

    # sends up to 8 bits to the LCD
    def sendbits(self, value, n):
        #print(f'send value {value} in {n} bits')
        bits = ''
        for i in range(n - 1, -1, -1):
            self._data.value(bool(value & (1 << i)))
            self._wr.value(1)
            self._wr.value(0)
            bits += str(int(bool(value & (1 << i))))
        self._data.value(0)

    # sends command 100 and 9 bits of command
    def sendcmd(self, cmd):
        self._cs.value(0)
        self.sendbits(LCD_COMMAND, 3)
        self.sendbits(cmd, 9)
        self._cs.value(1)

    # sends command 101 (Write mode) followed by an address and then 4 bits of data
    def writemode(self, idx, data):
        addr = idx << 2
        # each segment is divided into 4
        for i in range(0, 4):
            dval = ((data << (i * 4)) >> 12) & 0x0F
            self._cs.value(0)   # enable read
            self.sendbits(LCD_WRITE, 3)
            self.sendbits(addr + i, 6)
            self.sendbits(dval, 4)
            self._cs.value(1)   # disable read

    def off(self):
        self.sendcmd(0x04)  # LCD_OFF

    def on(self):
        self.sendcmd(0x06)  # LCD_ON

    def clear(self):
        for i in range(0, 12):  # 0-9 are the character locations, 10-11 are decimals
            self.writemode(i, 0x0000)

    def allon(self):
        for i in range(0, 12):
            self.writemode(i, 0xFFFF)

    # inserts a decimal place
    def dp_insert(self, i):
        if i < 1:
            self.writemode(10, 0)
            self.writemode(11, 0)
        elif i < 4:
            self.writemode(10, 0)
            self.writemode(11, LCD_DPBITS[i - 1])
        elif i < 10:
            self.writemode(10, LCD_DPBITS[i - 1])
            self.writemode(11, 0)
        else:
            self.writemode(10, 0)
            self.writemode(11, 0)

    # deletes decimal places
    def dp_clear(self):
        self.writemode(10, 0x0000)
        self.writemode(11, 0x0000)

    # display an integer number
    def printint(self, n):
        self.clear()
        s = str(n)
        idx = 0
        for c in reversed(s):
            self.writemode(idx, LCD_CHAR_MAPPING.get(c, 0x0000))
            idx = idx + 1

    # display a single character
    def printchar(self, idx, c):
        self.writemode(idx, LCD_CHAR_MAPPING.get(c, 0x0000))

    # display text
    def printtext(self, s):
        idx = 10 - len(s)
        for c in reversed(s):
            self.printchar(idx, c)
            idx = idx + 1

    # scroll text
    def scrolltext(self, s, t):
        s1 = s + ' ' 
        for i in range(len(s1)):
            self.printtext(s1[i:i+9])
            time.sleep(t)
            
    # rotor :-)
    def rotor(self, idx, cnt, t):
        for _ in range(cnt):
                           #      FEDCBA9876543210
            self.writemode(idx, 0b0000010001000000)
            time.sleep(t)
            self.writemode(idx, 0b0000100000010000)
            time.sleep(t)
            self.writemode(idx, 0b0001000000001000)
            time.sleep(t)
            self.writemode(idx, 0b0100000000000100)
            time.sleep(t)
        # clear at the end
        self.writemode(idx, 0b0000000000000000)


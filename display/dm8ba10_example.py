from dm8ba10.DM8BA10 import DM8BA10
import time

def main():
    print('main starts....')
    myLCD = DM8BA10(data_pin=20, wr_pin=21, cs_pin=22)
    myLCD.clear()
    
    myLCD.scrolltext('The quick brown fox jumps over the lazy dog', 0.1)

    for i in range(0, 10):
        myLCD.dp_insert(i)
        time.sleep(0.1)
    myLCD.dp_insert(0) # clear DP

    myLCD.printtext('-->   <--')
    myLCD.rotor(5, 5, 0.2)
    
    myLCD.clear()

main()


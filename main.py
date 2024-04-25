#!/bin/python3
"""Стартовый модуль."""
import clock
 
from machine import Pin, Timer, RTC
import tm1637

#! SEG_A = 0b00000001
#! SEG_B = 0b00000010
#! SEG_C = 0b00000100
#! SEG_D = 0b00001000
#! SEG_E = 0b00010000
#! SEG_F = 0b00100000
#! SEG_G = 0b01000000

#          11->A
#        ---------
# 10->F |   5->G  | 7->B
#        ---------  
#  1->E |         | 4->C
#        --------- 
#          2->D

#! DIGITS_SET = [0b00000110, 0b01011011, 0b01001111, 0b01100110, 0b01101101, 0b01111101 ]

#! HELLO2 = [0b01110110, 0b00111000, 0b00111000, 0b0011111, 0, 0]
#! HELLO3 = [0b00111000, 0b00111000, 0b01110110, 0, 0, 0b0011111]
#! HELLO4 = [0b00111000, 0b01111001, ]
#! H = 0b01110110
#! E = 0b01111001
#! L = 0b00111000
#! O = 0b00111111

#! !HELLO = [H, E, L, L, O, 0]

#! DIGIT1 = 3
#! DIGIT2 = 2

# 321654
def reorder(input_array):
    """Переставляет знаки в массиве в соответствии с дикой адресацией дисплея."""
    output_array = []
    output_array.append(input_array[2])
    output_array.append(input_array[1])
    output_array.append(input_array[0])
    output_array.append(input_array[5])
    output_array.append(input_array[4])
    output_array.append(input_array[3])
    return output_array


#! def test():
    
#!  clock_pin = Pin(0)
#!    dio_pin = Pin(4)
#!    tm = tm1637.TM1637(clk=clock_pin, dio=dio_pin)
#!    tm.write([0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000])
#!    tm.write(reorder(clock.START_MSG))
#!    tm.write([0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000])
    

def main():

    app = clock.CPerfectClock()
#    app.run()
#    if clock.DEBUG:
        
#        print("Terminated.")

# *** Если это главный модуль и отладка выключена..
if (__name__ == '__main__'):
    
    # *** Стартуем программу автоматически
    main()


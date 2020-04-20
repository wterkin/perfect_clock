#!/bin/python3

from machine import Pin
import timers
from time import sleep

# *** Константы ESP
GPIO_LIST = (16, 5, 4, 0, 2, 14, 12, 13, 15)

# *** Константы конфига
LATCH = "latch"
CLOCK = "clock"
SERIAL = "serial"
BLINK_PIN = 5

DIGITS = (int('00111111', 2), # 0
          int('00001100', 2), # 1
          int('01011011', 2), # 2
          int('01011110', 2), # 3
          int('01101100', 2), # 4
          int('01110110', 2), # 5
          int('01110111', 2), # 6
          int('00011100', 2), # 7
          int('11111111', 2), # 8
          int('11111110', 2)  # 9
         )
#          11->A
#        ---------
# 10->F |   5->G  | 7->B
#        ---------  
#  1->E |         | 4->C
#        --------- 
#          2->D
# StArt         
START_MSG = (int("01110110", 2), # S
             int("01100011", 2), # t
             int("11111101", 2), # A
             int("00110001", 2), # r
             int("01100011", 2), # t
            )

class CPerfectClock():
    """Основной класс."""

    def __init__(self, pdc_сonfig):
        """Конструктор."""

        self.config = pdc_сonfig
        # *** Моргающий светодиод
        self.blink_led_state = False
        self.blink_led = Pin(GPIO_LIST[BLINK_PIN], Pin.OUT)
        self.blink_timer = timers.create_timer(1000, self.blink)
        # *** Сдвиговый регистр
        self.clock_pin = Pin(GPIO_LIST[self.config[CLOCK]])
        self.latch_pin = Pin(GPIO_LIST[self.config[LATCH]])
        self.latch_pin.off()
        self.serial_pin = Pin(GPIO_LIST[self.config[SERIAL]])
        self.shift_out(START_MSG)
        
    def shift_out(p_data):
        
        for bit in range(0, 8):
            
            l_value = p_data & (1 << (7-bit))
            self.serial_pin.value(l_value)
            self.clock_pin.off()
            self.clock_pin.on()
        self.latch_pin.on()    
            
    def blink(self, some_param):
        """ Моргание светодиодом."""

        if self.blink_led_state is True:
            
            self.blink_led.off()
            self.blink_led_state = False
        else:
            
            self.blink_led.on()    
            self.blink_led_state = True


    def run(self):
        """Основной цикл."""

        while True:

            pass
            


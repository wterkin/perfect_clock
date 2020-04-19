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

class CPerfectClock():
    """Основной класс."""

    def __init__(self, pdc_сonfig):
        """Конструктор."""

        self.config = pdc_сonfig
        self.blink_led_state = False
        self.blink_led = Pin(GPIO_LIST[BLINK_PIN], Pin.OUT)
        # print("@__init__")
        self.blink_timer = timers.create_timer(1000, self.blink)

    def blink(self):
        """ Моргание светодиодом."""

        # print("@blink")
        if self.blink_led_state is True:
            
            # print("-")
            self.blink_led.off()
            self.blink_led_state = False
        else:
            
            #print("+")
            self.blink_led.on()    
            self.blink_led_state = True

    def run(self):
        """Основной цикл."""

        while True:

            pass
            


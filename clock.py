#!/bin/python3

from machine import Pin
import timers

# *** Константы ESP
GPIO_LIST = (16, 5, 4, 0, 2, 14, 12, 13, 15)

# *** Константы конфига
LATCH = "latch"
CLOCK = "clock"
SERIAL = "serial"
BLINK_PIN = 5

class CPerfectClock():
    """Основной класс."""
    def __init(pdc_сonfig):
        """Конструктор."""

        self.config = pdc_сonfig
        self.blink_led_state = False
        self.blink_led = Pin(GPIO_LIST[BLINK_PIN],machine.Pin.OUT)
        # self.blink_timer = create_timer(1000, blink)
        pass

    def blink():
        """ Моргание светодиодом."""

        if self.led_state is True:
            pin.off()
            self.led_state = False
        else:
            pin.on()    
            self.led_state = True

    def run(self):
        """Основной цикл."""
        try:
            
            while True:
                
                blink()    
                sleep(0.5)
                pass
        except:
            
            pass
            # self.blink_timer.deinit()

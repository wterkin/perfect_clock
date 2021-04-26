#!/bin/python3

import gc
import time
from time import sleep
import esp
import machine
from machine import Pin, Timer, RTC
import network
import ntptime
import utime
import tm1637

try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct


# *** Константы ESP
GPIO_LIST = (16, 5, 4, 0, 2, 14, 12, 13, 15)

# *** Константы конфига
LATCH = "latch"
CLOCK = "clock"
SERIAL = "serial"
BLINK_PIN = 1
CONNECTED_PIN = 4

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

WORK_PERIOD = 60*1000
DEBUG = True


class CPerfectClock():
    """Основной класс."""

    def __init__(self, pdc_сonfig):
        """Конструктор."""

        print("__init__")
        self.exit_flag = False
        self.config = pdc_сonfig
        # *** Моргающий светодиод
        self.blink_led_state = False
        self.blink_led = Pin(GPIO_LIST[BLINK_PIN], Pin.OUT)
        self.blink_timer = timers.create_timer(1, self.callback_blink, 1000)
        # *** Светодиод соединения с сетью Wi-Fi
        self.connected_led = Pin(GPIO_LIST[CONNECTED_PIN])
        # *** Если мы в отладочном режиме - выставляем таймер на выход
        if DEBUG:
            
            self.terminate_timer = timers.create_timer(2, self.callback_terminate, WORK_PERIOD)
        # *** Создаем объект tm1637
        clock_pin = Pin(GPIO_LIST[self.config["clock.CLOCK"]])
        dio_pin = Pin(GPIO_LIST[self.config["clock.DIO"]])
        self.timemachine = tm1637.TM1637(clk=clock_pin, dio=dio_pin)
        self.timemachine.write(START_MSG)
        # *** Соединяемся с сетью Wi-Fi
        self.estabilish_connection()
       
       
    def callback_blink(self, some_param):
        """ Функция обратного вызова для моргания светодиодом."""

        if DEBUG:
    
            print("*", end="")
           
        if self.blink_led_state is True:
            
            self.blink_led.off()
            self.blink_led_state = False
        else:
            
            self.blink_led.on()    
            self.blink_led_state = True
            

    def callback_terminate(self, some_param):
        """Функция обратного вызова для остановки программы."""

        self.exit_flag = True
        if DEBUG:

            print("Terminate program.")
        self.terminate_timer.deinit()
        self.blink_timer.deinit()


    def estabilish_connection(self):
        """ Процедура осуществляет соединение с выбранной сетью Wi-Fi """

        self.connected_led.off()
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

        if not self.wlan.isconnected():

            self.wlan.connect(self.config["clock.SSID"], self.config["clock.PASSWORD"])
            while not self.wlan.isconnected():

                pass
        self.connected_led.on()

    def synchronize():
        """ Процедура синхронизирует системные часы с NTP сервером """

        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1b
        addr = socket.getaddrinfo('pool.ntp.org', 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
        s.close()
        val = struct.unpack("!I", msg[40:44])[0]
        tm = utime.localtime(val - NTP_DELTA)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        machine.RTC().datetime(tm)



    def run(self):
        """Основной цикл."""
        print("Main loop.")
        while not self.exit_flag:
         
             
            if self.exit_flag:
                
                print("Stopping...")
                break
        return None


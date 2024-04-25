#!/bin/python3

import timers
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
import sys

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

# *** Конфигурация
BLINK_PIN = 1
DISPLAY_DIO_PIN = 2
DISPLAY_CLOCK_PIN = 3
NETWORK_SSID = "icemobile"
NETWORK_PASS = "dex12345"
WORK_PERIOD = 180*1000
DEBUG = False
BLINK_TIMER = 1
TERMINATE_TIMER = 2
CLOCK_TIMER = 4
UTC_DIFF = 3
NTP_DELTA = 3155673600
TRY_COUNT = 50
#          11->A
#        ---------
# 10->F |   5->G  | 7->B
#        ---------  
#  1->E |         | 4->C
#        --------- 
#          2->D
EMPTY_DISPLAY = [0, 0, 0, 0, 0, 0]

#                HGFEDCBA
FAIL_MSG = (int('01110001', 2), # F
            int('01110111', 2), # A
            int('00000110', 2), # I
            int('00111000', 2), # L
            0,
            0)  


DIGITS = (int('00111111', 2), # 0
          int('00000110', 2), # 1
          int('01011011', 2), # 2
          int('01001111', 2), # 3
          int('01100110', 2), # 4
          int('01101101', 2), # 5
          int('01111101', 2), # 6
          int('00000111', 2), # 7
          int('01111111', 2), # 8
          int('01101111', 2)  # 9
         )

DIGITS_DOT = (int('10111111', 2), # 0
              int('10000110', 2), # 1
              int('11011011', 2), # 2
              int('11001111', 2), # 3
              int('11100110', 2), # 4
              int('11101101', 2), # 5
              int('11111101', 2), # 6
              int('10000111', 2), # 7
              int('11111111', 2), # 8
              int('11101111', 2)  # 9
         )

START_MSG = (int("01101101", 2), # S
             int("01111000", 2), # t
             int("01110111", 2), # A
             int("00110001", 2), # r
             int("01111000", 2), # t
             0            
            )

CONNECT_MSG = (int('00111001', 2), # C
               int('00111111', 2), # o
               int('00110111', 2), # n
               int('00110111', 2), # n
               int('01111001', 2), # e
               int('00111001', 2)) # c

SUCCESS_MSG = (int("01101101", 2), # S
               int('00111110', 2), # U
               int('00111001', 2), # C
               int('00111001', 2), # C
               int('01111001', 2), # E
               int("01101101", 2)) # S
             

class CPerfectClock():
    """Основной класс."""

    def __init__(self):
        """Конструктор."""

        self.digits = EMPTY_DISPLAY
        self.exit_flag = False
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        # *** Если мы в отладочном режиме - выставляем таймер на выход
        if DEBUG:
            
            self.terminate_timer = timers.create_timer(TERMINATE_TIMER, self.callback_terminate, WORK_PERIOD)
        # *** Создаем объект tm1637
        clock_pin = Pin(GPIO_LIST[DISPLAY_CLOCK_PIN])
        dio_pin = Pin(GPIO_LIST[DISPLAY_DIO_PIN])
        self.timemachine = tm1637.TM1637(clk=clock_pin, dio=dio_pin)
        self.timemachine.write(EMPTY_DISPLAY)
        self.clock_timer = None
        self.timemachine.write(self.reorder(CONNECT_MSG))
        # *** Соединяемся с сетью Wi-Fi
        print("\n ******** 0007")
        if self.connect():

            self.timemachine.write(self.reorder(SUCCESS_MSG))
            self.synchronize()
            self.clock_timer = timers.create_timer(CLOCK_TIMER, self.callback_clock, 1000)
        else:

            self.timemachine.write(self.reorder(FAIL_MSG))
            sys.exit()
    

    def read_time(self):
        """Читает время в переменные класса."""

        date_time = time.localtime()
        self.hours = date_time[3] + UTC_DIFF
        if self.hours > 23:

            self.hours = hours - 24
        self.minutes = date_time[4]
        self.seconds = date_time[5]


    def tick(self):
        """Пересчитывает время на секунду вперед."""

        if self.seconds < 59:
            
            self.seconds += 1
        else:
        
            self.seconds = 0
            if self.minutes < 59:
                
                self.minutes += 1
            else:
                
                self.minutes = 0
                if self.hours < 23:
                    
                    self.hours += 1
                else:
                
                    self.hours = 0


    def callback_clock(self, some_param):
        """Функция обратного вызова для часов."""
        
        self.tick()
            
        # *** 0. десятки минут
        self.digits[0] = DIGITS[self.minutes//10]
        # *** 1. часы
        self.digits[1] = DIGITS_DOT[self.hours%10]
        # *** 2. десятки часов
        self.digits[2] = DIGITS[self.hours//10]
        # *** 3. секунды
        self.digits[3] = DIGITS[self.seconds%10]
        # *** 4. десятки секунд
        self.digits[4] = DIGITS[self.seconds//10]
        # *** 5. минуты
        self.digits[5] = DIGITS_DOT[self.minutes%10]
        # *** Выводим.
        self.timemachine.write(self.digits)
        if self.seconds == 59:
            
            self.read_time()
        if self.minutes == 59:

            if self.wlan.isconnected():

                self.synchronize()
            else:

                if self.connect():
                
                    self.synchronize()
                else:

                    sys.exit()


    def callback_terminate(self, some_param):
        """Функция обратного вызова для остановки программы."""

        self.exit_flag = True
        if DEBUG:

            print("Terminate program.")
        self.terminate_timer.deinit()
        if self.clock_timer is not None:

            self.clock_timer.deinit()

    def connect(self):
        """Соединяемся с интернетом."""

        connected = False
        
        for try_number in range(TRY_COUNT):

            # print(try_number, NETWORKS[SSID_IDX], NETWORKS[PWD_IDX])
            if self.estabilish_connection():
                    
                connected = True
                break
            if connected:
            
                break
        return connected        
    

    def estabilish_connection(self):
        """ Процедура осуществляет соединение с выбранной сетью Wi-Fi """

        self.wlan = network.WLAN(network.STA_IF)
        if not self.wlan.isconnected():
            
            print(f"Connecting to {NETWORK_SSID} with pass {NETWORK_PASS}")
            self.wlan.active(True)
            self.wlan.connect(NETWORK_SSID, NETWORK_PASS)
            if not self.wlan.isconnected():
                print("Fail.")
            return self.wlan.isconnected()
        return True
 
    def synchronize(self):
        """ Процедура синхронизирует системные часы с NTP сервером """

        self.NTP_QUERY = bytearray(48)
        self.NTP_QUERY[0] = 0x1b
        server_address = socket.getaddrinfo('pool.ntp.org', 123)[0][-1]
        net_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        net_socket.settimeout(1)
        res = net_socket.sendto(self.NTP_QUERY, server_address)
        msg = net_socket.recv(48)
        net_socket.close()
        val = struct.unpack("!I", msg[40:44])[0]
        tm = utime.localtime(val - NTP_DELTA)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        machine.RTC().datetime(tm)
        self.read_time()


    def reorder(self, input_array):
        """Переставляет знаки в массиве в соответствии с дикой адресацией диспл"""
        output_array = []
        output_array.append(input_array[2])
        output_array.append(input_array[1])
        output_array.append(input_array[0])
        output_array.append(input_array[5])
        output_array.append(input_array[4])
        output_array.append(input_array[3])
        return output_array


#    def run(self):
#        """Основной цикл."""
##        print("Main loop.")
#        while not self.exit_flag:
#
#            if self.exit_flag:
#
#                print("Stopping...")
#                break
#        return None

# import os;os.rename("clock.py", "_clock.py");print("reset ESP!!!")

#!/bin/python3

import timers
import gc
import time
from time import sleep
import esp
import machine
import network
import ntptime
import utime
import tm1637
import sys
import ujson

try:

    import usocket as socket
except:

    import socket
try:

    import ustruct as struct
except:

    import struct

# *** Константы ESP
GPIO_LIST = (16, 5, 4, 0, 2, 14, 12, 13, 15, 3, 1)

# *** Конфигурация
# BLINK_PIN = 7
HALT_BUTTON_PIN = 0
MOTION_LED_PIN = 1
DISPLAY_DIO_PIN = 2
DISPLAY_CLOCK_PIN = 3
PIR_PIN = 4

CREDENTIAL_FILE = "credential"
WORK_PERIOD = 360*1000
BLINK_TIMER = 1
TERMINATE_TIMER = 2
CLOCK_TIMER = 4
CLOCK_TIMER_PERIOD = 1000
DEBUG = True
UTC_DIFF = 3
NTP_DELTA = 3155673600
TRY_COUNT = 5
TRY_SLEEP = 1  # sec
DISPLAY_TIME = 10  # sec
GLOBAL_DEBUG: bool = True
MOTION_FLAG: bool = False
SYNCHRONIZE_TIME: int = 1
#          11->A
#        ---------
# 10->F |   5->G  | 7->B
#        ---------  
#  1->E |         | 4->C
#        --------- 
#          2->D
#                H  G  F  E  D  C  B  A

EMPTY_DISPLAY = [0, 0, 0, 0, 0, 0]

DARK_TABLE = (int('00000000', 2),
              int('00000000', 2),
              int('00000000', 2),
              int('00000000', 2),
              int('00000000', 2),
              int('00000000', 2))  


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
             
TRY_MSG = [int("01111000",2),  # t
           int("00110001",2),  # r
           int("01101110",2),  # y
           0,
           0,
           0]


def debug(pmsg: str):

	print(pmsg)


def motion_detector(pin):
        
    debug("*** Motion detected! ***")
    global MOTION_FLAG
    MOTION_FLAG = True


class CPerfectClock():
    """Основной класс."""

    def __init__(self):
        """Конструктор."""
        debug(" *** __init__")
        self.digits = EMPTY_DISPLAY
        self.exit_flag = False
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        self.refresh = False
        self.display_time = DISPLAY_TIME
        self.motion_detected = False
		self.ssid = ""
        self.pass = ""
        # *** Если мы в отладочном режиме - выставляем таймер на выход
        if DEBUG:
            
            self.terminate_timer = timers.create_timer(TERMINATE_TIMER, self.callback_terminate, WORK_PERIOD)
            cred_file = open("cred_test", "r")
            
        else:
       
            cred_file = open("credential", "r")
        json = cred_file.read()
        cred_file.close()
        credential = ujson.load(json)
        self.ssid = credential["ssid"] 
        self.pass = credential["pass"] 
        
        # *** Светодиод должен загораться при срабатывании детектора движения
        self.motion_led_pin = machine.Pin(GPIO_LIST[MOTION_LED_PIN], machine.Pin.OUT)

        # *** Кнопка для остановки таймера
        self.halt_button = machine.Pin(GPIO_LIST[HALT_BUTTON_PIN], machine.Pin.IN)

        # *** Создаем объект tm1637
        clock_pin = machine.Pin(GPIO_LIST[DISPLAY_CLOCK_PIN], machine.Pin.OUT)
        dio_pin = machine.Pin(GPIO_LIST[DISPLAY_DIO_PIN], machine.Pin.OUT)
        self.timemachine = tm1637.TM1637(clk=clock_pin, dio=dio_pin)
        self.timemachine.write(EMPTY_DISPLAY)
        
        # *** Датчик движения
        self.pir_sensor = machine.Pin(GPIO_LIST[PIR_PIN], machine.Pin.IN)
        self.pir_sensor.irq(trigger=machine.Pin.IRQ_RISING, handler=motion_detector)
        
        self.clock_timer = None
        self.display(CONNECT_MSG)
        
        # *** Соединяемся с сетью Wi-Fi
        if self.connect():
            
            self.display(SUCCESS_MSG)
            self.synchronize()
            self.clock_timer = timers.create_timer(CLOCK_TIMER, self.callback_clock, CLOCK_TIMER_PERIOD)
        else:

            self.display(FAIL_MSG)
            sys.exit()
    
    def indicate(self):
        """Функция выводит текущее время на индикатор."""

        # *** Кодируем текущее время для индицирования
        # * Минуты
        self.digits[0] = DIGITS[self.minutes//10]
        # * 1. часы
        if self.refresh:
            
            self.digits[1] = DIGITS_DOT[self.hours%10]
        else:
            
            self.digits[1] = DIGITS[self.hours%10]      
        # * 2. десятки часов
        self.digits[2] = DIGITS[self.hours//10]
        # * 3. секунды
        self.digits[3] = DIGITS[self.seconds%10]
        # * 4. десятки секунд
        self.digits[4] = DIGITS[self.seconds//10]
        # * 5. минуты
        self.digits[5] = DIGITS[self.minutes%10]

        # *** Выводим.
        self.timemachine.write(self.digits)


    def read_time(self):
        """Читает время в переменные класса."""
    
        debug(" *** read_time ")
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
        global MOTION_FLAG
        # *** Пересчитываем время
        self.tick()
        
        # *** Проверим, не нажата ли кнопка остановки?
        if self.halt_button.value() == 0:

            print("*** Terminated!!! ")
            self.clock_timer.deinit()
            self.terminate_timer.deinit()

        if MOTION_FLAG:

			# *** Если индикация выключена.
            if self.display_time == 0:

                MOTION_FLAG = False
                debug("On!")
                self.display_time = DISPLAY_TIME
                self.motion_led_pin.value(1)

    	if self.display_time > 0:

            self.display_time -=1
            if 	self.display_time == 0:

                debug("Off!")
                self.motion_led_pin.value(0)
                self.display(DARK_TABLE)

            else:

                self.indicate()
            
        
        # *** Каждую минуту получаем время из системных часов
        if self.seconds == 59:
            
            self.read_time()

        # *** По наступлении 11-й минуты запрашиваем время по ntp   
        # if self.minutes % 11 == 0 and self.seconds == 11:
        if self.minutes == SYNCHRONIZE_TIME and self.seconds == SYNCHRONIZE_TIME:

     		# *** Если соединение установлено...
            if self.wlan.isconnected():

				# *** .. получаем время с NTP сервера...
                self.synchronize()
            else:

				# *** .. иначе соединяемся с сетью...
                if self.connect():
                
					# *** .. если удачно - получаем время..
                    self.synchronize()
                else:

					# *** Если нет - увы...
                    self.callback_terminate("")
                    sys.exit()


    def callback_terminate(self, some_param):
        """Функция обратного вызова для остановки программы."""

        debug(" *** callback_terminate")
        self.exit_flag = True
        self.terminate_timer.deinit()
        if self.clock_timer is not None:

            self.clock_timer.deinit()


    def connect(self):
        """Соединяемся с интернетом."""
        debug(" *** connect ")
        connected = False
        for try_number in range(TRY_COUNT):

            msg = TRY_MSG
            msg[4] = DIGITS[try_number+1]
            self.display(msg)
            if self.estabilish_connection():
                    
                connected = True
                break
            else:     

                sleep(TRY_SLEEP)
            if connected:
            
                break
        return connected        
    

    def estabilish_connection(self):
        """ Процедура осуществляет соединение с выбранной сетью Wi-Fi """
        debug(" *** estabilish_connection ")
    
        self.wlan = network.WLAN(network.STA_IF)
        if not self.wlan.isconnected():
            
            debug(f"Connecting to {NETWORK_SSID} with pass {NETWORK_PASS}")
            self.wlan.active(True)
            self.wlan.connect(self.ssid, self.pass)
            debug(self.wlan.ifconfig())
            if not self.wlan.isconnected():
                
                debug("Fail.")
            return self.wlan.isconnected()
        return True
 

    def synchronize(self):
        """ Процедура синхронизирует системные часы с NTP сервером """
        debug(" *** synchronize ")        
    
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
        self.refresh = not self.refresh
        debug(" *** Synced!! ")


    def display(self, text):
        """Выводит информацию на табло."""
        debug(" *** display ")        
        buffer = []
        if len(text) == 6:

            buffer.append(text[2])
            buffer.append(text[1])
            buffer.append(text[0])
            buffer.append(text[5])
            buffer.append(text[4])
            buffer.append(text[3])
            self.timemachine.write(buffer)
        else:
     
            debug("Incorrect length of text!")    

#!/bin/python3
"""Стартовый модуль."""
import clock
 
# *** Конфигурация
CONFIG = {clock.DIO: 2,
          clock.CLOCK: 3,
          clock.SSID: "darKraiNXX",
          clock.PASSWORD: "_7xDsk0_36!7"
          }


def estabilish_connection():
    """ Процедура осуществляет соединение с выбранной сетью Wi-Fi """

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():

        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():

            pass
    g_conn_led.on()


def main():

    app = clock.CPerfectClock(CONFIG)
    app.run()
    if clock.DEBUG:
        
        print("Terminated.")


# *** Если это главный модуль и отладка выключена..
if (__name__ == '__main__'): # and not clock.DEBUG:
    
    # *** Стартуем программу автоматически
    main()


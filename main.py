#!/bin/python3
"""Стартовый модуль."""
import clock
 
from machine import Pin, Timer, RTC
import tm1637
  

def main():

    app = clock.CPerfectClock()

# *** Если это главный модуль и отладка выключена..
if (__name__ == '__main__'):
    
    # *** Стартуем программу автоматически
    main()


#!/bin/python3
"""Стартовый модуль."""
import clock
 
# *** Конфигурация
CONFIG = {clock.LATCH: 7,
          clock.CLOCK: 8,
          clock.SERIAL: 6}


def main():

    app = clock.CPerfectClock(CONFIG)
    app.run()

    

if __name__ == '__main__':

    main()

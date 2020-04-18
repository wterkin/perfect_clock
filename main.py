#!/bin/python3
"""Стартовый модуль."""
 import clock
 
# *** Конфигурация
CONFIG = {clock.LATCH: 7,
          clock.CLOCK: 8,
          clock.SERIAL: 6}


if __name__ == '__main__':
    app = CPerfectClock(CONFIG)
    app.run()

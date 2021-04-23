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


# *** Если это главный модуль и отладка выключена..
if (__name__ == '__main__') and not clock.DEBUG:
    
    # *** Стартуем программу автоматически
    main()

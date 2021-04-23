#!/bin/python3

from machine import Timer


def create_timer(pi_timer, po_func=None, pi_period=1000):
    """Создает и запускает свободный таймер."""

    if pi_timer not in (3,5,6):

        lo_timer = Timer(pi_timer)
        lo_timer.init(mode=Timer.PERIODIC,
                      period=pi_period,
                      callback=po_func)
        return lo_timer
    else:

        return None


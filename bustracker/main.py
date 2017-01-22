import curses
import locale
import arrow
import time

from bustracker.departures import Stop
from bustracker.display import BusTrackerDisplay

def main(scr, SLEEP_TIME=10):

    bus_stops = Stop('E1060'), Stop('E1059'), Stop('E1058'), Stop('E1057'), Stop('E1116', services=['550',], max_display=4)

    btd = BusTrackerDisplay(scr, bus_stops)

    locale.setlocale(locale.LC_ALL, '')
    code = locale.getpreferredencoding()

    curses.start_color()
    curses.use_default_colors()
    scr.keypad(True)
    scr.nodelay(1)
    curses.noecho()

    # color pair 1 = red text on white background
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    btd.draw_all_stops()
    scr.refresh()

    char = -1
    while char != 27:
        time.sleep(SLEEP_TIME)
        btd.draw_all_stops()
        scr.refresh()
        char = scr.getch()

    curses.endwin()



if __name__ == '__main__':
    curses.wrapper(main)

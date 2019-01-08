import curses
import argparse
import locale
import arrow
import time

from os import path

from bustracker.departures import Stop
from bustracker.display import BusTrackerDisplay
from bustracker.config import load_config
from bustracker.weather import WeatherController

def launch_bt():
    parser = argparse.ArgumentParser(description='Display departures for Helsinki area buses/trams/trains/metro')
    parser.add_argument('--config', dest='config',
                        default='~/.bustracker.yaml',
                        help='path to configuration file',
                        )

    args = parser.parse_args()
    curses.wrapper(main, args.config)

def main(scr, config_path, SLEEP_TIME=10):

    config_path = path.expanduser(config_path)
    if not path.exists(config_path):
        raise Exception("Config file not found: {}".format(config_path))
    config = load_config(config_path)
    stops = config['stops']

    weather = None
    if 'weather' in config:
        weather = WeatherController(config['weather'])

    btd = BusTrackerDisplay(scr, stops, weather)

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
    launch_bt()

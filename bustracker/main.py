import curses
import locale
import arrow

from bustracker.departures import Stop

def main(scr, critical_minutes=10, warning_minutes=15):

    bus_stops = Stop('E1060'), Stop('E1059'), Stop('E1058'), Stop('E1057'), Stop('E1116', services=['550',])

    locale.setlocale(locale.LC_ALL, '')
    code = locale.getpreferredencoding()

    curses.start_color()
    curses.use_default_colors()
    scr.keypad(True)
    curses.noecho()

    # color pair 1 = red text on white background
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    last_updated = arrow.get().to("Europe/Helsinki")

    scr.addstr("Last updated {}\n\n".format(last_updated.format("HH:mm") ))
    scr.refresh()

    for stop in bus_stops:
        scr.addstr(stop.name, curses.A_BOLD)
        scr.addstr('\n')
        if not stop.latest_departures:
            scr.addstr("\tNo buses/trains/trams\n")
            continue

        for dep in stop.latest_departures:
            scr.addstr('\t')
            scr.addstr(dep.train)
            scr.addstr('\t')
            scr.addstr(dep.destination)

            scr.addstr(' ' * (26 - len(dep.destination)))

            minutes_left = dep.minutes_left()

            if minutes_left < critical_minutes:
                color = 1  # RED
            elif minutes_left <= warning_minutes:
                color = 2  # Yellow
            else:
                color = 0  # green

            scr.addstr(dep.departure.format('HH:mm'))
            scr.addstr('\t')
            scr.addstr(dep.departure.humanize(), curses.color_pair(color))
            scr.addstr('\n')

        scr.refresh()

    scr.refresh()
    scr.getch()

    curses.endwin()


if __name__ == '__main__':
    curses.wrapper(main)

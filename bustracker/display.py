import arrow
import curses



class BusTrackerDisplay:
    destination_width = 26
    critical_minutes=10
    warning_minutes=15

    def __init__(self, scr, stops):
        '''
        :param scr:  Ncurses screen
        '''
        self.scr = scr
        self.stops = stops
        self.debug = False


    @property
    def next_update_duration(self):
        departures = [s.latest_departures for s in self.stops]
        time_left = [d[0].minutes_left() for d in departures if d and d[0].minutes_left() > 0]
        return min(time_left) * 60

    def update_all_stops(self):
        for stop in self.stops:
            stop._update()


    def draw_all_stops(self):
        self.scr.clear()
        self.last_updated = arrow.get()
        self.scr.addstr("Last updated {}\n\n".format(self.last_updated.to("Europe/Helsinki").format("HH:mm")))
        self.scr.refresh()

        for stop in self.stops:
            self.draw_stop(stop)
            self.scr.refresh()

        self.do_update()

    def do_update(self):
        if self.next_update_duration <= 1:
            if self.debug:
                self.scr.addstr("\nUpdating departure times....")
                self.scr.refresh()

            self.update_all_stops()

        elif self.debug:
            self.scr.addstr("\nUpdating in {} seconds".format(self.next_update_duration))
            self.scr.refresh()


    def draw_stop(self, stop):
        self.scr.addstr(stop.name, curses.A_BOLD)
        self.scr.addstr('\n')
        if not stop.latest_departures:
            self.scr.addstr("\tNo buses/trains/trams\n")
            return

        for dep in stop.latest_departures:
            minutes_left = dep.minutes_left()
            if minutes_left < 0:
                continue

            self.scr.addstr('\t')
            self.scr.addstr(dep.train)
            self.scr.addstr('\t')
            self.scr.addstr(dep.destination)

            self.scr.addstr(' ' * (self.destination_width - len(dep.destination)))


            if minutes_left < self.critical_minutes:
                color = 1  # RED
            elif minutes_left <= self.warning_minutes:
                color = 2  # Yellow
            else:
                color = 0  # green

            self.scr.addstr(dep.departure.format('HH:mm'))
            self.scr.addstr('\t')
            self.scr.addstr(dep.departure.humanize(), curses.color_pair(color))
            self.scr.addstr('\n')


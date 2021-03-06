import arrow
import curses

from requests.exceptions import ConnectionError

class BusTrackerDisplay:
    critical_minutes=10
    warning_minutes=15
    max_destination_gap=26

    def __init__(self, scr, stops, weather):
        '''
        :param scr:  Ncurses screen
        '''
        self.scr = scr
        self.stops = stops
        self.debug = False
        self.weather = weather
        self.first = True 

    @property
    def next_update_duration(self):
        departures = [s.latest_departures for s in self.stops]
        time_left = [d[0].minutes_left() for d in departures if d and d[0].minutes_left() > 0]
        return min(time_left) * 60

    def update_stops(self):
        for stop in self.stops:
            departures = stop.latest_departures
            valid_minutes_left = [d.minutes_left()*60 for d in departures]

            if valid_minutes_left and min(valid_minutes_left) < 1:
                if self.debug:
                    self.scr.addstr("\n{} in {} - UPDATEING".format(stop.name, min(valid_minutes_left)))
                    self.scr.refresh()
                stop.update()
            elif valid_minutes_left and self.debug:
                self.scr.addstr("\n{} in {}".format(stop.name, min(valid_minutes_left)))
                self.scr.refresh()


    def draw_all_stops(self):
        self.scr.clear()
        self.y, self.x = self.scr.getmaxyx()


        self.last_updated = arrow.get()

        if self.weather:
            weather_string = self.weather.display_string
        else:
            weather_string = ""

        # 17 = last update HH:mm
        width = self.x
        last_update_string = "Last update {}".format(self.last_updated.to("Europe/Helsinki").format("HH:mm"))

        if len(last_update_string) + len(weather_string) > self.x:
            self.scr.addstr("{}\n{}\n".format(last_update_string,weather_string))
        else:
            spaces = self.x - len(last_update_string) - len(weather_string)
            self.scr.addstr("{}{}{}\n\n".format(last_update_string,
                                                " " * spaces,
                                                weather_string))
        if not self.first:
            self.scr.refresh()



        for stop in self.stops:

            try:
                self.draw_stop(stop)
            except curses.error:
                break
            except ConnectionError:
                # No connection
                break
            if not self.first:
                self.scr.refresh()

        try:
            self.update_stops()
        except ConnectionError:
            self.scr.addstr("No connection")

        if self.first:
            self.scr.refresh()
            self.first = False 


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

            width = self.destination_width

            text = "{:>8}    {:<" + "{}".format(width) + "}"
            text = text.format(dep.train, dep.destination)
            self.scr.addstr(text)

            if minutes_left < self.critical_minutes:
                color = 1  # RED
            elif minutes_left <= self.warning_minutes:
                color = 2  # Yellow
            else:
                color = 0  # green

            self.scr.addstr(dep.departure.to("Europe/Helsinki").format('HH:mm'))

            text = " {}".format(dep.departure.humanize())
            self.scr.addstr(text, curses.color_pair(color))
            self.scr.addstr('\n')

    @property
    def destination_width(self):
        width = self.x - 8 - 4 - 5 - 14

        return min(width, self.max_destination_gap)


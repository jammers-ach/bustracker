import requests
import arrow

from math import floor

url = 'http://api.reittiopas.fi/hsl/prod/'


class Departure:
    line_data = {}

    def __init__(self, train, destination, departure):
        '''
        :param str train: e.g. 'L'
        :param str destination: e.g. 'Helsinki'
        :param arrow departure_time: when the transport will leave
        '''
        self.train = train
        self.destination = destination
        self.departure = departure

    def minutes_left(self, time=None):
        if time == None:
            time = arrow.get()
        minutes_left = (self.departure - time).total_seconds() / 60
        return minutes_left

    @classmethod
    def from_json(cls, json_data, user, password, timezone="Europe/Helsinki"):
        '''
        Turns a departure (e.g. {'code': '3002A 2', 'date': 20170117, 'time': 2219})
        into something that can be parsed by a human
        '''

        line_info = cls._line_info(json_data['code'], user, password)

        train_code = line_info['code_short']
        destination = line_info['line_end']

        departure_date= arrow.get(str(json_data['date']),'YYYYMMDD')
        departure_time = json_data['time']

        if departure_time > 2359:
            departure_time -= 2400
            departure_date = departure_date.replace(days=1)

        hours = floor(departure_time / 100)
        minutes = departure_time - (hours * 100)

        departure = departure_date.replace(hour=hours, minute=minutes)
        departure = departure.replace(tzinfo=timezone)

        return cls(train_code, destination, departure)


    @classmethod
    def _line_info(cls, line_code, user, password):
        if line_code not in cls.line_data:
            data = {
                'query':line_code,
                'request':'lines',
                'user':user,
                'pass':password,
            }
            resp = requests.get(url, params=data)
            resp.raise_for_status()
            data = resp.json()
            for i in data:
                cls.line_data[i['code']] = i

        return cls.line_data[line_code]




class Stop:
    # default time limit of 62 as we want to see departures in exactly 1 hour
    def __init__(self, stop_code, user, password, time_limit=62, services=None, stop_type="Train", max_display=None):
        """
        :param str stop_code:
        :param str user: username for reittiopas api
        :param str password: password for reittiopas api
        :param int time_limit: when we get departures get them for this many minutes
        :param None|array services: None, show all stops, else only show trains with these codse
             e.g. None shows all, ['A','L'] shows only trains A and L
        :parap str stop_tpe: Bus/ Train/Tram etc
        :param None|int max_display: how many departures to keep at one time
        """
        self.stop_code = stop_code
        self.time_limit = time_limit
        self.services = services
        self.stop_type = stop_type
        self.last_data = None
        self.max_display = max_display
        self.user = user
        self.password = password

    def update(self):
        self._update()
        self._remove_expired_departures()

    def _update(self):
        self.last_data = Stop._get_next_departures(self.stop_code, self.user, self.password)[0]

    def _remove_expired_departures(self):
        for d in self.last_data['departures']:
            dep = Departure.from_json(d, self.user, self.password)
            if dep.minutes_left() < 0:
                self.last_data['departures'].remove(d)

    @property
    def latest_departures(self):

        if not self.last_data:
            self._update()

        departures = [Departure.from_json(d, self.user, self.password) for d in self.last_data['departures']]
        if self.services:
            departures = [d for d in departures if d.train in self.services]

        if self.max_display:
            return departures[0:self.max_display]
        else:
            return departures

    @property
    def name(self):
        if not self.last_data:
            self._update()

        return self.last_data['name_fi']

    @staticmethod
    def _get_next_departures(stop_id, user, password, data_ovr={}):
        """Gets the next: set of departures for a set of stops
        see http://developer.reittiopas.fi/pages/en/http-get-interface/1.2.1.php

        :param str stop_id: text of the stop e.g. E1060
        :param dict data_ovr: override for the get paramsif anything needs to be added to request
        :returns: requests.Response"""
        data = {
            'user':user,
            'pass':password,
            'code':stop_id,
            'request':'stop',
            'time_limit':60,
            'request':'stop'
        }
        data.update(data_ovr)

        resp = requests.get(url, params=data)
        resp.raise_for_status()
        return resp.json()

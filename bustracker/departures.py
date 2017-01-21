import requests
import arrow
from bustracker.auth import USER, PASS

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


    @classmethod
    def from_json(cls, json_data, timezone="Europe/Helsinki"):
        '''
        Turns a departure (e.g. {'code': '3002A 2', 'date': 20170117, 'time': 2219})
        into something that can be parsed by a human
        '''

        line_info = cls._line_info(json_data['code'])

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
    def _line_info(cls, line_code):
        if line_code not in cls.line_data:
            data = {
                'query':line_code,
                'request':'lines',
                'user':USER,
                'pass':PASS,
            }
            resp = requests.get(url, params=data)
            resp.raise_for_status()
            data = resp.json()
            for i in data:
                cls.line_data[i['code']] = i

        return cls.line_data[line_code]




class Stop:
    def __init__(self, stop_code, time_limit=60, filter_codes=[], stop_type="Train"):
        """
        :param str stop_code:
        """
        self.stop_code = stop_code
        self.time_limit = time_limit
        self.filter_codes = filter_codes
        self.stop_type = stop_type
        self._update()

    def _update(self):
        self.last_data = Stop._get_next_departures(self.stop_code)[0]

    @property
    def latest_departures(self):
        return [Departure.from_json(d) for d in self.last_data['departures']]

    @property
    def name(self):
        return self.last_data['name_fi']

    @staticmethod
    def _get_next_departures(stop_id, data_ovr={}):
        """Gets the next: set of departures for a set of stops
        see http://developer.reittiopas.fi/pages/en/http-get-interface/1.2.1.php

        :param str stop_id: text of the stop e.g. E1060
        :param dict data_ovr: override for the get paramsif anything needs to be added to request
        :returns: requests.Response"""
        data = {
            'user':USER,
            'pass':PASS,
            'code':stop_id,
            'request':'stop',
            'time_limit':60,
            'request':'stop'
        }
        data.update(data_ovr)

        resp = requests.get(url, params=data)
        resp.raise_for_status()
        return resp.json()

import requests
import arrow

from math import floor

url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'

class Departure:

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
    def from_json(cls, json_data, timezone="Europe/Helsinki"):
        '''
        Turns a departure (e.g. {'code': '3002A 2', 'date': 20170117, 'time': 2219})
        into something that can be parsed by a human
        '''

        train_code = json_data['code_short']
        destination = json_data['destination']
        departure = json_data['date']

        return cls(train_code, destination, departure)



class Stop:
    # default time limit of 62 as we want to see departures in exactly 1 hour
    def __init__(self, stop_code, time_limit=62, services=None, stop_type="Train", max_display=None):
        """
        :param str stop_code:
        :param int time_limit: when we get departures get them for this many minutes
        :param None|array services: None, show all stops, else only show trains with these codse
             e.g. None shows all, ['A','L'] shows only trains A and L
        :parap str stop_tpe: Bus/ Train/Tram etc
        :param None|int max_display: how many departures to keep at one time
        """
        self.stop_id = None
        self.stop_code = stop_code
        self.time_limit = time_limit
        self.services = services
        self.stop_type = stop_type
        self.last_data = None
        self.max_display = max_display
        self.stop_name = None

    def update(self):
        self._update()
        self._remove_expired_departures()

    def _update(self):
        self.last_data = self.get_next_departures()

    def _remove_expired_departures(self):
        for d in self.last_data['departures']:
            dep = Departure.from_json(d)
            if dep.minutes_left() < 0:
                self.last_data['departures'].remove(d)

    @property
    def latest_departures(self):

        if not self.last_data:
            self._update()

        departures = [Departure.from_json(d) for d in self.last_data['departures']]
        if self.services:
            departures = [d for d in departures if d.train in self.services]

        if self.max_display:
            return departures[0:self.max_display]
        else:
            return departures

    @property
    def name(self):
        if not self.stop_name:
            self._update()

        return self.stop_name

    def get_next_departures(self, data_ovr={}):
        """Gets the next: set of departures for a set of stops
        see https://digitransit.fi/en/developers/apis/1-routing-api/stops/

        :param str stop_id: text of the stop e.g. E1060
        :param dict data_ovr: override for the get paramsif anything needs to be added to request
        :returns: requests.Response"""

        # Get the stop id
        if not self.stop_id:
            query = '''{{
    stops(name: "{}") {{
        gtfsId
        name
    }}
    }}'''.format(self.stop_code)
            headers = {'content-type': 'application/graphql'}
            resp = requests.post(url, data=query, headers=headers)
            resp.raise_for_status()
            stop_info = resp.json()['data']
            assert len(stop_info["stops"]) ==1, "Too many stops in response for {}".format(self.stop_code)
            self.stop_id = stop_info["stops"][0]["gtfsId"]
            self.stop_name = stop_info["stops"][0]["name"]

        # now get the departure info
        query = '''
        {{
  stop(id: "{}") {{
      stoptimesWithoutPatterns(numberOfDepartures: 3 omitNonPickups: true) {{
      stop {{
        platformCode
        name
      }}
      serviceDay
      scheduledArrival
      scheduledDeparture
      trip {{
        route {{
          shortName
        }}
        tripHeadsign
        directionId
      }}
    }}
  }}
}}
        '''.format(self.stop_id)

        headers = {'content-type': 'application/graphql'}
        resp = requests.post(url, data=query, headers=headers)
        resp.raise_for_status()
        departures = resp.json()['data']

        return Stop.parse_new_data(departures)

    @classmethod
    def parse_new_data(cls, departures):
        '''
        Parses a new format of departure info, into something
        resembling the old format
        '''
        data = []
        for s in departures['stop']['stoptimesWithoutPatterns']:
            data.append({
                'code_short': s['trip']['route']['shortName'],
                'destination': s['trip']['tripHeadsign'],
                'date': cls._from_date(s['serviceDay'], s['scheduledDeparture']),
            })

        return {
            'departures': data
        }

    @classmethod
    def _from_date(cls, day, time, timezone="Europe/Helsinki"):
        '''
        returns an arrow from a date and time from the format
        of the reitiopass api
        "Scheduled arrival time. Format: seconds since midnight of the departure date"
        "Departure date of the trip. Format: Unix timestamp (local time) in seconds."
        '''
        timestamp = day + time
        date = arrow.Arrow.fromtimestamp(timestamp)
        return date

if __name__ == '__main__':
    s = Stop("E1060")
    print(s)

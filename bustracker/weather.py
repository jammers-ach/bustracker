import requests


# Update weather every 30 minutes
DEFAULT_INTERVAL = 30
url = "http://api.openweathermap.org/data/2.5/weather"

class WeatherController:

    def __init__(self, config):
        '''
        :param city: the name of the city to be querying
        :param config: the configuration to use
        '''
        self.api_key = config['api']
        self.city = config['city']
        self.interval = config.get('interval', DEFAULT_INTERVAL)
        self.last_response = None
        self.fetch()

    @property
    def display_string(self):
        if not self.last_response:
            self.fetch()
            return ""
        else:
            return "{}°C {}".format(self.last_response['main']['temp'],
                                  self.last_response['weather'][0]['description'])

    def fetch(self):
        '''Gets the latest weather information'''
        params = {
            'appid': self.api_key,
            'q':self.city,
            'units':'metric'
        }

        response = requests.get(url, params)
        response.raise_for_status()
        self.last_response = response.json()

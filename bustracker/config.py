import yaml
import sys

from bustracker.departures import Stop

def load_config(filename):
    """
    :param str filename: location of config file to laod
    :returns array[Stop]: list of stops
    """
    with open(filename) as f:
        config = yaml.load(f)

    assert 'stops' in config, "No stops in config"

    stops = []
    for stop in config['stops']:
        assert 'code' in stop, 'Missing code for one stop'
        stops.append(Stop(
            stop['code'],
            stop.get('time_limit', 62),
            stop.get('services', None),
            stop.get('stop_type', "Train"),
            stop.get('max_display', None),
        ))

    config['stops'] = stops
    return config



if __name__ == '__main__':
    load_config(sys.argv[1])



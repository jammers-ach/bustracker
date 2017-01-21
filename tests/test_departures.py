import arrow
from bustracker.departures import Departure, Stop

def test_departure_parsing():
    d = Departure.from_json({'code': '3002A 2', 'date': 20170117, 'time': 2219})

    assert d.train == 'A'
    assert d.destination == "Helsinki"
    assert d.departure == arrow.get('2017-01-17 22:19').replace(tzinfo="Europe/Helsinki")

def test_departure_parsing_post_midnight():
    d = Departure.from_json({'code': '3002A 2', 'date': 20170117, 'time': 2401})
    assert d.departure == arrow.get('2017-01-18 00:01').replace(tzinfo="Europe/Helsinki")


    d = Departure.from_json({'code': '3002A 2', 'date': 20170117, 'time': 2601})
    assert d.departure == arrow.get('2017-01-18 02:01').replace(tzinfo="Europe/Helsinki")


def test_departure_parsing_early_morning():
    d = Departure.from_json({'code': '3002A 2', 'date': 20170117, 'time': 1})
    assert d.departure == arrow.get('2017-01-17 00:01').replace(tzinfo="Europe/Helsinki")


    d = Departure.from_json({'code': '3002A 2', 'date': 20170117, 'time': 400})
    assert d.departure == arrow.get('2017-01-17 04:00').replace(tzinfo="Europe/Helsinki")


def test_stop_update():
    s = Stop("E1060")
    # update is called by __init__
    assert s.last_data is not None


def test_stop_departures():
    s = Stop("E1060")
    for d in s.latest_departures:
        assert isinstance(d, Departure)


def test_minutes_left():

    d = Departure.from_json({'code': '3002A 2', 'date': 20170117, 'time': 400})
    assert d.minutes_left(time=arrow.get('2017-01-17 03:40').replace(tzinfo="Europe/Helsinki")) == 20
    assert d.minutes_left(time=arrow.get('2017-01-17 03:39:30').replace(tzinfo="Europe/Helsinki")) == 20.5

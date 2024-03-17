#!/usr/bin/env python3
import datetime
import requests
import asyncio

import python_weather
import math

from secrets import primary_key

url ="https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
stops = ["HSL:2111504", "HSL:2111552", "HSL:2112261", "HSL:2112401"]
excluded_routes = ["520", "553K","553", "550", "522", "522B"]


class bcolors:
    RED = '\033[31m'
    YELLOW = '\033[33m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def do_bus_query(stops, limit=20):
    # Headers for the POST request
    headers = {
        'Content-Type': 'application/graphql',  # Adjust the content type as needed
        'digitransit-subscription-key': primary_key
    }


    body = """{
stops(ids: """ + str(stops).replace('\'','\"') +  """ ) {
name
gtfsId
stoptimesWithoutPatterns(numberOfDepartures: """ + str(limit) + """) {
    realtimeDeparture
    serviceDay
    headsign
    trip {
    route {
        shortName
        mode
    }
    }
}
}
}"""

    response = requests.post(url, data=body, headers=headers)

    if response.status_code == 200:
        return response.json()
    return None

def extract_timetable(stop_data, excluded_routes=[]):

    time = datetime.time()
    departures = stop_data['stoptimesWithoutPatterns']

    timetable = []
    for dep in departures:
        dep_time = datetime.datetime.fromtimestamp(dep["realtimeDeparture"] + dep["serviceDay"])
        route_name = dep["trip"]["route"]["shortName"]
        mode = dep["trip"]["route"]["mode"]
        headsign = dep["headsign"] or ""

        # Hack, the stop returns terminating trains without a headsign
        if route_name == "A" and headsign == "":
            continue

        if route_name not in excluded_routes:
            timetable.append([dep_time, route_name, headsign, mode])

    return timetable


def render_bus_timetable(row_per_stop = 2):
    times = do_bus_query(stops)
    now = datetime.datetime.now()
    for stop in times["data"]["stops"]:
        timetable = extract_timetable(stop, excluded_routes)
        print(f"          {timetable[0][-1]:5}")

        for i, row in enumerate(timetable):
            if i > row_per_stop:
                break
            dep_time, route_name, headsign, mode = row
            print_time = dep_time.strftime("%H:%M")

            time_left = dep_time - now
            mins_left = math.floor(time_left.total_seconds() / 60)
            warning = f"in {mins_left} mins   " if mins_left < 60 else ""
            data = f'        {print_time:<9} {route_name:<5} {warning}'


            if mins_left < 3:
                print(f"{bcolors.RED}{data}{bcolors.ENDC}")
            elif mins_left < 10:
                print(f"{bcolors.YELLOW}{data}{bcolors.ENDC}")
            elif mins_left < (3*60):
                print(data)



async def get_weather(location="Leppävaara"):
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        # fetch a weather forecast from a city
        weather = await client.get(location)

        return weather.current


def draw_home_row():
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")

    try:
        weather = asyncio.run(get_weather())
        weather = f"{weather.temperature}°C {weather.description} {weather.kind.emoji}"
    except Exception:
        weather = ""

    text_len = len(weather)

    print(f"Last updated: {time}{weather:>40}")


def run():
    draw_home_row()
    render_bus_timetable()


if __name__ == "__main__":
    run()

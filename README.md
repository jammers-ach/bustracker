# bustracker
Ncurses application to display the next departures for the HSL area trains/trams/buses/metro

```
Last Updated 21:25

Leppävaaran asema, Laituri 4
        A       Helsinki                  21:26 in seconds
        A       Helsinki                  21:56 in 30 minutes
Vallikatu
        203N    Uusmäki                   21:34 in 8 minutes
        203N    Uusmäki                   22:04 in 38 minutes

```


Primarily intended to be used on a Raspberry Pi with a screen.

## installation

```
python setup.py install
bustracker
```

## Configuration

Get credentials from here: http://developer.reittiopas.fi/pages/en/home.php

Then create a config file: `~/.bustracker.yaml` is the default, unless `--config` is specified

Example config file:
```yaml
username: from reittiopas credentials
password: from reittiopas credentials
stops:
    - code: E1060
      max_display: 4        # Optional, limit the maximum displayed departures to this amount
      time_limit: 60        # Only display departures this many minutes into the future
    - code: E1020

```

## Installing on a Raspberry pi

See `./setup.md`

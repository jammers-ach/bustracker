# Howto setup the bustracker on a raspberry pi with a screen

This guide is primarily created for me in case my SD card dies again and I need to reinstall again.

## Install minibian

Follow instructions here:

https://minibianpi.wordpress.com/

Make sure to resize the image to the full sd card size:
`apt-get install raspi-config`


## Setup wifi

setup wifi: https://www.raspberrypi.org/forums/viewtopic.php?f=66&t=108863

For the wifi chip I have, some combination of:
```
apt-get install firmware-realtek
```
```
wget https://github.com/lwfinger/rtl8188eu/raw/c83976d1dfb4793893158461430261562b3a5bf0/rtl8188eufw.bin -O /lib/firmware/rtlwifi/rtl8188eufw.bin
```
```
modprobe r8188eu
```

## Screen

My screen came from ebay, it's a waveshare clone

```
cat LCD35-show | sed 's/sudo //' | sh
```

### Stopping console login
```
apt-get install kbd
```
edit `/etc/kbd/config`
set 
```
BLANK_TIME=0 
 POWERDOWN_TIME=0
```

also add `consoleblank=0` to `/boot/cmdline.txt`


## Bustracker

get bustracker: 
You can do this without installing git, if space is of concern:
```
wget https://github.com/jammers-ach/bustracker/archive/master.zip && unzip master.zip
```
or
```
git clone git@github.com:jammers-ach/bustracker.git
```

## Install python
```
apt-get install python3
```
```
apt-get install python3-setuptools
```

```
cd bustracker
```
```
python3 setup.py develop
```

check it works
```
bustracker
```

## Getting it to startup on login

After checking the bustracker works

'vi /etc/systemd/system/getty@tty1.service.d/override.conf'

'[Service]
ExecStart=
ExecStart=-/root/bustracker/start.sh
StandardInput=tty
StandardOutput=tty'

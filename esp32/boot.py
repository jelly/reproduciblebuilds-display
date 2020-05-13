#
# MIT licensed, see ./LICENSE
#
# Copyright (c) 2019 Jelle van der Waa
# Copyright (c) 2020 Holger Levsen

import time
import network
from machine import SPI, Pin, deepsleep, RTC
import ntptime
import urequests
from generic_dotstar import DotStar

version='23.36'

# Status url
url = 'https://tests.reproducible-builds.org/trbo.status'
# how long the device should sleep before querying the above URL again
sleeptime = 600

#################################################################
#								#
# nothing to customize here!					#
#								#
# configuration is parsed from ./config, see ./config.example,	#
# when using ./deploy2device.sh 				#
#								#
# enjoy!							#
#								#
#################################################################


# Network SSID
ssid = 'SSID'
password = 'PASSWORD'

# time related
ntptime.host = 'NTPHOST'
rtc = RTC()

# Pixel defines
num_pixels = 6
clk = Pin(13, Pin.OUT)
dout = Pin(15, Pin.OUT)
pixels = DotStar(clk, dout, num_pixels)


def show_version():
    print('version '+version)
    print()


def show_logo():
    print('+------------------------------------------------------------+')
    print('|                          ~++++~~                           |')
    print('|                         ~++++++++~                         |')
    print('|                        ~++++++++++~                        |')
    print('|                        ~++++++++++~                        |')
    print('|                 +~      +++++++~+~      ~+~                |')
    print('|              ~++o+        ~~++~~~       +oo~               |')
    print('|             ~oooo+                      +ooo+~~            |')
    print('|            +ooooo+                      +ooooo~            |')
    print('|            +ooooo++~+~~~~~      ~~+~~~~+oooooo+            |')
    print('|            +oooooooooooo+~      ~+oooooooooooo~            |')
    print('|            +ooooooooo++~          ~+oooooooooo+            |')
    print('|            +++++o++++~             ~~++++++++~~            |')
    print('|  ~~~~+~~                               ~          ~~++~~   |')
    print('|~~++++++++~                                      ~++++++++~ |')
    print('|~++++++++++~                                    ~++++++++++~|')
    print('|+++++++++++                                     ~+++++++++++|')
    print('| +++++++++~     ~~~ ~                    ~~      ~+++++++++ |')
    print('|  ~~+++~~        +o~~~                  +o+       ~~~+~+~   |')
    print('|                ~ooo++~~             ~+ooo+~                |')
    print('|                ~oooo+~~            ~ooooo+                 |')
    print('|        ~~~~~~~~~+oooo+~            +oooooo~~~~~~~~         |')
    print('|         +ooooooo+oooo+~            +oooooooooooo++         |')
    print('|           +ooooooooooo~            ~oooooooooo++           |')
    print('|            ~++++o+ooo+~            ~++ooo+o+++~            |')
    print('|                          ~~~~~~                            |')
    print('|                         ~++~+++++~                         |')
    print('|                        ~++++++++++~                        |')
    print('|                        ~~+++++++++~                        |')
    print('|                        ~~++++++++~                         |')
    print('|                         ~~+++++~~                          |')
    print('+------------------------------------------------------------+')
    print()
    print('Many thanks to Jelle!')
    print('Based on https://github.com/jelly/reproduciblebuilds-display')
    print()


def pretty_number(i):
    if i < 10:
        pretty_number = '0' + str(i)
    else:
        pretty_number = str(i)

    return pretty_number


def pretty_time():
    hour = pretty_number(int(rtc.datetime()[4]))
    minute = pretty_number(int(rtc.datetime()[5]))
    pretty_time = hour + ':' + minute + ' UTC'
    return pretty_time


def uptime_time():
    try:
        ntptime.settime()
        current_time = pretty_time()
        print('The time from NTP is ' + current_time)
        print('Debug info: ', rtc.datetime())
    except Exception:
        print('Cannot update time from NTP.')
    print()


def redefine_intensity_by_hour():
    current_time = pretty_time()
    # time is in UTC, mycropython doesnt do timezones
    if rtc.datetime()[4] >= 17 and rtc.datetime()[4] < 22:
        print(current_time, '- setting display intensity for twilight.')
        intensity = 8
    elif rtc.datetime()[4] >= 22 or rtc.datetime()[4] <= 6:
        print(current_time, '- setting display intensity for night.')
        intensity = 1
    elif rtc.datetime()[4] <= 12 and rtc.datetime()[4] >= 11:
        print(current_time, '- setting display intensity for noon.')
        intensity = 31
    else:
        print(current_time, '- setting display intensity for daytime.')
        intensity = 23

    return intensity

def connectwifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    print('Connecting to', ssid)

    # Wait at maximum for 10 seconds since connecting can be slow
    station.connect(ssid,password)
    counter = 10

    while not station.isconnected():
        if counter < 0:
            print('Could not connect to', ssid)
            break
        time.sleep(1)
        counter = counter - 1

    return station


def staticdisplay(color):
    for i in range(0, num_pixels):
        pixels[i] = color
    pixels.show()


def get_repro_status():
    print('Trying to download', url)
    try:
        r = urequests.get(url)
    except Exception:
        print('Unable to get URL!')
        staticdisplay(repro_color)
        return
    try:
        print('Defining color based on trbo.status', (int(r.text)))
        g = int(r.text)
        o = 255-int(r.text)
        status_color = (o, g, 23, intensity)
    except Exception:
        print('Unable to parse response.')
	red_color = (204, 0, 0, intensity)
        staticdisplay(red_color)
        return
    staticdisplay(status_color)
    print('Display color uses intensity', intensity)


#
# main
#
show_logo()
show_version()
# Add sleep to allow ctrl-c
print('Sleeping for 3 seconds so you can press CTRL-C.')
time.sleep(3)

station = connectwifi()
uptime_time()

while True:
    intensity = redefine_intensity_by_hour()
    repro_color = (30, 91, 150, intensity)
    if station.isconnected():
        get_repro_status()
    else:
        staticdisplay(repro_color)
        print('Disconnected. Rebooting in 10 seconds.')
	# ctrl-c is not possible during deepsleep
        deepsleep(10000)

    print('Sleeping for ' + str(sleeptime) + ' seconds, press CTRL-C to interrupt.')
    time.sleep(sleeptime)


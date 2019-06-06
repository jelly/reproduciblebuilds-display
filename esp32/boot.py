import time

import network
from machine import SPI, Pin, deepsleep

import urequests

from generic_dotstar import DotStar

# Status url
url = 'https://jenkins.debian.net/view/reproducible/view/Node_maintenance/job/reproducible_node_health_check_amd64_jenkins/badge/icon'

# Pixel defines
num_pixels = 6
clk = Pin(13, Pin.OUT)
dout = Pin(15, Pin.OUT)
pixels = DotStar(clk, dout, num_pixels)

# (r, g, b, intensity)
intensity = 0.2
repro_color = (30, 91, 150, intensity)
green_color = (68, 204, 17, intensity)
red_color = (204, 0, 0, intensity)

# Network SSID
ssid = 'hamburg.freifunk.net'

def connectwifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    print('connecting to', ssid)
    station.connect(ssid)
    counter = 5
    while not station.isconnected():
        if counter < 0:
            print('wifi not found')
            break
        time.sleep(1)
        counter = counter - 1

    return station


def staticdisplay(color):
    for i in range(0, num_pixels):
        pixels[i] = color
    pixels.show()


def get_repro_status():
    try:
        r = urequests.get(url)
    except Exception:
        print('unable to get status')
        staticdisplay(repro_color)
        return

    if 'passing' in r.text:
        print('status passed')
        staticdisplay(green_color)
    else:
        print('status failed')
        staticdisplay(red_color)


station = connectwifi()

if station.isconnected():
    print('connected get repro status')
    get_repro_status()
else:
    staticdisplay(repro_color)

# Add sleep to allow ctrl-c
time.sleep(10)

# Sleep for 60 seconds
deepsleep(60000)
